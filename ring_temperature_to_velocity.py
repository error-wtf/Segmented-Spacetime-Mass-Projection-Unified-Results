#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empirical forward test for Section 4.6:
Given per-ring temperature proxy T (e.g., dust temperature or excitation temperature),
predict the radial expansion speed profile using v ~ gamma^{-1/2} and gamma ~ T.

Input CSV columns:
- ring: integer ring index in increasing radius order (0 … N)
- T_proxy_K: temperature proxy per ring (Kelvin or any monotonic proxy)
- v_obs_kms: (optional) observed expansion speed per ring (km/s)

Usage:
    # With real data:
    python ring_temperature_to_velocity.py /path/to/real_data.csv --v0 10.0
    
    # Auto-discover real data (falls back to example):
    python ring_temperature_to_velocity.py --v0 10.0

Outputs:
- prints per-ring table with T, q_k, v_pred, v_obs (if given) and residuals
- prints total predicted Δv = v_N - v_0
"""

import argparse
import sys
import io
import os

# Force UTF-8 for stdout/stderr (Windows-safe)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from pathlib import Path
import pandas as pd
import numpy as np

def find_real_ring_data(search_root: Path) -> Path | None:
    """
    Search for real ring temperature data in common locations.
    Priority order:
    1. agent_out/reports/ring_*.csv
    2. experiments/*/ring_*.csv
    3. out/ring_*.csv
    4. data/ring_*.csv (but not example_rings.csv)
    """
    search_patterns = [
        "agent_out/reports/ring_temperature*.csv",
        "agent_out/reports/ring_data*.csv",
        "experiments/*/ring_*.csv",
        "out/ring_temperature*.csv",
        "out/ring_data*.csv",
        "data/ring_temperature*.csv",
        "data/ring_data*.csv",
    ]
    
    for pattern in search_patterns:
        matches = list(search_root.glob(pattern))
        # Filter out example files
        real_matches = [m for m in matches if "example" not in m.name.lower()]
        if real_matches:
            # Return most recent
            return max(real_matches, key=lambda p: p.stat().st_mtime)
    
    return None

def main():
    ap = argparse.ArgumentParser(
        description="Ring temperature → velocity prediction (Section 4.6)"
    )
    ap.add_argument("csv", nargs="?", help="CSV file with columns: ring,T_proxy_K[,v_obs_kms]")
    ap.add_argument("--v0", type=float, default=10.0, help="Baseline expansion speed at ring 0 [km/s]")
    ap.add_argument("--no-fallback", action="store_true", help="Don't use example data as fallback")
    args = ap.parse_args()

    # Determine CSV path
    csv_path = None
    data_source = "unknown"
    
    if args.csv:
        # Explicit path provided
        csv_path = Path(args.csv)
        if not csv_path.exists():
            sys.exit(f"ERROR: CSV file not found: {csv_path}")
        data_source = f"user-specified: {csv_path.name}"
    else:
        # Auto-discover real data
        here = Path(__file__).resolve().parent
        real_data = find_real_ring_data(here)
        
        if real_data:
            csv_path = real_data
            data_source = f"real data: {csv_path.relative_to(here)}"
            print(f"[INFO] Found real ring data: {csv_path}")
        elif not args.no_fallback:
            # Fallback to example
            csv_path = here / "data" / "example_rings.csv"
            if csv_path.exists():
                data_source = f"example data (fallback): {csv_path.name}"
                print(f"[WARN] No real ring data found, using example: {csv_path}")
            else:
                sys.exit("ERROR: No ring data found and no example file available.")
        else:
            sys.exit("ERROR: No ring data found and --no-fallback specified.")
    
    # Load and validate
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        sys.exit(f"ERROR: Failed to read CSV: {e}")
    
    for col in ["ring", "T_proxy_K"]:
        if col not in df.columns:
            sys.exit(f"ERROR: missing required column '{col}' in {csv_path}")

    df = df.sort_values("ring").reset_index(drop=True)
    
    # Remove rows with NaN temperatures
    original_len = len(df)
    df = df.dropna(subset=["T_proxy_K"]).reset_index(drop=True)
    if len(df) < original_len:
        print(f"[INFO] Dropped {original_len - len(df)} rows with missing T_proxy_K")

    if len(df) == 0:
        sys.exit("ERROR: No valid temperature data after cleanup")

    # Compute q_k = gamma_k / gamma_{k-1} ~ T_k / T_{k-1}
    q = [np.nan]
    for i in range(1, len(df)):
        q.append(df.loc[i, "T_proxy_K"] / df.loc[i-1, "T_proxy_K"])
    df["q_k"] = q

    # Predict speeds: v_k = v_{k-1} * q_k^{-1/2}
    v_pred = [args.v0]
    for i in range(1, len(df)):
        v_pred.append(v_pred[-1] * (df.loc[i, "q_k"]) ** (-0.5))
    df["v_pred_kms"] = v_pred

    # Residuals if v_obs is present
    has_obs = "v_obs_kms" in df.columns and df["v_obs_kms"].notna().any()
    if has_obs:
        df["residual_kms"] = df["v_obs_kms"] - df["v_pred_kms"]

    # Summary
    delta_v = df["v_pred_kms"].iloc[-1] - df["v_pred_kms"].iloc[0]
    ratio = df["v_pred_kms"].iloc[-1] / df["v_pred_kms"].iloc[0]

    # Print report
    print("\n" + "="*70)
    print("Ring Temperature → Velocity Prediction (Section 4.6)")
    print("="*70)
    print(f"Data source: {data_source}")
    print(f"Number of rings: {len(df)}")
    print(f"Baseline v0: {args.v0:.3f} km/s")
    print("="*70 + "\n")
    
    cols_to_show = ["ring", "T_proxy_K", "q_k", "v_pred_kms"]
    if has_obs:
        cols_to_show += ["v_obs_kms", "residual_kms"]
    
    print(df[cols_to_show].to_string(index=False, justify="center", float_format=lambda x: f"{x:,.3f}"))
    
    print("\n" + "="*70)
    print(f"Predicted total Δv = {delta_v:.3f} km/s (factor {ratio:.3f}×)")
    
    if has_obs:
        mae = df["residual_kms"].abs().mean()
        rmse = np.sqrt((df["residual_kms"]**2).mean())
        print(f"Mean absolute error (MAE) = {mae:.3f} km/s")
        print(f"Root mean square error (RMSE) = {rmse:.3f} km/s")
    
    print("="*70 + "\n")
    
    # Save results
    output_csv = csv_path.parent / f"{csv_path.stem}_results.csv"
    df.to_csv(output_csv, index=False)
    print(f"[OK] Results saved to: {output_csv}")


if __name__ == "__main__":
    main()
