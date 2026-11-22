# Project Options & Verified Data Findings

> **Status:** Shortlist finalized ahead of Thanksgiving break. All options run at **$0 cost** with **no database or paid server** (local Python/PyArrow/DuckDB or free Google Colab; public static hosting on **GitHub Pages** or free **Streamlit Community Cloud**).
>
> **Deadline Reminder:** Purdue submission closes **December 11, 2026 at 11:59 PM** (~10–12 days after break).

---

## 1. Verified Data Snapshot (`data/raw/`)

Inspected all 5 compact `.parquet` tables from the official Box dataset (`NCAA Women's Basketball Data Files 2026`, SportsDataverse / `wehoop` schema):

| File | Size | Rows | Cols | Coverage & Key Notes |
|---|---:|---:|---:|---|
| `teams.parquet` | 0.23 MB | 362 | 32 | Current D1 team directory (names, colors, logos, current conference) |
| `rankings.parquet` | 0.03 MB | 79 | 38 | **2026 Postseason Week 3** AP Top 25 & Coaches Poll snapshot only |
| `games.parquet` | 13.62 MB | 114,705 | 87 | **2006–2026** (21 seasons): `112,082` reg/conf-tourn (`season_type=2`), `2,623` national postseason (`season_type=3`) |
| `team_box.parquet` | 6.03 MB | 120,032 | 59 | **2017–2026** full coverage (`93.2%–100%` of games; `100%` of March Madness 2015–2026); sparse in 2006–2013 |
| `game_box.parquet` | 36.45 MB | 1,686,837 | 55 | **45,610** athletes; `sum(player points) == team_score` reconciles in **99.90%** of 2017–2026 team-games |

*(Note: `play_by_play.parquet` [620 MB] and duplicate `.csv` files are excluded; play-by-play is unnecessary for these options.)*

### Key Empirical Findings & Caveats
1. **Regular-Season AP Rankings AND NCAA Tournament Seeds Exist (2024–2026):**
   - In `games.parquet` for **2024, 2025, and 2026** (`17,625` games), `home_current_rank` / `away_current_rank` are `100%` populated:
     - **Regular season (`season_type == 2`):** Live weekly **AP Top-25 rank** (`1..25`, or `99.0` for unranked; `675–700` Top-25 games/yr). Higher AP rank won `85.1%` overall (`305` upsets: `183` by unranked teams and `122` in Top-25-vs-Top-25 matchups, where the higher rank won only `65.7%`).
     - **March Madness (`tournament_id == 22.0`):** Actual **NCAA Tournament Seeds (`1..16`)** across all **201 tournament games** (`84.8%` better-seed win rate, `28` seed upsets across `184` non-equal-seed games).
   - *(2006–2023 has `NaN` in `home_current_rank`/`away_current_rank`.)*
2. **Clean Postseason Isolation:** `season_type == 3 & tournament_id == 22.0` isolates all **1,280 NCAA Tournament games** (`63`/yr in 2006–2019 & 2021; `0` in 2020; `67`/yr in 2022–2026), separate from WNIT (`37.0`), WBI (`38.0`), WBIT (`62.0`), and conference tournaments (`season_type == 2`).
3. **Box-Score Completeness & Era Boundaries:**
   - Core `team_box` stats (shooting, rebounds, turnovers, assists, steals, blocks) have **0% nulls** in 2017–2026.
   - `fast_break_points`, `points_in_paint`, and `turnover_points` are **2024–2026 only** (`100%` null before 2024); `lead_changes` and `lead_percentage` are **2026 only**.
   - In `game_box.parquet`, always filter `did_not_play == False` (never `active == True`), and avoid 2006–2013 `minutes` (`0` on `>90%` of played rows).
4. **Supplemental Data:** Permitted under BTAA rules as long as this NCAA Women's Basketball dataset remains the core (e.g., optional public BartTorvik NCAAW T-Rank / NCAA NET snapshots for Layer 1 comparison).
5. **AI Policy & Scope:** No live open LLM chatbot on the public submission URL (avoids API-key exposure, cost, latency, and stat hallucinations). Any qualitative summaries can be pre-generated offline into static JSON, and AI assistance will be disclosed concisely on the submission form.

---

## 2. Final Shortlist (4 Options to Re-Evaluate After Break)

### Option 1 (Primary Candidate): Ranking Audit -> New Hybrid Team Rating System
- **Core Question:** *How accurate are human rankings (AP Top-25, NCAA Seeds) vs. objective efficiency ratings—where are their blind spots, and can a new rating combining SOS-adjusted efficiency with `game_box` player consistency outperform them?*
- **Target Awards:** **Emerging Innovator** (undergrad technical skill + fresh approach), **Excellence in Business Insights** (fair-value vs. poll/seed pricing), and **Visionary Visualization** / **BTAA Advancement**.
- **Incremental 3-Layer Build Plan (Shippable at Each Layer):**
  1. **Layer 1 — Audit Existing Rankings (Foundation, shippable standalone):** Benchmark 2024–2026 AP Polls and NCAA Seeds against a transparent SOS-adjusted efficiency baseline (and optional public BartTorvik/NET snapshot). Map agreement, upset rates over time, and specific blind spots.
  2. **Layer 2 — New Hybrid Rating Metric (Differentiator):** Address Layer 1's holes by testing under-used signals (`game_box` scoring concentration/consistency, Four Factors, variance, or calibrated ML weights) across all 362 D1 teams (2017–2026), verifying out-of-sample gains over AP/Seeds/baseline efficiency.
  3. **Layer 3 — Mispricing & Matchup View (Optional Polish):** Add an interactive matchup/mispricing explorer highlighting the largest *New Rating vs. AP/Seed* disagreements (plus optional pre-generated offline scouting callouts).
- **Long-Term Value:** Clean SportsDataverse (`wehoop`/`hoopR`)-compatible rating core in `src/` that can be extended to Men's CBB or NBA later.

### Option 2 (Focused Fallback): Matchup & Seed Mispricing Explorer (2024–2026)
- **Core Question:** *Which individual Top-25 and March Madness matchups show the largest gap between objective efficiency metrics and AP Rank / Seed expectations?*
- **Why Keep as Backup:** Skips building a full 362-team rating system if time is tight after break, while keeping the "fair value vs. poll/seed price" framing.

### Option 3 (Pure `game_box` Alternative): When Does Star Power Beat Balance? (2017–2026)
- **Core Question:** *Rather than assuming balanced scoring is always better, when does relying on a high-usage star help (e.g., underdog upset ceiling) vs. break down in March?*
- **Initial Signal Observed:** In 2017–2026 March Madness (`1,174` team-games), teams with `top1_share >= 35%` won `38.2%` vs. `66.1%` when `< 25%`, while bench share dropped from `26.3%` (regular season) to `19.9%` (March)—requiring a pre-game season-average test to control for trailing-team bias.

### Option 4 (Personal Interest / Pure Prediction): Pure Matchup & Game-Outcome Simulator (2017–2026)
- **Core Question:** *Using all available pre-game box-score, schedule, and roster signals, how accurately can an ML model predict individual game winners and expected point margins?*
- **Why Keep as Option 4:** Directly aligns with personal interest in predicting game outcomes and building a reusable SportsDataverse forecasting engine (`wehoop`/`hoopR`), though it ranks #4 for Love Data Week because a pure predictor needs strong visual storytelling around *why* predictions happen to score well on the BTAA Data Viz rubric.

---

## 3. Pickup Plan After Break

1. Confirm Option 1 (or pivot to Option 2/3/4) before writing modeling code.
2. Start directly on **Layer 1** in `src/` + `notebooks/`: build the clean `2017–2026` game/box-score loader and run the 2024–2026 AP Poll & NCAA Seed accuracy audit.
3. Move to **Layer 2** (hybrid rating + out-of-sample validation), export precomputed JSONs to `data/processed/`, and build the static interactive visualization in `app/` for **GitHub Pages** ahead of **December 11**.
