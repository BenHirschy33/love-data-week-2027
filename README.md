# Love Data Week 2027 — Boiler Up, Hammer Data Challenge

Purdue University **Boiler Up, Hammer Data Challenge** (Love Data Week 2027) project exploring the official NCAA Women's Basketball dataset.

- **Submission Deadline:** December 11, 2026 (11:59 PM)
- **Purdue Showcase:** January 22, 2027
- **BTAA Data Viz Championship:** February 8–12, 2027

## Directory Structure

```text
├── app/            # Publicly hosted interactive visualization / web app
├── data/
│   ├── raw/        # Official Box dataset (gitignored; stored locally or in Colab/Drive)
│   └── processed/  # Cleaned/aggregated outputs used by the app
├── docs/           # Project notes, methodology, and showcase materials
├── notebooks/      # Exploratory analysis & prototyping notebooks (local or Colab)
└── src/            # Reusable data loading, feature engineering, and modeling modules
```

## Dataset

Official NCAA Women's Basketball dataset (via Purdue IDA+A / BTAA):
- Download from the Box link provided in the challenge announcement and place files in `data/raw/`.
- Raw data is intentionally excluded from git via `.gitignore`.
