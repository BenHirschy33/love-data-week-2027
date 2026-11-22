# Project Options & Verified Data Findings (Love Data Week 2027)

This document captures verified structural findings from the official NCAA Women's Basketball dataset in `data/raw/` and ranks four candidate project directions for review, reordering, and additions before committing to implementation.

See [COMPETITION_GUIDE.md](./COMPETITION_GUIDE.md) for competition deadlines, no-login public hosting requirements, and Purdue / BTAA award rubrics.

---

## 1. Verified Data Snapshot (`data/raw/`)

Inspection of the five local Parquet files in `data/raw/` confirms the following schema, coverage, and scale:

| File | Rows | Columns | Coverage / Scope | Notes |
| --- | ---: | ---: | --- | --- |
| `teams.parquet` | 362 | 32 | Current Division I team directory | Team metadata, colors, logos, conferences |
| `rankings.parquet` | 79 | 38 | 2026 Week 3 snapshot only | Not a longitudinal poll history; single-week snapshot |
| `games.parquet` | 114,705 | 87 | Seasons 2006–2026 | Schedule, scores, venue, attendance, tournament flags, recent rank/broadcast cols |
| `team_box.parquet` | 120,032 | 59 | Team-game box scores | Shooting splits, rebounds, turnovers, Four Factors inputs, recent situational cols |
| `game_box.parquet` | 1,686,837 | 55 | 45,610 unique athletes | Player-level box scores across seasons |

> **Scope Note on `play_by_play.parquet`:** The optional `play_by_play.parquet` file (~620 MB) is not downloaded in `data/raw/` and is **not needed** unless the project pivots to 2020–2026 shot-location or lineup micro-analysis.

### Key Empirical Caveats (Verified in Exploration)

1. **Box Score Coverage & Minutes Validity (`team_box` & `game_box`)**
   - Full box-score coverage runs from **2017–2026** (**93.2%–100%** of games overall, and **100%** of NCAA Tournament games across **2015–2026**).
   - **2006–2013** box-score coverage is sparse, and `game_box.minutes` is `0` on **>90%** of played rows during 2006–2013.
   - **Filtering rule:** Always filter active player rows with `did_not_play == False` — never `active == True` (which drops valid participants depending on feed encoding).
2. **NCAA Tournament Isolation & Missing Seeds (`games`)**
   - Filtering `season_type == 3` AND `tournament_id == 22.0` cleanly isolates **1,280** NCAA March Madness games: **63/year** in 2006–2019 and 2021, **0** in 2020 (cancelled), and **67/year** in 2022–2026 (First Four expansion).
   - **No tournament seeds** are present in the dataset.
   - `home_current_rank`, `away_current_rank`, and `broadcast_*` columns only exist in **2024–2026**.
3. **Attendance Coverage Shift (`games.attendance`)**
   - Non-zero attendance (`attendance > 0`) jumps from **24%–31%** coverage in **2014–2019** (heavily skewed toward major programs) to **91%–96%** coverage in **2020** and **2022–2026**.
   - Any multi-era attendance analysis must use **balanced team panels** or explicit **era splits** to avoid reporting reporting-coverage artifacts as real attendance growth.
4. **Recent-Only Advanced Box Columns**
   - `fast_break_points`, `points_in_paint`, and `turnover_points` are populated for **2024–2026 only**.
   - `lead_changes` and `lead_percentage` are populated for **2026 only**.

---

## 2. Ranked Candidate Project Options

Options are ordered **1–4** by technical distinctiveness, data completeness, and alignment with Purdue and BTAA judging criteria. All options are open for reordering, scoping adjustments, or additions.

### Option 1 (Recommended Hybrid): Roster Balance / Star Power + March Madness Win-Probability & "Why" Explorer (2017–2026)

- **Core Question:** Does top-heavy star concentration or balanced scoring/rotation depth travel better in March Madness, and which measurable style and strength factors explain tournament upsets?
- **Data & Methodology:**
  - Combine `game_box` player distributions (**99.90%** exact player-to-team point reconciliation) to quantify star share, scoring concentration (e.g., Gini / Herfindahl / top-2 share), and bench depth.
  - Join `team_box` **Four Factors** (eFG%, TOV%, ORB%, FTR) and internal pre-tournament **Elo / SRS** ratings built from `games` (avoiding dependency on missing seeds).
  - Surface calibrated win probabilities alongside a transparent, factor-by-factor **"Why" matchup & upset explainer** whose modeling pattern transfers directly to NBA/pro basketball analytics.
- **Why It Ranks #1:** Leverages the richest reliable window (2017–2026, 100% tournament box coverage), tells an intuitive basketball story, and pairs predictive modeling with honest visual attribution rather than black-box scores.
- **Best Award Fit:** *Emerging Innovator* (applied modeling + feature engineering) + *Visionary Visualization* (interactive factor decomposition & bracket/matchup explorer).

### Option 2: 21-Year Evolution of Women's Basketball — Blowouts, 3-Point Shift & Attendance Boom (2006–2026)

- **Core Question:** How has the women's college game structurally transformed over 21 seasons across competitiveness, perimeter shooting, and fan demand?
- **Verified Signal Highlights:**
  - **Competitiveness / Margin:** Blowout rate (>= 20-point margin) climbed from **24.5%** in 2006 to **32.1%** in 2026.
  - **Perimeter Shift:** 3-point attempt share (`3PA / FGA`) rose from **31.1%** in 2017 to **34.0%** in 2026.
  - **Attendance Surge:** Regular-season attendance grew **+42%** across **2022–2025** (evaluated on consistent high-coverage reporting years), while NCAA Tournament average attendance peaked at **9,443** in **2024**.
- **Strengths & Watch-outs:** Extremely accessible narrative for general audiences and strong visual storytelling potential; requires careful era-gating and balanced-panel design so 2006–2013 sparse box scores and 2014–2019 attendance selection bias are explicitly disclosed and controlled.
- **Best Award Fit:** *Visionary Visualization* + *BTAA Chart Topper / Love It!* (broad public appeal and clean scrollytelling/dashboard design).

### Option 3: Conference Realignment, Scheduling & Attendance Economics (2006–2026 / 2024–2026)

- **Core Question:** How have conference realignment waves and national broadcast exposure reshaped travel/scheduling parity, venue fill rates, and commercial demand?
- **Data & Methodology:**
  - Track historical `home_conference_id` / `away_conference_id` transitions over 21 seasons (e.g., Big Ten expansion **11 -> 12 -> 14 -> 18** teams).
  - Analyze stadium demand via `venue_capacity` utilization (**53.3%** populated across `games`), paired with **2024–2026** `broadcast_market` and `broadcast_name` coverage to examine media visibility vs. gate attendance.
- **Strengths & Watch-outs:** Directly addresses business and conference-economics questions (especially timely for a Big Ten / BTAA audience); constrained by `broadcast_*` existing only in 2024–2026 and ~47% missing `venue_capacity`.
- **Best Award Fit:** *Excellence in Business Insights* (Daniels School of Business track).

### Option 4: Pure Pre-Game Tournament Elo / Upset Simulator (2017–2026)

- **Core Question:** How accurately can an internal pre-tournament Elo / margin-of-victory rating system predict March Madness outcomes and simulate bracket upset probabilities without official NCAA seeds?
- **Data & Methodology:**
  - Compute rolling season-to-date Elo ratings from `games` prior to `season_type == 3 & tournament_id == 22.0`, calibrate home/neutral adjustments, and run Monte Carlo bracket or matchup simulations.
- **Strengths & Watch-outs:** Cleanest engineering scope and fast to prototype, but narrower storytelling and visualization depth compared to Option 1's player/roster + Four Factors decomposition.
- **Best Award Fit:** *Emerging Innovator* (standalone predictive simulation, though weaker on multi-angle visual storytelling than Option 1).

---

## 3. AI Chatbot vs. Deterministic "Why" Explainer Trade-off

Because both the Purdue Challenge and BTAA Data Viz Championship require a **publicly viewable URL with no login** (see [COMPETITION_GUIDE.md](./COMPETITION_GUIDE.md)), embedding a live public LLM chatbot introduces serious operational and judging risks:

| Dimension | Live Public LLM Chatbot | Deterministic / Pre-Computed "Why" Explainer |
| --- | --- | --- |
| **API Keys & Cost Exposure** | No-login public URL exposes endpoints to abuse, rate-limit exhaustion, or unintended billing spikes without auth gates or proxy quotas. | Zero runtime LLM API calls; static or locally computed JSON/Parquet outputs host cleanly at zero variable cost. |
| **Latency & Reliability** | Cold starts, streaming delays, and provider outages can break live judging or showcase demos. | Sub-second interactive filtering, factor breakdowns, and tooltip explanations. |
| **Hallucination & Rubric Risk** | LLMs can invent stats, misquote margins, or conflate correlation with causation — directly violating BTAA's *Accuracy & Ethical Data Representation* criterion. | Every natural-language explanation is generated directly from exact model coefficients, Shapley/feature contributions, and verified box-score deltas. |

**Recommendation:** Use deterministic, template-backed **"Why" narratives** driven by exact pre-computed feature attributions and game stats rather than a live LLM chat widget.
