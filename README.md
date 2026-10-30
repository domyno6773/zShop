# zShop — Wii U eShop restoration research

> **Status: experimental, desktop-only prototype. Not a Wii U plugin, not an installable shop.**

zShop explores restoring a usable catalog and navigation experience **inside the original Nintendo Wii U eShop application**, on a console running Aroma. The Nintendo applet is the target UI host; replacing it with a homebrew application is **not** the design goal.

The supplied **newShop.wps / uShop Access v2.2.0-safe** was studied as an external reference, **not** accepted as safe or reused as a binary in this repository. The observed problems on a 5.5.5E console were: Best Sellers and New Releases can trap navigation; other categories return Home; titles are repeated. An update from an older Aroma release fixed the incompatible-plugin loader error but **not** those catalog issues. They could be server-side; the cause has not yet been verified.

## What is here

- `backend.py`: localhost-only, dependency-free diagnostic catalog server (Python 3.9+). Plain HTML and links designed to be a conservative starting point for the Wii U's older browser.
- `catalog.example.json`: **fictional** sample titles; no real games or content URLs.
- `tools/inspect_wps.py`: passive ELF/WPS inspector. It reads a file you provide but never executes, patches or uploads it.
- `tests/`: tests for navigation, escaping, parsing and disabled installs.
- `docs/ROADMAP.md`: milestones, architecture and safety gates.

## Run locally

```sh
python backend.py
# open http://127.0.0.1:8080/ninja/wood_index.html
python -m unittest discover -s tests -v
python tools/inspect_wps.py "newShop(1).wps" -o report.json
```

The original binary is deliberately **not committed**; the inspector test skips itself when it is not locally available. By default the demo listens only on 127.0.0.1:8080; it cannot be used by a Wii U on another device without further deliberate development and testing.

## Non-goals and constraints

- No proprietary eShop HTML, Nintendo branding assets or full Nintendo interface clone committed.
- No credential collection, ticket forging, license bypassing, or unaudited redirects of Nintendo authentication/commerce services.
- No SSL bypass, IOSU memory patching, automatic installs or changes to console firmware.
- Download support, if added later, must use legal/authorized content and preserve platform access checks.
- The test backend does **not** prove the native eShop API, browser history, HOME or B behavior on console.

## Milestones

See [ROADMAP](docs/ROADMAP.md). First verify the eShop navigation and its native browser APIs on **real hardware**; only then build a minimal Aroma WUPS adapter and connect it to an explicitly configured backend. At this stage, **do not copy any files from this repository to the Wii U SD card**.

## Technical references

- [Pretendo Grove](https://github.com/PretendoNetwork/Grove) — archived research on native eShop JavaScript APIs.
- [Aroma](https://github.com/wiiu-env/Aroma)
- [Inkay](https://github.com/PretendoNetwork/Inkay)
- [Ninja server notes](https://github.com/kinnay/NintendoClients/wiki/Ninja-Server)

This repository is a research prototype, not an official Nintendo/Pretendo project.
