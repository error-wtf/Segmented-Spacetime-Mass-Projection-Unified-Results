#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_vfall_from_z.py
-----------------------
Liest einen Datensatz mit Rotverschiebungen / Frequenz- oder Wellenlängen-
verhältnissen, schätzt die φ-Stufe n*, berechnet Residuen zum φ-Gitter
und definiert die dualen Skalen
    vfall/c := R  und  vesc/c := 1/R
so dass vesc * vfall = c^2 (in Einheiten von c).
Schreibt Ergebnisse und Summary ins Ausgabeverzeichnis.

Aufruf-Beispiele
----------------
python compute_vfall_from_z.py --in real_data_full.csv --outdir out
python compute_vfall_from_z.py --in real_data_full.csv --outdir out --f-emit f_emit_Hz --f-obs f_obs_Hz
python compute_vfall_from_z.py --in real_data_full.csv --outdir out --lambda-obs lambda_obs --lambda-rest lambda_rest
python compute_vfall_from_z.py --in real_data_full.csv --outdir out --z-col z
"""

from __future__ import annotations

import argparse
import json
import math
import os
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


PHI_DEFAULT = (1 + 5 ** 0.5) / 2  # 1.618033988749895...


# ---------- Utilities ----------

def _normcols(cols):
    """Lowercase + strip für einfache Erkennung."""
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
    """
    Liefert R = f_emit/f_obs als numpy-Array >0 und ein column_log.
    Erkennung in der Reihenfolge:
      1) ratio_col explizit
      2) z_col explizit  -> R = 1 + z
      3) f_emit & f_obs explizit -> R = f_emit / f_obs
      4) lambda_obs & lambda_rest explizit -> R = lambda_obs / lambda_rest
      5) Auto-Heuristik über gängige Namen
    """
    collog: Dict[str, str] = {}

    # Helper: sichere Numerik (coerce -> NaN)
    def colnum(c): return pd.to_numeric(df[c], errors="coerce").to_numpy()

    # 1) Explizit ratio
    if ratio_col and ratio_col in df.columns:
        R = colnum(ratio_col)
        collog["used_ratio"] = ratio_col
        return R, collog

    # 2) Explizit z
    if z_col and z_col in df.columns:
        z = colnum(z_col)
        R = 1.0 + z
        collog["used_z"] = z_col
        return R, collog

    # 3) Explizit f_emit / f_obs
    if f_emit and f_obs and (f_emit in df.columns) and (f_obs in df.columns):
        fe = colnum(f_emit)
        fo = colnum(f_obs)
        R = fe / fo
        collog["used_f_emit"] = f_emit
        collog["used_f_obs"] = f_obs
        return R, collog

    # 4) Explizit lambda_obs / lambda_rest
    if lambda_obs and lambda_rest and (lambda_obs in df.columns) and (lambda_rest in df.columns):
        lo = colnum(lambda_obs)
        lr = colnum(lambda_rest)
        R = lo / lr
        collog["used_lambda_obs"] = lambda_obs
        collog["used_lambda_rest"] = lambda_rest
        return R, collog

    # 5) Auto-Heuristik
    lc = _normcols(df.columns)

    # typische Kandidaten
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

    # f_emit/f_obs?
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

    # lambda_obs/lambda_rest?
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

    # Nichts gefunden
    raise ValueError(
        "Keine passenden Spalten gefunden. "
        "Gib sie per --ratio-col oder --z-col oder --f-emit/--f-obs oder --lambda-obs/--lambda-rest an."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input-CSV")
    ap.add_argument("--outdir", required=True, help="Ausgabeverzeichnis")
    ap.add_argument("--phi", type=float, default=PHI_DEFAULT, help="φ (default golden ratio)")
    # optionale Spalten
    ap.add_argument("--ratio-col", default=None)
    ap.add_argument("--z-col", default=None)
    ap.add_argument("--f-emit", default=None)
    ap.add_argument("--f-obs", default=None)
    ap.add_argument("--lambda-obs", default=None)
    ap.add_argument("--lambda-rest", default=None)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    df = pd.read_csv(args.inp)
    R, collog = autodetect_columns(
        df,
        ratio_col=args.ratio_col,
        z_col=args.z_col,
        f_emit=args.f_emit,
        f_obs=args.f_obs,
        lambda_obs=args.lambda_obs,
        lambda_rest=args.lambda_rest,
    )

    # Säubern: gültig sind positive, endliche R
    R = np.asarray(R, dtype=float)
    mask = np.isfinite(R) & (R > 0)
    R = R[mask]
    rows_used = int(np.sum(mask))

    if rows_used == 0:
        raise ValueError("Nach Säuberung sind keine gültigen Ratio-Werte übrig.")

    # φ-Stufe und Residuen
    lnphi = math.log(args.phi)
    n_star = np.log(R) / lnphi
    n_round = np.rint(n_star)
    residual = n_star - n_round
    abs_residual = np.abs(residual)

    # Duale Geschwindigkeiten (Einheiten: c)
    vfall_over_c = R
    vesc_over_c = 1.0 / R

    # Produkt-Abweichung vom Ideal 1
    prod_rel_err = vesc_over_c * vfall_over_c - 1.0
    prod_rel_err_abs = np.abs(prod_rel_err)

    # Ergebnisse als DataFrame (nur die gefilterten Zeilen)
    out = pd.DataFrame(
        {
            "R": R,
            "n_star": n_star,
            "n_round": n_round,
            "residual": residual,
            "abs_residual": abs_residual,
            "vfall_over_c": vfall_over_c,
            "vesc_over_c": vesc_over_c,
            "prod_minus_1": prod_rel_err,          # = vesc/c * vfall/c - 1
            "abs_prod_minus_1": prod_rel_err_abs,  # |…|
        }
    )

    out_csv = os.path.join(args.outdir, "vfall_results.csv")
    out.to_csv(out_csv, index=False)

    # Summary
    summary = {
        "rows_used": rows_used,
        "abs_residual_median": float(np.nanmedian(abs_residual)),
        "prod_rel_err_median": float(np.nanmedian(prod_rel_err_abs)),
        "phi": float(args.phi),
        "column_log": collog,
        "outdir": args.outdir,
    }
    sum_json = os.path.join(args.outdir, "vfall_summary.json")
    with open(sum_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Console output (knapp, wie gewohnt)
    print(f"[OK] rows used: {rows_used}")
    print(f"[OK] abs_residual_median: {summary['abs_residual_median']}")
    print(f"[OK] prod_rel_err_median: {summary['prod_rel_err_median']}")
    print(f"[OK] outdir: {args.outdir}")
    print(f"[INFO] column_log: {json.dumps(collog, ensure_ascii=False)}")


if __name__ == "__main__":
    main()

