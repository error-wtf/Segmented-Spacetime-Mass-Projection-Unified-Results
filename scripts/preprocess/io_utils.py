from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

import pandas as pd

CORE_COLS = ("ra", "dec")


def _has_core_columns(df: pd.DataFrame) -> bool:
    return all(col in df.columns for col in CORE_COLS)


def _read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if not _has_core_columns(df):
        raise ValueError(f"CSV file {path} is missing required columns {CORE_COLS}")
    return df


def _read_parquet(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if not _has_core_columns(df):
        raise ValueError(f"Parquet file {path} is missing required columns {CORE_COLS}")
    return df


def ensure_both_formats(base_path: str | Path, prefer_parquet: bool = True) -> Dict[str, Path | None]:
    """
    Ensure both CSV and Parquet representations exist for a dataset.

    Parameters
    ----------
    base_path: str | Path
        The dataset path without file extension.
    prefer_parquet: bool
        Controls which format is returned as the primary path.

    Returns
    -------
    Dict[str, Path | None]
        Mapping with keys "primary", "csv", "parquet".
    """

    base = Path(base_path)
    csv_path = base.with_suffix(".csv")
    parquet_path = base.with_suffix(".parquet")

    has_csv = csv_path.exists()
    has_parquet = parquet_path.exists()

    if not has_csv and not has_parquet:
        raise FileNotFoundError(f"Neither CSV nor Parquet found for base path {base}")

    if has_csv and not has_parquet:
        df = _read_csv(csv_path)
        df.to_parquet(parquet_path, index=False)
        has_parquet = True
    elif has_parquet and not has_csv:
        df = _read_parquet(parquet_path)
        df.to_csv(csv_path, index=False)
        has_csv = True
    else:
        # Validate both when present
        _read_csv(csv_path)
        _read_parquet(parquet_path)

    preferred_order = (parquet_path, csv_path) if prefer_parquet else (csv_path, parquet_path)
    primary = preferred_order[0] if preferred_order[0].exists() else preferred_order[1]

    return {
        "primary": primary,
        "csv": csv_path if has_csv else None,
        "parquet": parquet_path if has_parquet else None,
    }
