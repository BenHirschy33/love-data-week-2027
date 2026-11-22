"""Exploratory profiler for raw datasets placed in data/raw/.

Supports Parquet, CSV, TSV, and JSON files using DuckDB (preferred) or a
PyArrow + Pandas fallback so schemas, row counts, season ranges, and samples
can be inspected with minimal memory overhead.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def resolve_data_dir(cli_dir: str | None) -> Path:
    """Resolve data directory from CLI arg, DATA_DIR env var, or default."""
    raw = cli_dir or os.environ.get("DATA_DIR") or "data/raw"
    path = Path(raw).expanduser().resolve()
    if not path.exists():
        print(f"Error: data directory does not exist: {path}", file=sys.stderr)
        sys.exit(1)
    return path


def list_data_files(data_dir: Path) -> list[Path]:
    """Return sorted supported tabular data files under data_dir."""
    return sorted(
        p
        for p in data_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in {".parquet", ".csv", ".tsv", ".json"}
    )


def profile_with_duckdb(data_dir: Path, files: list[Path]) -> None:
    """Profile files using DuckDB."""
    import duckdb  # type: ignore

    con = duckdb.connect(database=":memory:")
    for file_path in files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print("=" * 80)
        print(f"FILE: {file_path.relative_to(data_dir)} ({size_mb:.2f} MB)")
        suffix = file_path.suffix.lower()
        escaped = str(file_path).replace("'", "''")
        if suffix == ".parquet":
            relation = f"read_parquet('{escaped}')"
        elif suffix in {".csv", ".tsv"}:
            delim = "\t" if suffix == ".tsv" else ","
            relation = f"read_csv_auto('{escaped}', delim='{delim}')"
        else:
            relation = f"read_json_auto('{escaped}')"

        row_count = con.execute(f"SELECT COUNT(*) FROM {relation}").fetchone()[0]
        print(f"ROWS: {row_count:,}")

        schema = con.execute(f"DESCRIBE SELECT * FROM {relation}").fetchall()
        print(f"COLUMNS ({len(schema)}):")
        for col_name, col_type, *_ in schema:
            print(f"  - {col_name}: {col_type}")

        col_names = {c[0].lower(): c[0] for c in schema}
        if "season" in col_names:
            scol = col_names["season"]
            s_min, s_max, s_cnt = con.execute(
                f'SELECT MIN("{scol}"), MAX("{scol}"), COUNT(DISTINCT "{scol}") FROM {relation}'
            ).fetchone()
            print(f"SEASONS ({scol}): {s_min} .. {s_max} ({s_cnt} distinct)")

        print("SAMPLE (first 3 rows):")
        sample_df = con.execute(f"SELECT * FROM {relation} LIMIT 3").fetchdf()
        print(sample_df.to_string(index=False))


def profile_with_pyarrow(data_dir: Path, files: list[Path]) -> None:
    """Profile Parquet/CSV files using PyArrow and Pandas."""
    import pandas as pd  # type: ignore
    import pyarrow.parquet as pq  # type: ignore

    for file_path in files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print("=" * 80)
        print(f"FILE: {file_path.relative_to(data_dir)} ({size_mb:.2f} MB)")
        suffix = file_path.suffix.lower()
        if suffix == ".parquet":
            pf = pq.ParquetFile(file_path)
            print(f"ROWS: {pf.metadata.num_rows:,}")
            schema = pf.schema_arrow
            print(f"COLUMNS ({len(schema)}):")
            for field in schema:
                print(f"  - {field.name}: {field.type}")

            col_names = {f.name.lower(): f.name for f in schema}
            if "season" in col_names:
                scol = col_names["season"]
                seasons = pq.read_table(file_path, columns=[scol]).to_pandas()[scol].dropna()
                print(
                    f"SEASONS ({scol}): {seasons.min()} .. {seasons.max()} "
                    f"({seasons.nunique()} distinct)"
                )

            first_batch = next(pf.iter_batches(batch_size=3), None)
            if first_batch is not None:
                print("SAMPLE (first 3 rows):")
                print(first_batch.to_pandas().to_string(index=False))
        elif suffix in {".csv", ".tsv"}:
            sep = "\t" if suffix == ".tsv" else ","
            df = pd.read_csv(file_path, sep=sep, nrows=3)
            print(f"COLUMNS ({len(df.columns)}):")
            for col in df.columns:
                print(f"  - {col}: {df[col].dtype}")
            print("SAMPLE (first 3 rows):")
            print(df.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile raw datasets in data/raw/")
    parser.add_argument(
        "--data-dir",
        help="Path to raw data directory (defaults to DATA_DIR or data/raw)",
    )
    args = parser.parse_args()

    data_dir = resolve_data_dir(args.data_dir)
    files = list_data_files(data_dir)
    if not files:
        print(f"No supported data files (.parquet, .csv, .tsv, .json) found in {data_dir}")
        return

    try:
        import duckdb  # noqa: F401

        profile_with_duckdb(data_dir, files)
    except ImportError:
        try:
            import pyarrow  # noqa: F401

            profile_with_pyarrow(data_dir, files)
        except ImportError:
            print(
                "Error: neither duckdb nor pyarrow is installed in the active Python environment.\n"
                "Run `uv sync` or `pip install duckdb pyarrow pandas` first.",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
