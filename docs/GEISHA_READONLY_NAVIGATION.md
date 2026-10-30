# Navigazione Geisha in sola lettura — prima estensione dopo Work

**Stato:** base Home Geisha visibile sulla Wii U, confermata dall'utente dopo
la correzione eseguita in Work; questa estensione di ricerca/classifiche
richiede ancora un test hardware. Non è un eShop completo.

## Modifiche implementate

- Nessuna modifica a `zShop.wps`, Inkay, DNS, account o bridge di avvio Wii U.
- `always02_01.html`: il vero campo di ricerca dell'archivio viene racchiuso
  in un form HTML GET verso `shelf02_01.html`. Il controllo mantiene
  le classi storiche `search-submit se` e `search-label`.
- `shelf02_01.html`: `#shelf-list` non rimane su `Loading...`. Il
  server riempie le righe usando classi e strutture presenti nei template
  storici: `m-list-item`, `list-title-outline`, `list-title-icon`,
  `list-title-summary`, `el-purchase`.
- La vecchia pagina archivio contiene un wrapper di bootstrap invisibile
  e un wrapper di classifiche. Il CSS locale rivela soltanto il secondo.
- Il menu storico `#ft_navi` usa link HTML Home, Back e Search funzionanti
  senza eseguire il JavaScript alterato nell'archivio di terzi.
- Gli archivi di Nintendo rimangono fuori dal repository zShop; i dati
  visualizzati sono soltanto titoli fittizi di prova.

**Limitazioni:** non ci sono schede gioco vere, catalogo ufficiale,
ordinamento interattivo, pagina utente, acquisti o download. Le righe sono
intenzionalmente statiche; il selettore di ordinamento storico rimane
disabilitato fino all'implementazione di un'azione reale. Non riattivare
`environment.js` o `boot.js` dell'archivio esterno come scorciatoia.

## Test sulla Wii U (Windows ZIP)

La copia locale Geisha è già nella cartella zShop e non deve essere riscaricata.
Arresta il backend precedente con `Ctrl+C` e da PowerShell:

```powershell
Set-Location 'C:\Users\gianl\Desktop\zShop-main'
Invoke-WebRequest 'https://raw.githubusercontent.com/domyno6773/zShop/main/tools/update_backend.ps1' -OutFile '.\update_backend.ps1' -UseBasicParsing
& '.\update_backend.ps1' -Destination (Get-Location).Path
python backend.py --host 0.0.0.0 --port 80 --geisha-root '.\Greeeeen-lol.github.io-main'
```

Lo script scarica in staging **tutti** i moduli del backend dallo stesso commit
e ne controlla la sintassi prima della sostituzione, salvando una copia dei
file precedenti. Il backend mostra la versione con `X-zShop-Build` e
`/__zshop__/status`.

Sulla Wii U controlla nell'ordine:
1. La **Home già funzionante** mantiene layout e apertura.
2. **Search** apre la pagina originale di ricerca con CSS Geisha.
3. Cercando una parte del nome di un gioco demo e premendo Search viene
   aperto il relativo elenco.
4. **Charts** mostra l'elenco demo ordinato, non `Loading...`.
5. I collegamenti **Home**, **Back** e **Search** del menu laterale aprono
   le pagine corrette.

Se una pagina non si apre, ripristina la copia `zshop-code-backup-*`
creata dallo script con Python fermo e conserva le diagnostiche anonime.
La verifica sul GamePad resta necessaria anche dopo il verde dei test CI.

## Riproducibilità

`python -m unittest discover -s tests -v` include fixture sintetiche
e test HTTP per i percorsi di ricerca e classifica. I test del browser WebKit
moderni e Chromium non sono equivalenti alla Wii U.
