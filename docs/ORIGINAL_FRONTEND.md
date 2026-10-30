# Fase 2: recuperare il frontend originale dell'eShop Wii U

## Requisito

Il proprietario del progetto richiede ESATTAMENTE la vera interfaccia originale Nintendo eShop Wii U, non una replica, mockup o grafica ispirata.

## Architettura verificata

Il Wii U carica l'applet eShop originale e interroga /ninja/wood_index.html. In origine il servizio Ninja reindirizzava al vero frontend su https://geisha-wup.cdn.nintendo.net/geisha/. La parte originale HTML, CSS e JS era quindi distribuita remotamente e non si recupera automaticamente dall'applet rimasta sulla console.

Fonte: https://github.com/kinnay/NintendoClients/wiki/Ninja-Server

I percorsi segnalati nelle analisi storiche includono geisha/index.html, geisha/always02_01.html (ricerca) e geisha/shelf02_01.html (classifiche). Essi sono indizi, non un archivio completo verificato.

## Risultato della verifica dei progetti pubblici

- PretendoNetwork/Grove contiene un ambiente di prova e API JavaScript Wii U, NON la UI Nintendo completa. La pagina views/home.hbs si definisce esplicitamente testing environment.
- nitrate92/Nintendo-3DS-Wii-U-eShop-Images conserva immagini e metadata, non dimostra di contenere il vero frontend HTML/CSS/JS.
- ArchiveTeam elenca principalmente dati, immagini e contenuti eShop; un backup completo di Geisha non è ancora stato identificato e verificato.

## Decisione

Il falso frontend HTML/CSS personalizzato introdotto in Fase 2 è stato rimosso da main. Il backend diagnostico precedente rimane per verificare il collegamento LAN, senza essere presentato come eShop originale. zShop.wps v0.2.0-alpha e Inkay ufficiale non sono stati modificati.

## Prossimi requisiti tecnici

1. Recuperare legalmente una copia completa delle risorse Geisha originali (pagine, script, stili, immagini e dipendenze) e verificarne provenienza/integrità.
2. Mappare le API Geisha/Ninja usate dalle pagine, senza reindirizzare account, ticket e servizi di commercio.
3. Preparare una modalità locale che possa servire le risorse che l'utente possiede legittimamente, senza includere nel repository asset proprietari non autorizzati.
4. Validare la navigazione originale sul GamePad e con Inkay ufficiale attivo.

NON sollecitare certificati client Wii U, chiavi, credenziali o token; NON pubblicare file originali Nintendo senza autorizzazione.

Stato: ricerca e recupero del vero frontend non ancora conclusi.

## Inventario offline di un backup locale

Per valutare un'eventuale copia delle risorse Geisha in possesso dell'utente:

    python tools/inspect_geisha_archive.py "C:\\percorso\\al\\backup"

Lo strumento non scarica né esegue materiale Nintendo e non necessita di certificati o credenziali. Legge pagine HTML e CSS, censisce link a risorse mancanti e domini esterni; non prova la completezza dell'applicazione, il funzionamento sul GamePad o la provenienza legittima dei file.

## 30 ottobre 2026 — identificato un archivio significativo

La repository pubblica [Greeeeen-lol/Greeeeen-lol.github.io](https://github.com/Greeeeen-lol/Greeeeen-lol.github.io) contiene un albero di circa 1.200 file (compresi altri progetti) e una cartella `geisha_wup.cdn.nintendo.net/geisha-wup.cdn.nintendo.net/geisha` con pagine storiche, librerie JS, fogli di stile e immagini dell'interfaccia Nintendo Wii U eShop.

File osservati: `index.html`, `always01_01.html`, `always02_01.html`, `shelf02_01.html`, `css/minified/index.css`, `js/minified/boot.js`, `js/functions/wood.define.js`, diversi `template/*.html` e immagini nella cartella `image/`.

**L'archivio NON è puro:** `js/environment.js` crea mock delle API Wii U e forza user agent/language, `js/database.js` contiene un catalogo fittizio e `js/gameaboutpage.js` legge dati da quel catalogo. Alcuni file originali sono dunque stati alterati o affiancati da codice di una simulazione. La repository non espone una licenza che autorizzi genericamente la redistribuzione di asset originali Nintendo.

### Modalità `--geisha-root` nel backend

Il backend zShop accetta una cartella **locale** che contiene una copia di Geisha. Il percorso iniziale `/ninja/wood_index.html` reindirizza a `/geisha/index.html`, dove i file HTML/CSS/immagini storici vengono serviti dal PC **senza copiarli in GitHub**.

Le misure prudenziali della prima prova sono intenzionalmente restrittive:

- Script tag rimossi dalle risposte HTML; file `.js` non erogati.
- Blocchi `iframe`, `<object>`, URL remoti, attributi evento e form attivi rimossi.
- CSS esterno remoto e `@import` bloccati.
- Content-Security-Policy restrittiva come ulteriore protezione (non ci affidiamo alla sola CSP su vecchio WebKit).
- Percorsi `.git`, file di credenziali, API Ninja/IAS/ECS/CCS e traversal rifiutati.
- Nessun cambio a Inkay/WUPS, nessuna chiamata di download o account.

### Limite visivo concreto

Il vecchio Geisha si basava su JavaScript per comporre i suoi scaffali; **senza script si possono verificare la vera struttura HTML, gli stili e alcuni asset, ma non ottenere ancora una Home pienamente funzionante**. Chi vede una pagina con elementi vuoti o 'Loading' sta osservando questa restrizione, non una nuova grafica inventata. Riabilitare script originali o modificati richiede revisione preventiva delle API Wii U e del codice; non si deve attivare automaticamente.

### Prova LAN

1. Mantieni inalterato `zShop.wps` e Inkay ufficiale.
2. Tieni l'archivio di terzi separato dalla repository zShop, senza caricarlo su GitHub.
3. `python backend.py --host 0.0.0.0 --port 80 --geisha-root "C:\percorso\alla\cartella"`.
4. Apri l'eShop originale sulla Wii U e osserva le strutture originali disponibili.
5. Per ripristinare la pagina diagnostica, riavvia il backend senza `--geisha-root`.

Questa è una **anteprima tecnica, non il recupero completo dell'eShop**. La possibilità di pubblicare le risorse originali, la loro autenticità e il funzionamento delle API commerciali sono ancora da verificare.
