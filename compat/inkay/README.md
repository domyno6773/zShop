# Inkay/Pretendo coexistence research

**Status: source-level proof of concept only. NOT a finished Pretendo-compatible zShop. Do not replace your currently working Inkay installation with this experimental build.**

## Verified cause (upstream Inkay commit `f3a18d7021f31b9af30057f8e743a2e3723096c0`)

Pretendo Inkay includes an eShop-specific `FSOpenFile` hook on
`vol/content/initial.oma` in
[`src/patches/eshop_applet.cpp`](https://github.com/PretendoNetwork/Inkay/blob/f3a18d7021f31b9af30057f8e743a2e3723096c0/src/patches/eshop_applet.cpp).
It overwrites an initial Nintendo Ninja URL in memory with a Pretendo Samurai URL,
and updates the eShop browser allowlist. The hook is installed via
`patchEshop();` in
[`src/main.cpp`](https://github.com/PretendoNetwork/Inkay/blob/f3a18d7021f31b9af30057f8e743a2e3723096c0/src/main.cpp).

Inkay also rewrites IOSU-side URLs independently in `src/iosu_url_patches.h`
(e.g. ECS, NUS, account-related), so **skipping `patchEshop()` alone does
not undo all Pretendo shop-related changes**, and cannot by itself provide a
working store or Nintendo account compatibility.

The existing zShop **v0.1.0 is passive**: it does not rewrite the eShop
entry URL. Therefore it does not stop the Pretendo error "This eShop is not
available on Pretendo" (reported as code 377-0001 on test console).

## Research patch

`patch_skip_eshop.py` makes **one change only** to a separate local copy
of the pinned official Inkay source: skip the call `patchEshop();`.
Other Pretendo hooks and URLs are left untouched. This avoids fighting with
two active eShop-specific FSOpenFile hooks. The patch aborts if the upstream
source shape does not match.

A GitHub Action compiles a research WPS/WMS pair for inspection. The artifact
is **not recommended for installation** until isolated hardware testing and
further integration with zShop. This is *not* a plugin that can be copied in
addition to the existing Inkay; Inkay uses a plugin **and** a module which must
match, and two simultaneous versions would conflict.

## Required work before a usable build

1. Confirm that stock Inkay's eShop hook is the cause of the Pretendo error.
2. Decide on a supported eShop-only opt-out for Inkay, preferably an upstream
   configurable option instead of a permanent fork.
3. Extend zShop with its **own opt-in applet page redirect**, maintaining
   the original Nintendo applet/gamepad.
4. Keep all Wii U native account, authentication and commerce services outside
   zShop's redirection and avoid silent fallback to unknown hosts.
5. On hardware, verify original applet entry URL, HOME/B/back navigation,
   other Pretendo services, failed-network behavior and rollback.
6. No download support until license/security flows are reviewed.

## Do not do

- Do NOT disable Pretendo globally as a *permanent* requirement of zShop.
- Do NOT unlink NNID or PNID, reset accounts or expose account credentials.
- Do NOT install an unsigned replacement Inkay pair simply to eliminate an error
  before a real zShop page exists.
- Do NOT claim this patch gives access to the old Nintendo shop.
- Do NOT tamper with Inkay's official GitHub repository or claim a third-party
  fork is supported by Pretendo.

## License

Inkay itself is GPLv3; any redistributed build derived from it must comply
with GPLv3, preserve attribution, and include the complete corresponding source
or a compliant written offer. The research CI pins the public upstream source
and this exact minimal modification so the changes are reproducible.
zShop's standalone MIT-licensed diagnostic module stays separate.
