#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SSZ Visualization Toolkit (v6)
--------------------------------
Loads the outputs produced by ssz_proof_sweep_v6.py and renders
consistent plots: stability heatmaps, disagreement maps, boundary
curves (λ_A,crit vs Ω0), and λ_A-difference maps.
This script is tolerant to slight schema changes and can also read v4/v5 files.

USAGE
-----
python ssz_viz_v6.py --data-dir /mnt/data --prefix v6

Expected files (under --data-dir):
- proof_sweep_results_<prefix>.csv
- stability_boundaries_<prefix>.csv
- proof_sweep_summary_<prefix>.json

Outputs (PNG) will be written to the same directory.
"""
import argparse
import json
import os
from typing import Tuple, Optional, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


# ----------------------------
# Helpers
# ----------------------------
def _path(data_dir: str, base: str, prefix: str) -> str:
    return os.path.join(data_dir, f"{base}_{prefix}")

def _load_csv(path: str) -> Optional[pd.DataFrame]:
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"[warn] failed to read CSV: {path}: {e}")
        return None

def _load_json(path: str) -> Optional[Dict]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[warn] failed to read JSON: {path}: {e}")
        return None

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

# Determine stability boolean from columns
def _stable_from(df: pd.DataFrame, col_direct: str="stable_direct", col_logG: str="logG") -> pd.Series:
    if col_direct in df.columns:
        return df[col_direct].astype(bool)
    if col_logG in df.columns:
        return (df[col_logG] <= 0.0)
    # try logG_direct naming
    for c in df.columns:
        if "log" in c.lower() and "g" in c.lower():
            return (df[c] <= 0.0)
    # fallback: all False
    return pd.Series([False]*len(df))

def _criterion_from(df: pd.DataFrame, col: str="stable_criterion") -> Optional[pd.Series]:
    if col in df.columns:
        return df[col].astype(bool)
    # heuristic: a column named Xi or criterion may exist (<=0 stable)
    for c in df.columns:
        cl = c.lower()
        if "xi" in cl or "criterion" in cl:
            try:
                return (df[c] <= 0.0)
            except Exception:
                pass
    return None


# ----------------------------
# Plots
# ----------------------------
def plot_stability_heatmap(df: pd.DataFrame, segment_mode: str, out_path: str, title_suffix: str="v6"):
    if df is None or df.empty:
        print("[skip] stability heatmap: empty dataframe")
        return

    dfm = df.copy()
    if "segment_mode" in dfm.columns:
        dfm = dfm[dfm["segment_mode"] == segment_mode]

    # compute fraction stable (direct) per (K, lambda_A)
    if "K" not in dfm.columns or "lambda_A" not in dfm.columns:
        print("[skip] stability heatmap: missing columns K/lambda_A")
        return

    stable = _stable_from(dfm)
    grp = dfm.assign(stable=stable).groupby(["K", "lambda_A"], as_index=False)["stable"].mean()
    pivot = grp.pivot(index="K", columns="lambda_A", values="stable")

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    im = ax.imshow(
        pivot.values,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[pivot.columns.min(), pivot.columns.max(), pivot.index.min(), pivot.index.max()],
        cmap="viridis",
        vmin=0.0,
        vmax=1.0,
    )
    ax.set_xlabel("lambda_A")
    ax.set_ylabel("K")
    ax.set_title(f"SSZ Stability Heatmap ({segment_mode}) {title_suffix}")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Fraction stable (direct)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"[ok] saved {out_path}")


def plot_disagreement_map(df: pd.DataFrame, segment_mode: str, out_path: str, title_suffix: str="v6"):
    if df is None or df.empty:
        print("[skip] disagreement map: empty dataframe")
        return

    dfm = df.copy()
    if "segment_mode" in dfm.columns:
        dfm = dfm[dfm["segment_mode"] == segment_mode]

    if "K" not in dfm.columns or "lambda_A" not in dfm.columns:
        print("[skip] disagreement map: missing columns K/lambda_A")
        return

    direct = _stable_from(dfm)
    crit = _criterion_from(dfm)
    if crit is None or len(crit) != len(direct):
        print("[warn] no criterion series found; defaulting to zeros")
        crit = pd.Series([False]*len(direct))

    disagree = (direct != crit).astype(float)

    grp = dfm.assign(disagree=disagree).groupby(["K", "lambda_A"], as_index=False)["disagree"].mean()
    pivot = grp.pivot(index="K", columns="lambda_A", values="disagree")

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    im = ax.imshow(
        pivot.values,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[pivot.columns.min(), pivot.columns.max(), pivot.index.min(), pivot.index.max()],
        cmap="magma",
        vmin=0.0,
        vmax=1.0,
    )
    ax.set_xlabel("lambda_A")
    ax.set_ylabel("K")
    ax.set_title(f"Stability Disagreement Map ({segment_mode}) {title_suffix}")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Disagreement ratio")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"[ok] saved {out_path}")


def plot_boundaries(bound_df: pd.DataFrame, out_path: str, title_suffix: str="v6"):
    if bound_df is None or bound_df.empty:
        print("[skip] boundaries: empty dataframe")
        return

    # Heuristics for column names
    c_omega = "Omega0" if "Omega0" in bound_df.columns else ("omega0" if "omega0" in bound_df.columns else None)
    c_dir = None
    c_crit = None
    for c in bound_df.columns:
        cl = c.lower()
        if "lambda" in cl and "crit" in cl and ("direct" in cl or cl.endswith("_d")):
            c_dir = c
        if "lambda" in cl and "crit" in cl and ("criterion" in cl or "critn" in cl or cl.endswith("_c")):
            c_crit = c
    if c_dir is None:
        for c in bound_df.columns:
            if "lambda" in c.lower() and "direct" in c.lower():
                c_dir = c
    if c_crit is None:
        for c in bound_df.columns:
            if "lambda" in c.lower() and "criterion" in c.lower():
                c_crit = c

    if c_omega is None or c_dir is None:
        print("[skip] boundaries: missing Omega0 or lambdaA_crit_direct column")
        return

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    ax.plot(bound_df[c_omega], bound_df[c_dir], "o-", label="direct")
    if c_crit and c_crit in bound_df.columns:
        ax.plot(bound_df[c_omega], bound_df[c_crit], "s--", label="criterion")
    ax.set_xlabel("Omega0")
    ax.set_ylabel("lambda_A crit")
    ax.set_title(f"lambda_A crit vs Omega0 ({title_suffix})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"[ok] saved {out_path}")


def plot_lambdaA_diff_map(bound_df: pd.DataFrame, out_path: str, title_suffix: str="v6"):
    if bound_df is None or bound_df.empty:
        print("[skip] lambdaA diff map: empty dataframe")
        return

    # Expect K and Omega0 grids, plus crit columns
    if "K" not in bound_df.columns:
        # allow single-K boundaries: add a fake K=0 so we can still draw a strip
        bound_df = bound_df.copy()
        bound_df["K"] = 0

    # infer columns
    c_omega = "Omega0" if "Omega0" in bound_df.columns else ("omega0" if "omega0" in bound_df.columns else None)
    c_dir = None
    c_crit = None
    for c in bound_df.columns:
        cl = c.lower()
        if "lambda" in cl and "crit" in cl and "direct" in cl:
            c_dir = c
        if "lambda" in cl and "crit" in cl and ("criterion" in cl or "critn" in cl):
            c_crit = c

    if c_omega is None or c_dir is None or c_crit is None:
        print("[skip] lambdaA diff map: missing required columns")
        return

    tmp = bound_df.dropna(subset=[c_dir, c_crit]).copy()
    if tmp.empty:
        print("[skip] lambdaA diff map: no paired boundaries")
        return

    tmp["diff"] = np.abs(tmp[c_dir] - tmp[c_crit])
    # aggregate duplicates before pivoting
    tmp = tmp.groupby(["K", c_omega], as_index=False)["diff"].mean()
    pivot = tmp.pivot(index="K", columns=c_omega, values="diff")
    fig = plt.figure(figsize=(14, 4))
    ax = fig.add_subplot(111)
    im = ax.imshow(
        pivot.values,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[pivot.columns.min(), pivot.columns.max(), pivot.index.min(), pivot.index.max()],
        cmap="viridis",
        norm=Normalize(vmin=0.0, vmax=max(0.1, float(tmp["diff"].max())))
    )
    ax.set_xlabel("Omega0")
    ax.set_ylabel("K")
    ax.set_title(f"Boundary disagreement ({title_suffix})")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("|lambdaA_crit difference|")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"[ok] saved {out_path}")


# ----------------------------
# Main
# ----------------------------
def main():
    ap = argparse.ArgumentParser(description="SSZ v6 Visualization Toolkit")
    ap.add_argument("--data-dir", default="/mnt/data", help="directory with CSV/JSON results")
    ap.add_argument("--prefix", default="v6", help="file suffix (e.g., v6, v5, v4)")
    args = ap.parse_args()

    data_dir = args.data_dir
    prefix = args.prefix
    _ensure_dir(data_dir)

    # Load data
    df_results = _load_csv(_path(data_dir, "proof_sweep_results", prefix) + ".csv")
    df_bounds = _load_csv(_path(data_dir, "stability_boundaries", prefix) + ".csv")
    summary = _load_json(_path(data_dir, "proof_sweep_summary", prefix) + ".json")

    if summary:
        print("[info] summary:", json.dumps(summary, indent=2))

    # Figure outputs
    out_heat_uniform = os.path.join(data_dir, f"heatmap_stability_uniform_{prefix}.png")
    out_heat_weight = os.path.join(data_dir, f"heatmap_stability_weighted_{prefix}.png")
    out_disag_uniform = os.path.join(data_dir, f"disagreement_map_uniform_{prefix}.png")
    out_disag_weight = os.path.join(data_dir, f"disagreement_map_weighted_{prefix}.png")
    out_boundary = os.path.join(data_dir, f"boundary_lambdaA_vs_Omega0_{prefix}.png")
    out_diff = os.path.join(data_dir, f"lambdaA_diff_map_{prefix}.png")

    # Plots from results
    if df_results is not None and not df_results.empty:
        segment_modes = ["uniform", "weighted"]
        for mode in segment_modes:
            plot_stability_heatmap(df_results, mode, out_heat_uniform if mode=="uniform" else out_heat_weight, title_suffix=prefix)
            plot_disagreement_map(df_results, mode, out_disag_uniform if mode=="uniform" else out_disag_weight, title_suffix=prefix)
    else:
        print("[warn] proof_sweep_results not found or empty")

    # Plots from boundaries
    if df_bounds is not None and not df_bounds.empty:
        plot_boundaries(df_bounds, out_boundary, title_suffix=prefix)
        plot_lambdaA_diff_map(df_bounds, out_diff, title_suffix=prefix)
    else:
        print("[warn] stability_boundaries not found or empty")

if __name__ == "__main__":
    main()
