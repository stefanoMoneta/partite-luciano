# Partite Luciano — aggiornamento v0.3

Questa versione sostituisce API-Football con i dati calendario ESPN.

## Perché

Il piano gratuito API-Football non dà accesso alla stagione corrente
2026/27. Per questa piccola app vengono invece richiesti i calendari ESPN
di Serie A (`ita.1`) e Serie B (`ita.2`).

## Cosa sostituire

Sostituire:

- `scripts/aggiorna_partite.py`
- `.github/workflows/aggiorna-partite.yml`

Non serve modificare `app.js`, `style.css`, `index.html` o gli altri file.

## Secret GitHub

`API_FOOTBALL_KEY` non viene più usato e può essere eliminato dalle
impostazioni della repository, anche se lasciarlo presente non crea problemi.

## Test

Dopo il push:

1. GitHub → Actions
2. `Aggiorna partite`
3. `Run workflow`

Nel log dello step `Scarica le partite` vengono stampate tutte le partite
raccolte, così è facile verificare subito date, orari e campionato.
