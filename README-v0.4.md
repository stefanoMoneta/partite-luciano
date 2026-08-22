# Partite Luciano — v0.4

Modifiche:

- rimossa l'intestazione superiore;
- rimossa l'etichetta Serie A / Serie B dalle singole partite;
- aumentata la dimensione dei nomi delle squadre;
- evidenziate le partite del Pisa;
- italianizzati alcuni nomi ESPN (`Inter Milan` → `Inter`, `AS Roma` → `Roma`, ecc.);
- mantenuto soltanto l'orario di ultimo aggiornamento, in piccolo in fondo.

## File da sostituire

- `index.html`
- `style.css`
- `app.js`
- `scripts/aggiorna_partite.py`

Dopo il push, eseguire manualmente `Actions → Aggiorna partite → Run workflow`
per rigenerare subito `data/partite.json` con i nomi italianizzati.
