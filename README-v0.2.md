# Aggiornamento automatico delle partite

Questa versione aggiunge:

- Serie A e Serie B reali tramite API-Football;
- orizzonte: oggi + 3 giorni;
- fuso orario Europe/Rome;
- aggiornamento automatico 4 volte al giorno;
- aggiornamento manuale da GitHub Actions;
- chiave API conservata come GitHub secret;
- mancata sovrascrittura dei dati se l'API restituisce un errore.

## File da aggiungere/sostituire

Aggiungere:

- `scripts/aggiorna_partite.py`
- `.github/workflows/aggiorna-partite.yml`

Sostituire:

- `app.js`
- `service-worker.js`

## Secret necessario

Nelle impostazioni della repository creare un Actions secret chiamato:

`API_FOOTBALL_KEY`

e assegnargli come valore la propria chiave API-Football.

Dopo il push, aprire **Actions → Aggiorna partite → Run workflow** per eseguire subito
il primo aggiornamento senza aspettare il cron.
