# zShop — ripristino dell'esperienza eShop Wii U

> **Stato: Fase 2 sperimentale. Recuperati riferimenti a file storici Geisha; attiva un'anteprima locale di sola lettura. Non è ancora un eShop completo.**

zShop è un progetto open-source per recuperare la navigazione del **Nintendo eShop originale Wii U**, usando l'applet Nintendo e il Wii U GamePad anziché sostituirli con una homebrew indipendente.

## Compatibilità con Pretendo: requisito vincolante

**Inkay deve rimanere esattamente quello ufficiale.** Nessun fork, modulo
WMS alternativo, modifica ai file di Pretendo o disattivazione di Pretendo.

Su Wii U 5.5.5E + Aroma, il vecchio `newShop.wps` apre l'eShop
alternativo **con Inkay standard attivo**. La vecchia build diagnostica `zShop v0.1.0` non applicava redirect e mostrava
l'errore Pretendo `377-0001 — This eShop is not available on Pretendo`.

La **nuova v0.2.0-alpha** tenta invece una strada meno invasiva: mentre Inkay
ufficiale prepara l'applet, zShop intercetta **solo nel processo eShop** le
risoluzioni DNS dell'host HTTP `samurai.wup.shop.pretendo.cc` e le invia
all'IP privato del PC configurato nel menu Aroma. Non modifica URL in RAM,
Inkay, certificati, servizi IOSU o account. L'efficacia dipende da come
l'applet risolve il nome: è ancora da verificare su Wii U.

L'analisi statica di `newShop.wps` ha individuato riferimenti espliciti
`inkay-url`, `inkay-allowlist`, `nintendo-url` e
`nintendo-allowlist`, nonché il dominio `samurai.wup.shop.pretendo.cc`.
Questo prova che il binario riconosce le due varianti degli URL; **non**
dimostra ancora l'esatta sequenza delle patch in memoria.

La soluzione deve essere autonoma e **limitata al processo eShop**.
La compatibilità del negozio non deve richiedere il cambio globale della rete
Pretendo né modifiche all'installazione Inkay.

La precedente prova di compilazione di un Inkay modificato è **abbandonata**:
i file sorgente e la workflow di quel fork sono stati rimossi da `main`.
Non installare i vecchi artefatti della prova.

Vedi [analisi compatibilità con Inkay](docs/INKAY_COMPATIBILITY.md)
e [issue #2](https://github.com/domyno6773/zShop/issues/2).

## Fase 2 — primi file storici Geisha individuati

Abbiamo individuato [una raccolta pubblica di pagine e risorse Geisha](https://github.com/Greeeeen-lol/Greeeeen-lol.github.io) con circa 1.200 file nell'intera repository. Contiene `geisha/index.html`, `always02_01.html`, `shelf02_01.html`, CSS, immagini e template originari dell'eShop Wii U, **insieme a JavaScript e dati modificati dall'autore per una simulazione offline**. Non è un dump originale intatto, né materiale con diritti di redistribuzione verificati.

zShop **non include** quei materiali. Introduce però una modalità locale, opt-in e in sola lettura, per visualizzare il layout storico da una copia dell'archivio già presente sul tuo PC. **Questa non è ancora la Fase 2 completa:** per sicurezza la modalità blocca gli script e quindi alcune sezioni originali rimarranno vuote o sulla schermata di caricamento.

Se disponi di una copia delle risorse Geisha, aggiorna la repository zShop e avvia da PowerShell:

```powershell
git pull origin main
python backend.py --host 0.0.0.0 --port 80 --geisha-root "C:\percorso\alla\copia\dell-archivio"
```

Puoi indicare sia la cartella radice dell'archivio sopra citato, sia la cartella `geisha` contenente `index.html`. Il backend effettua il redirect dalla pagina d'ingresso dell'eShop a `/geisha/index.html` e serve soltanto risorse statiche sicure. Lascia **Inkay e zShop.wps invariati**, con l'IPv4 LAN già impostato.

Per tornare alla pagina diagnostica originale basta riavviare Python **senza** `--geisha-root`.

Il test non utilizza account, certificati, ticket, acquisti o API native di installazione. Non aprire la porta 80 sul router. Non caricare file originali Nintendo nella repository zShop.

Vedi [indagine e limiti tecnici](docs/ORIGINAL_FRONTEND.md).

## Prima prova LAN v0.2.0-alpha

**Guida completa:** [Collegamento a server locale e rollback](docs/PHASE1B_LAN_ROUTE.md).

1. Installa l'artefatto sperimentale `zShop.wps` da
   [GitHub Actions](https://github.com/domyno6773/zShop/actions/workflows/build-plugin.yml).
2. Non modificare Inkay ufficiale; disattiva soltanto il vecchio `newShop.wps`.
3. Sul PC avvia `python backend.py --host 0.0.0.0 --port 80`.
4. Sul Wii U GamePad, menu plugin: imposta l'IP **LAN privato** del PC
   e abilita il route eShop, disattivato per impostazione predefinita.
5. Apri l'eShop originale e verifica la pagina diagnostica temporanea, non la UI Nintendo.

Il backend contiene solo **titoli fittizi**; nessun download/installazione.

## Cosa funziona già

- ✅ Backend LAN Python diagnostico: non è l'interfaccia originale Nintendo eShop.
- ✅ Plugin WUPS **`plugin/zShop.wps`** compilabile da C++ con toolchain Wii U ufficiale.
- ✅ Intercettazione **passiva** di `FSOpenFile` per riconoscere il caricamento di `vol/content/initial.oma`.
- ✅ Tentativo di route DNS LAN opt-in, limitato all'eShop e al solo dominio dell'applet Inkay.
- ✅ Interruttore nel menu Aroma, **disabilitato per impostazione predefinita**, con stato del rilevamento.
- ✅ Test automatici Python e compilazione Docker nella CI di GitHub Actions.
- ✅ Reindirizzamento verso catalogo LAN provato con successo dall'utente su Wii U con Inkay originale.
- ❌ Nessun download o installazione di titoli.

Il plugin v0.2.0-alpha può cambiare la destinazione DNS dell'eShop **solo dopo opt-in**, senza modificare Inkay, servizi di autenticazione, memoria IOSU o certificati SSL. La build v0.1.0 rimane il riferimento diagnostico precedente.

## Scaricare la build sperimentale

Apri [GitHub Actions — Build zShop Aroma plugin](https://github.com/domyno6773/zShop/actions/workflows/build-plugin.yml), scegli una build riuscita e scarica l'artefatto **`zShop-v0.2.0-inkay-stock-lan-alpha`**. All'interno c'è il file `zShop.wps`.

Per installazione, verifiche e rollback leggi **[Fase 1b — LAN](docs/PHASE1B_LAN_ROUTE.md)**. La vecchia [Fase 1 diagnostica](docs/PHASE1_DIAGNOSTIC.md) rimane come documentazione storica.

### Importante: non caricare due plugin contemporaneamente

Prima di provare zShop, rinomina `sd:/wiiu/environments/aroma/plugins/newShop.wps` in `newShop.wps.disabled`. Non eliminare l'originale. Dopo il test puoi rimuovere `zShop.wps` e ripristinare `newShop.wps`.

La console di riferimento ha firmware **5.5.5E e Aroma aggiornato**. Il collegamento LAN è stato provato su console; l'interfaccia della **Fase 2** necessita ancora di prove visive e di navigazione sul GamePad.

## Sviluppo

```sh
# Test del backend
python -m unittest discover -s tests -v
python backend.py
# http://127.0.0.1:8080/ninja/wood_index.html

# Compilazione del plugin
docker build -f plugin/Dockerfile -t zshop-wups-builder plugin
docker run --rm -v "$PWD/plugin:/project" zshop-wups-builder make
# plugin/zShop.wps

# Analisi passiva del vecchio plugin, solo se possiedi una copia locale
python tools/inspect_wps.py "newShop(1).wps" -o report.json
```

## Architettura e piano

Consulta [ROADMAP](docs/ROADMAP.md) e [audit del plugin originale](docs/ORIGINAL_PLUGIN_AUDIT.md).

Il vecchio `newShop.wps`, fornito per l'analisi, non viene distribuito qui. Mostrava reindirizzamenti di servizi sensibili verso un server non verificato. zShop non eredita tali patch.

## Limitazioni e sicurezza

- Nessuna raccolta di credenziali o informazioni di account.
- Nessuna modifica di NNID/PNID, ticket, autorizzazioni o servizi commerciali Nintendo.
- Nessuna alterazione IOSU o SSL; nessuna installazione automatica.
- Integrazioni future solo per contenuti distribuiti e installati con autorizzazioni valide.
- Nessuna garanzia di funzionamento dell'eShop originale, ormai chiuso ai nuovi acquisti.

## Riferimenti tecnici

- [Wii U Plugin System](https://github.com/wiiu-env/WiiUPluginSystem)
- [Aroma](https://github.com/wiiu-env/Aroma)
- [Pretendo Grove](https://github.com/PretendoNetwork/Grove) — riferimento archiviato sulle API JavaScript native dell'eShop.

Progetto indipendente, non affiliato a Nintendo o Pretendo.
