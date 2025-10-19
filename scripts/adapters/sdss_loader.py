from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from scripts.tools.logging_utils import get_logger


class SDSSLoader:
    """Load SDSS CSV exports produced by the smoke fetch process."""

    def __init__(self, run_id: str, logger: logging.Logger | None = None) -> None:
        self.run_id = run_id
        self.log = logger or get_logger("SDSS_LOADER", run_id)

    def load_csv(self, path: str | Path) -> pd.DataFrame:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"SDSS csv missing: {path}")
        df = pd.read_csv(path)
        if df.empty:
            raise ValueError(f"SDSS dataset empty: {path}")
        expected = {"ra", "dec", "u", "g", "r", "i", "z"}
        missing = sorted(expected - set(df.columns))
        if missing:
            raise ValueError(f"SDSS csv missing required columns: {missing}")
        self.log.info("Loaded SDSS csv: %s rows=%d", path, len(df))
        return df

    def load_for_run(self) -> pd.DataFrame:
        base = Path(f"data/raw/sdss/{self.run_id}/sdss_quick.csv")
        return self.load_csv(base)
