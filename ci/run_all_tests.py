from __future__ import annotations
import sys, subprocess, shutil, os
from pathlib import Path
from scripts.tests.data_smoke_fetch import smoke_paths, fetch_gaia_quick, fetch_sdss_quick
from scripts.tools.logging_utils import get_logger

def main(run_id: str):
    log = get_logger("RUN_ALL_TESTS", run_id)
    paths = smoke_paths(run_id)
    # 1) Daten sicherstellen (ohne Login)
    if not paths["gaia_parquet"].exists():
        fetch_gaia_quick(str(paths["gaia_parquet"]))
    if not paths["sdss_csv"].exists():
        fetch_sdss_quick(str(paths["sdss_csv"]), limit=5000)
    if not paths["planck_fits"].exists():
        log.warning("Planck FITS fehlt: %s (skipping Planck test)", paths["planck_fits"])

    # 2) pytest starten (JUnit XML optional)
    cmd = [sys.executable, "-m", "pytest", "scripts/tests", "-s", "-q"]
    log.info("Running pytest: %s", " ".join(cmd))
    rc = subprocess.call(cmd)
    log.info("pytest exit code=%s", rc)
    sys.exit(rc)

if __name__ == "__main__":
    run_id = sys.argv[1] if len(sys.argv)>1 else "2025-10-17_gaia_ssz_real"
    main(run_id)
