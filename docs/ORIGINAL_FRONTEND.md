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
