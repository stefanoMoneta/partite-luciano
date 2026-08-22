# Partite Luciano

Una piccola web-app pensata per mostrare nel modo più semplice possibile le prossime partite di **Serie A** e **Serie B**.

## Versione 0.1

Questa prima versione usa dati di esempio e serve solo a verificare l'interfaccia su telefono e tablet.

Caratteristiche:

- nessun menu;
- Serie A e Serie B nella stessa lista;
- partite raggruppate per giorno;
- ordinamento cronologico;
- "OGGI" e "DOMANI" evidenziati;
- ora molto visibile;
- layout adatto a telefono e tablet;
- predisposizione come PWA installabile.

## Pubblicazione con GitHub Pages

Dopo aver caricato i file nella repository:

1. apri **Settings** della repository;
2. vai su **Pages**;
3. in **Build and deployment**, seleziona **Deploy from a branch**;
4. scegli il branch `main` e la cartella `/ (root)`;
5. salva.

GitHub mostrerà poi l'indirizzo pubblico della pagina.

## Prossimo passo

Sostituire `data/partite.json` con un file aggiornato automaticamente tramite API.
