#!/usr/bin/env python3

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROME = ZoneInfo("Europe/Rome")
OUTPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "partite.json"

LEAGUES = {
    "ita.1": "Serie A",
    "ita.2": "Serie B",
    "ita.coppa_italia": "Coppa Italia",
}

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer"

# Nomi mostrati nell'app. La mappa può essere estesa facilmente
# se ESPN dovesse usare altre denominazioni internazionali.
TEAM_NAMES = {
    "Inter Milan": "Inter",
    "Internazionale": "Inter",
    "AS Roma": "Roma",
    "AC Milan": "Milan",
    "Hellas Verona": "Verona",
    "Juventus Turin": "Juventus",
    "SSC Napoli": "Napoli",
    "SS Lazio": "Lazio",
    "AC Monza": "Monza",
    "US Lecce": "Lecce",
    "US Cremonese": "Cremonese",
    "UC Sampdoria": "Sampdoria",
    "Spezia Calcio": "Spezia",
    "FC Südtirol": "Sudtirol",
    "Südtirol": "Sudtirol",
    "Pisa SC": "Pisa",
    "Pisa Sporting Club": "Pisa",
    "Virtus Entella": "Entella",
}

DAY_OFFSET = 7

FAVORITE_TEAM = "Pisa"
MIN_FAVORITE_MATCHES = 2

# Per evitare di cercare indefinitamente se il calendario
# delle giornate future non è ancora stato pubblicato.
MAX_FAVORITE_LOOKAHEAD = 60

def italian_team_name(name):
    return TEAM_NAMES.get(name, name)


def is_favorite_match(match):
    return (
        match["home"] == FAVORITE_TEAM
        or match["away"] == FAVORITE_TEAM
    )


def fetch_scoreboard(league_code, day):
    date_string = day.strftime("%Y%m%d")
    params = urllib.parse.urlencode({
        "dates": date_string,
        "limit": 100,
    })
    url = f"{BASE_URL}/{league_code}/scoreboard?{params}"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 partite-luciano/1.0"
            ),
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"ESPN ha risposto con HTTP {exc.code} per {league_code} "
            f"({date_string}): {body[:500]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Impossibile contattare ESPN per {league_code} "
            f"({date_string}): {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Risposta ESPN non valida per {league_code} ({date_string})"
        ) from exc

    events = payload.get("events")
    if events is None:
        raise RuntimeError(
            f"Formato ESPN inatteso per {league_code} ({date_string}): "
            "campo 'events' assente"
        )

    return events


def normalize_event(event, competition):
    competitions = event.get("competitions") or []
    if not competitions:
        raise RuntimeError(
            f"Evento ESPN {event.get('id', '?')} senza dati della partita"
        )

    match = competitions[0]
    competitors = match.get("competitors") or []

    home = None
    away = None

    for competitor in competitors:
        team = competitor.get("team") or {}
        name = (
            team.get("shortDisplayName")
            or team.get("displayName")
            or team.get("name")
        )
        name = italian_team_name(name)

        if competitor.get("homeAway") == "home":
            home = name
        elif competitor.get("homeAway") == "away":
            away = name

    if not home or not away:
        raise RuntimeError(
            f"Impossibile identificare casa/trasferta per evento "
            f"ESPN {event.get('id', '?')}"
        )

    event_date = event.get("date")
    if not event_date:
        raise RuntimeError(
            f"Evento ESPN {event.get('id', '?')} senza data"
        )

    fixture_dt = datetime.fromisoformat(
        event_date.replace("Z", "+00:00")
    ).astimezone(ROME)

    status = (
        ((event.get("status") or {}).get("type") or {}).get("name")
        or "STATUS_SCHEDULED"
    )

    return {
        "id": f"espn-{event['id']}",
        "date": fixture_dt.date().isoformat(),
        "time": fixture_dt.strftime("%H:%M"),
        "home": home,
        "away": away,
        "competition": competition,
        "status": status,
    }


def main():
    now = datetime.now(ROME)
    start_date = now.date()

    # DAY_OFFSET comprende anche oggi:
    # 7 = oggi + i 6 giorni successivi
    end_date = start_date + timedelta(days=DAY_OFFSET - 1)

    matches = []

    # ---------------------------------------------------------
    # 1. Calendario normale: tutte le partite di A e B
    #    nei prossimi DAY_OFFSET giorni
    # ---------------------------------------------------------

    for offset in range(DAY_OFFSET):
        day = start_date + timedelta(days=offset)

        for league_code, competition in LEAGUES.items():
            events = fetch_scoreboard(league_code, day)

            for event in events:
                normalized = normalize_event(event, competition)

                if (
                    start_date.isoformat() 
                    <= normalized["date"] 
                    <= end_date.isoformat()
                ):
                    matches.append(normalized)

    # ---------------------------------------------------------
    # 2. Controlla quante partite del Pisa abbiamo già
    # ---------------------------------------------------------

    favorite_matches = [
        match for match in matches
        if is_favorite_match(match)
    ]

    # ---------------------------------------------------------
    # 3. Se sono meno di due, cerca oltre la finestra standard.
    #    Oltre i 7 giorni vengono aggiunte SOLO le partite Pisa.
    # ---------------------------------------------------------

    search_day = end_date + timedelta(days=1)

    search_until = start_date + timedelta(
        days=MAX_FAVORITE_LOOKAHEAD
    )

    while (
        len(favorite_matches) < MIN_FAVORITE_MATCHES
        and search_day <= search_until
    ):

        for league_code, competition in LEAGUES.items():
            events = fetch_scoreboard(league_code, search_day)

            for event in events:
                normalized = normalize_event(event, competition)

                if is_favorite_match(normalized):
                    matches.append(normalized)
                    favorite_matches.append(normalized)

            # Se abbiamo già trovato le due partite,
            # evitiamo richieste inutili all'altra categoria.
            if len(favorite_matches) >= MIN_FAVORITE_MATCHES:
                break

        search_day += timedelta(days=1)

    # ---------------------------------------------------------
    # 4. Elimina eventuali duplicati e ordina tutto
    # ---------------------------------------------------------

    unique = {match["id"]: match for match in matches}

    matches = sorted(
        unique.values(),
        key=lambda match: (
            match["date"],
            match["time"],
            match["home"],
            match["away"],
        ),
    )

    output = {
        "exampleData": False,
        "updatedAt": now.isoformat(timespec="seconds"),
        "source": "ESPN",
        "window": {
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
        },
        "matches": matches,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary = OUTPUT_FILE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(
            output, 
            ensure_ascii=False, 
            indent=2
        ) + "\n",
        encoding="utf-8",
    )

    temporary.replace(OUTPUT_FILE)

    print(
        f"Aggiornate {len(matches)} partite. "
        f"Finestra standard: "
        f"{start_date.isoformat()} - {end_date.isoformat()}."
    )

    if favorite_matches:
        print(
            f"Partite del Pisa incluse: "
            f"{len(favorite_matches)}"
        )
    else:
        print(
            "Nessuna partita futura del Pisa trovata "
            "nel calendario disponibile."
        )

    for match in matches:
        print(
            f"{match['date']} {match['time']} "
            f"[{match['competition']}] "
            f"{match['home']} - {match['away']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
