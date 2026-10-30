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

## Fase 2 — vero frontend Geisha Nintendo: NON ANCORA RIPRISTINATO

- [x] Verificata architettura originale Ninja → Geisha.
- [x] Rimosso il precedente frontend inventato: contrario al requisito.
- [x] Ripristinato il backend diagnostico LAN già funzionante.
- [x] Individuata una raccolta pubblica con pagine Geisha originali e risorse, ma mescolate a file alterati; NON verificata come dump intatto.
- [x] Prima modalità locale di sola lettura per verificare HTML/CSS/immagini in possesso dell'utente, senza eseguire JS.
- [ ] Separare rigorosamente gli script originali dai mock/sostituzioni del progetto di terzi.
- [ ] Reperire e convalidare un archivio integro di HTML/CSS/JS Geisha.
- [ ] Verificare provenienza, diritti d'uso, integrità e dipendenze.
- [ ] Implementare sul server locale l'erogazione dell'interfaccia originale, senza pubblicare asset proprietari non autorizzati.
- [ ] Ricostruire le chiamate Ninja/Geisha non sensibili e verificare comandi e navigation GamePad.

Vedi docs/ORIGINAL_FRONTEND.md. Nessuna ulteriore UI ispirata o mockup deve essere presentata come originale.

## Fase 3 — download autorizzati

- [ ] Ricerca sui flussi legittimi per titoli posseduti, aggiornamenti e contenuti liberi.
- [ ] Integrazione trasparente con verifiche di licenza e autorizzazione.
- [ ] Test separati di integrità, spazio, ripresa e uscita sicura.
- [ ] Niente token inventati, ticket falsificati o bypass SSL.

## Gate di rilascio

Build CI verde != prova hardware. Non pubblicare release dichiarate stabili prima di test reali. Nessuna distribuzione dell'eseguibile esterno newShop originale.
