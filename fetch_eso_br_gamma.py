
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_eso_br_gamma.py
=====================

Purpose
-------
Fetch Br-γ (Brackett-gamma) related objects/measurements from ESO services and
export a normalized CSV usable by `segspace_all_in_one.py`.

Why this file?
--------------
As of 2025-07-15, the Br-γ acquisition pipeline reportedly switched to a
"get_proof" style endpoint (here referenced as "get-proof" mode). This script
supports BOTH:
  1) mode=get-proof  -> new API (post-2025-07-15, token-based)
  2) mode=tap        -> legacy ESO TAP query (pre-2025-07-15)

You can run either mode depending on which backend you have access to.
This script does not assume a particular private URL; it expects environment
variables and/or CLI flags for endpoints and tokens.

Output
------
A normalized CSV with columns that `segspace_all_in_one.py` consumes:

  - case:           object identifier (string)
  - category:       coarse class, e.g. "s-star", "jet", "psr", "agn"
  - M_solar:        mass in solar masses (float)
  - a_m:            semi-major axis in meters (float)
  - e:              eccentricity (float)
  - f_deg:          true anomaly in degrees at observation epoch (float)
  - z:              measured redshift (dimensionless)
  - z_geom_hint:    geometric/GR hint z (dimensionless), optional
  - r_emit_m:       emission radius in meters (float), optional if a_m/e/f available
  - v_tot_mps:      total speed in m/s (float), optional
  - v_los_mps:      line-of-sight speed in m/s (float), optional

Notes on Units
--------------
- Distances in meters, speeds in m/s, masses in solar masses.
- Redshift z is dimensionless.
- If the upstream service returns other units (e.g., km/s), convert here.

Auth & Endpoints
----------------
"get-proof" mode:
  - Set environment variable ESO_TOKEN to your bearer token (or use --token).
  - Provide --endpoint pointing to the new proof endpoint.
  - Provide --since YYYY-MM-DD to restrict data to a time window, if applicable.

"tap" mode:
  - Provide --endpoint with a TAP base URL.
  - A default TAP ADQL example is included; adjust as needed.

Usage
-----
Examples:
  # New pipeline (post-2025-07-15)
  python fetch_eso_br_gamma.py --mode get-proof --endpoint https://example.eso.org/api/get_proof \
      --since 2025-07-15 --out real_data_full.csv --token $ESO_TOKEN

  # Legacy TAP
  python fetch_eso_br_gamma.py --mode tap --endpoint https://tap.eso.org/tap --out real_data_full.csv

This script is designed to be explicit and reproducible: it writes a small JSON
sidecar with the query metadata next to the CSV.

"""

import os
import csv
import json
import sys
import time
import math
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests  # Only required when you actually fetch
except Exception:
    requests = None


def to_float(x) -> Optional[float]:
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:
        return None


def kmps_to_mps(v_km_s: Optional[float]) -> Optional[float]:
    if v_km_s is None:
        return None
    return v_km_s * 1000.0


def normalize_row(src: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map raw fields (from get-proof or TAP) to the normalized schema.

    This function contains conservative defaults and example mappings.
    You should adapt the keys to match actual API responses.

    Expected fields (adjust the code below):
      - name / object_id -> case
      - class           -> category (normalize to lower case labels)
      - mass_solar      -> M_solar
      - a_m, e, f_deg   -> orbital geometry
      - z, z_hint       -> redshift measurements
      - r_emit_m        -> emission radius (optional)
      - v_tot_km_s      -> total speed, km/s
      - v_los_km_s      -> LOS speed, km/s
    """
    case = str(src.get("name") or src.get("object_id") or src.get("case") or "").strip()
    category = str(src.get("class") or src.get("category") or "").strip().lower()

    out = {
        "case": case,
        "category": category,
        "M_solar": to_float(src.get("mass_solar")),
        "a_m": to_float(src.get("a_m")),
        "e": to_float(src.get("e")),
        "f_deg": to_float(src.get("f_deg")),
        "z": to_float(src.get("z")),
        "z_geom_hint": to_float(src.get("z_hint") or src.get("z_geom_hint")),
        "r_emit_m": to_float(src.get("r_emit_m")),
        "v_tot_mps": kmps_to_mps(to_float(src.get("v_tot_km_s"))) if src.get("v_tot_km_s") is not None else to_float(src.get("v_tot_mps")),
        "v_los_mps": kmps_to_mps(to_float(src.get("v_los_km_s"))) if src.get("v_los_km_s") is not None else to_float(src.get("v_los_mps")),
    }

    # Light post-processing: ensure empty strings for Nones in CSV
    for k, v in list(out.items()):
        if v is None:
            out[k] = ""
    return out


def write_csv(rows: List[Dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["case","category","M_solar","a_m","e","f_deg","z","z_geom_hint","r_emit_m","v_tot_mps","v_los_mps"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})


def write_sidecar(meta: Dict[str, Any], out_path: Path) -> None:
    sidecar = out_path.with_suffix(out_path.suffix + ".meta.json")
    sidecar.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


# ----------- Fetchers -----------

def fetch_get_proof(endpoint: str, token: str, since: Optional[str], until: Optional[str], dry_run: bool=False) -> List[Dict[str, Any]]:
    """
    Placeholder implementation for post-2025-07-15 "get_proof" style endpoint.
    Expects a bearer token and allows date window filtering.
    Adjust the payload according to the actual API spec.
    """
    payload = {"band": "Br-gamma", "since": since, "until": until}
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    if dry_run or requests is None:
        # Dry-run returns an example set; replace with real fetch logic for production.
        example = [
            {"name": "S14_SgrA*", "class": "s-star", "mass_solar": 4.1e6,
             "a_m": "", "e": "", "f_deg": "", "z": 1.734e-04, "z_hint": 9.614e-04,
             "r_emit_m": "", "v_tot_km_s": "", "v_los_km_s": ""},
            {"name": "M87*_jet", "class": "jet", "mass_solar": 6.5e9,
             "a_m": "", "e": "", "f_deg": "", "z": 1.0e-03, "z_hint": "",
             "r_emit_m": "", "v_tot_km_s": "", "v_los_km_s": ""},
        ]
        return example

    # Real request (adjust to spec)
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Expect "results" to be an array of dicts; adjust if necessary
    rows = data.get("results", data)
    return rows


def fetch_tap(endpoint: str, dry_run: bool=False) -> List[Dict[str, Any]]:
    """
    Legacy TAP fetch via ADQL. This is a placeholder with a demo ADQL string.
    Update the ADQL to target your exact table and columns.
    """
    adql = """
    SELECT
      object_name AS name,
      class AS class,
      mass_solar AS mass_solar,
      a_m AS a_m,
      e AS e,
      f_deg AS f_deg,
      redshift AS z,
      z_hint AS z_hint,
      r_emit_m AS r_emit_m,
      v_tot_km_s AS v_tot_km_s,
      v_los_km_s AS v_los_km_s
    FROM br_gamma_catalog
    WHERE band = 'Br-gamma'
    """
    if dry_run or requests is None:
        example = [
            {"name": "Cyg_X-1", "class": "xrb", "mass_solar": 15.0, "a_m": "", "e": "", "f_deg": "",
             "z": 1.18e-02, "z_hint": "", "r_emit_m": "", "v_tot_km_s": 300.0, "v_los_km_s": 200.0},
            {"name": "V404_Cyg", "class": "xrb", "mass_solar": 9.0, "a_m": "", "e": "", "f_deg": "",
             "z": 1.535e-03, "z_hint": "", "r_emit_m": "", "v_tot_km_s": 150.0, "v_los_km_s": 100.0},
        ]
        return example

    # Real TAP call would go here (usually POST to /tap/sync with ADQL)
    # This is kept abstract; you can plug in your TAP client or requests-based call.
    raise NotImplementedError("Implement TAP client or use dry-run")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["get-proof","tap"], default="get-proof",
                    help="Select data source: get-proof (>= 2025-07-15) or tap (legacy).")
    ap.add_argument("--endpoint", type=str, required=True, help="API base URL or TAP base URL.")
    ap.add_argument("--out", type=str, default="real_data_full.csv", help="Output CSV path.")
    ap.add_argument("--since", type=str, default=None, help="Start date (YYYY-MM-DD) for get-proof mode.")
    ap.add_argument("--until", type=str, default=None, help="End date (YYYY-MM-DD) for get-proof mode.")
    ap.add_argument("--token", type=str, default=os.environ.get("ESO_TOKEN", ""),
                    help="Bearer token for get-proof mode (or set ESO_TOKEN).")
    ap.add_argument("--dry-run", action="store_true", help="Do not call network; emit example rows.")
    args = ap.parse_args()

    t0 = time.time()

    if args.mode == "get-proof":
        rows_raw = fetch_get_proof(args.endpoint, args.token, args.since, args.until, dry_run=args.dry_run)
        source = {"mode": "get-proof", "endpoint": args.endpoint, "since": args.since, "until": args.until,
                  "used_token": bool(args.token)}
    else:
        rows_raw = fetch_tap(args.endpoint, dry_run=args.dry_run)
        source = {"mode": "tap", "endpoint": args.endpoint}

    # Normalize
    rows = [normalize_row(r) for r in rows_raw]

    # Write CSV + meta
    out_path = Path(args.out)
    write_csv(rows, out_path)
    meta = {
        "source": source,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "row_count": len(rows),
        "schema": ["case","category","M_solar","a_m","e","f_deg","z","z_geom_hint","r_emit_m","v_tot_mps","v_los_mps"],
        "notes": "Units: distances in meters, speeds in m/s, masses in solar masses, z dimensionless."
    }
    write_sidecar(meta, out_path)

    dt = time.time() - t0
    print(f"Wrote {len(rows)} rows to {out_path} in {dt:.2f}s")
    print(f"Metadata: {out_path.with_suffix(out_path.suffix + '.meta.json')}")


if __name__ == "__main__":
    main()
