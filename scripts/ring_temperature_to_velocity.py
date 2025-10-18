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

Usage (example):
    python ring_temperature_to_velocity.py /path/to/data.csv --v0 10.0 --output report.txt

Outputs:
- prints per-ring table with T, q_k, v_pred, v_obs (if given) and residuals
- prints total predicted Δv = v_N - v_0
- saves detailed report to file if --output specified
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    ap = argparse.ArgumentParser(
        description="Predict expansion velocity from temperature proxy (Section 4.6)"
    )
    ap.add_argument("csv", help="CSV file with columns: ring,T_proxy_K[,v_obs_kms]")
    ap.add_argument("--v0", type=float, default=10.0, 
                    help="Baseline expansion speed at ring 0 [km/s]")
    ap.add_argument("--output", "-o", type=str, default=None,
                    help="Output report file (default: stdout only)")
    ap.add_argument("--csv-output", type=str, default=None,
                    help="Save full prediction table as CSV")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"ERROR: Input file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    
    # Check for required columns - allow "T" as alias for "T_proxy_K"
    if "ring" not in df.columns:
        sys.exit(f"ERROR: missing required column 'ring' in {args.csv}")
    
    # Handle temperature column flexibly
    temp_col = None
    if "T_proxy_K" in df.columns:
        temp_col = "T_proxy_K"
    elif "T" in df.columns:
        temp_col = "T"
        df["T_proxy_K"] = df["T"]  # Create alias
        print(f"[INFO] Using column 'T' as temperature proxy (renamed to 'T_proxy_K')")
    else:
        sys.exit(f"ERROR: missing temperature column ('T_proxy_K' or 'T') in {args.csv}")

    df = df.sort_values("ring").reset_index(drop=True)

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
    if "v_obs_kms" in df.columns:
        df["residual_kms"] = df["v_obs_kms"] - df["v_pred_kms"]
        df["rel_err_pct"] = 100 * df["residual_kms"] / df["v_obs_kms"]

    # Summary statistics
    delta_v = df["v_pred_kms"].iloc[-1] - df["v_pred_kms"].iloc[0]
    ratio = df["v_pred_kms"].iloc[-1] / df["v_pred_kms"].iloc[0]

    # Build report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("Ring Temperature → Velocity Prediction (Section 4.6)")
    report_lines.append("=" * 80)
    report_lines.append(f"Timestamp: {datetime.now().isoformat()}")
    report_lines.append(f"Input file: {csv_path}")
    report_lines.append(f"Number of rings: {len(df)}")
    report_lines.append(f"Baseline velocity v0: {args.v0:.3f} km/s")
    report_lines.append("")
    report_lines.append("Model: v_k = v_{k-1} * (T_k / T_{k-1})^{-1/2}")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Table
    cols_to_show = ["ring", "T_proxy_K", "q_k", "v_pred_kms"]
    if "v_obs_kms" in df.columns:
        cols_to_show += ["v_obs_kms", "residual_kms", "rel_err_pct"]
    
    table_str = df[cols_to_show].to_string(index=False, justify="center", 
                                            float_format=lambda x: f"{x:,.3f}")
    report_lines.append(table_str)
    report_lines.append("")
    report_lines.append("-" * 80)
    report_lines.append("SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"Initial velocity (ring 0):     {df['v_pred_kms'].iloc[0]:8.3f} km/s")
    report_lines.append(f"Final velocity (ring {df['ring'].iloc[-1]:2d}):      {df['v_pred_kms'].iloc[-1]:8.3f} km/s")
    report_lines.append(f"Predicted Δv (total):          {delta_v:8.3f} km/s")
    report_lines.append(f"Velocity ratio (v_N / v_0):    {ratio:8.3f}x")
    
    if has_obs:
        mae = df["residual_kms"].abs().mean()
        rmse = np.sqrt((df["residual_kms"] ** 2).mean())
        mape = df["rel_err_pct"].abs().mean()
        report_lines.append("")
        report_lines.append("Comparison with observations:")
        report_lines.append(f"  Mean Absolute Error (MAE):    {mae:8.3f} km/s")
        report_lines.append(f"  Root Mean Square Error (RMSE): {rmse:8.3f} km/s")
        report_lines.append(f"  Mean Absolute % Error (MAPE):  {mape:8.2f} %")
    
    report_lines.append("=" * 80)

    report_text = "\n".join(report_lines)

    # Print to stdout
    print(report_text)

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding="utf-8")
        print(f"\n[INFO] Report saved to: {output_path}")

    # Save CSV if requested
    if args.csv_output:
        csv_out_path = Path(args.csv_output)
        csv_out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_out_path, index=False)
        print(f"[INFO] Full prediction table saved to: {csv_out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
