# Phase 1 — passive WUPS probe (v0.1.0)

**This is an initial diagnostic plugin, not a working custom eShop.**
The original eShop stays unchanged. No catalog redirection or download logic exists yet.

## Why passive first?

The old third-party newShop.wps appears to rewrite Nintendo service URLs and use
optional IOSU patches. We will **not** copy that behavior blindly. First we must
confirm the applet file entry point \`vol/content/initial.oma\` on the target Wii U.

The diagnostic plugin hooks FSOpenFile with the official WUPS API, compares the file
path to the applet entry point and passes **every** call to the original function with
all the original arguments, always returning its original result. When opted in, it
only sets an in-memory "observed" flag if the path matches.

The default is OFF. No files or network data are read, written or sent.
This first build does not change the eShop, and it cannot repair page navigation.

## Compile

The reproducible CI build uses:

- \`ghcr.io/wiiu-env/devkitppc:20260225\`
- \`ghcr.io/wiiu-env/wiiupluginsystem:20260418\`
- the official \`wups_rules\` generated WPS format.

On a machine with Docker:

\`\`\`sh
docker build -f plugin/Dockerfile -t zshop-wups-builder plugin
docker run --rm -v "$PWD/plugin:/project" zshop-wups-builder make
# -> plugin/zShop.wps
\`\`\`

The GitHub Action **Build Aroma diagnostic plugin** compiles \`zShop.wps\`
and provides the artifact under the successful run; CI build success does **not**
prove compatibility with every Aroma version or firmware.

## Hardware testing (opt-in)

**Before using this diagnostic build:**

1. Copy your SD contents to a safe backup.
2. **Rename** existing \`sd:/wiiu/environments/aroma/plugins/newShop.wps\`
   to \`newShop.wps.disabled\` (do not run the two plugins together).
3. Place \`zShop.wps\` under \`sd:/wiiu/environments/aroma/plugins/\`.
4. Start Aroma. Open its plugin menu via **L + D-Pad Down + Minus**.
5. Find **zShop diagnostic**, set **Enable passive eShop detection** to ON.
6. Close the menu, open the stock eShop, then reopen the plugin menu.
   The indicator should say whether \`initial.oma\` was seen in the current
   plugin session. If it remains "not observed", **do not** assume the plugin is broken:
   the file path/hook may differ on this title or build.
7. Try HOME. If the console hangs or a crash occurs, power down, remove
   \`zShop.wps\` from the SD and reboot; you can always put the old plugin back
   **after** removing zShop. Please report the observations, not account data.

Because the official Nintendo eShop is retired for new purchases, its unmodified
pages may no longer be accessible; **the probe can only detect actual file opens**.
An absence of a detection is inconclusive.

## What will happen in Phase 1b

Only after a verified applet entry point and official ContentRedirection API review
will we add an **opt-in, local-only** page replacement and validate UI history/B/HOME
behavior. Never intercept account, payment or title authorization requests.
