from __future__ import annotations
import os, sys, json, time, traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

import pandas as pd

# Lazy imports so das Script ohne astroquery-Importfehler starten kann,
# selbst wenn kurzzeitig Pakete fehlen. Fehler werden geloggt & erklärt.
def _lazy_imports():
    global Gaia, SDSS, fits
    from astroquery.gaia import Gaia
    from astroquery.sdss import SDSS
    from astropy.io import fits
    return Gaia, SDSS, fits

# -------- Logging ----------
import logging
from logging.handlers import RotatingFileHandler
def make_logger(run_id: str, name: str = "AUTOFETCH") -> logging.Logger:
    logdir = Path("data/logs"); logdir.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    ts = time.strftime("%Y%m%d_%H%M%S")
    fh = RotatingFileHandler(logdir / f"autofetch_{run_id}_{ts}.log",
                             maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    fh.setFormatter(fmt); fh.setLevel(logging.INFO)
    sh = logging.StreamHandler(); sh.setFormatter(fmt); sh.setLevel(logging.INFO)
    log.addHandler(fh); log.addHandler(sh)
    log.propagate = False
    log.info("Logger ready. run_id=%s", run_id)
    return log

# -------- Retry -----------
import random, time as _t
def retry(max_tries=5, base=1.0, jitter=0.5, factor=2.0, exceptions=(Exception,)):
    def deco(fn):
        def wrap(*a, **k):
            delay = base
            for i in range(max_tries):
                try:
                    return fn(*a, **k)
                except exceptions as e:
                    if i == max_tries - 1:
                        raise
                    _t.sleep(delay + random.random()*jitter)
                    delay *= factor
        return wrap
    return deco

# -------- Config ----------
@dataclass
class AutoFetchConfig:
    run_id: str = "2025-10-17_gaia_ssz_real"
    # Eingangsquellen: Falls leer, werden sie erstellt/gezogen
    gaia_base: Path = Path("data/raw/gaia/2025-10-17_gaia_ssz_real/gaia_dr3_core")
    sdss_base: Path = Path("data/raw/sdss/2025-10-17_gaia_ssz_real/sdss_catalog")
    planck_fits: Path = Path("data/raw/planck/2025-10-17_gaia_ssz_real/planck_map.fits")
    prefer_parquet: bool = True
    # Pipeline / Tests
    run_pipeline: bool = True
    run_pytest: bool = True

# -------- Helpers ----------
def ensure_dirs_for_base(base: Path):
    base.parent.mkdir(parents=True, exist_ok=True)

def ensure_both_formats(base: Path, prefer_parquet: bool = True) -> Dict[str, Optional[Path]]:
    """Stellt sicher, dass base.csv und base.parquet existieren (konvertiert falls nötig)."""
    p_csv = base.with_suffix(".csv")
    p_parq = base.with_suffix(".parquet")
    have_csv, have_parq = p_csv.exists(), p_parq.exists()

    if not have_csv and not have_parq:
        raise FileNotFoundError(f"Neither CSV nor Parquet exist for {base}")

    if have_csv and not have_parq:
        df = pd.read_csv(p_csv)
        df.to_parquet(p_parq, index=False)
        have_parq = True
    if have_parq and not have_csv:
        try:
            df = pd.read_parquet(p_parq)
        except Exception:
            p_parq.unlink(missing_ok=True)
            raise
        df.to_csv(p_csv, index=False)
        have_csv = True

    if have_parq:
        try:
            pd.read_parquet(p_parq, columns=["source_id"]).head(1)
        except Exception:
            p_parq.unlink(missing_ok=True)
            have_parq = False
    if have_csv:
        try:
            pd.read_csv(p_csv, nrows=1)
        except Exception:
            p_csv.unlink(missing_ok=True)
            have_csv = False

    if not have_parq and have_csv:
        df = pd.read_csv(p_csv)
        df.to_parquet(p_parq, index=False)
        have_parq = True
    if not have_csv and have_parq:
        df = pd.read_parquet(p_parq)
        df.to_csv(p_csv, index=False)
        have_csv = True

    ordered = (p_parq, p_csv) if prefer_parquet else (p_csv, p_parq)
    primary = ordered[0] if ordered[0].exists() else ordered[1]
    return {"primary": primary, "csv": p_csv if have_csv else None, "parquet": p_parq if have_parq else None}

# -------- Fetchers --------
GAIA_ADQL_PATH = Path(__file__).resolve().parents[1] / "queries" / "gaia_dr3_core.sql"
GAIA_ROW_LIMIT = 50000


REQUIRED_GAIA_COLUMNS = {
    "ra",
    "dec",
    "parallax",
    "pmra",
    "pmdec",
    "ra_error",
    "dec_error",
    "parallax_error",
    "pmra_error",
    "pmdec_error",
}
@retry(max_tries=4, base=1.5)
def fetch_gaia_parquet_quick(out_parquet: Path, log: logging.Logger) -> Path:
    Gaia, *_ = _lazy_imports()
    Gaia.BASE_URL = "https://gea.esac.esa.int/tap-server/tap"
    Gaia.ROW_LIMIT = -1
    if not GAIA_ADQL_PATH.exists():
        raise FileNotFoundError(f"GAIA ADQL template missing: {GAIA_ADQL_PATH}")
    adql = GAIA_ADQL_PATH.read_text(encoding="utf-8").strip()
    adql = adql[:-1] if adql.endswith(";") else adql
    limit_clause = f"SELECT * FROM ({adql}) AS base_query LIMIT {GAIA_ROW_LIMIT}" if GAIA_ROW_LIMIT else adql
    log.info("[GAIA] Using ADQL from %s", GAIA_ADQL_PATH)
    log.info("[GAIA] Row limit: %s", GAIA_ROW_LIMIT)
    ensure_dirs_for_base(out_parquet)
    job = Gaia.launch_job_async(limit_clause)
    table = job.get_results()
    df = table.to_pandas()
    if df.empty:
        raise RuntimeError("GAIA query returned no rows")
    missing_cols = REQUIRED_GAIA_COLUMNS.difference(df.columns)
    if missing_cols:
        raise RuntimeError(
            "GAIA query missing required columns: " + ", ".join(sorted(missing_cols))
        )
    df.to_parquet(out_parquet, index=False)
    log.info("[GAIA] wrote %s (rows=%d)", out_parquet, len(df))
    return out_parquet

@retry(max_tries=4, base=1.5)
def fetch_sdss_csv_quick(out_csv: Path, limit: int, log: logging.Logger) -> Path:
    _, SDSS, _ = _lazy_imports()
    sql = f"""
    SELECT TOP {int(limit)}
      p.objid, p.ra, p.dec,
      p.u, p.g, p.r, p.i, p.z,
      p.run, p.camcol, p.field
    FROM PhotoObj AS p
    WHERE p.type = 3
      AND p.u BETWEEN 14 AND 24
      AND p.g BETWEEN 14 AND 24
      AND p.r BETWEEN 14 AND 24
    """
    res = SDSS.query_sql(sql)
    if res is None or len(res) == 0:
        raise RuntimeError("SDSS returned no rows")
    df = res.to_pandas()
    for c in ("u","g","r","i","z"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    ensure_dirs_for_base(out_csv)
    df.to_csv(out_csv, index=False)
    log.info("[SDSS] wrote %s (rows=%d)", out_csv, len(df))
    return out_csv

def check_planck(p: Path, log: logging.Logger) -> bool:
    ok = p.exists()
    if ok:
        log.info("[PLANCK] found %s", p)
    else:
        log.warning("[PLANCK] missing %s (skipping planck-dependent steps)", p)
    return ok

# -------- Orchestrator ----
def autofetch(cfg: AutoFetchConfig) -> Dict[str, Optional[str]]:
    log = make_logger(cfg.run_id)
    manifest = {"run_id": cfg.run_id, "artifacts": {}, "errors": []}

    # 1) GAIA
    try:
        base = cfg.gaia_base
        pq = base.with_suffix(".parquet")
        if not pq.exists():
            fetch_gaia_parquet_quick(pq, log)
        ensure = ensure_both_formats(base, cfg.prefer_parquet)
        manifest["artifacts"]["gaia_primary"] = str(ensure["primary"])
        manifest["artifacts"]["gaia_parquet"] = str(ensure["parquet"])
        manifest["artifacts"]["gaia_csv"] = str(ensure["csv"])
    except Exception as e:
        log.error("[GAIA] failed: %s", e)
        log.debug(traceback.format_exc())
        manifest["errors"].append(f"GAIA: {e}")

    # 2) SDSS
    try:
        base = cfg.sdss_base
        csv = base.with_suffix(".csv")
        if not csv.exists():
            fetch_sdss_csv_quick(csv, limit=5000, log=log)
        ensure = ensure_both_formats(base, cfg.prefer_parquet)
        manifest["artifacts"]["sdss_primary"] = str(ensure["primary"])
        manifest["artifacts"]["sdss_parquet"] = str(ensure["parquet"])
        manifest["artifacts"]["sdss_csv"] = str(ensure["csv"])
    except Exception as e:
        log.error("[SDSS] failed: %s", e)
        log.debug(traceback.format_exc())
        manifest["errors"].append(f"SDSS: {e}")

    # 3) Planck
    try:
        present = check_planck(cfg.planck_fits, log)
        manifest["artifacts"]["planck_fits"] = str(cfg.planck_fits) if present else None
    except Exception as e:
        log.error("[PLANCK] check failed: %s", e)
        log.debug(traceback.format_exc())
        manifest["errors"].append(f"PLANCK: {e}")

    # 4) Optional: Pipeline
    if cfg.run_pipeline:
        try:
            import importlib
            if Path("run_gaia_ssz_pipeline.py").exists():
                mod = importlib.import_module("run_gaia_ssz_pipeline")
                if hasattr(mod, "run_ssz_cosmo"):
                    log.info("[PIPELINE] running run_ssz_cosmo()")
                    mod.run_ssz_cosmo("configs/cosmology_segmented.yaml", "configs/ssz_params.yaml")
                else:
                    log.warning("[PIPELINE] run_ssz_cosmo not found; skipping")
            else:
                log.warning("[PIPELINE] run_gaia_ssz_pipeline.py not found; skipping")
        except ModuleNotFoundError as e:
            log.warning("[PIPELINE] module missing: %s", e)
        except Exception as e:
            log.error("[PIPELINE] failed: %s", e)
            log.debug(traceback.format_exc())
            manifest["errors"].append(f"PIPELINE: {e}")

    # 5) Optional: pytest
    if cfg.run_pytest:
        try:
            import subprocess
            cmd = [sys.executable, "-m", "pytest", "scripts/tests", "-q", "--disable-warnings"]
            log.info("[TESTS] running: %s", " ".join(cmd))
            rc = subprocess.call(cmd)
            manifest["tests_exit_code"] = rc
            if rc != 0:
                manifest["errors"].append(f"TESTS exit_code={rc}")
        except Exception as e:
            log.error("[TESTS] failed to run: %s", e)
            log.debug(traceback.format_exc())
            manifest["errors"].append(f"TESTS: {e}")

    # 6) Manifest schreiben
    out_dir = Path(f"experiments/{cfg.run_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    mpath = out_dir / "autofetch_manifest.json"
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    log.info("[DONE] manifest -> %s", mpath)
    return manifest

def main():
    run_id = sys.argv[1] if len(sys.argv) > 1 else "2025-10-17_gaia_ssz_real"
    cfg = AutoFetchConfig(run_id=run_id)
    # Proxy/Netz optional via ENV:
    # os.environ["HTTP_PROXY"] = "http://user:pass@proxy:port"
    # os.environ["HTTPS_PROXY"] = "http://user:pass@proxy:port"
    try:
        autofetch(cfg)
    except Exception as e:
        log = make_logger(run_id, "AUTOFETCH_FATAL")
        log.error("Fatal: %s", e)
        log.debug(traceback.format_exc())
        sys.exit(2)

if __name__ == "__main__":
    main()
