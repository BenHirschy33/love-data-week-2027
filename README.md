# Love Data Week 2027 — Boiler Up, Hammer Data Challenge

Purdue University **Boiler Up, Hammer Data Challenge** (Love Data Week 2027) project exploring the official NCAA Women's Basketball dataset.

- **Submission Deadline:** December 11, 2026 (11:59 PM)
- **Purdue Showcase:** January 22, 2027
- **BTAA Data Viz Championship:** February 8–12, 2027

## Directory Structure

```text
├── .github/        # CI workflows, PR template, and issue templates
├── app/            # Publicly hosted interactive visualization / web app
├── data/
│   ├── raw/        # Official Box dataset (gitignored; stored locally or in Colab/Drive)
│   └── processed/  # Cleaned/aggregated outputs used by the app
├── docs/           # Competition docs, methodology, and showcase materials
│   ├── COMPETITION_GUIDE.md  # Live-linked guide across Purdue & BTAA stages
│   └── PROJECT_OPTIONS.md    # Verified dataset findings and ranked project options
├── notebooks/      # Exploratory analysis & prototyping notebooks (local or Colab)
├── src/            # Reusable data loading, feature engineering, and modeling modules
│   └── explore.py  # DuckDB / PyArrow schema, row count, and season profiler
├── tests/          # Unit tests (pytest / unittest)
├── pyproject.toml  # Python dependencies and project configuration (uv / pip)
└── ruff.toml       # Python lint & formatting configuration
```

## Quickstart

1. Place the official NCAA Women's Basketball dataset files in `data/raw/` (gitignored).
2. Install dependencies and run the dataset profiler or unit tests:
   ```bash
   uv sync --dev
   uv run python src/explore.py
   uv run pytest
   ```

## Development Workflow

- Work on feature branches and merge into `main` via Pull Request (never commit directly to `main`).
- GitHub Actions runs separate **Lint** ([lint.yml](.github/workflows/lint.yml)) and **Test** ([test.yml](.github/workflows/test.yml)) workflows on every PR.
- Raw datasets belong in `data/raw/` locally (or Google Drive/Colab) and are excluded from git via `.gitignore`.
