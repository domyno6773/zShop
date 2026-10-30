# Fase 2 — Prima interfaccia stile Wii U eShop

## Risultato attuale

La console 5.5.5E con Aroma e Inkay ufficiale ha già aperto correttamente
il backend zShop tramite il plugin **v0.2.0-alpha** sulla LAN. Questa fase
modifica solamente il **backend Python e i suoi file HTML/CSS/JS**.

Non serve installare un nuovo `.wps`, disattivare Pretendo o alterare Inkay.

### Nuove pagine

- Home con banner, categorie, sezioni In evidenza e Ultime uscite
- Giochi Wii U: elenco completo fittizio
- Classifiche: ordine per popolarità del catalogo
- Ultime uscite: ordine decrescente per data
- Mario: demo della categoria filtrata
- Ricerca: titolo, descrizione e genere
- Scheda software con immagine CSS di prova, genere/data e scaricamento disattivato
- Il mio menu: nessun accesso a NNID/PNID, profilo soltanto dimostrativo

Le voci **Home**, **Indietro**, **Ricerca** e **Il mio menu** hanno link veri,
non sono pulsanti senza destinazione. Il ritorno dalla scheda software
riporta alla sezione d'origine tramite parametro `frm`.

### Perché non ancora identico al Nintendo eShop originale

La grafica è una **ricostruzione originale ispirata ai layout storici**:
barra laterale chiara e arrotondata, navigazione superiore, sezioni a tessere,
palette arancione/ciano e schede su fondo bianco. Non comprende asset
proprietari Nintendo, vere copertine, login o catalogo reale. Per migliorare
la fedeltà bisogna confrontare screenshot di rendering su GamePad e TV.

Riferimenti:
- https://www.nintendo.co.jp/en/wiiu/software/eshop/index.html
- https://www.nintendo.com/it-it/Wii-U/Software-preinstallati/Nintendo-eShop/Nintendo-eShop-666623.html
- https://github.com/PretendoNetwork/Grove

### Compatibilità

Il browser Wii U utilizza un WebKit datato. Per questo il frontend:
- usa **pagine HTML renderizzate dal server** e link GET veri;
- usa CSS semplice (inline-block, float, percentuali), senza grid/flex/calc;
- usa JavaScript ES5 per invocare soltanto le due funzioni native dell'applet
  già utilizzate dal precedente backend: `endStartUp(true)` e
  `lockHomeButtonMenu(false)`, quando disponibili;
- non richiede web font, CDN esterni, fetch API, moduli o service worker;
- non dipende da sessioni, cookie, account o storage del browser.

**Limitazione esplicita:** non è stato dimostrato che il pulsante **B**
generi un evento JavaScript equivalente a Backspace/Escape. La barra laterale
e i link di ritorno sono invece disponibili da verificare sul touchscreen.
HOME viene lasciato al sistema; non va intercettato per simulare un menu.

## Come provarlo sulla Wii U

Sul PC Windows, nella copia aggiornata del repository:

```powershell
git pull
python backend.py --host 0.0.0.0 --port 80
```

Se il vecchio processo Python è ancora in esecuzione, fermalo con
**Ctrl+C** e riavvialo. La Wii U userà il medesimo IP di rete locale
salvato in zShop (**192.168.1.100**, se invariato). Non cambiare il plugin.

Apri l'eShop originale su Wii U. Verifica in questo ordine:

1. **Home**: vengono mostrati banner e griglie senza tagli o sovrapposizioni?
2. **Classifiche**: le schede sono ordinate e il pulsante Indietro torna alla Home?
3. **Ultime uscite**: l'ordine è diverso dalle classifiche?
4. **Mario**: mostra soltanto la categoria di prova?
5. **Ricerca**: cercando `Corse` appare la demo corse?
6. **Scheda gioco**: apre i dettagli e torna alla categoria d'origine?
7. **Il mio menu**: apre una pagina dimostrativa e torna alla Home?
8. **B** e **HOME**: segna il comportamento effettivo su GamePad, senza assumere
   che le funzioni native dell'applet siano tutte esposte.

Se qualcosa fallisce, uno screenshot della console e la pagina aperta
sono sufficienti a riprodurre il problema. Non condividere credenziali,
identificativi della console o cookie.

### Test automatici

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions controlla le rotte, il contenuto HTML, la ricerca, i link,
il tipo MIME degli asset e che non vengano esposti endpoint di commercio
o autenticazione. Non sostituisce i test grafici su GamePad.

## Sicurezza e perimetro

Nessuna operazione di acquisto o installazione. Nessun utilizzo del CDN,
account, ticket o certificati Wii U. Il backend deve rimanere nella rete
privata e **non** essere esposto su Internet.
