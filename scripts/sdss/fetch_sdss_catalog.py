#!/usr/bin/env python
"""Fetch an SDSS photometric catalog sample using astroquery."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from astroquery.sdss import SDSS
except ImportError as exc:  # pragma: no cover - handled at runtime
    SDSS = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

DEFAULT_LIMIT = 1000
DEFAULT_RELEASE = "dr18"
DEFAULT_QUERY_TEMPLATE = """
SELECT TOP {limit}
    p.objid,
    p.ra,
    p.dec,
    p.u,
    p.g,
    p.r,
    p.i,
    p.z,
    p.err_u,
    p.err_g,
    p.err_r,
    p.err_i,
    p.err_z,
    p.type
FROM PhotoObj AS p
WHERE p.type = 3 -- galaxies
  AND p.g BETWEEN 14 AND 24
  AND p.r BETWEEN 14 AND 24
ORDER BY p.g
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch SDSS photometric catalog via astroquery")
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Destination CSV path (e.g. data/raw/sdss/<run>/sdss_catalog.csv)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Number of rows to fetch (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--release",
        default=DEFAULT_RELEASE,
        help=f"SDSS data release to query (default: {DEFAULT_RELEASE})",
    )
    parser.add_argument(
        "--query",
        help="Custom SQL query. Use {limit} placeholder to inject --limit value.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output file if it already exists",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Network timeout in seconds",
    )
    return parser.parse_args()


def ensure_astroquery_available() -> None:
    if SDSS is None:
        raise RuntimeError(
            "astroquery.sdss is not available in this environment. Install astroquery to continue"
        ) from _IMPORT_ERROR


def build_query(limit: int, template: str | None) -> str:
    base = template or DEFAULT_QUERY_TEMPLATE
    if "{limit}" in base:
        return base.format(limit=limit)
    return base


def fetch_catalog(sql: str, release: str, timeout: float) -> "pd.DataFrame":
    from astropy.table import Table  # lazy import
    import pandas as pd

    # Configure astroquery timeout
    SDSS.TIMEOUT = timeout

    try:
        result: Table | None = SDSS.query_sql(sql, timeout=timeout, data_release=release)
    except TypeError as exc:  # fallback for release handling issues
        result = SDSS.query_sql(sql, timeout=timeout)
        if result is None:
            raise
    except Exception:
        result = SDSS.query_sql(sql, timeout=timeout)

    if result is None or len(result) == 0:
        raise RuntimeError("SDSS query returned no results")

    df = result.to_pandas()
    numeric_cols = ["u", "g", "r", "i", "z", "err_u", "err_g", "err_r", "err_i", "err_z"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def main() -> int:
    args = parse_args()

    if args.limit <= 0:
        raise SystemExit("--limit must be positive")

    if args.output.exists() and not args.overwrite:
        print(
            f"[SDSS FETCH] Output already exists at {args.output}. Use --overwrite to replace.",
            file=sys.stderr,
        )
        return 0

    ensure_astroquery_available()

    sql = build_query(args.limit, args.query)
    try:
        df = fetch_catalog(sql, args.release, args.timeout)
    except Exception as exc:  # broad to surface download/query issues
        print(f"[SDSS FETCH] Query failed: {exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"[SDSS FETCH] Catalog saved to {args.output} ({len(df)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
