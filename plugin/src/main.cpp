#include <atomic>
#include <cstring>
#include <exception>
#include <string_view>

#include <coreinit/filesystem.h>
#include <wups.h>
#include <wups/config/WUPSConfigCategory.h>
#include <wups/config/WUPSConfigItemBoolean.h>
#include <wups/config/WUPSConfigItemStub.h>
#include <wups/config_api.h>

// Phase 1: a PASS-THROUGH diagnostic probe, NOT an eShop redirect.
// No content mutation, filesystem writes, network calls or title installation.
WUPS_PLUGIN_NAME("zShop diagnostic");
WUPS_PLUGIN_DESCRIPTION("Passive eShop entrypoint probe; no redirects or downloads");
WUPS_PLUGIN_VERSION("v0.1.0");
WUPS_PLUGIN_AUTHOR("domyno6773 / zShop contributors");
WUPS_PLUGIN_LICENSE("MIT");

WUPS_USE_WUT_DEVOPTAB();
WUPS_USE_STORAGE("zshop_diagnostic");

namespace {
constexpr char kProbeKey[] = "enablePassiveProbe";
constexpr char kAppletPath[] = "vol/content/initial.oma";

std::atomic_bool sProbeEnabled{false};
std::atomic_bool sSawApplet{false};

bool matchesAppletPath(const char *path) {
    if (path == nullptr) {
        return false;
    }
    const size_t pathLen   = std::strlen(path);
    const size_t targetLen = sizeof(kAppletPath) - 1;
    if (pathLen < targetLen) {
        return false;
    }
    // Match exact suffix; an optional volume prefix is permitted.
    return std::strcmp(path + pathLen - targetLen, kAppletPath) == 0;
}

void probeChanged(ConfigItemBoolean *item, bool enabled) {
    if (item != nullptr && std::string_view(item->identifier) == kProbeKey) {
        sProbeEnabled.store(enabled, std::memory_order_relaxed);
        WUPSStorageAPI::Store(kProbeKey, enabled);
    }
}

WUPSConfigAPICallbackStatus configOpened(WUPSConfigCategoryHandle rootHandle) {
    try {
        WUPSConfigCategory root(rootHandle);
        root.add(WUPSConfigItemBoolean::Create(
            kProbeKey, "Enable passive eShop detection", false,
            sProbeEnabled.load(std::memory_order_relaxed), probeChanged));
        root.add(WUPSConfigItemStub::Create(
            sSawApplet.load(std::memory_order_relaxed)
                ? "eShop initial.oma: observed during this plugin session"
                : "eShop initial.oma: not observed yet"));
        root.add(WUPSConfigItemStub::Create("No network or game downloads; no redirect"));
        root.add(WUPSConfigItemStub::Create("Disable newShop.wps for isolated tests"));
    } catch (const std::exception &) {
        return WUPSCONFIG_API_CALLBACK_RESULT_ERROR;
    }
    return WUPSCONFIG_API_CALLBACK_RESULT_SUCCESS;
}

void configClosed() {
    WUPSStorageAPI::SaveStorage();
}
} // namespace

INITIALIZE_PLUGIN() {
    bool enabled = false; // default off, including on storage errors
    if (WUPSStorageAPI::GetOrStoreDefault(kProbeKey, enabled, false) ==
        WUPS_STORAGE_ERROR_SUCCESS) {
        sProbeEnabled.store(enabled, std::memory_order_relaxed);
    }

    WUPSConfigAPIOptionsV1 configOptions = {.name = "zShop diagnostics"};
    WUPSConfigAPI_Init(configOptions, configOpened, configClosed);
}

// Always call the original FSOpenFile with identical arguments and return result.
// We deliberately do not patch initial.oma until its structure is understood.
DECL_FUNCTION(int, FSOpenFile,
              FSClient *client, FSCmdBlock *block, const char *path,
              const char *mode, int *handle, int error) {
    if (sProbeEnabled.load(std::memory_order_relaxed) && matchesAppletPath(path)) {
        sSawApplet.store(true, std::memory_order_relaxed);
    }
    return real_FSOpenFile(client, block, path, mode, handle, error);
}

WUPS_MUST_REPLACE(FSOpenFile, WUPS_LOADER_LIBRARY_COREINIT, FSOpenFile);
