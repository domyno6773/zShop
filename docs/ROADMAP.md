# zShop roadmap — aggiornato al 30/10/2026

**Requisito non negoziabile:** mantenere l'applet eShop Nintendo originale, con navigazione tramite Wii U GamePad.

## Diagnosi della console

- Wii U europea 5.5.5E con Aroma aggiornato.
- Aggiornare Aroma ha risolto il messaggio `newShop.wps Incompatible version`.
- Nel vecchio uShop: Best Sellers / New Releases bloccano Back / My Profile; altre categorie tornano alla Home; titoli ripetuti.
- La causa non è ancora attribuibile con certezza al server: servono verifiche su hardware.

## Fase 0 — base diagnostica locale: COMPLETATA

- [x] Repository GitHub e documentazione.
- [x] Analizzatore ELF/WPS non esecutivo.
- [x] Backend Python localhost con catalogo completamente fittizio.
- [x] Test per categorie, link, ricerca, escaping e profilo.

## Fase 1a — toolchain e plugin WUPS passivo: COMPILATA

- [x] Verificare gli esempi ufficiali WUPS e la toolchain corrente.
- [x] Sorgente C++ del plugin compilabile con toolchain PowerPC pin.
- [x] Hook `FSOpenFile` pass-through: nessun argomento o risultato modificato.
- [x] Semplice rilevamento `initial.oma`, opt-in e senza telemetria.
- [x] Menu di configurazione Aroma e salvataggio della preferenza.
- [x] GitHub Actions per la build WPS.
- [ ] Verificare il caricamento su Wii U 5.5.5E.
- [ ] Rilevare `initial.oma` sulla console.
- [ ] Verificare HOME, uscita dall'eShop e rimozione del plugin.

## Vincolo Pretendo — IN RICERCA, SENZA MODIFICARE INKAY

- [x] Confermato su console: `newShop.wps` apre eShop alternativo con Inkay ufficiale attivo.
- [x] Identificato redirect dell'applet da parte di Inkay tramite `patchEshop()`.
- [x] Isolati nel vecchio binario marker `inkay-url`, `inkay-allowlist`, `nintendo-url`, `nintendo-allowlist`.
- [x] Eliminato il ramo di sviluppo che ricompilava/modificava Inkay; non è parte della soluzione.
- [ ] Verificare il punto e l'ordine effettivo dei redirect quando entrambi i plugin sono attivi.
- [x] Implementato e verificato su console il redirect DNS confinato al processo eShop, con opt-in e rollback.
- [x] L'utente ha verificato che l'eShop alternativo si apre con Inkay originale attivo. Restano da testare le singole funzioni online di Pretendo.
- [ ] Non toccare i servizi di autenticazione, IOSU, ticket, SSL o le impostazioni globali Inkay.

## Fase 1b — DNS solo per applet con Inkay originale: PROVATO SU HARDWARE

- [x] Individuata un'alternativa a ContentRedirection: hook mirati a getaddrinfo/gethostbyname per SOLO il processo eShop.
- [x] Intercettato solo l'hostname HTTP dell'applet generato da Inkay ufficiale.
- [x] Indirizzo IPv4 di backend configurabile nel menu Aroma e limitato a RFC1918.
- [x] Route opt-in, OFF di default, nessun accesso ad account, ticket, IOSU o certificati.
- [x] Il reindirizzamento DNS verso backend LAN funziona su Wii U 5.5.5E con Inkay originale.
- [x] Confermata dall'utente l'apertura del backend PC su porta 80 nell'eShop originale.
- [ ] Verificare i percorsi di navigazione e il recupero con HOME/B.
- [ ] Se il hook non viene chiamato, indagare una seconda soluzione confinata al processo eShop senza toccare Inkay.

## Fase 2 — esperienza eShop originale: PRIMA IMPLEMENTAZIONE

- [x] Prima interfaccia in stile Wii U eShop: rail laterale, navigazione superiore, layout schede software.
- [x] Pagine Home, categorie, ricerca, dettaglio e profilo fittizio navigabili.
- [x] CSS e JS con fallback per vecchio WebKit, senza framework o CDN esterne.
- [x] Link espliciti per Back/Home, schede con ritorno alla categoria da cui si proviene.
- [x] Nessun accesso ad account, acquisti, ticket o download.
- [ ] Espandere il catalogo con metadati/immagini distribuibili legalmente e verificati.
- [ ] Confrontare il rendering reale con screenshot originali su GamePad 854×480 e TV.
- [ ] Verificare comportamento B / HOME; non assumere bridge nativi non documentati.
- [ ] Iterare fino a una riproduzione visiva più fedele senza asset Nintendo redistribuiti.

## Fase 3 — download autorizzati

- [ ] Ricerca sui flussi legittimi per titoli posseduti, aggiornamenti e contenuti liberi.
- [ ] Integrazione trasparente con verifiche di licenza e autorizzazione.
- [ ] Test separati di integrità, spazio, ripresa e uscita sicura.
- [ ] Niente token inventati, ticket falsificati o bypass SSL.

## Gate di rilascio

Build CI verde != prova hardware. Non pubblicare release dichiarate stabili prima di test reali. Nessuna distribuzione dell'eseguibile esterno newShop originale.
