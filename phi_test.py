#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phi_test.py — φ-Schritt-Test auf CSV-Daten
Autor: you

Nutzt eine der folgenden Kombinationen (in dieser Reihenfolge):
  1) ratio        -> R = ratio
  2) f_emit/f_obs -> R = f_emit / f_obs
  3) λ_rest/λ_obs -> R = λ_rest / λ_obs
  4) z            -> R = 1 + z

Beispiele:
  python phi_test.py --in real_data_full_filled.csv --outdir agent_out_phi2
  python phi_test.py --in data.csv --outdir out --lambda-obs lambda_obs --lambda-rest lambda_rest
  python phi_test.py --in data.csv --outdir out --f-emit f_emit_Hz --f-obs f_obs_Hz
  python phi_test.py --in data.csv --outdir out --ratio-col ratio
  python phi_test.py --in data.csv --outdir out --z-col z

Hinweis:
  Reine „raw scrape“-Dateien ohne beobachtete Größen (z. B. ohne lambda_obs/f_obs)
  liefern kein gültiges R und werden sauber abgefangen mit einer klaren Fehlermeldung.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PHI = (1.0 + 5.0 ** 0.5) / 2.0
LN_PHI = math.log(PHI)


def ensure_outdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _num(s: pd.Series) -> pd.Series:
    """robuste Zahlkonvertierung (unterstützt Dezimal-Komma)"""
    if s is None:
        return pd.Series(dtype=float)
    s = s.astype(str).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def pick_ratio(
    df: pd.DataFrame,
    ratio_col: Optional[str],
    f_emit: Optional[str],
    f_obs: Optional[str],
    l_obs: Optional[str],
    l_rest: Optional[str],
    z_col: Optional[str],
) -> Tuple[pd.Series, dict]:
    """
    Liefert Series R (f_emit/f_obs, λ_rest/λ_obs, ratio, 1+z) und ein Log-Dict.
    Reihenfolge der Priorität:
      ratio -> f_emit/f_obs -> λ_rest/λ_obs -> (1+z)
    """
    log = {}
    R = pd.Series(np.nan, index=df.index, dtype=float)

    # ratio
    if ratio_col and ratio_col in df.columns:
        cand = _num(df[ratio_col])
        R = R.fillna(cand)
        log["used_ratio_col"] = ratio_col

    # f_emit/f_obs
    if f_emit and f_obs and f_emit in df.columns and f_obs in df.columns:
        cand = _num(df[f_emit]) / _num(df[f_obs])
        R = R.fillna(cand)
        log["used_f_emit"] = f_emit
        log["used_f_obs"] = f_obs

    # λ_rest/λ_obs
    if l_rest and l_obs and l_rest in df.columns and l_obs in df.columns:
        cand = _num(df[l_rest]) / _num(df[l_obs])
        R = R.fillna(cand)
        log["used_lambda_rest"] = l_rest
        log["used_lambda_obs"] = l_obs

    # 1+z
    if z_col and z_col in df.columns:
        cand = 1.0 + _num(df[z_col])
        R = R.fillna(cand)
        log["used_z_col"] = z_col

    # Auto-Erkennung, falls nichts explizit gesetzt:
    if R.isna().all():
        # try common names
        # ratio
        for c in ["ratio", "R", "ratio_val"]:
            if c in df.columns:
                R = _num(df[c])
                log["autodetected_ratio_col"] = c
                break

    if R.isna().all():
        # f_emit/f_obs
        emit_candidates = [c for c in df.columns if "f_emit" in c]
        obs_candidates = [c for c in df.columns if "f_obs" in c]
        if emit_candidates and obs_candidates:
            cand = _num(df[emit_candidates[0]]) / _num(df[obs_candidates[0]])
            R = cand
            log["autodetected_f_emit"] = emit_candidates[0]
            log["autodetected_f_obs"] = obs_candidates[0]

    if R.isna().all():
        # λ_rest/λ_obs
        rest_candidates = [c for c in df.columns if "lambda_rest" in c or "lam_rest" in c]
        obs_candidates = [c for c in df.columns if "lambda_obs" in c or "lam_obs" in c]
        if rest_candidates and obs_candidates:
            cand = _num(df[rest_candidates[0]]) / _num(df[obs_candidates[0]])
            R = cand
            log["autodetected_lambda_rest"] = rest_candidates[0]
            log["autodetected_lambda_obs"] = obs_candidates[0]

    if R.isna().all():
        # z
        zc = None
        for c in ["z", "redshift", "z_obs"]:
            if c in df.columns:
                zc = c
                break
        if zc:
            R = 1.0 + _num(df[zc])
            log["autodetected_z_col"] = zc

    return R, log


def compute(df: pd.DataFrame, R: pd.Series) -> pd.DataFrame:
    """Berechnet n*, n_round, residual, abs_residual für gültige R."""
    mask = np.isfinite(R) & (R > 0) & (R < 1e12)
    if mask.sum() == 0:
        raise ValueError("Nach Säuberung sind keine gültigen Ratio-Werte übrig.")

    Rv = R[mask]
    n_star = np.log(Rv) / LN_PHI
    n_round = np.rint(n_star)
    residual = n_star - n_round
    abs_residual = np.abs(residual)

    out = df.loc[mask].copy()
    out["R"] = Rv
    out["n_star"] = n_star
    out["n_round"] = n_round.astype(int)
    out["residual"] = residual
    out["abs_residual"] = abs_residual
    return out


def summarize(df_res: pd.DataFrame) -> dict:
    """Kleine Zusammenfassung."""
    return {
        "rows_used": int(len(df_res)),
        "abs_residual_mean": float(df_res["abs_residual"].mean()),
        "abs_residual_median": float(df_res["abs_residual"].median()),
        "abs_residual_max": float(df_res["abs_residual"].max()),
        "residual_mean": float(df_res["residual"].mean()),
        "residual_std": float(df_res["residual"].std(ddof=1)) if len(df_res) > 1 else 0.0,
        "phi": PHI,
        "ln_phi": LN_PHI,
    }


def make_plots(df_res: pd.DataFrame, outdir: str) -> None:
    # QQ gegen Uniform(-0.5,0.5) — Referenzlinie
    q_theo = np.linspace(-0.5, 0.5, len(df_res))
    q_obs = np.sort(df_res["residual"].to_numpy())

    plt.figure(figsize=(10, 6))
    plt.plot(q_theo, q_obs, lw=2)
    plt.title("Residuals vs. Uniform(-0.5,0.5) reference")
    plt.xlabel("Theoretical quantiles")
    plt.ylabel("Observed residuals")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "phi_step_qq_uniform.png"))
    plt.close()

    # |residual| Streuung
    plt.figure(figsize=(12, 6))
    plt.plot(df_res.index.values, df_res["abs_residual"].to_numpy(), ".", ms=2)
    plt.title("|Residual| to nearest φ-step per row")
    plt.xlabel("Row index")
    plt.ylabel("|Residual|")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "phi_step_residual_abs_scatter.png"))
    plt.close()

    # Histogramm Residuen
    plt.figure(figsize=(12, 8))
    plt.hist(df_res["residual"].to_numpy(), bins=101, density=True)
    plt.title("Residuals to nearest φ-step (n* - round(n*))")
    plt.xlabel("Residual in steps")
    plt.ylabel("Density")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "phi_step_residual_hist.png"))
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input CSV")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--tol", type=float, default=1e-3, help="nur Beschriftungszweck")
    # optionale explizite Spaltennamen:
    ap.add_argument("--ratio-col", default=None)
    ap.add_argument("--f-emit", default=None)
    ap.add_argument("--f-obs", default=None)
    ap.add_argument("--lambda-obs", default=None)
    ap.add_argument("--lambda-rest", default=None)
    ap.add_argument("--z-col", default=None)
    args = ap.parse_args()

    ensure_outdir(args.outdir)

    df = pd.read_csv(args.inp)
    R, log = pick_ratio(
        df,
        args.ratio_col,
        args.f_emit,
        args.f_obs,
        args.lambda_obs,
        args.lambda_rest,
        args.z_col,
    )

    try:
        df_res = compute(df, R)
    except ValueError as e:
        # Hilfefall: zeige kurz, was fehlt
        cols = df.columns.tolist()
        hint = {
            "has_ratio": "ratio" in cols,
            "has_f_emit": any("f_emit" in c for c in cols),
            "has_f_obs": any("f_obs" in c for c in cols),
            "has_lambda_rest": any("lambda_rest" in c for c in cols),
            "has_lambda_obs": any("lambda_obs" in c for c in cols),
            "has_z": any(c.lower() == "z" for c in cols),
        }
        print("[FATAL]", repr(e))
        print("[HINT] Spaltenübersicht:", hint)
        print("[HINT] Typischer Fix für raw-scrape-Dateien: enrich zuerst oder gib --lambda-obs/--f-obs an.")
        raise SystemExit(1)

    # Dateien schreiben
    df_res.to_csv(os.path.join(args.outdir, "phi_step_results.csv"), index=False)

    # Top-50 kleinste |residual|
    df_top = df_res.nsmallest(50, "abs_residual")
    df_top.to_csv(os.path.join(args.outdir, "phi_step_top50.csv"), index=False)

    # Debug Full
    df_res.to_csv(os.path.join(args.outdir, "phi_step_debug_full.csv"), index=False)

    # Summary
    summary = summarize(df_res)
    summary.update({"column_log": log})
    with open(os.path.join(args.outdir, "phi_step_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Plots
    make_plots(df_res, args.outdir)

    print("[OK] rows used:", summary["rows_used"])
    print("[OK] abs_residual_median:", summary["abs_residual_median"])
    print("[OK] outdir:", args.outdir)
    print("[INFO] column_log:", json.dumps(log))


if __name__ == "__main__":
    main()
