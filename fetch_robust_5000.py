#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robuster VizieR-Fetcher für >=5000 Zeilen mit z:
- Mirror-Failover (CDS/CfA/ESO/UKIRT), HTTP/HTTPS Umschaltung
- Exponentielle Retries mit kurzen Timeouts
- RA-Kachelung (24 Bins) für SDSS DR12Q; optional 2dFGRS/6dFGS als Fallback
- Rekonstruiert f_emit/f_obs aus z (Hα), keine NaNs in Pflichtfeldern
- Schreibt real_data_full.csv

Benötigt: pip install astroquery pandas
"""

from __future__ import annotations
import math, time, os, sys
import pandas as pd

C = 299_792_458.0
HALPHA_HZ = C / 656.281e-9

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
    # Astroquery baut selbst URLs; TIMEOUT/USERAGENT setzen wir separat
    os.environ["ASTROQUERY_USER_AGENT"] = "SSZ-Fetcher/1.0 (+local)"

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
                        # Keine Tabelle -> aber kein Netzwerkfehler
                        return pd.DataFrame()
                    t = max(tlist, key=lambda x: len(x))
                    return t.to_pandas()
                except (RequestException, urllib.error.URLError, urllib.error.HTTPError, ConnectionError) as e:
                    # kurzer Backoff und erneut versuchen
                    back = 1.5 ** k
                    print(f"[warn] {viz_id}@{host} ({'https' if use_https else 'http'}): {e} -> retry in {back:.1f}s", file=sys.stderr)
                    time.sleep(back)
                except Exception as e:
                    # Unbekannter Fehler -> Mirror wechseln
                    print(f"[warn] {viz_id}@{host} unexpected: {e}", file=sys.stderr)
                    break
    return None

def fetch_primary_dr12q_rowchunks(target_rows: int = 5000, bin_count: int = 24) -> pd.DataFrame:
    """
    Holt DR12Q in RA-Kacheln, um große Antworten zu vermeiden.
    Bricht ab, sobald >= target_rows Zeilen mit gültigem z beisammen sind.
    """
    viz_id, cols, cat, zcol = PRIMARY
    per_bin = max(250, target_rows // bin_count + 1)  # konservativ
    acc = []
    for i in range(bin_count):
        ra_min = i   * (360.0 / bin_count)
        ra_max = (i+1) * (360.0 / bin_count)
        where = {zcol: ">-0.99", "RAJ2000": f">{ra_min} & <={ra_max}"}
        df = try_query_vizier(viz_id, cols, zcol, where, limit=per_bin)
        if df is None:
            continue
        # Normalisieren
        if not df.empty:
            acc.append(norm_and_build(df, cat, "SDSS_NAME", "RAJ2000", "DEJ2000", zcol))
        total = sum(len(a) for a in acc)
        print(f"[info] DR12Q bin {i+1}/{bin_count}: +{len(acc[-1]) if acc else 0} → total {total}")
        if total >= target_rows:
            break
    if not acc:
        return pd.DataFrame()
    big = pd.concat(acc, ignore_index=True)
    big = big.drop_duplicates(subset=["name"])
    return big

def fetch_fallback(viz_id: str, cols: list[str], cat: str, zcol: str, limit: int = 5000) -> pd.DataFrame:
    df = try_query_vizier(viz_id, cols, zcol, {zcol: ">-0.99"}, limit)
    if df is None or df.empty:
        return pd.DataFrame()
    if viz_id.startswith("VII/250"):
        return norm_and_build(df, cat, "Name", "RAJ2000", "DEJ2000", zcol)
    if viz_id.startswith("VII/259"):
        return norm_and_build(df, cat, "Name", "RAJ2000", "DEJ2000", zcol)
    return pd.DataFrame()

def norm_and_build(df: pd.DataFrame, cat_label: str, name_col: str, ra_col: str, dec_col: str, z_col: str) -> pd.DataFrame:
    def to_float(x):
        try:
            if x is None: return None
            f = float(x)
            if not math.isfinite(f): return None
            return f
        except Exception:
            return None

    out = []
    for _, r in df.iterrows():
        name = str(r.get(name_col) or "").strip()
        ra   = to_float(r.get(ra_col))
        dec  = to_float(r.get(dec_col))
        z    = to_float(r.get(z_col))
        if not name or ra is None or dec is None or z is None:
            continue
        denom = 1.0 + z
        if denom == 0.0: 
            continue
        f_emit = HALPHA_HZ
        f_obs  = f_emit / denom
        if not (f_emit>0 and f_obs>0 and math.isfinite(f_emit) and math.isfinite(f_obs)):
            continue
        out.append({
            "name": name,
            "category": cat_label,
            "ra_deg": ra,
            "dec_deg": dec,
            "z": z,
            "f_emit_Hz": f_emit,
            "f_obs_Hz": f_obs,
        })
    return pd.DataFrame(out)

def main():
    target = 5000
    frames = []

    print("[step] DR12Q (gekachelt)…")
    dr12 = fetch_primary_dr12q_rowchunks(target_rows=target, bin_count=24)
    if not dr12.empty:
        frames.append(dr12)

    # Falls DR12Q nicht reicht, Fallback-Kataloge dazunehmen
    rows_now = sum(len(f) for f in frames)
    for viz_id, cols, cat, zcol in FALLBACKS:
        if rows_now >= target:
            break
        need = max(500, target - rows_now)
        print(f"[step] Fallback {viz_id} (need ~{need})…")
        fb = fetch_fallback(viz_id, cols, cat, zcol, limit=min(need*2, 20000))
        if not fb.empty:
            frames.append(fb)
            rows_now = sum(len(f) for f in frames)
            print(f"[info] after {viz_id}: total {rows_now}")

    if not frames:
        print("[FATAL] Keine Daten geholt (Netz blockiert?). Nochmal laufen lassen; sonst Mirrorliste erweitern.", file=sys.stderr)
        sys.exit(2)

    big = pd.concat(frames, ignore_index=True)
    big = big.drop_duplicates(subset=["name"]).reset_index(drop=True)

    print(f"[OK] rows={len(big)}  (unique)")
    big.to_csv("real_data_full.csv", index=False)
    print("[DONE] real_data_full.csv geschrieben.")

if __name__ == "__main__":
    main()
