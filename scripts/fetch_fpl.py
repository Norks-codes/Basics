#!/usr/bin/env python3
"""
Fetch live Fantasy Premier League data and save it as JSON files in /data.

This runs on GitHub's servers (via the Actions workflow), NOT in the browser,
so it can call the FPL API directly with no CORS proxy needed. The website then
reads these files from the same origin — reliable, no middle-man.

Configure your team and mini-league below.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

# ------------------------------------------------------------------
# CONFIG — change these if your team or league ever changes.
# ------------------------------------------------------------------
ENTRY_ID = "2537434"     # your FPL team id
LEAGUE_ID = "52140"      # your classic mini-league id

API = "https://fantasy.premierleague.com/api"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept": "application/json",
}


def get(path, tries=4):
    """GET a JSON endpoint with a few retries."""
    url = API + path
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last}")


def write(name, data):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    print(f"  wrote {name} ({os.path.getsize(path)//1024} KB)")


def main():
    os.makedirs(OUT, exist_ok=True)
    print("Fetching FPL core data…")
    boot = get("/bootstrap-static/")
    write("bootstrap.json", boot)
    write("fixtures.json", get("/fixtures/"))

    # Work out the gameweek to read picks for: current if live, else the last
    # finished one, else the next.
    events = boot.get("events", [])
    cur = next((e for e in events if e.get("is_current")), None)
    nxt = next((e for e in events if e.get("is_next")), None)
    finished = [e for e in events if e.get("finished")]
    gw_candidates = []
    if cur:
        gw_candidates.append(cur["id"])
    if finished:
        gw_candidates.append(max(e["id"] for e in finished))
    if nxt:
        gw_candidates.append(nxt["id"] - 1)
        gw_candidates.append(nxt["id"])
    gw_candidates.append(1)

    print(f"Fetching team {ENTRY_ID}…")
    entry = get(f"/entry/{ENTRY_ID}/")
    write(f"entry-{ENTRY_ID}.json", entry)

    picks = None
    used_gw = None
    for g in dict.fromkeys(gw_candidates):  # de-dup, keep order
        if g < 1:
            continue
        try:
            picks = get(f"/entry/{ENTRY_ID}/event/{g}/picks/")
            used_gw = g
            break
        except Exception:  # noqa: BLE001
            continue
    if picks:
        write(f"picks-{ENTRY_ID}.json", picks)
        print(f"  picks from GW{used_gw}")
    else:
        print("  (no picks available yet — season may not have started)")

    print(f"Fetching mini-league {LEAGUE_ID}…")
    try:
        league = get(f"/leagues-classic/{LEAGUE_ID}/standings/")
        write(f"league-{LEAGUE_ID}.json", league)

        # Scout each rival: pull their squad + captain for the same gameweek.
        results = (league.get("standings") or {}).get("results", [])
        teams = {}
        for r in results[:60]:
            eid = r.get("entry")
            if eid is None:
                continue
            team = {
                "name": r.get("entry_name"),
                "manager": r.get("player_name"),
                "rank": r.get("rank"),
                "total": r.get("total"),
                "event_total": r.get("event_total"),
            }
            if used_gw:
                try:
                    p = get(f"/entry/{eid}/event/{used_gw}/picks/")
                    plist = p.get("picks", [])
                    team["picks"] = [x["element"] for x in plist]
                    team["captain"] = next(
                        (x["element"] for x in plist if x.get("is_captain")), None)
                except Exception:  # noqa: BLE001
                    team["picks"] = []
            teams[str(eid)] = team
        write("league-picks.json", {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "gw": used_gw,
            "league_name": (league.get("league") or {}).get("name"),
            "me": ENTRY_ID,
            "teams": teams,
        })
        print(f"  scouted {len(teams)} rival squads")
    except Exception as e:  # noqa: BLE001
        print(f"  league fetch failed: {e}")

    meta = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entry": ENTRY_ID,
        "league": LEAGUE_ID,
        "current_gw": (cur or {}).get("id"),
        "next_gw": (nxt or {}).get("id"),
        "picks_gw": used_gw,
    }
    write("meta.json", meta)
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
