# Schermata bianca Geisha: verifica del 30 ottobre 2026

## Risultati osservati, prima delle modifiche

Il test usa l'archivio già estratto sul PC dell'utente. Nessuna risorsa Nintendo
è stata aggiunta a zShop. Il confronto parte da `main` al commit
`694dcec85eda6b615bfa8eb0a4e9302cdf15ced3`.

| Prova reale in Edge, viewport 1280×720 | Risultato |
| --- | --- |
| Codice presente sul Desktop, stessi asset locali | `#wrapper` con `display:none`, rettangolo 0×0; pagina vuota |
| Codice di `main` 694dcec, stessi asset locali | Home visibile, wrapper 1280×861, menu 160×720 |
| Entrata `/ninja/wood_index.html?version=1.0.0` | 302 relativo, poi HTML 200; nessun cambio di host/porta |
| CSS, bridge, immagini richiesti dalla Home | 200, MIME corretti; immagini decodificate |
| Codifica HTML e CSS Home | UTF-8 senza caratteri sostitutivi |
| JS della Home | Nessuna eccezione; solo bridge locale, sorgenti dell'archivio rimossi |
| Classifiche `/geisha/shelf02_01.html` | Wrapper ancora nascosto: il precedente override copriva solo `index.html` |

La copia locale di `geisha_archive.py` **non conteneva** l'override del commit
694dcec. La differenza spiega la schermata vuota riprodotta con quella copia.
Non dimostra quale processo/versione fosse in esecuzione durante ogni prova Wii U
precedente. All'inizio di questa sessione nessun server ascoltava sulla porta 80.

Nessuna evidenza nel test desktop di CSP che blocchi il bridge, errori di encoding,
asset mancanti della Home, ulteriori elementi invisibili della Home o zoom che
nasconda l'intera pagina. L'unico 404 iniziale era `/favicon.ico`, senza effetto
sull'interfaccia. Il layout storico è fisso a 1280 pixel: una finestra 854×480
ne mostra una parte. Non abbiamo introdotto un ridimensionamento ipotetico.

Verificato anche un bind temporaneo reale su `0.0.0.0:80`: richieste dal PC a
`192.168.1.100:80`, con Host dell'applet `samurai.wup.shop.pretendo.cc`, hanno
ottenuto health, ingresso, CSS e bridge con 200 e build coerente. Il redirect
mantiene HTTP e la porta 80. Questo controlla il server locale, non il percorso
attraverso firewall/rete dalla console, già verificato dall'utente.

## Cambiamenti e limiti

- L'override di visibilità copre tutte le pagine che possiedono `#wrapper`,
  comprese le classifiche. Nessuno script storico viene riattivato.
- `X-zShop-Build` identifica i cinque file di runtime, anche nelle copie ZIP.
  Il calcolo normalizza CRLF/LF. `/health` riporta finalmente `geisha-preview`
  quando questa modalità è attiva, anziché il vecchio valore fisso `demo`.
- Il bridge ES5 registra geometria del wrapper e avanzamento delle due chiamate
  native. Un'eccezione in `endStartUp(true)` non impedisce il tentativo separato
  di `lockHomeButtonMenu(false)`.
- Restano CSS/struttura/immagini dell'archivio locale e un catalogo dimostrativo.
  Non sono ripristinati scaffali dinamici, ricerca funzionante o negozio completo.
  Le classifiche possono ora mostrare il loro placeholder `Loading...`.

Il bridge usa le stesse due chiamate già presenti. Il loro uso è riscontrabile
anche in [Grove](https://github.com/PretendoNetwork/Grove/blob/355e08c6d31e25c7e28d153a3a920b5110c84602/public/js/grove.js).
Nessuna parte delle altre funzioni di Grove viene importata o eseguita.

## Aggiornamento di una cartella scaricata come ZIP

Ferma Python con `Ctrl+C`. Mantieni `Greeeeen-lol.github.io-main` dov'è.
Il seguente aggiornamento scarica cinque piccoli file di runtime, da **un solo
commit**; li valida prima della copia e salva una copia del codice precedente.

```powershell
Set-Location 'C:\Users\gianl\Desktop\zShop-main'
Invoke-WebRequest 'https://raw.githubusercontent.com/domyno6773/zShop/main/tools/update_backend.ps1' -OutFile '.\update_backend.ps1' -UseBasicParsing
& '.\update_backend.ps1' -Destination (Get-Location).Path
python backend.py --host 0.0.0.0 --port 80 --geisha-root '.\Greeeeen-lol.github.io-main' --diagnostic-log '.\geisha-test.jsonl'
```

Lo script accetta anche `-Ref <SHA completo>` per usare una versione precisa.
Non cancella né riscarica l'archivio. Il backup `zshop-code-backup-*` contiene i
file precedenti; per ripristinarli, a server fermo, ricopiali nella stessa cartella.
Gli eventuali file nuovi rimasti non sono importati dal vecchio codice.

Da un'altra finestra PowerShell verifica il processo realmente sulla porta 80:

```powershell
Invoke-RestMethod 'http://192.168.1.100/health' | Format-List
$r = Invoke-WebRequest 'http://192.168.1.100/geisha/index.html' -UseBasicParsing
$r.Headers['X-zShop-Build']
$r.Content.Contains('#wrapper{display:block!important}')
Invoke-RestMethod 'http://192.168.1.100/__zshop__/status' | ConvertTo-Json -Depth 8
```

`mode` deve essere `geisha-preview`, il build deve coincidere con quello stampato
all'avvio e la verifica del wrapper deve restituire `True`. Questi controlli
distinguono codice vecchio, processo vecchio e file scaricati in un'altra cartella.
HTML, CSS, JS e redirect inviano `no-store`, `Pragma: no-cache`, `Expires: 0`.

## Esperimenti incrementali sulla Wii U

Mantieni zShop.wps, Inkay, DNS e IP già verificati. Chiudi completamente l'eShop
tra due prove. Ferma e riavvia Python per ciascun esperimento, modificando **una
sola opzione** rispetto alla prova precedente. Usa un nome di log diverso per
ciascuna prova; evita di aprire il sito dal PC durante la raccolta Wii U, perché
i log non identificano il dispositivo.

1. **Versione aggiornata, impostazioni normali.** Usa il comando precedente.
   Controlla la Home sull'applet e poi consulta lo stato dal PC.
2. **Solo se ancora bianco: pagina indipendente dall'archivio.** Aggiungi
   `--geisha-entry probe`. Il risultato atteso è una pagina etichettata
   `zShop display probe`, con sfondo blu e blocchi verde/arancione. Non è una UI
   sostitutiva. `JavaScript OK` distingue esecuzione del bridge da semplice HTML.
3. **Isola le chiamate native, sulla stessa probe.** Confronta prima
   `--geisha-native startup` (solo fine avvio), poi `--geisha-native all`.
   `--geisha-native off` e `unlock` sono controlli aggiuntivi: omettere
   `endStartUp` può lasciare attiva la schermata nativa e quindi una prova bianca
   in queste modalità NON dimostra che l'HTML sia invisibile.
4. **Se la probe compare, torna a Geisha e isola il redirect.** Riparti dal
   comando normale aggiungendo solo `--geisha-entry direct`: invia l'HTML con
   200 direttamente all'ingresso dell'applet. Un `<base>` locale conserva gli
   asset sotto `/geisha/`. Non cambia destinazione DNS né porta.
5. **Se serve, confronta Geisha con/senza CSS.** Sulla stessa modalità d'ingresso
   aggiungi `--geisha-css off`. Il testo deve diventare semplice HTML; una
   differenza rispetto alla versione con CSS indirizza l'analisi al rendering.

Le stesse opzioni sono disponibili nel browser:
`/geisha/index.html?zshop_native=off&zshop_css=off` e
`/__zshop__/probe?zshop_native=startup`. I redirect inoltrano esclusivamente questi
parametri diagnostici; non inoltrano query di account/applet.

## Come leggere le tracce

`/__zshop__/status` contiene impronte/byte/UTF-8 dei sorgenti Home/CSS, indicatori
della Home trasformata e gli ultimi 160 eventi. Con `--diagnostic-log` gli eventi
sono anche aggiunti al file JSONL scelto. Ogni documento ha un ID casuale di otto
cifre esadecimali, visibile in `X-zShop-Page` e nei beacon dello stesso documento.

| Traccia | Cosa permette di concludere |
| --- | --- |
| `http`, route `entry`, 302 e `home`, 200 | Server raggiunto e Home inviata |
| `http`, route `bridge`, 200 | File bridge richiesto; non prova ancora l'esecuzione |
| `client`, stage `bridge` | JavaScript effettivamente iniziato |
| `dom` / `load`, `w`, `h`, `visible`, `broken` | Geometria DOM e stato immagini prima/dopo il caricamento |
| `browser-missing` / `startup-missing` | API/proprietà non disponibili secondo il controllo JS |
| `startup-ok`, `unlock-ok` | Le chiamate sono ritornate senza eccezione JS |
| `startup-error`, `unlock-error` | Eccezione intercettata, senza raccoglierne messaggio o dati |

I beacon sono immagini locali asincrone, compatibili con `connect-src 'none'`.
Non usare l'ordine d'arrivo come sequenza precisa: una chiamata nativa che arresta
l'applet può impedire anche l'invio dei beacon già avviati. L'assenza di un evento
non prova da sola un crash. Un esito `ok` non prova che il display hardware abbia
disegnato l'interfaccia. Gli eventi possono provenire da altri client LAN: non
sono una certificazione hardware.

Non si registrano IP client, Host, User-Agent, cookie, Authorization, Referer,
query originali, nomi arbitrari di percorsi, account, token o messaggi d'errore.
Le richieste sono classificate (`entry`, `home`, `css`, `image`, `unknown`, ...).
Gli eventi client accettano solo nomi fissi e misure numeriche limitate.

## Riproduzione automatica

```powershell
python -m unittest discover -s tests -v
python -m pip install playwright==1.63.0
python tools/check_geisha_browser.py '.\Greeeeen-lol.github.io-main' --channel msedge --output '.\browser-results'
```

Il controllo reale dell'archivio scrive screenshot e un report tecnico nella
cartella scelta, senza copiare gli asset sorgenti nel repository. Verifica HTTP,
MIME, asset caricati, CSP effettiva del browser, geometria, JS disabilitato,
viewport 1280×720/854×480, redirect/direct/probe, CSS escluso, API assenti,
chiamata startup che genera un'eccezione e isolamento delle due API.

La CI esegue inoltre una fixture sintetica con Chromium e WebKit moderni; non
contiene risorse Nintendo. Il WebKit locale non è stato installabile durante
questa sessione (timeout dei mirror). Anche una CI WebKit riuscita non emula
il vecchio motore Wii U né le API native. La conferma su console rimane aperta.
