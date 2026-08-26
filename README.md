# FPL Edge — your gameweek assistant

A personal Fantasy Premier League tool that pulls **live data**, assesses your squad's
strengths and weaknesses, and tells you — gameweek to gameweek — **who to captain, who to
buy/sell, and when to play your chips**. It remembers your season in your browser.

It's a single file (`index.html`). No installing, no terminal.

---

## Get it running (pick ONE — no terminal needed)

### Option A — Just open it (30 seconds, easiest)
1. On the GitHub page for this repo, click **`index.html`**.
2. Click the **Download raw file** button (top-right of the file view).
3. On your computer, **double-click the downloaded file**. It opens in your web browser. Done.

> This works because the tool is fully self-contained. The only thing it needs the internet
> for is fetching live FPL data, which it does through a public relay (see "Why a relay?" below).

### Option B — A proper web address you can bookmark (GitHub Pages, ~2 minutes, still no terminal)
1. On this repo's GitHub page, click **Settings** (top menu).
2. In the left sidebar, click **Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Under **Branch**, pick the branch this file is on
   (`claude/fpl-gameweek-recommendations-qc5roe`) and folder **/ (root)**, then **Save**.
5. Wait ~1 minute, refresh the page. GitHub shows a link like
   **`https://norks-codes.github.io/Basics/`** — that's your live app. Bookmark it on your
   phone and laptop.

> Tip: if you'd rather have the app on the neat `main` address, tell me and I'll set `main`
> as the default branch for you.

---

## How to use it

1. **Tab 1 — My Team.** Enter your **FPL Team ID** and click *Load my team*.
   - Your Team ID is the number in your team's web address on the official FPL site:
     go to the **Points** tab while logged in, and look at the address bar for
     `/entry/`**`1234567`**`/`. That number is your ID.
   - It loads your real 15 players, budget and bank, and shows a **strengths/weaknesses**
     read-out. (No ID? Open "build a squad by hand" and search players in.)
2. **Tab 2 — This Gameweek.** Your **captain pick**, **transfer ideas** (with the projected
   points gain and whether a −4 hit is worth it), and **chip watch**.
3. **Tab 3 — Find Players.** A ranked, filterable table to hunt for value buys or
   differentials. Click **+ add** to slot one into your squad and re-run the numbers.
4. **Tab 4 — Season Log.** Record your points, rank and mini-league position each week.
   **This is how it remembers you between gameweeks** — it's all saved in your browser.
5. **Tab 5 — How to Win.** The strategy the tool's advice is built on.

---

## How it actually works (the honest version)

- **Where the data comes from:** the official Fantasy Premier League feed
  (`fantasy.premierleague.com/api`) — the same numbers the real game uses: prices, form,
  fixtures, injuries, ownership.
- **Why a relay?** That feed refuses to be read directly by a web page (a browser security
  rule called *CORS*). **This is the single most common reason home-made FPL tools look
  broken.** FPL Edge fixes it by routing requests through free public relays and
  automatically trying a backup if one is busy. If data ever fails to load, wait a moment
  and click *Load my team* again.
- **How it stores data between gameweeks:** everything (your squad, chips used, bank, and
  your gameweek log) is saved in your browser's local storage under one key (`fplEdge.v1`).
  It stays on the device you use. It is **not** synced across devices — if you want that,
  that's the next upgrade (a tiny free cloud database), just ask.
- **The recommendation logic (no black box):** every player gets a projected score:

  > **projected points = recent form × fixture difficulty × chance of playing**

  - *Form* blends recent points-per-game with the season rate.
  - *Fixture difficulty* uses FPL's 1–5 rating: easy games multiply the score up, hard
    games multiply it down. Double gameweeks count both games; blank gameweeks score zero.
  - *Chance of playing* discounts anyone injured, suspended or doubtful — an unavailable
    player scores nothing, because a player who doesn't play scores nothing.
  - **Captain** = your available player with the highest projection this gameweek.
  - **Transfers** = your weakest/injured starters vs. the best player you can afford in the
    same position; it shows the net gain over 5 gameweeks and whether that beats a −4 hit.
  - **Chips** = pattern alerts (Bench Boost when your bench has a double gameweek, Triple
    Captain on an in-form premium in a double, Free Hit on a blank, Wildcard when the squad
    needs 4+ changes).

---

## Roadmap (things I can add next — just ask)
- Pull your **mini-league table** and rivals' teams, so advice targets the people you're
  actually racing.
- **Cross-device sync** so your season log follows you from phone to laptop.
- A **best-XI / auto-bench** picker and captaincy history charts.

---

## Notes
This is an unofficial personal project, not affiliated with the Premier League. Projections
are estimates to guide decisions, not guarantees.

Strategy sources: [Premier League — FPL champion guide](https://www.premierleague.com/en/news/4672128/fpl-champion-how-to-pick-your-captain-and-maximise-your-chips),
[Fantasy Football Scout — chip strategy](https://www.fantasyfootballscout.co.uk/2025/09/12/fpl-chip-strategy-5-ideas-for-those-yet-to-use-one),
[Fantasy Football Fix — chip strategy](https://www.fantasyfootballfix.com/blog-index/fpl-chip-strategy/).
FPL API reference: [Frenzel Timothy — API endpoints guide](https://medium.com/@frenzelts/fantasy-premier-league-api-endpoints-a-detailed-guide-acbd5598eb19).
