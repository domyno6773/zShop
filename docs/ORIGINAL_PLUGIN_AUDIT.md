# External newShop.wps: static audit notes

Source: user-provided binary ("newShop(1).wps"), **not distributed here**.

- SHA-256: dfe8cff45304b2f43926f933ea254d622a13325528a6f3223a70d299978f675b
- Size: 91,716 bytes
- Format: PowerPC ELF32, big-endian, WUPS sections compressed with zlib
- Embedded name: uShop Access
- Embedded version: v2.2.0-safe; WUPS metadata advertises wups=0.9.1
- Embedded build timestamp: Oct 1 2026 17:43:22
- Inspected text references: FunctionPatcher, FSOpenFile target vol/content/initial.oma,
  ECommerceSOAP, IdentityAuthenticationSOAP, NetUpdateSOAP, /ccs/download,
  reporting endpoint /plugreport, and unsafe opt-in vol/content/ushop-unsafe.txt.
- Remote IPv4 host hardcoded in URLs: 141.148.168.106, including HTTP-based
  redirects to account/commerce-related services.

**Interpretation:** these are static indicators, not proof of executed behavior.
Neither server integrity nor download safety has been established. zShop will not
ship or enable these remote authentication redirects, IOSU writes or SSL bypasses.
Avoid installing unverified tickets/content while analyzing this plugin.

To regenerate your own report locally:
\`python tools/inspect_wps.py "newShop(1).wps" -o report.json\`

Do **not** commit the original WPS or reports containing account/session data.

## Evidenza aggiuntiva: supporto Inkay integrato

Dopo decompressione delle sezioni ELF, la sezione `.rodata` contiene
i marker `inkay-url`, `inkay-allowlist`, `nintendo-url`,
`nintendo-allowlist`, l'URL `http://samurai.wup.shop.pretendo.cc/ninja/wood_index.html?`,
e il corrispondente URL originale
`https://ninja.wup.shop.nintendo.net/ninja/wood_index.html?`.

Questi riferimenti, insieme alle costanti di destinazione uShop,
indicano una logica prevista **anche quando Inkay è presente**. È coerente
con il test reale dell'utente: il vecchio plugin apre la pagina uShop
senza modificare Inkay. Non è ancora una prova del preciso ordine degli
hook o dell'effettiva compatibilità dei download.

Scelta progettuale: **replicare solo la gestione necessaria della pagina
dell'applet nel plugin zShop**, non i redirect di autenticazione/commerce
o le patch IOSU. Non distribuire il vecchio binario.
