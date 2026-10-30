# Fase 1b — zShop v0.2.0-alpha, test con Inkay ufficiale

**Prima build sperimentale che prova a collegare la pagina dell'eShop originale al backend zShop.**
NON è un negozio completo, NON scarica giochi e richiede un server HTTP su PC nella stessa LAN.

## Perché funziona senza modificare Inkay

Inkay ufficiale cambia l'URL iniziale dell'eShop in:

`http://samurai.wup.shop.pretendo.cc/ninja/wood_index.html?`

e modifica la lista dei domini consentiti dal browser originale Wii U.
Invece di disabilitare Inkay o effettuare rischiose sostituzioni in RAM, zShop
intercetta **solo nel processo eShop** la risoluzione DNS del nome esatto
`samurai.wup.shop.pretendo.cc`.

Se l'opzione è abilitata e il PC ha un IP privato valido, zShop risolve
quell'unico nome verso l'indirizzo IPv4 configurato. Il resto di Inkay, la
risoluzione degli account e gli altri servizi **non vengono alterati da zShop**.

Questo non è ancora validato sull'hardware: il browser potrebbe usare una strada
diversa da `getaddrinfo`/`gethostbyname` oppure essere influenzato da cache.
Non viene modificata nessuna funzione di autenticazione, ticket, download o memoria IOSU.

## Prima di provare la build

1. Fai un backup della SD.
2. Lascia **Inkay originale esattamente com'è**; non installare fork o moduli Inkay ricompilati.
3. Disattiva il vecchio `newShop.wps` rinominandolo in `newShop.wps.disabled`;
   non farlo girare insieme a zShop.
4. Installa SOLO `zShop.wps` nel percorso
   `sd:/wiiu/environments/aroma/plugins/`.

## Avviare il backend sul PC

Il backend attuale è un **catalogo fittizio con cinque schede di prova**.
Non usa server Nintendo, licenze o credenziali.

Dal PC con Python, nella cartella della repository:

```powershell
python backend.py --host 0.0.0.0 --port 80
```

Il PC e la Wii U devono essere sulla **stessa rete locale**.
Dal PC, visita `http://127.0.0.1/ninja/wood_index.html`: devi vedere il
catalogo dimostrativo zShop. Se non parte, verifica se un altro servizio usa
la porta 80. Su Windows consenti Python nella rete **privata** se il firewall
lo richiede. Non aprire alcuna porta sul router verso internet.

Trova l'IPv4 locale del PC usando `ipconfig` (per esempio `192.168.1.23`).

## Configurazione su Wii U

1. Avvia Aroma, apri il menu plugin con **L + giù + –**.
2. Nel menu **zShop (experimental)** imposta **Backend PC IPv4 (LAN)** sull'IP del tuo PC.
3. Attiva **Route eShop to LAN backend (PORT 80)**.
4. Facoltativamente attiva **Enable passive eShop detection**.
5. Chiudi il menu, riavvia la console per eliminare eventuali cache DNS,
   quindi apri l'**eShop originale**.
6. Controlla se appare la pagina diagnostica zShop con Home, Best Sellers,
   New Releases, Mario Games, My Profile. Il suo aspetto **non è ancora**
   quello dell'eShop originale; l'applet, invece, deve essere quello Nintendo.
7. Se l'eShop continua a mostrare 377-0001, controlla nel menu se
   **Inkay eShop hostname: observed** o **Local DNS route: attempted**:
   queste informazioni distinguono un hook non attraversato da un problema
   nel server locale. La pagina deve essere raggiungibile dal browser di
   un altro dispositivo sulla LAN prima di attribuire il problema al plugin.
8. Verifica B, HOME e ritorno dalle categorie. **Non tentare installazioni**.

## Rimozione / rollback

Dal menu plugin disattiva `Route eShop to LAN backend (PORT 80)` e riavvia.
Se la console si blocca, spegnila, rimuovi `zShop.wps` dalla SD e riavvia.
Inkay resta invariato. Puoi ripristinare `newShop.wps` soltanto dopo aver
rimosso zShop.

## Vincoli di sicurezza

- Route disabilitata per impostazione predefinita; IP predefinito 0.0.0.0.
- Accetta solamente IP privati 10/8, 172.16/12 e 192.168/16.
- Solo processo eShop e solo `samurai.wup.shop.pretendo.cc`.
- Nessuna manipolazione dell'URL HTML o del browser; è possibile un errore
  se la Wii U usa un risolutore differente (test hardware indispensabile).
- Nessuna destinazione pubblica, nessuna patch SSL, IOSU o Inkay.
- Backend demo non autentica e non archivia dati personali; non esporlo ad internet.

## Compilazione

La CI `Build Aroma diagnostic plugin` ora produce `zShop.wps` v0.2.0-alpha
come **artefatto sperimentale** per test controllati, non come release stabile.
