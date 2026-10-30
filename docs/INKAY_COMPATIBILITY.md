# zShop + Inkay/Pretendo (senza modificare Inkay)

## Requisito confermato

L'utente ha verificato che l'originale `newShop.wps` (uShop Access
v2.2.0-safe) riesce ad aprire il negozio alternativo con Pretendo attivo
e **senza modificare Inkay**. L'interfaccia ha però bug nelle categorie
e nei pulsanti di navigazione.

La build zShop v0.1.0 è solamente pass-through e non cambia la pagina:
l'errore `377-0001` con Inkay attivo è il comportamento previsto.

## Evidenza dal binario e dal sorgente pubblico

L'originale contiene quattro identificatori di ricerca:

- `nintendo-url`
- `inkay-url`
- `nintendo-allowlist`
- `inkay-allowlist`

Contiene inoltre i due URL di apertura:
`https://ninja.wup.shop.nintendo.net/ninja/wood_index.html?`
e `http://samurai.wup.shop.pretendo.cc/ninja/wood_index.html?`.

Il [sorgente ufficiale Inkay](https://github.com/PretendoNetwork/Inkay/blob/main/src/patches/eshop_applet.cpp)
mostra che la funzione `patchEshop()` associa la patch a
`FSOpenFile` quando viene aperto `vol/content/initial.oma`; sostituisce
l'URL originale Ninja con l'URL Pretendo e aggiorna la allowlist.
Quindi zShop dovrà gestire *entrambe* le forme, senza cambiare Inkay.

Non conosciamo ancora la sequenza temporale precisa degli hook nel
vecchio binario: sarà verificata prima della build che modifica la pagina.

## Strategia corretta

1. Continuare a usare Inkay **ufficiale** e invariato.
2. Consentire a zShop di agire **solo nell'applet eShop**, senza toccare
   identità, multiplayer, Miiverse, account, certificati o servizi IOSU.
3. Implementare un reindirizzamento **opt-in** per la sola pagina
   d'ingresso; non introdurre scansioni di memoria illimitate o scritture
   non validate.
4. Prevedere la gestione esplicita di URL/allowlist sia Nintendo sia
   Pretendo, con controlli di lunghezza e fallback sicuro.
5. Testare caricamento e navigazione con **Inkay originale attivo**;
   verificare B/HOME, ritorno alla Home e gli altri servizi Pretendo.

Qualsiasi incompatibilità dovrà essere corretta in zShop, **non in Inkay**.

## Esperimento scartato

Una precedente prova di ricerca aveva creato una variante di Inkay con
l'hook eShop disattivato. Tale approccio è stato **abbandonato** perché
contrario al vincolo dell'utente. La relativa CI e il codice di patch
sono stati rimossi dalla repository principale. Gli artefatti storici
di GitHub Actions non devono essere installati.

Non esiste ancora una build zShop che reindirizzi la pagina. La v0.1.0
diagnostica rimane priva di questa funzione.

## Implementazione alternativa v0.2.0-alpha (non ancora verificata su console)

Un'altra strategia evita completamente la scrittura in RAM e l'interazione con
l'ordine degli hook Inkay: conservare il suo URL di ingresso HTTP
`http://samurai.wup.shop.pretendo.cc/ninja/wood_index.html?` e intercettare
solamente le chiamate `getaddrinfo` e `gethostbyname` di quell'esatto nome
nel processo **eShop**. Se abilitato e con IP LAN valido, il resolver WUPS
restituisce l'IP del backend, lasciando intatto l'Host HTTP e la allowlist Inkay.

**Limiti:** non sappiamo ancora se il motore browser dell'eShop attraversa gli
hook DNS di nsysnet. La tecnica necessita di prova reale su firmware 5.5.5E.
Se il browser usa un resolver diverso o cache persistente, può ancora comparire
l'errore 377-0001. Il test non modifica Inkay, IOSU o certificati.

Vedi [istruzioni LAN](PHASE1B_LAN_ROUTE.md). Il backend ascolta sulla porta
**80** della LAN; nessuna configurazione del router deve renderlo pubblico.
