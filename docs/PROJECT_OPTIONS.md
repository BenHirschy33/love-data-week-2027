# Project Options & Verified Data Findings

> **Cost & Infrastructure Constraint:** All options below run at **$0 cost** with **no database or paid server** required. Training/aggregation on the 56.5 MB Parquet tables runs in seconds locally on 16 GB RAM (or in free Google Colab if needed), and the public submission can be hosted free on **GitHub Pages** (static HTML/JS/Plotly reading precomputed JSONs in `data/processed/`) or **Streamlit Community Cloud**.

---

## 1. Verified Data Snapshot (`data/raw/`)

Inspected all 5 compact `.parquet` tables from the official Box dataset (`NCAA Women's Basketball Data Files 2026`, SportsDataverse / `wehoop` schema):

| File | Size | Rows | Cols | Coverage & Key Notes |
|---|---:|---:|---:|---|
| `teams.parquet` | 0.23 MB | 362 | 32 | Current D1 team directory (names, colors, logos, current conference) |
| `rankings.parquet` | 0.03 MB | 79 | 38 | **2026 Postseason Week 3** AP Top 25 & Coaches Poll snapshot only |
| `games.parquet` | 13.62 MB | 114,705 | 87 | **2006–2026** (21 seasons): `112,082` reg/conf-tourn (`season_type=2`), `2,623` national postseason (`season_type=3`) |
| `team_box.parquet` | 6.03 MB | 120,032 | 59 | **2017–2026** full coverage (93.2%–100% of games; 100% of March Madness 2015–2026); sparse in 2006–2013 |
| `game_box.parquet` | 36.45 MB | 1,686,837 | 55 | **45,610** athletes; `sum(player points) == team_score` reconciles in **99.90%** of 2017–2026 team-games |

*(Note: `play_by_play.parquet` [620 MB] and duplicate `.csv` files were excluded; play-by-play is unnecessary unless pivoting to 2020–2026 shot-location/lineup-stint micro-analysis.)*

### Crucial Empirical Discoveries & Caveats
1. **Regular-Season Rankings AND NCAA Tournament Seeds DO Exist (2024–2026):**
   - In `games.parquet` for **2024, 2025, and 2026** (`17,625` games), `home_current_rank` and `away_current_rank` are populated for **100%** of games:
     - **Regular season (`season_type == 2`):** Live weekly AP Poll rank (`1..25`, or `99.0` for unranked) throughout the season (`675–700` Top-25 games/yr).
     - **March Madness (`tournament_id == 22.0`):** Actual **NCAA Tournament Seeds (`1..16`)** for all **201 tournament games** across 2024, 2025, and 2026.
   - *(2006–2023 has `NaN` in `home_current_rank`/`away_current_rank`.)*
2. **Clean Postseason Isolation:** `season_type == 3 & tournament_id == 22.0` isolates all **1,280 NCAA Tournament games** (63/yr in 2006–2019 & 2021; 0 in 2020; 67/yr in 2022–2026), separate from WNIT (`37.0`), WBI (`38.0`), WBIT (`62.0`), and conference tournaments (which live in `season_type == 2`).
3. **Box-Score Era Split:**
   - Core shooting/rebound/turnover stats (`team_box`) have **0% nulls** in 2017–2026.
   - `fast_break_points`, `points_in_paint`, and `turnover_points` are populated **only in 2024–2026** (`100%` null before 2024); `lead_changes` and `lead_percentage` exist **only in 2026**.
   - In `game_box.parquet`, filter `did_not_play == False` (never `active == True`), and avoid 2006–2013 `minutes` (`0` on >90% of played rows).
4. **Attendance Reporting Bias:** `attendance > 0` jumps from 24%–31% coverage in 2014–2019 (major-program biased) to 91%–96% in 2020 and 2022–2026; use 2022–2026 or fixed-program panels for regular-season attendance trends.

---

## 2. Plug-and-Play Architecture Note (Future Men's CBB / NBA Reuse)

This dataset uses the open-source **SportsDataverse (`wehoop`)** schema, which Men's College Basketball (`hoopR`) shares nearly column-for-column. Keeping a clean `src/` data adapter separate from feature engineering and modeling means the exact same evaluation/prediction core can ingest Men's CBB or NBA data later—without building custom multi-sport infrastructure before the December 11 deadline.

---

## 3. Ranked Project Options (Ordered for Review)

### Option 1 (Top Pick): Poll & Seed Mispricing — True Efficiency vs. Reputation (2017–2026, Benchmark 2024–2026)
- **Core Question:** *How accurately do weekly AP Poll rankings and NCAA Tournament seeds (2024–2026) price true team strength—and which Four Factors + roster-depth metrics expose overrated and underrated teams?*
- **What You Build:**
  - Train a calibrated team-strength & game-margin model (2017–2026 rolling Four Factors, pace, home/away, Elo, plus `game_box` roster concentration/bench depth).
  - Benchmark model ratings directly against **2024–2026 AP Poll ranks & NCAA Tournament seeds** to measure where voters/committees overvalue scoring margin or star hype vs. underlying efficiency.
  - Present 3 crisp editorial charts (True Strength vs. Seed/AP Rank mispricing map, upset drivers, calibration vs. seed baseline) in a zero-cost GitHub Pages or Streamlit site.
- **Why #1:** Directly builds a **mispricing evaluator** (same mental model as comparing fair value against betting odds later), taps the under-explored `game_box` table, and tells a clear, original visual story for **Emerging Innovator**, **Excellence in Business Insights**, and **Visionary Visualization**.

### Option 2: Single-Game Matchup & Point-Margin Predictor (SportsDataverse Engine)
- **Core Question:** *Which pre-game team efficiency and roster features best predict single-game win probability and point margin—and how sensitive are upsets to style matchups?*
- **What You Build:**
  - Clean single-game win-probability + expected point-margin (spread) pipeline trained on 2017–2026 (~50k games), replacing brittle bracket-wide optimization with calibrated per-game inference.
  - Interactive **Single-Game Matchup Explorer** (pick Team A vs. Team B -> see win %, expected margin, and top stat drivers).
- **Why #2:** Closest direct prototype for Men's CBB / NBA game and spread modeling; **\$0** on Streamlit Community Cloud (or static GitHub Pages for featured/tournament matchups). Requires strong narrative framing so judges see a clear story, not just a prediction widget.

### Option 3: Star Power vs. Roster Depth — What Survives March? (`game_box.parquet`, 2017–2026)
- **Core Question:** *Using 1.69M player box rows, do top-heavy rosters reliant on 1–2 stars or balanced 8–9 player rotations perform better in regular season vs. March Madness?*
- **What You Build:**
  - Compute per-team scoring concentration (top-1/top-2 share, HHI/Gini), bench minutes share, and foul-trouble sensitivity across ~108,000 team-games, spotlighting Big Ten / Purdue and NCAA Tournament survivors (`tournament_id == 22.0`).
- **Why #3:** Uses the dataset's richest under-explored table (`game_box.parquet`) and delivers clear basketball-operations/staff insights (**Excellence in Business Insights**), though it is less focused on game-by-game prediction.

### Option 4 (Lowest Priority): 21-Year Macro Evolution — Blowouts, 3-Point Shift & Attendance Boom (2006–2026)
- **Core Question:** *How have scoring margins (20+ pt blowouts rising from 24.5% in 2006 to 32.1% in 2026), 3-point attempt rates (31.1% to 34.0%), and post-2022 attendance (+42%) reshaped the sport?*
- **Why #4:** Strong editorial fit for **Visionary Visualization** / **BTAA Chart Topper** and trivial static hosting, but lower personal interest and no predictive/mispricing component.

---

## 4. AI Chatbot Scope Decision

- **Out of scope for the core submission:** A live LLM chatbot on a no-login public URL introduces API key cost/abuse risk, latency, and stat-hallucination risk.
- **Recommended instead:** Deterministic, data-backed summary callouts generated directly from model outputs and team stats (zero cost, instant load, 100% accurate).
