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

## Fase 1a — toolchain e plugin WUPS passivo: COMPILATA; HARDWARE DA TESTARE

- [x] Verificare gli esempi ufficiali WUPS e la toolchain corrente.
- [x] Sorgente C++ del plugin compilabile con toolchain PowerPC pin.
- [x] Hook `FSOpenFile` pass-through: nessun argomento o risultato modificato.
- [x] Semplice rilevamento `initial.oma`, opt-in e senza telemetria.
- [x] Menu di configurazione Aroma e salvataggio della preferenza.
- [x] GitHub Actions per la build WPS.
- [ ] Verificare il caricamento su Wii U 5.5.5E.
- [ ] Rilevare `initial.oma` sulla console.
- [ ] Verificare HOME, uscita dall'eShop e rimozione del plugin.

## Fase 1b — reindirizzamento dell'applet, dopo i test

- [ ] Studiare e validare l'API ContentRedirection su Aroma aggiornato.
- [ ] Progettare una sorgente di pagina con destinazione locale esplicitamente impostata.
- [ ] Introdurre l'opt-in al reindirizzamento mantenendolo OFF di default.
- [ ] Limitare il reindirizzamento alla pagina applet, senza toccare autenticazione o CDN.
- [ ] Verificare il rollback senza residui e l'assenza di interferenze con altri plugin.

## Fase 2 — esperienza eShop originale

- [ ] Catalogo completo di metadati legalmente distribuibili.
- [ ] Pagine Home / categorie / ricerca / dettaglio.
- [ ] Back / B / HOME / My Profile sempre coerenti.
- [ ] Test in WebKit Wii U con API native appropriate.
- [ ] Test hardware italiano/europeo, senza account autenticato.

## Fase 3 — download autorizzati

- [ ] Ricerca sui flussi legittimi per titoli posseduti, aggiornamenti e contenuti liberi.
- [ ] Integrazione trasparente con verifiche di licenza e autorizzazione.
- [ ] Test separati di integrità, spazio, ripresa e uscita sicura.
- [ ] Niente token inventati, ticket falsificati o bypass SSL.

## Gate di rilascio

Build CI verde != prova hardware. Non pubblicare release dichiarate stabili prima di test reali. Nessuna distribuzione dell'eseguibile esterno newShop originale.
