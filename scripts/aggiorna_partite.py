#!/usr/bin/env python3

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


API_URL = "https://v3.football.api-sports.io/fixtures"
ROME = ZoneInfo("Europe/Rome")

# API-Football / API-Sports league IDs
LEAGUES = {
    135: "Serie A",
    136: "Serie B",
}

OUTPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "partite.json"


def current_season(today):
    """API-Football identifies a European season by its starting year."""
    return today.year if today.month >= 7 else today.year - 1


def fetch_fixtures(api_key, league_id, season, start_date, end_date):
    params = urllib.parse.urlencode(
        {
            "league": league_id,
            "season": season,
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
            "timezone": "Europe/Rome",
        }
    )

    request = urllib.request.Request(
        f"{API_URL}?{params}",
        headers={
            "x-apisports-key": api_key,
            "User-Agent": "partite-luciano/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"API-Football ha risposto con HTTP {exc.code}: {body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Impossibile contattare API-Football: {exc}") from exc

    errors = payload.get("errors")
    if errors:
        raise RuntimeError(f"Errore restituito da API-Football: {errors}")

    return payload.get("response", [])


def normalize_fixture(item, competition):
    fixture = item["fixture"]
    fixture_dt = datetime.fromisoformat(fixture["date"]).astimezone(ROME)

    return {
        "id": fixture["id"],
        "date": fixture_dt.date().isoformat(),
        "time": fixture_dt.strftime("%H:%M"),
        "home": item["teams"]["home"]["name"],
        "away": item["teams"]["away"]["name"],
        "competition": competition,
        "status": fixture["status"]["short"],
    }


def main():
    api_key = os.environ.get("API_FOOTBALL_KEY")
    if not api_key:
        print(
            "Variabile API_FOOTBALL_KEY non impostata. "
            "Aggiungila come GitHub Actions secret.",
            file=sys.stderr,
        )
        return 1

    now = datetime.now(ROME)
    start_date = now.date()
    end_date = start_date + timedelta(days=3)
    season = current_season(start_date)

    matches = []

    # Se anche una sola chiamata fallisce, lo script termina prima di
    # sovrascrivere il JSON esistente: l'app conserva così gli ultimi dati validi.
    for league_id, competition in LEAGUES.items():
        fixtures = fetch_fixtures(
            api_key=api_key,
            league_id=league_id,
            season=season,
            start_date=start_date,
            end_date=end_date,
        )

        for fixture in fixtures:
            matches.append(normalize_fixture(fixture, competition))

    # Elimina eventuali duplicati e ordina A+B insieme per data e ora.
    unique = {match["id"]: match for match in matches}
    matches = sorted(
        unique.values(),
        key=lambda match: (match["date"], match["time"], match["home"]),
    )

    output = {
        "exampleData": False,
        "updatedAt": now.isoformat(timespec="seconds"),
        "window": {
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
        },
        "matches": matches,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary = OUTPUT_FILE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(OUTPUT_FILE)

    print(
        f"Aggiornate {len(matches)} partite "
        f"dal {start_date.isoformat()} al {end_date.isoformat()}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
