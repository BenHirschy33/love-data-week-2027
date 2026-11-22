"""Unit tests for the raw dataset profiler in src/explore.py."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pyarrow as pa
import pyarrow.parquet as pq

from src.explore import list_data_files, profile_with_pyarrow, resolve_data_dir


class TestExplore(unittest.TestCase):
    """Self-contained tests for dataset discovery and profiling."""

    def test_resolve_data_dir_valid_cli_and_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp).resolve()
            self.assertEqual(resolve_data_dir(tmp), tmp_path)

            with mock.patch.dict(os.environ, {"DATA_DIR": tmp}, clear=False):
                self.assertEqual(resolve_data_dir(None), tmp_path)

    def test_resolve_data_dir_missing_exits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "does_not_exist")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as ctx:
                    resolve_data_dir(missing)
            self.assertEqual(ctx.exception.code, 1)
            self.assertIn("does not exist", stderr.getvalue())

    def test_list_data_files_filters_and_sorts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "nested"
            nested.mkdir()

            parquet_file = root / "b_games.parquet"
            csv_file = nested / "a_teams.csv"
            ignored_txt = root / "notes.txt"
            ignored_docx = root / "dictionary.docx"
            ignored_keep = root / ".gitkeep"

            for path in (parquet_file, csv_file, ignored_txt, ignored_docx, ignored_keep):
                path.write_text("placeholder", encoding="utf-8")

            found = list_data_files(root)
            self.assertEqual(found, sorted([parquet_file, csv_file]))

    def test_profile_with_pyarrow_synthetic_parquet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parquet_path = root / "sample_games.parquet"
            table = pa.table(
                {
                    "game_id": [1, 2, 3, 4],
                    "season": [2021, 2022, 2024, 2024],
                    "team": ["Purdue", "Indiana", "Iowa", "Purdue"],
                }
            )
            pq.write_table(table, parquet_path)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                profile_with_pyarrow(root, [parquet_path])

            output = stdout.getvalue()
            self.assertIn("FILE: sample_games.parquet", output)
            self.assertIn("ROWS: 4", output)
            self.assertIn("COLUMNS (3):", output)
            self.assertIn("- game_id:", output)
            self.assertIn("- season:", output)
            self.assertIn("- team:", output)
            self.assertIn("SEASONS (season): 2021 .. 2024 (3 distinct)", output)
            self.assertIn("SAMPLE (first 3 rows):", output)


if __name__ == "__main__":
    unittest.main()
