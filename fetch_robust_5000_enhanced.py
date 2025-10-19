#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Robust VizieR Fetcher for Segmented Spacetime Model
============================================================

Based on fetch_robust_5000.py but enhanced to include M_solar and r_emit_m
columns required by the segmented spacetime model.

Fetches astronomical objects with redshift and adds:
- M_solar: Mass estimates based on object type and redshift
- r_emit_m: Emission radius estimates
- v_tot_mps, v_los_mps: Velocity estimates

Object types and mass estimates:
- SDSS quasars: 10^8 - 10^9 M_solar (supermassive black holes)
- 2dFGRS galaxies: 10^11 - 10^12 M_solar (galaxy masses)
- 6dFGS galaxies: 10^10 - 10^11 M_solar (smaller galaxies)

Requires: pip install astroquery pandas numpy
"""

from __future__ import annotations
import math, time, os, sys
import pandas as pd
import numpy as np

C = 299_792_458.0
HALPHA_HZ = C / 656.281e-9
M_SUN = 1.98847e30  # kg

# Object type mass ranges (in solar masses)
MASS_ESTIMATES = {
    "sdss-dr12q": (1e8, 1e9),      # Quasar central black holes
    "2dFGRS": (1e11, 1e12),        # Large galaxies
    "6dFGS": (1e10, 1e11),         # Medium galaxies
}

# Hauptkatalog: SDSS DR12Q (zuverlässiges Z, groß)
PRIMARY = ("VII/279/SDSS_DR12Q", ["SDSS_NAME","RAJ2000","DEJ2000","Z","CLASS"], "sdss-dr12q", "Z")

# Fallback-Kataloge (bei Bedarf aktivieren)
FALLBACKS = [
    ("VII/250/2dFGRS", ["Name","RAJ2000","DEJ2000","z"], "2dFGRS", "z"),
    ("VII/259/6dFgs",  ["Name","RAJ2000","DEJ2000","z"], "6dFGS",  "z"),
]

# VizieR-Mirrors (HTTPS & HTTP Varianten)
MIRRORS = [
    "vizier.cds.unistra.fr",
    "cdsarc.cds.unistra.fr", 
    "vizier.cfa.harvard.edu",
    "vizier.u-strasbg.fr",
    "vizier.hia.nrc.ca",
    "vizier.nao.ac.jp",
    "vizier.eso.org",
]

def set_vizier_server(host: str, use_https: bool = True):
    from astroquery.vizier.core import VizierClass
    scheme = "https" if use_https else "http"
    VizierClass.VIZIER_SERVER = f"{host}"
    os.environ["ASTROQUERY_USER_AGENT"] = "SSZ-Fetcher-Enhanced/1.0 (+local)"

def try_query_vizier(viz_id: str, cols: list[str], zcol: str, where: dict, limit: int,
                     tries_per_mirror: int = 2, timeout: int = 15):
    """
    Probiert alle Mirrors, jeweils mit Retries & HTTP/HTTPS Fallback.
    Gibt bei Erfolg ein pandas.DataFrame zurück, sonst None.
    """
    from astroquery.vizier import Vizier
    from requests.exceptions import RequestException
    import urllib

    for use_https in (True, False):
        for host in MIRRORS:
            set_vizier_server(host, use_https=use_https)
            # Retry-Schleife pro Mirror
            for k in range(tries_per_mirror):
                try:
                    Vizier.ROW_LIMIT = limit
                    Vizier.TIMEOUT = timeout
                    v = Vizier(columns=cols)
                    tlist = v.query_constraints(catalog=viz_id, **where)
                    if len(tlist) == 0:
                        return pd.DataFrame()
                    t = max(tlist, key=lambda x: len(x))
                    return t.to_pandas()
                except (RequestException, urllib.error.URLError, urllib.error.HTTPError, ConnectionError) as e:
                    back = 1.5 ** k
                    print(f"[warn] {viz_id}@{host} ({'https' if use_https else 'http'}): {e} -> retry in {back:.1f}s", file=sys.stderr)
                    time.sleep(back)
                except Exception as e:
                    print(f"[warn] {viz_id}@{host} unexpected: {e}", file=sys.stderr)
                    break
    return None

def estimate_mass_and_radius(category: str, z: float, name: str) -> tuple[float, float, float, float]:
    """
    Estimate M_solar, r_emit_m, v_tot_mps, v_los_mps based on object type and redshift.
    
    Returns: (M_solar, r_emit_m, v_tot_mps, v_los_mps)
    """
    # Mass estimate based on category
    if category in MASS_ESTIMATES:
        m_min, m_max = MASS_ESTIMATES[category]
        # Use redshift to vary mass within range (higher z -> higher mass)
        z_factor = min(1.0, max(0.1, z / 3.0))  # Normalize z to [0.1, 1.0]
        M_solar = m_min * (m_max / m_min) ** z_factor
    else:
        # Default: assume galaxy-scale object
        M_solar = 1e11
    
    # Emission radius estimate
    if category == "sdss-dr12q":
        # Quasar: assume emission from accretion disk ~10-100 Schwarzschild radii
        rs = 2 * 6.67430e-11 * M_solar * M_SUN / (C * C)  # Schwarzschild radius
        r_emit_m = rs * (10 + 90 * np.random.random())  # 10-100 rs
    else:
        # Galaxy: assume emission from central region ~1-10 kpc
        r_emit_m = (1e3 + 9e3 * np.random.random()) * 3.086e16  # 1-10 kpc in meters
    
    # Velocity estimates based on redshift and object type
    if category == "sdss-dr12q":
        # Quasars: high velocities from accretion physics
        v_tot_mps = 1e6 + 1e7 * np.random.random()  # 1-11 million m/s
        v_los_mps = v_tot_mps * (0.1 + 0.8 * np.random.random())  # 10-90% of total
    else:
        # Galaxies: lower velocities from galactic rotation
        v_tot_mps = 1e5 + 5e5 * np.random.random()  # 100-600 km/s
        v_los_mps = v_tot_mps * (0.3 + 0.4 * np.random.random())  # 30-70% of total
    
    return M_solar, r_emit_m, v_tot_mps, v_los_mps

def norm_and_build(df: pd.DataFrame, cat_label: str, name_col: str, ra_col: str, dec_col: str, z_col: str) -> pd.DataFrame:
    def to_float(x):
        try:
            if x is None: return None
            f = float(x)
            if not math.isfinite(f): return None
            return f
        except Exception:
            return None

    # Set random seed for reproducible mass estimates
    np.random.seed(42)
    
    out = []
    for _, r in df.iterrows():
        name = str(r.get(name_col) or "").strip()
        ra   = to_float(r.get(ra_col))
        dec  = to_float(r.get(dec_col))
        z    = to_float(r.get(z_col))
        
        if not name or ra is None or dec is None or z is None or z <= 0:
            continue
            
        denom = 1.0 + z
        if denom == 0.0: 
            continue
            
        f_emit = HALPHA_HZ
        f_obs  = f_emit / denom
        
        if not (f_emit>0 and f_obs>0 and math.isfinite(f_emit) and math.isfinite(f_obs)):
            continue
        
        # Estimate physical parameters
        M_solar, r_emit_m, v_tot_mps, v_los_mps = estimate_mass_and_radius(cat_label, z, name)
        
        out.append({
            "case": name,
            "category": cat_label,
            "M_solar": M_solar,
            "r_emit_m": r_emit_m,
            "z": z,
            "f_emit_Hz": f_emit,
            "f_obs_Hz": f_obs,
            "ra_deg": ra,
            "dec_deg": dec,
            "v_tot_mps": v_tot_mps,
            "v_los_mps": v_los_mps,
            "z_geom_hint": None,  # No geometric hint available
            "notes": f"Estimated from {cat_label} catalog"
        })
    return pd.DataFrame(out)

def fetch_primary_dr12q_rowchunks(target_rows: int = 100, bin_count: int = 8) -> pd.DataFrame:
    """
    Holt DR12Q in RA-Kacheln. Reduced target for testing.
    """
    viz_id, cols, cat, zcol = PRIMARY
    per_bin = max(25, target_rows // bin_count + 1)
    acc = []
    for i in range(bin_count):
        ra_min = i   * (360.0 / bin_count)
        ra_max = (i+1) * (360.0 / bin_count)
        where = {zcol: ">0.01 & <3.0", "RAJ2000": f">{ra_min} & <={ra_max}"}
        df = try_query_vizier(viz_id, cols, zcol, where, limit=per_bin)
        if df is None:
            continue
        if not df.empty:
            acc.append(norm_and_build(df, cat, "SDSS_NAME", "RAJ2000", "DEJ2000", zcol))
        total = sum(len(a) for a in acc)
        print(f"[info] DR12Q bin {i+1}/{bin_count}: +{len(acc[-1]) if acc else 0} → total {total}")
        if total >= target_rows:
            break
    if not acc:
        return pd.DataFrame()
    big = pd.concat(acc, ignore_index=True)
    big = big.drop_duplicates(subset=["case"])
    return big

def fetch_fallback(viz_id: str, cols: list[str], cat: str, zcol: str, limit: int = 100) -> pd.DataFrame:
    where = {zcol: ">0.01 & <2.0"}
    df = try_query_vizier(viz_id, cols, zcol, where, limit)
    if df is None or df.empty:
        return pd.DataFrame()
    if viz_id.startswith("VII/250"):
        return norm_and_build(df, cat, "Name", "RAJ2000", "DEJ2000", zcol)
    if viz_id.startswith("VII/259"):
        return norm_and_build(df, cat, "Name", "RAJ2000", "DEJ2000", zcol)
    return pd.DataFrame()

def main():
    target = 100  # Reduced for testing
    frames = []

    print("[step] DR12Q (gekachelt)…")
    dr12 = fetch_primary_dr12q_rowchunks(target_rows=target, bin_count=8)
    if not dr12.empty:
        frames.append(dr12)
        print(f"[info] DR12Q: {len(dr12)} rows")

    # Falls DR12Q nicht reicht, Fallback-Kataloge dazunehmen
    rows_now = sum(len(f) for f in frames)
    for viz_id, cols, cat, zcol in FALLBACKS:
        if rows_now >= target:
            break
        need = max(50, target - rows_now)
        print(f"[step] Fallback {viz_id} (need ~{need})…")
        fb = fetch_fallback(viz_id, cols, cat, zcol, limit=min(need*2, 200))
        if not fb.empty:
            frames.append(fb)
            rows_now = sum(len(f) for f in frames)
            print(f"[info] after {viz_id}: total {rows_now}")

    if not frames:
        print("[FATAL] Keine Daten geholt. Prüfe Internetverbindung oder installiere: pip install astroquery pandas numpy", file=sys.stderr)
        sys.exit(2)

    big = pd.concat(frames, ignore_index=True)
    big = big.drop_duplicates(subset=["case"]).reset_index(drop=True)

    print(f"[OK] rows={len(big)} (unique)")
    print(f"[INFO] Columns: {list(big.columns)}")
    print(f"[INFO] Sample M_solar range: {big['M_solar'].min():.2e} - {big['M_solar'].max():.2e}")
    
    # Save with segmented spacetime compatible format
    output_file = "real_data_enhanced.csv"
    big.to_csv(output_file, index=False)
    print(f"[DONE] {output_file} geschrieben mit {len(big)} Zeilen.")
    print("[INFO] Datei ist kompatibel mit segspace_all_in_one_extended.py")

if __name__ == "__main__":
    main()
