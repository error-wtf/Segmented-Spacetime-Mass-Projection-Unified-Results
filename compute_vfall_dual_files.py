#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute vfall for two input CSV files.

This script is designed to work with the Segmented‑Spacetime mass projection
repository.  It reads two redshift/frequency datasets (for example
``real_data_full.csv`` and ``real_data_full_filled.csv``) and, for each
dataset, derives the dual velocity scale ``v_fall`` along with several
diagnostic quantities.  The core logic mirrors the `compute_vfall_from_z.py`
script shipped in the repository, but is documented in English and
generalised to process two files in one run.

For each input CSV the following steps are performed:

* A ratio ``R = f_emit / f_obs`` is constructed.  The script will
  attempt to autodetect suitable columns for a direct ratio, a redshift
  ``z`` (which implies ``R = 1+z``), frequency columns ``f_emit`` and
  ``f_obs``, or wavelength columns ``lambda_obs`` and ``lambda_rest``.
  You can also explicitly specify column names via command‑line options.

* Rows where the ratio is not finite or not strictly positive are dropped.

* The (fractional) φ‑stage ``n_star = ln(R) / ln(φ)`` is computed and
  compared to the nearest integer ``n_round``.  The difference
  ``residual = n_star - n_round`` measures how well the measured ratio
  aligns with the golden‑ratio lattice.  The script records the absolute
  residual for later summary.

* The dual velocities in units of the speed of light are defined as
  ``vfall_over_c = R`` and ``vesc_over_c = 1/R``.  Their product should
  equal unity in the exact dual‑velocity picture.  The script therefore
  logs ``prod_minus_1 = vesc_over_c * vfall_over_c − 1``.

Results are written to a CSV and a JSON summary in the output directory.
The summary includes the number of rows used, the median absolute
φ‑residual, the median absolute product deviation, the φ constant used and
the column detection log.  Summaries for both input files are printed to
STDOUT so you can quickly compare the filled and unfilled datasets.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


PHI_DEFAULT = (1 + 5 ** 0.5) / 2  # the golden ratio, ≈1.618


def _normcols(cols):
    """Helper: return lower‑cased and stripped column names."""
    return [str(c).strip().lower() for c in cols]


def autodetect_columns(
    df: pd.DataFrame,
    ratio_col: Optional[str],
    z_col: Optional[str],
    f_emit: Optional[str],
    f_obs: Optional[str],
    lambda_obs: Optional[str],
    lambda_rest: Optional[str],
) -> Tuple[np.ndarray, Dict[str, str]]:
    """Return the ratio R and a column‑log based on the provided DataFrame.

    The detection proceeds in the following order:

    1. Use an explicitly provided ratio column.
    2. Use an explicitly provided redshift column (R = 1+z).
    3. Use explicitly provided frequency columns f_emit & f_obs (R = f_emit/f_obs).
    4. Use explicitly provided wavelength columns lambda_obs & lambda_rest (R = lambda_obs/lambda_rest).
    5. Try a set of common names for ratio, redshift, frequency and wavelength columns.

    If none of these conditions are met, a ``ValueError`` is raised.  The
    returned dictionary records which columns were used.
    """
    collog: Dict[str, str] = {}

    def colnum(c):  # convert a column to numeric array with NaN for non‑numeric
        return pd.to_numeric(df[c], errors="coerce").to_numpy()

    # 1) explicit ratio column
    if ratio_col and ratio_col in df.columns:
        R = colnum(ratio_col)
        collog["used_ratio"] = ratio_col
        return R, collog

    # 2) explicit redshift column
    if z_col and z_col in df.columns:
        z = colnum(z_col)
        R = 1.0 + z
        collog["used_z"] = z_col
        return R, collog

    # 3) explicit frequency columns
    if f_emit and f_obs and (f_emit in df.columns) and (f_obs in df.columns):
        fe = colnum(f_emit)
        fo = colnum(f_obs)
        R = fe / fo
        collog["used_f_emit"] = f_emit
        collog["used_f_obs"] = f_obs
        return R, collog

    # 4) explicit wavelength columns
    if lambda_obs and lambda_rest and (lambda_obs in df.columns) and (lambda_rest in df.columns):
        lo = colnum(lambda_obs)
        lr = colnum(lambda_rest)
        R = lo / lr
        collog["used_lambda_obs"] = lambda_obs
        collog["used_lambda_rest"] = lambda_rest
        return R, collog

    # 5) heuristic detection based on common names
    lc = _normcols(df.columns)

    # candidate names for ratio and redshift
    try_names_ratio = ["ratio", "f_ratio", "femit_over_fobs", "f_emit_over_f_obs"]
    try_names_z = ["z", "redshift"]
    try_names_fe = ["f_emit_hz", "femit_hz", "f_emit", "femit", "nu_emit", "nu_emit_hz"]
    try_names_fo = ["f_obs_hz", "fobs_hz", "f_obs", "fobs", "nu_obs", "nu_obs_hz"]
    try_names_lo = ["lambda_obs", "lam_obs", "wavelength_obs", "lambda_observed"]
    try_names_lr = ["lambda_rest", "lam_rest", "wavelength_rest", "lambda_0", "lambda_restframe"]

    # ratio?
    for name in try_names_ratio:
        if name in lc:
            col = df.columns[lc.index(name)]
            R = colnum(col)
            collog["auto_ratio"] = col
            return R, collog

    # z?
    for name in try_names_z:
        if name in lc:
            col = df.columns[lc.index(name)]
            z = colnum(col)
            collog["auto_z"] = col
            return 1.0 + z, collog

    # f_emit / f_obs?
    fe_col = None
    fo_col = None
    for name in try_names_fe:
        if name in lc:
            fe_col = df.columns[lc.index(name)]
            break
    for name in try_names_fo:
        if name in lc:
            fo_col = df.columns[lc.index(name)]
            break
    if fe_col and fo_col:
        R = colnum(fe_col) / colnum(fo_col)
        collog["autodetected_f_emit"] = fe_col
        collog["autodetected_f_obs"] = fo_col
        return R, collog

    # lambda_obs / lambda_rest?
    lo_col = None
    lr_col = None
    for name in try_names_lo:
        if name in lc:
            lo_col = df.columns[lc.index(name)]
            break
    for name in try_names_lr:
        if name in lc:
            lr_col = df.columns[lc.index(name)]
            break
    if lo_col and lr_col:
        R = colnum(lo_col) / colnum(lr_col)
        collog["autodetected_lambda_obs"] = lo_col
        collog["autodetected_lambda_rest"] = lr_col
        return R, collog

    raise ValueError(
        "No suitable columns found. Please specify them via --ratio-col, --z-col, "
        "--f-emit/--f-obs or --lambda-obs/--lambda-rest."
    )


def compute_vfall_for_file(
    filepath: str,
    outdir: str,
    phi: float,
    ratio_col: Optional[str] = None,
    z_col: Optional[str] = None,
    f_emit: Optional[str] = None,
    f_obs: Optional[str] = None,
    lambda_obs: Optional[str] = None,
    lambda_rest: Optional[str] = None,
) -> Dict[str, object]:
    """Process a single CSV file and write results and summary.

    Parameters
    ----------
    filepath : str
        Path to the input CSV file.
    outdir : str
        Directory where result CSVs and summary JSONs will be written.
    phi : float
        The golden ratio (or user‑provided value) used for computing the φ‑stage.
    ratio_col, z_col, f_emit, f_obs, lambda_obs, lambda_rest : Optional[str]
        Explicit column names overriding autodetection.

    Returns
    -------
    Dict[str, object]
        The summary dictionary describing how many rows were used and median
        deviations.
    """
    # Load CSV
    df = pd.read_csv(filepath)
    # Derive ratio R and log which columns were used
    R, collog = autodetect_columns(
        df,
        ratio_col=ratio_col,
        z_col=z_col,
        f_emit=f_emit,
        f_obs=f_obs,
        lambda_obs=lambda_obs,
        lambda_rest=lambda_rest,
    )
    # Ensure numeric array
    R = np.asarray(R, dtype=float)
    # Filter: only finite and positive values
    mask = np.isfinite(R) & (R > 0)
    R = R[mask]
    rows_used = int(np.sum(mask))
    if rows_used == 0:
        raise ValueError(f"No valid ratio values left after cleaning for file {filepath}.")
    # φ-stage and residuals
    lnphi = math.log(phi)
    n_star = np.log(R) / lnphi
    n_round = np.rint(n_star)
    residual = n_star - n_round
    abs_residual = np.abs(residual)
    # Dual velocities (in units of c)
    vfall_over_c = R
    vesc_over_c = 1.0 / R
    # Product deviation from unity
    prod_minus_1 = vesc_over_c * vfall_over_c - 1.0
    abs_prod_minus_1 = np.abs(prod_minus_1)
    # Assemble results DataFrame
    out_df = pd.DataFrame({
        "R": R,
        "n_star": n_star,
        "n_round": n_round,
        "residual": residual,
        "abs_residual": abs_residual,
        "vfall_over_c": vfall_over_c,
        "vesc_over_c": vesc_over_c,
        "prod_minus_1": prod_minus_1,
        "abs_prod_minus_1": abs_prod_minus_1,
    })
    # Write detailed results
    base = os.path.splitext(os.path.basename(filepath))[0]
    out_csv = os.path.join(outdir, f"{base}_vfall_results.csv")
    out_df.to_csv(out_csv, index=False)
    # Build summary
    summary = {
        "rows_used": rows_used,
        "abs_residual_median": float(np.nanmedian(abs_residual)),
        "prod_rel_err_median": float(np.nanmedian(abs_prod_minus_1)),
        "phi": float(phi),
        "column_log": collog,
        "input_file": filepath,
        "results_csv": out_csv,
    }
    # Write summary JSON
    summary_json = os.path.join(outdir, f"{base}_vfall_summary.json")
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="""
        Compute dual velocities v_fall and diagnostic metrics for two CSV files.

        Each input file should contain either a redshift column (z), a direct
        ratio column (f_emit/f_obs), or matching frequency/wavelength columns.
        See the script documentation for details on how columns are detected.
        """
    )
    parser.add_argument(
        "--csv1",
        type=str,
        default="real_data_full.csv",
        help="First input CSV file (default: real_data_full.csv)",
    )
    parser.add_argument(
        "--csv2",
        type=str,
        default="real_data_full_filled.csv",
        help="Second input CSV file (default: real_data_full_filled.csv)",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="vfall_dual_out",
        help="Directory where output CSVs and summaries will be stored",
    )
    parser.add_argument(
        "--phi",
        type=float,
        default=PHI_DEFAULT,
        help="Value of φ (golden ratio) to use; defaults to the canonical value",
    )
    # optional explicit columns
    parser.add_argument("--ratio-col", default=None, help="Explicit ratio column name")
    parser.add_argument("--z-col", default=None, help="Explicit redshift column name")
    parser.add_argument("--f-emit", default=None, help="Explicit f_emit (emitted frequency) column name")
    parser.add_argument("--f-obs", default=None, help="Explicit f_obs (observed frequency) column name")
    parser.add_argument("--lambda-obs", default=None, help="Explicit observed wavelength column name")
    parser.add_argument("--lambda-rest", default=None, help="Explicit restframe wavelength column name")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    # Process both files
    summaries = []
    for csv_path in [args.csv1, args.csv2]:
        if not os.path.exists(csv_path):
            print(f"[WARNING] Input file does not exist: {csv_path}")
            continue
        summary = compute_vfall_for_file(
            csv_path,
            args.outdir,
            phi=args.phi,
            ratio_col=args.ratio_col,
            z_col=args.z_col,
            f_emit=args.f_emit,
            f_obs=args.f_obs,
            lambda_obs=args.lambda_obs,
            lambda_rest=args.lambda_rest,
        )
        summaries.append(summary)
        # Print a brief console summary
        print(f"\n[SUMMARY] Results for {csv_path}")
        print(f"  Rows used              : {summary['rows_used']}")
        print(f"  Median |phi residual|  : {summary['abs_residual_median']:.6e}")
        print(f"  Median |prod-1|        : {summary['prod_rel_err_median']:.6e}")
        print(f"  Result CSV             : {summary['results_csv']}")
    if not summaries:
        print("No input files were processed. Please check the provided paths.")


if __name__ == "__main__":
    main()