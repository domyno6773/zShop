#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <exception>
#include <string_view>

#include <coreinit/filesystem.h>
#include <netdb.h>
#include <wups.h>
#include <wups/config/WUPSConfigCategory.h>
#include <wups/config/WUPSConfigItemBoolean.h>
#include <wups/config/WUPSConfigItemIPAddress.h>
#include <wups/config/WUPSConfigItemStub.h>
#include <wups/config_api.h>

// v0.2.0: eShop-only, opt-in DNS routing for the existing Pretendo/Inkay applet.
// No Inkay modification, memory patches, IOSU access, ticket or title handling.
WUPS_PLUGIN_NAME("zShop");
WUPS_PLUGIN_DESCRIPTION("Local eShop catalog routing compatible with stock Inkay");
WUPS_PLUGIN_VERSION("v0.2.0-alpha");
WUPS_PLUGIN_AUTHOR("domyno6773 / zShop contributors");
WUPS_PLUGIN_LICENSE("MIT");

WUPS_USE_WUT_DEVOPTAB();
WUPS_USE_STORAGE("zshop_diagnostic");

namespace {
constexpr char kProbeKey[] = "enablePassiveProbe";
constexpr char kRouteKey[] = "enableLocalRoute";
constexpr char kAddressKey[] = "localBackendIp";
constexpr char kAppletPath[] = "vol/content/initial.oma";

// Inkay already changes the Nintendo applet URL to this HTTP hostname and
// adds it to the browser allowlist. Do not modify Inkay; redirect DNS only
// in the eShop process. Do NOT intercept any ECS/IAS/NUS/CCS/account hosts.
constexpr char kInkayShopHost[] = "samurai.wup.shop.pretendo.cc";

std::atomic_bool sProbeEnabled{false};
std::atomic_bool sRouteEnabled{false};
std::atomic_bool sSawApplet{false};
std::atomic_bool sSawInkayHost{false};
std::atomic_bool sRoutedHost{false};
std::atomic<uint32_t> sLocalAddress{0};

// These addresses are intentionally limited to RFC 1918 local networks.
// No implicit public server, loopback, or third-party login host allowed.
bool isPrivateNetwork(uint32_t ip) {
    const uint8_t a = static_cast<uint8_t>(ip >> 24);
    const uint8_t b = static_cast<uint8_t>(ip >> 16);
    return a == 10 || (a == 172 && b >= 16 && b <= 31) ||
           (a == 192 && b == 168);
}

bool makeBackendAddress(char (&out)[16]) {
    if (!sRouteEnabled.load(std::memory_order_relaxed)) {
        return false;
    }
    const uint32_t ip = sLocalAddress.load(std::memory_order_relaxed);
    if (!isPrivateNetwork(ip)) {
        return false;
    }
    const int len = std::snprintf(out, sizeof(out), "%u.%u.%u.%u",
                                  (ip >> 24) & 0xff, (ip >> 16) & 0xff,
                                  (ip >> 8) & 0xff, ip & 0xff);
    return len > 0 && len < static_cast<int>(sizeof(out));
}

bool isShopHostname(const char *name) {
    return name != nullptr && std::strcmp(name, kInkayShopHost) == 0;
}

bool matchesAppletPath(const char *path) {
    if (path == nullptr) {
        return false;
    }
    const size_t pathLen   = std::strlen(path);
    const size_t targetLen = sizeof(kAppletPath) - 1;
    if (pathLen < targetLen) {
        return false;
    }
    return std::strcmp(path + pathLen - targetLen, kAppletPath) == 0;
}

void probeChanged(ConfigItemBoolean *item, bool enabled) {
    if (item != nullptr && std::string_view(item->identifier) == kProbeKey) {
        sProbeEnabled.store(enabled, std::memory_order_relaxed);
        WUPSStorageAPI::Store(kProbeKey, enabled);
    }
}

void routeChanged(ConfigItemBoolean *item, bool enabled) {
    if (item != nullptr && std::string_view(item->identifier) == kRouteKey) {
        sRouteEnabled.store(enabled, std::memory_order_relaxed);
        WUPSStorageAPI::Store(kRouteKey, enabled);
    }
}

void addressChanged(ConfigItemIPAddress *item, uint32_t ip) {
    if (item != nullptr && std::string_view(item->identifier) == kAddressKey) {
        sLocalAddress.store(ip, std::memory_order_relaxed);
        WUPSStorageAPI::Store(kAddressKey, ip);
    }
}

WUPSConfigAPICallbackStatus configOpened(WUPSConfigCategoryHandle rootHandle) {
    try {
        WUPSConfigCategory root(rootHandle);
        root.add(WUPSConfigItemBoolean::Create(
            kProbeKey, "Enable passive eShop detection", false,
            sProbeEnabled.load(std::memory_order_relaxed), probeChanged));
        root.add(WUPSConfigItemBoolean::Create(
            kRouteKey, "Route eShop to LAN backend (PORT 80)", false,
            sRouteEnabled.load(std::memory_order_relaxed), routeChanged));
        root.add(WUPSConfigItemIPAddress::Create(
            kAddressKey, "Backend PC IPv4 (LAN)", 0,
            sLocalAddress.load(std::memory_order_relaxed), addressChanged));
        root.add(WUPSConfigItemStub::Create(
            sSawApplet.load(std::memory_order_relaxed)
                ? "eShop initial.oma: observed"
                : "eShop initial.oma: not observed"));
        root.add(WUPSConfigItemStub::Create(
            sSawInkayHost.load(std::memory_order_relaxed)
                ? "Inkay eShop hostname: observed"
                : "Inkay eShop hostname: not observed"));
        root.add(WUPSConfigItemStub::Create(
            sRoutedHost.load(std::memory_order_relaxed)
                ? "Local DNS route: attempted"
                : "Local DNS route: not attempted"));
        root.add(WUPSConfigItemStub::Create(
            isPrivateNetwork(sLocalAddress.load(std::memory_order_relaxed))
                ? "LAN address: accepted"
                : "LAN address: set a private-network IP first"));
        root.add(WUPSConfigItemStub::Create(
            "Requires Inkay ON and HTTP server on LAN port 80"));
        root.add(WUPSConfigItemStub::Create(
            "No downloads, logins, SSL bypass or IOSU patches"));
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
    bool probe = false;
    bool route = false;
    uint32_t ip = 0;
    // Read legacy opt-in probe setting and two new route settings.
    // Failure leaves routing OFF, IP 0.0.0.0.
    if (WUPSStorageAPI::GetOrStoreDefault(kProbeKey, probe, false) ==
        WUPS_STORAGE_ERROR_SUCCESS) {
        sProbeEnabled.store(probe, std::memory_order_relaxed);
    }
    if (WUPSStorageAPI::GetOrStoreDefault(kAddressKey, ip, uint32_t{0}) ==
        WUPS_STORAGE_ERROR_SUCCESS) {
        sLocalAddress.store(ip, std::memory_order_relaxed);
    }
    if (WUPSStorageAPI::GetOrStoreDefault(kRouteKey, route, false) ==
        WUPS_STORAGE_ERROR_SUCCESS) {
        sRouteEnabled.store(route, std::memory_order_relaxed);
    }

    WUPSConfigAPIOptionsV1 configOptions = {.name = "zShop (experimental)"};
    WUPSConfigAPI_Init(configOptions, configOpened, configClosed);
}

// Passive detection remains available on the same applet, with a process
// restriction to reduce interference with other system software.
DECL_FUNCTION(int, FSOpenFile,
              FSClient *client, FSCmdBlock *block, const char *path,
              const char *mode, int *handle, int error) {
    if (sProbeEnabled.load(std::memory_order_relaxed) && matchesAppletPath(path)) {
        sSawApplet.store(true, std::memory_order_relaxed);
    }
    return real_FSOpenFile(client, block, path, mode, handle, error);
}
WUPS_MUST_REPLACE_FOR_PROCESS(FSOpenFile, WUPS_LOADER_LIBRARY_COREINIT,
                              FSOpenFile, WUPS_FP_TARGET_PROCESS_ESHOP);

// Restrict both DNS hooks to the native eShop process. The URL remains
// http://samurai.wup.shop.pretendo.cc/ninja/wood_index.html?...,
// preserving the allowlist already installed by stock Inkay.
// We change ONLY the name resolved to a LAN IP, never SSL/authentication.
DECL_FUNCTION(int, getaddrinfo, const char *node, const char *service,
              const struct addrinfo *hints, struct addrinfo **result) {
    if (!isShopHostname(node)) {
        return real_getaddrinfo(node, service, hints, result);
    }
    sSawInkayHost.store(true, std::memory_order_relaxed);
    char ip[16];
    if (makeBackendAddress(ip)) {
        const int status = real_getaddrinfo(ip, service, hints, result);
        if (status == 0) {
            sRoutedHost.store(true, std::memory_order_relaxed);
            return status;
        }
    }
    return real_getaddrinfo(node, service, hints, result);
}
WUPS_MUST_REPLACE_FOR_PROCESS(getaddrinfo, WUPS_LOADER_LIBRARY_NSYSNET,
                              getaddrinfo, WUPS_FP_TARGET_PROCESS_ESHOP);

DECL_FUNCTION(struct hostent *, gethostbyname, const char *name) {
    if (!isShopHostname(name)) {
        return real_gethostbyname(name);
    }
    sSawInkayHost.store(true, std::memory_order_relaxed);
    char ip[16];
    if (makeBackendAddress(ip)) {
        struct hostent *host = real_gethostbyname(ip);
        if (host != nullptr) {
            sRoutedHost.store(true, std::memory_order_relaxed);
            return host;
        }
    }
    return real_gethostbyname(name);
}
WUPS_MUST_REPLACE_FOR_PROCESS(gethostbyname, WUPS_LOADER_LIBRARY_NSYSNET,
                              gethostbyname, WUPS_FP_TARGET_PROCESS_ESHOP);
