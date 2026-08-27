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
SOLIO_URL = "https://fpl.solioanalytics.com/api/data/latest"  # public projections feed
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


from html.parser import HTMLParser
import unicodedata


class _TableParser(HTMLParser):
    """Collect every <table> as a list of rows, each a list of cell texts."""
    def __init__(self):
        super().__init__()
        self.tables, self.cur, self.row, self.cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table": self.cur = []
        elif tag == "tr" and self.cur is not None: self.row = []
        elif tag in ("td", "th") and self.row is not None: self.cell = []

    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append("".join(self.cell).strip()); self.cell = None
        elif tag == "tr" and self.row is not None:
            self.cur.append(self.row); self.row = None
        elif tag == "table" and self.cur is not None:
            self.tables.append(self.cur); self.cur = None


def _norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return _re_mod.sub(r"[^a-z]", "", s.lower())


import re as _re_mod


def parse_solio(html, boot):
    """Extract Solio's projection table and match each player to an FPL id."""
    p = _TableParser(); p.feed(html)
    target = None
    for t in p.tables:
        if not t: continue
        header = [c.lower() for c in t[0]]
        if any("player" in c for c in header) and any("proj" in c for c in header):
            target = t; break
    if not target: return None
    header = [c.lower() for c in target[0]]

    def col(*names):
        for i, c in enumerate(header):
            if any(n in c for n in names): return i
        return None
    ci_name, ci_team, ci_pos = col("player"), col("team"), col("pos")
    ci_price, ci_proj, ci_own = col("price"), col("proj"), col("own")
    if ci_name is None or ci_proj is None: return None

    short = {t["short_name"].upper(): t["id"] for t in boot["teams"]}
    posmap = {"GK": 1, "GKP": 1, "DEF": 2, "MID": 3, "FWD": 4, "FOR": 4}
    elems = boot["elements"]

    def num(x):
        try: return float(_re_mod.sub(r"[^0-9.]", "", x))
        except Exception: return None

    players = []
    for row in target[1:]:
        need = [i for i in (ci_name, ci_proj) if i is not None]
        if len(row) <= max(need): continue
        name = row[ci_name].strip()
        proj = num(row[ci_proj])
        if not name or proj is None: continue
        team = row[ci_team].strip().upper() if ci_team is not None else ""
        pos = posmap.get(row[ci_pos].strip().upper()) if ci_pos is not None else None
        price = num(row[ci_price]) if ci_price is not None else None
        own = num(row[ci_own]) if ci_own is not None else None

        eid, tid, nn = None, short.get(team), _norm(name)
        if tid:
            best, bestscore = None, 0
            for e in elems:
                if e["team"] != tid: continue
                if pos is not None and e["element_type"] != pos: continue
                wn, sn, fn = _norm(e["web_name"]), _norm(e.get("second_name", "")), _norm(e.get("first_name", ""))
                score = 0
                if nn == wn: score = 100
                elif nn == fn: score = 75
                elif nn and (nn in sn or sn in nn): score = 80
                elif nn and len(nn) >= 4 and (nn[-4:] in wn or wn[-4:] in nn): score = 45
                if score and price is not None:
                    score -= abs(e["now_cost"] / 10 - price)
                if score > bestscore: bestscore, best = score, e
            if best and bestscore > 0: eid = best["id"]
        players.append({"name": name, "team": team, "proj": proj,
                        "price": price, "own": own, "element": eid})
    return players


def get_url(url, tries=3):
    """GET any absolute URL, returning parsed JSON."""
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

    print("Fetching Solio Analytics projections…")
    solio_ok = False
    try:
        req = urllib.request.Request(SOLIO_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
        gwm = _re_mod.search(r"Gameweek\s+(\d+)", body)
        genm = _re_mod.search(r"Generated\s+([\d.]+\s+[\d:]+\s+UTC)", body)
        players = parse_solio(body, boot)
        if players:
            matched = sum(1 for p in players if p["element"])
            write("solio.json", {
                "generated": genm.group(1) if genm else None,
                "gw": int(gwm.group(1)) if gwm else None,
                "source": "Solio Analytics",
                "url": SOLIO_URL,
                "players": players,
            })
            solio_ok = True
            print(f"  solio ✓ {len(players)} players, {matched} matched to FPL ids")
        else:
            print("  solio: could not find projection table")
    except Exception as e:  # noqa: BLE001
        print(f"  solio fetch failed: {e}")

    meta = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "solio": solio_ok,
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
