from __future__ import annotations
from pathlib import Path
import os, pandas as pd
from scripts.tools.logging_utils import get_logger
from scripts.tools.retry import retry

# Required dependency for data fetching tests
try:
    from astroquery.gaia import Gaia
    from astroquery.sdss import SDSS
    HAS_ASTROQUERY = True
except ImportError as e:
    HAS_ASTROQUERY = False
    import_error = e
    # Provide helpful error message
    def _missing_astroquery(*args, **kwargs):
        raise ImportError(
            "\n\n"
            "❌ MISSING DEPENDENCY: astroquery\n"
            "\n"
            "The data fetching tests require 'astroquery' to be installed.\n"
            "\n"
            "📦 To install:\n"
            "   pip install astroquery\n"
            "\n"
            "Or install all dependencies:\n"
            "   pip install -r requirements.txt\n"
            "\n"
            f"Original error: {import_error}\n"
        )
    Gaia = type('Gaia', (), {'launch_job_async': _missing_astroquery, 'BASE_URL': '', 'ROW_LIMIT': -1})()
    SDSS = type('SDSS', (), {'query_sql': _missing_astroquery})()

def ensure_dir(p: str|Path):
    Path(p).mkdir(parents=True, exist_ok=True)

@retry(max_tries=4, base_delay=1.5)
def fetch_gaia_quick(out_parquet: str) -> str:
    log = get_logger("GAIA_SMOKE", run_id="smoke")
    Gaia.BASE_URL = "https://gea.esac.esa.int/tap-server/tap"
    Gaia.ROW_LIMIT = -1
    q = """
    SELECT TOP 5000
      source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag, bp_rp
    FROM gaiaedr3.gaia_source
    WHERE parallax IS NOT NULL
      AND phot_g_mean_mag BETWEEN 8 AND 18
    """
    ensure_dir(Path(out_parquet).parent)
    job = Gaia.launch_job_async(q)
    table = job.get_results()
    df = table.to_pandas()
    if df.empty:
        raise RuntimeError("GAIA returned no rows")
    df.to_parquet(out_parquet, index=False)
    log.info("GAIA quick -> %s", out_parquet)
    return out_parquet

@retry(max_tries=4, base_delay=1.5)
def fetch_sdss_quick(out_csv: str, limit:int=5000) -> str:
    log = get_logger("SDSS_SMOKE", run_id="smoke")
    sql = f"""
    SELECT TOP {int(limit)}
      p.objid, p.ra, p.dec, p.u, p.g, p.r, p.i, p.z, p.run, p.camcol, p.field
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
    ensure_dir(Path(out_csv).parent)
    df.to_csv(out_csv, index=False)
    log.info("SDSS quick -> %s (rows=%d)", out_csv, len(df))
    return out_csv

def smoke_paths(run_id: str) -> dict:
    """Return expected paths for autofetch smoke test.
    
    For Planck, tries run-specific path first, then falls back to generic path.
    """
    base = Path("data/raw")
    
    # Check run-specific Planck path first, then generic
    planck_specific = Path(f"data/raw/planck/{run_id}/planck_map.fits")
    planck_generic = Path("data/raw/planck/planck_map.fits")
    
    planck_fits = planck_specific if planck_specific.exists() else planck_generic
    
    return {
        "gaia_parquet": base.parent / "gaia" / run_id / "gaia_quick.parquet",
        "sdss_csv":     base.parent / "sdss" / run_id / "sdss_quick.csv",
        "planck_fits":  planck_fits,
    }
