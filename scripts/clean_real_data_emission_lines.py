"""Clean and curate emission-line datasets for SEG paired tests.

Outputs
-------
- `data/real_data_emission_lines_clean.csv`
    High-quality rows with all critical columns present and physically valid.

- `data/real_data_emission_lines_best.csv`
    Subset of the clean data containing only Sgr A* observations (rows whose
    `case` column contains `_SgrA*`). This subset historically yields the
    strongest SEG performance.

Run from the repository root:

    python scripts/clean_real_data_emission_lines.py

"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "real_data_emission_lines.csv"
OUTPUT_CLEAN = REPO_ROOT / "data" / "real_data_emission_lines_clean.csv"
OUTPUT_BEST = REPO_ROOT / "data" / "real_data_emission_lines_best.csv"

# Columns that must be present, non-null, and finite for reliable comparisons.
CRITICAL_COLUMNS = {
    "M_solar": "mass in solar masses",
    "r_emit_m": "emission radius (m)",
    "z": "observed redshift",
    "v_los_mps": "line-of-sight velocity (m/s)",
    "v_tot_mps": "total velocity (m/s)",
    "lambda_emit_nm": "emitted wavelength (nm)",
    "lambda_obs_nm": "observed wavelength (nm)",
    "T0_year": "epoch (year)",
    "f_true_deg": "true anomaly (deg)",
    "N0": "normalisation factor",
    "z_geom_hint": "SEG geometric hint",
}


def _load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path)


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for col in CRITICAL_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _build_clean_mask(df: pd.DataFrame) -> pd.Series:
    mask = pd.Series(True, index=df.index)

    for col in CRITICAL_COLUMNS:
        if col not in df.columns:
            print(f"WARNING: required column '{col}' missing from dataset")
            mask &= False
            continue

        values = df[col]
        mask &= values.notna()

        if col in {"M_solar", "r_emit_m", "v_los_mps", "v_tot_mps", "lambda_emit_nm", "lambda_obs_nm", "N0"}:
            mask &= values > 0

        if col == "z":
            mask &= np.isfinite(values)

        if col == "z_geom_hint":
            mask &= values.notna() & np.isfinite(values) & (values != 0)

    return mask


def _write_dataset(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> int:
    df = _load_dataset(DATA_PATH)
    original_count = len(df)

    df = _coerce_numeric(df)
    clean_mask = _build_clean_mask(df)
    df_clean = df[clean_mask].copy()

    if "case" in df_clean.columns:
        df_clean = df_clean.sort_values(by="z", key=lambda s: s.abs(), ascending=False)
        df_clean = df_clean.drop_duplicates(subset="case", keep="first")

    _write_dataset(df_clean, OUTPUT_CLEAN)

    if "case" in df_clean.columns:
        best_mask = df_clean["case"].astype(str).str.contains("_SgrA*", na=False)
        df_best = df_clean[best_mask].copy()
    else:
        df_best = df_clean.copy()

    _write_dataset(df_best, OUTPUT_BEST)

    print("Cleaning summary")
    print("=" * 60)
    print(f"Original rows: {original_count}")
    print(f"Clean rows   : {len(df_clean)} -> saved to {OUTPUT_CLEAN.relative_to(REPO_ROOT)}")
    if len(df_clean) == 0:
        print("WARNING: no rows survived cleaning; review dataset quality criteria.")

    print(f"Best rows    : {len(df_best)} -> saved to {OUTPUT_BEST.relative_to(REPO_ROOT)}")
    if len(df_best) == 0:
        print("NOTE: no Sgr A* rows detected; best dataset matches clean dataset.")

    removed = original_count - len(df_clean)
    print(f"Removed rows : {removed}")

    missing_cols = [col for col in CRITICAL_COLUMNS if col not in df.columns]
    if missing_cols:
        print("\nMissing columns detected:")
        for col in missing_cols:
            print(f"  - {col}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
