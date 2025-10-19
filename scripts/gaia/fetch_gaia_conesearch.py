from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

import pandas as pd
from astroquery.gaia import Gaia
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GAIA cone searches defined in a JSON config")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--format", choices=["parquet", "csv", "fits"], default="parquet")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--log-dir", default=Path("data/logs"), type=Path)
    parser.add_argument("--sleep", type=float, default=2.0, help="Seconds to sleep between requests")
    return parser.parse_args()


def setup_logging(log_dir: Path, run_id: str) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"cones_{run_id}.log"
    logger = logging.getLogger("fetch_gaia_conesearch")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def load_regions(config_path: Path) -> Iterable[Dict[str, object]]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    regions = data.get("regions", [])
    if not regions:
        raise ValueError("No regions defined in cones config")
    return regions


def ensure_dirs(out_dir: Path, cache_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)


def run_cone_search(region: Dict[str, object]) -> Table:
    coord = SkyCoord(ra=region["ra_deg"] * u.deg, dec=region["dec_deg"] * u.deg, frame="icrs")
    radius = region["radius_deg"] * u.deg
    job = Gaia.cone_search_async(coord, radius)
    return job.get_results()


def write_output(table: Table, region_name: str, out_dir: Path, run_id: str, fmt: str, index: int) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    base = f"{run_id}__{region_name}__part{index:02d}_{timestamp}"
    if fmt == "parquet":
        path = out_dir / f"{base}.parquet"
        df = table.to_pandas()
        df.to_parquet(path, index=False)
    elif fmt == "csv":
        path = out_dir / f"{base}.csv"
        df = table.to_pandas()
        df.to_csv(path, index=False)
    else:
        path = out_dir / f"{base}.fits"
        table.write(path, overwrite=False)
    return path


def main() -> None:
    args = parse_args()
    logger = setup_logging(args.log_dir, args.run_id)
    ensure_dirs(args.out, args.cache)
    regions = list(load_regions(args.config))
    logger.info("Starting %d cone searches", len(regions))
    for idx, region in enumerate(regions):
        region_name = region.get("name", f"region_{idx}")
        logger.info("Querying region %s", region_name)
        table = run_cone_search(region)
        path = write_output(table, region_name, args.out, args.run_id, args.format, idx)
        logger.info("Wrote %d rows to %s", len(table), path)
        time.sleep(args.sleep)
    logger.info("All cone searches completed")


if __name__ == "__main__":
    main()
