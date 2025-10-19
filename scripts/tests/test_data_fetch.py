from __future__ import annotations
from pathlib import Path
import os, pytest, pandas as pd
from scripts.tests.data_smoke_fetch import fetch_gaia_quick, fetch_sdss_quick, smoke_paths
from scripts.tools.logging_utils import get_logger

RUN_ID = "2025-10-17_gaia_ssz_real"

def test_gaia_smoke(tmp_path: Path):
    log = get_logger("TEST_GAIA", RUN_ID)
    p = smoke_paths(RUN_ID)["gaia_parquet"]
    if p.exists():
        try:
            df = pd.read_parquet(p)
        except Exception:
            p.unlink(missing_ok=True)
            df = None
    else:
        df = None

    if df is None:
        fetch_gaia_quick(str(p))
        df = pd.read_parquet(p)

    assert len(df) > 100, "Too few GAIA rows"
    for col in ("ra","dec","parallax","pmra","pmdec","phot_g_mean_mag"):
        assert col in df.columns, f"Missing GAIA col {col}"
    log.info("GAIA smoke rows=%d", len(df))

def test_sdss_smoke(tmp_path: Path):
    log = get_logger("TEST_SDSS", RUN_ID)
    p = smoke_paths(RUN_ID)["sdss_csv"]
    if not p.exists():
        fetch_sdss_quick(str(p), limit=5000)
    assert p.exists(), f"SDSS csv not found: {p}"
    df = pd.read_csv(p)
    assert len(df) > 100, "Too few SDSS rows"
    for col in ("ra","dec","u","g","r","i","z"):
        assert col in df.columns, f"Missing SDSS col {col}"
    log.info("SDSS smoke rows=%d", len(df))

def test_planck_presence():
    """Test Planck data presence.
    
    Planck data (~2 GB) is auto-fetched during installation.
    If missing, run: python scripts/fetch_planck.py
    """
    log = get_logger("TEST_PLANCK", RUN_ID)
    p = smoke_paths(RUN_ID)["planck_fits"]
    assert p.exists(), (
        f"Planck FITS not found: {p}\n"
        f"The install script should auto-fetch this file.\n"
        f"Manual download: python scripts/fetch_planck.py"
    )
    log.info("Planck present -> %s", p)
