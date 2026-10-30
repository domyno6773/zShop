# zShop — ripristino dell'esperienza eShop Wii U

> **Stato: sperimentale. Build v0.1.0 diagnostica compilata per Aroma. Non è ancora un negozio funzionante.**

zShop è un progetto open-source per recuperare la navigazione del **Nintendo eShop originale Wii U**, usando l'applet Nintendo e il Wii U GamePad anziché sostituirli con una homebrew indipendente.

## Cosa funziona già

- ✅ Backend diagnostico locale in Python: categorie, ricerca, schede demo e navigazione di base (non ancora collegato alla Wii U).
- ✅ Plugin WUPS **`plugin/zShop.wps`** compilabile da C++ con toolchain Wii U ufficiale.
- ✅ Intercettazione **passiva** di `FSOpenFile` per riconoscere il caricamento di `vol/content/initial.oma`.
- ✅ Interruttore nel menu Aroma, **disabilitato per impostazione predefinita**, con stato del rilevamento.
- ✅ Test automatici Python e compilazione Docker nella CI di GitHub Actions.
- ❌ Nessun reindirizzamento del catalogo nelle build correnti.
- ❌ Nessun download o installazione di titoli.

Il plugin v0.1.0 **non modifica l'eShop**, i server di autenticazione Nintendo, la memoria IOSU o i certificati SSL. È concepito come prima prova di compatibilità sulla console.

## Scaricare la build diagnostica

Apri [GitHub Actions — Build Aroma diagnostic plugin](https://github.com/domyno6773/zShop/actions/workflows/build-plugin.yml), scegli una build riuscita e scarica l'artefatto **`zShop-phase1-diagnostic-wps`**. All'interno c'è il file `zShop.wps`.

Per istruzioni di installazione, verifica e rollback, leggi **[Fase 1 diagnostica](docs/PHASE1_DIAGNOSTIC.md)**.

### Importante: non caricare due plugin contemporaneamente

Prima di provare zShop, rinomina `sd:/wiiu/environments/aroma/plugins/newShop.wps` in `newShop.wps.disabled`. Non eliminare l'originale. Dopo il test puoi rimuovere `zShop.wps` e ripristinare `newShop.wps`.

La console di riferimento ha firmware **5.5.5E e Aroma aggiornato**. Il superamento dei test automatici non certifica la compatibilità sulla console: occorre una prova reale.

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
