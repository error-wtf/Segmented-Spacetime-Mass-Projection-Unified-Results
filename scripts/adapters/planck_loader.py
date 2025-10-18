from __future__ import annotations

import logging
from pathlib import Path

from astropy.io import fits

from scripts.tools.logging_utils import get_logger


class PlanckLoader:
    """Validate and ingest Planck FITS maps stored locally."""

    def __init__(self, run_id: str, logger: logging.Logger | None = None) -> None:
        self.run_id = run_id
        self.log = logger or get_logger("PLANCK_LOADER", run_id)

    def ensure_exists(self, path: str | Path) -> Path:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Planck FITS missing: {path}")
        return path

    def load_fits(self, path: str | Path):
        path = self.ensure_exists(path)
        with fits.open(path) as hdul:
            data = hdul[1].data if len(hdul) > 1 else hdul[0].data
            header = hdul[1].header if len(hdul) > 1 else hdul[0].header
        self.log.info("Loaded Planck FITS %s", path)
        return data, header

    def load_for_run(self):
        path = Path(f"data/raw/planck/{self.run_id}/planck_map.fits")
        return self.load_fits(path)
