# zShop roadmap

## Requirement

Keep the **original Nintendo Wii U eShop applet** and its GamePad navigation. Avoid replacing the console app with a normal homebrew front end. A desktop HTML prototype is **not** equivalent to an original eShop experience.

## Observations from real hardware (user-reported)

- Wii U firmware: 5.5.5E, Aroma. Plugin loader originally showed "Incompatible version" with Aroma 0.2.3.
- Updating Aroma allowed newShop.wps to load and the eShop applet to open.
- "Best Sellers" / "New Releases" pages respond visually to taps but Back / My Profile stop navigating.
- "Mario Games" and other categories return Home; titles repeat.
- The report does **not** establish whether the backend or frontend causes these bugs. We need controlled HTTP traces and console navigation tests.

## Phase 1 — local baseline (current)

- [x] Public repository created
- [x] Passive .wps metadata / compressed ELF inspection tool
- [x] Local diagnostic server using /ninja/wood_index.html
- [x] Separate, testable category pages, search, detail and profile
- [x] Default localhost-only, no account, ticket, installation or Nintendo CDN access
- [ ] Collect protocol-compatible page request/response traces on a test console
- [ ] Validate the native Back, B and HOME behaviors in an unmodified applet

## Phase 2 — minimally scoped Aroma adapter

- [ ] Review current WUPS, Aroma and function patcher headers and build requirements.
- [ ] Implement from source, **not a binary patch**, a narrowly scoped redirect of eShop applet entrypoint only.
- [ ] Make backend address explicitly configurable and disabled by default.
- [ ] Never redirect NNID/PNID login or Nintendo commerce/authentication hosts.
- [ ] Enable diagnostics without collecting user IDs, session cookies, tokens or passwords.
- [ ] Verify safe boot/disable behavior before a hardware build.

## Phase 3 — original-applet catalog integration

- [ ] Map supported eShop HTML structure and native Wii U JavaScript bridge APIs.
- [ ] Deliver stable Home, category, search, game detail, and Back/My Profile behavior.
- [ ] Ensure the Wii U's older browser can parse all markup and scripts.
- [ ] Use only licensed/distributable metadata and assets.
- [ ] Test every navigation path on 5.5.5E Aroma without a signed-in real account.

## Phase 4 — download integration (future research)

- [ ] Identify legitimate Nintendo CDN title/update flows and license requirements.
- [ ] Support only authorized content; do not forge tickets, bypass authorization or intercept credentials.
- [ ] Install/queue functionality only after independent testing and explicit safeguards.

## Release gates

A successful desktop unit test does NOT validate Wii U browser compatibility or any installer. A release requires tested hardware behaviors, reproducible build instructions, a documented rollback path and review of all network destinations. Do not ship an unsafe binary as an interim "fix".
