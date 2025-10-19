from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from astroquery.gaia import Gaia
from astropy.table import Table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GAIA data via ADQL query")
    parser.add_argument("--adql", required=True, type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--format", choices=["parquet", "csv", "fits"], default="parquet")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--log-dir", default=Path("data/logs"), type=Path)
    return parser.parse_args()


def setup_logging(log_dir: Path, run_id: str) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"fetch_{run_id}.log"
    logger = logging.getLogger("fetch_gaia_adql")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def load_query(adql_path: Path) -> str:
    return adql_path.read_text(encoding="utf-8")


def prepare_query(base_query: str, limit: Optional[int]) -> str:
    if limit is None:
        return base_query
    return f"SELECT * FROM ({base_query}) AS base_query LIMIT {limit}"


def ensure_output_dirs(out_path: Path, cache_dir: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"


def execute_query(query: str, logger: logging.Logger) -> pd.DataFrame:
    logger.info("Launching GAIA job")
    job = Gaia.launch_job_async(query)
    table = job.get_results()
    logger.info("Job finished with %d rows", len(table))
    return table.to_pandas()


def write_dataframe(df: pd.DataFrame, out_path: Path, fmt: str) -> Path:
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    if fmt == "parquet":
        df.to_parquet(tmp_path, index=False)
    elif fmt == "csv":
        df.to_csv(tmp_path, index=False)
    else:
        table = Table.from_pandas(df)
        table.write(tmp_path, overwrite=True)

    tmp_path.replace(out_path)
    return out_path


def main() -> None:
    args = parse_args()
    logger = setup_logging(args.log_dir, args.run_id)
    logger.info("Starting GAIA ADQL fetch")
    ensure_output_dirs(args.out, args.cache)
    base_query = load_query(args.adql)
    query = prepare_query(base_query, args.limit)
    df = execute_query(query, logger)
    path = write_dataframe(df, args.out, args.format)
    logger.info("Wrote dataset to %s", path)
    logger.info("Sleeping briefly to respect GAIA service load")
    time.sleep(2.0)


if __name__ == "__main__":
    main()
