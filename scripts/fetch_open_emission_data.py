#!/usr/bin/env python3
"""Token-free helpers for downloading emission-line datasets.

This script queries open astronomy archives (ESO TAP, KOA API, NED) and
produces ready-to-run shell scripts / CSV catalogs so users can fetch
science-ready products without signing in or managing API tokens.

Usage
-----
    python scripts/fetch_open_emission_data.py --out data/raw_fetch

Outputs in the chosen directory:
- `eso_gravity_metadata.csv` + `eso_gravity_downloads.sh`
- `koa_nirspec_metadata.csv` + `koa_nirspec_downloads.sh`
- `ned_velocity_<object>.csv`

Execute the generated shell scripts to download FITS/CSV products, then
process them as described in `docs/improvement/OPTIMAL_DATASET.md`.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from io import StringIO
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth


def _eso_tap_endpoints() -> list[str]:
    override = os.environ.get("ESO_TAP_BASE")
    if override:
        base = override.rstrip("/")
        return [f"{base}/tap/sync"]
    return [
        "https://archive.eso.org/tap_obs/tap/sync",  # main observational TAP endpoint
        "https://archive.eso.org/tap/tap/sync",      # theoretical TAP endpoint (legacy)
        "https://data.eso.org/tap/sync",             # current published endpoint
        "https://tap.esoidp.eso.org/tap/sync",       # legacy endpoint
    ]


ESO_TAP_ENDPOINTS = _eso_tap_endpoints()
KOA_PRIMARY_URL = "https://koa.ipac.caltech.edu/cgi-bin/KOA/nph-KOAapi"
KOA_SIA_URL = "https://koa.ipac.caltech.edu/cgi-bin/VOServ/nph-searchImage"
NED_VELOCITY_URL = "https://ned.ipac.caltech.edu/cgi-bin/objsearch"

ESO_USERNAME_ENV = "ESO_USERNAME"
ESO_PASSWORD_ENV = "ESO_PASSWORD"
ESO_TOKEN_ENV = "ESO_TOKEN"

ESO_ADQL_QUERY = """
SELECT TOP 100
  o.target,
  o.ra,
  o.dec,
  o.obs_id,
  o.prog_id,
  o.dataproduct_type,
  o.instrument,
  o.publisher_did
FROM ivoa.obscore AS o
WHERE o.instrument = 'GRAVITY'
  AND o.dataproduct_type = 'spectrum'
  AND o.calib_level = 3
  AND (
    o.target LIKE 'Sgr A%'
    OR o.target LIKE 'S2%'
  )
ORDER BY o.obs_id DESC
""".strip()

KOA_DEFAULT_PARAMS = {
    "database": "koa",
    "instrument": "NIRSPEC",
    "object": "Sgr A*",
    "ktc": "26",
    "level": "2",
    "OUTROWS": "200",
    "format": "csv",
}

KOA_SIA_PARAMS = {
    "POS": "CIRCLE 266.41683 -29.00781 0.05",  # ~Sgr A*
    "INSTRUMENT": "NIRSPEC",
    "OUTROWS": "200",
    "format": "csv",
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _assert_csv_response(resp: requests.Response, context: str) -> None:
    content_type = resp.headers.get("Content-Type", "").lower()
    snippet = resp.text.lstrip()[:100]
    if "text/csv" in content_type:
        return
    if "xml" in content_type:
        return
    if "application/json" in content_type:
        try:
            detail = resp.json()
        except Exception:
            detail = {"error": "unknown", "body": resp.text[:200]}
        raise RuntimeError(f"{context}: server returned JSON error {detail}")
    if snippet.startswith("<!DOCTYPE") or snippet.startswith("<html"):
        raise RuntimeError(f"{context}: received HTML error page instead of data")
    raise RuntimeError(f"{context}: unexpected response content-type '{content_type}'")


def _votable_to_csv(text: str) -> str:
    try:
        from astropy.io.votable import parse
        import pandas as pd
        import tempfile
        with tempfile.NamedTemporaryFile("w+b", delete=False, suffix=".vot") as tmp:
            tmp.write(text.encode("utf-8", errors="ignore"))
            tmp_path = tmp.name
        vot = parse(tmp_path)
        table = vot.get_first_table().to_table().to_pandas()
        csv_buffer = StringIO()
        table.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
    except Exception:
        return text


def fetch_eso_gravity(outdir: Path) -> Path:
    payload = {
        "request": "doQuery",
        "lang": "ADQL",
        "format": "csv",
        "MAXREC": "200000",
        "query": ESO_ADQL_QUERY,
    }

    eso_user = os.environ.get(ESO_USERNAME_ENV)
    eso_pass = os.environ.get(ESO_PASSWORD_ENV)
    eso_auth = HTTPBasicAuth(eso_user, eso_pass) if eso_user and eso_pass else None
    eso_token = os.environ.get(ESO_TOKEN_ENV)

    headers = {"Accept": "text/csv"}
    if eso_token:
        headers["Authorization"] = f"Bearer {eso_token}"

    request_kwargs: dict[str, object] = {"timeout": 120, "headers": headers}
    if eso_auth is not None:
        request_kwargs["auth"] = eso_auth

    last_error: Exception | None = None
    resp = None
    for endpoint in ESO_TAP_ENDPOINTS:
        try:
            try:
                resp = requests.post(endpoint, data=payload, **request_kwargs)
                resp.raise_for_status()
                break
            except requests.RequestException:
                # Some TAP services expect GET with URL parameters; try fallback.
                resp = requests.get(endpoint, params=payload, **request_kwargs)
                resp.raise_for_status()
                break
        except Exception as exc:
            last_error = exc
            continue

    if resp is None:
        raise RuntimeError(f"ESO TAP request failed for all endpoints: {last_error}")

    _assert_csv_response(resp, "ESO TAP query")

    text = resp.text
    if "xml" in resp.headers.get("Content-Type", "").lower():
        text = _votable_to_csv(text)

    metadata_csv = outdir / "eso_gravity_metadata.csv"
    metadata_csv.write_text(text, newline="\n")

    download_script = outdir / "eso_gravity_downloads.sh"
    with metadata_csv.open("r", newline="") as fh, download_script.open("w", newline="\n") as sh:
        reader = csv.DictReader(fh)
        sh.write("#!/usr/bin/env bash\nset -euo pipefail\n\n")
        for row in reader:
            did = row.get("publisher_did")
            if not did:
                continue
            url = f"https://dataportal.eso.org/dataPortal/api/falls/{did}/file"
            sh.write(f"wget -nc '{url}'\n")
    return download_script


def fetch_koa_nirspec(outdir: Path) -> Path:
    attempts = [
        (KOA_PRIMARY_URL, KOA_DEFAULT_PARAMS, "KOA API"),
        (KOA_SIA_URL, KOA_SIA_PARAMS, "KOA SIA fallback"),
    ]

    last_error: Exception | None = None
    resp: requests.Response | None = None
    context = "KOA request"
    for url, params, label in attempts:
        try:
            resp = requests.get(url, params=params, timeout=120, headers={"Accept": "text/csv,text/xml"})
            resp.raise_for_status()
            _assert_csv_response(resp, label)
            context = label
            break
        except Exception as exc:
            last_error = exc
            resp = None
            continue

    if resp is None:
        raise RuntimeError(f"KOA request failed: {last_error}")

    text = resp.text
    if "xml" in resp.headers.get("Content-Type", "").lower():
        text = _votable_to_csv(text)

    metadata_csv = outdir / "koa_nirspec_metadata.csv"
    metadata_csv.write_text(text, newline="\n")

    download_script = outdir / "koa_nirspec_downloads.sh"
    with metadata_csv.open("r", newline="") as fh, download_script.open("w", newline="\n") as sh:
        reader = csv.DictReader(fh)
        sh.write("#!/usr/bin/env bash\nset -euo pipefail\n\n")
        for row in reader:
            url = row.get("URL") or row.get("url")
            if not url:
                continue
            sh.write(f"wget -nc '{url}'\n")
    return download_script


def fetch_ned_velocity(outdir: Path, object_name: str = "NGC 4258") -> Path:
    params = {
        "objname": object_name,
        "extend": "no",
        "out_csys": "Equatorial",
        "out_equinox": "J2000.0",
        "of": "tab",
        "ot": "v",
    }
    resp = requests.get(NED_VELOCITY_URL, params=params, timeout=120)
    resp.raise_for_status()

    output_csv = outdir / f"ned_velocity_{object_name.replace(' ', '_')}.csv"
    output_csv.write_bytes(resp.content)
    return output_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Token-free emission-line data fetch helper")
    parser.add_argument("--out", type=Path, default=Path("data/raw_fetch"), help="output directory")
    parser.add_argument("--ned-object", type=str, default="NGC 4258", help="object name for NED velocity export")
    args = parser.parse_args()

    ensure_dir(args.out)

    try:
        eso_script = fetch_eso_gravity(args.out)
        print(f"ESO metadata saved. Run {eso_script} to download GRAVITY spectra.")
    except Exception as exc:
        print(f"[WARN] ESO TAP request failed: {exc}")

    try:
        koa_script = fetch_koa_nirspec(args.out)
        print(f"KOA metadata saved. Run {koa_script} to download NIRSPEC products.")
    except Exception as exc:
        print(f"[WARN] KOA API request failed: {exc}")

    try:
        ned_csv = fetch_ned_velocity(args.out, args.ned_object)
        print(f"NED velocity catalog saved to {ned_csv}")
    except Exception as exc:
        print(f"[WARN] NED velocity fetch failed: {exc}")

    print("\nNext steps:")
    print("  1. Execute the generated shell scripts to download FITS/CSV products.")
    print("  2. Derive SEG input columns (z, velocities, radii, z_geom_hint) as described in OPTIMAL_DATASET.md.")
    print("  3. Append new rows to data/real_data_emission_lines.csv and rerun the cleaning script.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
