#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redshift Robustness Analysis

Bootstrap and Jackknife analysis to assess stability of redshift predictions.
Tests sensitivity to outliers and velocity corrections.

Methods:
1. Bootstrap (1000 resamples): Confidence intervals
2. Jackknife (leave-one-out): Bias estimation
3. Outlier sensitivity: Remove top 5% velocity corrections
"""

import argparse
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
from scipy.stats import bootstrap


def bootstrap_analysis(data, n_resamples=1000, confidence_level=0.95, seed=42):
    """
    Perform bootstrap analysis on median |Δz|.
    
    Returns dict with mean, std, and confidence interval.
    """
    rng = np.random.default_rng(seed=seed)
    
    def median_func(x):
        return np.median(np.abs(x))
    
    result = bootstrap(
        (data,),
        median_func,
        n_resamples=n_resamples,
        random_state=rng,
        confidence_level=confidence_level,
        method='percentile'
    )
    
    # Compute bootstrap distribution
    bootstrap_samples = []
    for _ in range(n_resamples):
        sample = rng.choice(data, size=len(data), replace=True)
        bootstrap_samples.append(median_func(sample))
    
    return {
        "mean": float(np.mean(bootstrap_samples)),
        "std": float(np.std(bootstrap_samples)),
        "ci_lower": float(result.confidence_interval.low),
        "ci_upper": float(result.confidence_interval.high),
        "confidence_level": confidence_level,
        "n_resamples": n_resamples,
    }


def jackknife_analysis(data):
    """
    Perform jackknife (leave-one-out) analysis.
    
    Returns dict with bias and variance estimates.
    """
    n = len(data)
    theta_full = np.median(np.abs(data))
    
    # Leave-one-out estimates
    theta_i = []
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        theta_i.append(np.median(np.abs(data[mask])))
    
    theta_i = np.array(theta_i)
    
    # Jackknife bias
    theta_jack = np.mean(theta_i)
    bias = (n - 1) * (theta_jack - theta_full)
    
    # Jackknife variance
    variance = ((n - 1) / n) * np.sum((theta_i - theta_jack) ** 2)
    
    return {
        "full_estimate": float(theta_full),
        "jackknife_mean": float(theta_jack),
        "bias": float(bias),
        "bias_relative_pct": float(100 * bias / theta_full),
        "variance": float(variance),
        "std_error": float(np.sqrt(variance)),
    }


def outlier_sensitivity(df, metric_col="Δz_seg", percentile=95):
    """
    Test sensitivity to outliers by removing top percentile.
    
    Assumes df has velocity correction flags or residuals.
    """
    data_all = df[metric_col].dropna().values
    median_all = np.median(np.abs(data_all))
    
    # Remove top percentile
    threshold = np.percentile(np.abs(data_all), percentile)
    data_filtered = data_all[np.abs(data_all) < threshold]
    median_filtered = np.median(np.abs(data_filtered))
    
    delta = median_filtered - median_all
    delta_pct = 100 * delta / median_all
    
    return {
        "median_all": float(median_all),
        "median_filtered": float(median_filtered),
        "delta": float(delta),
        "delta_pct": float(delta_pct),
        "percentile": percentile,
        "n_all": len(data_all),
        "n_filtered": len(data_filtered),
        "n_removed": len(data_all) - len(data_filtered),
    }


def main():
    ap = argparse.ArgumentParser(
        description="Redshift robustness: Bootstrap + Jackknife + Outlier Sensitivity"
    )
    ap.add_argument("--input", "-i", required=True,
                    help="Input CSV with redshift residuals")
    ap.add_argument("--metric", default="Δz_seg",
                    help="Column name for residuals (default: Δz_seg)")
    ap.add_argument("--bootstrap-samples", type=int, default=1000,
                    help="Number of bootstrap resamples")
    ap.add_argument("--output", "-o", type=str, default=None,
                    help="Output JSON file")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    
    # Load data
    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"ERROR: Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    if args.metric not in df.columns:
        sys.exit(f"ERROR: Column '{args.metric}' not found in {input_path}")
    
    data = df[args.metric].dropna().values
    
    print(f"[INFO] Loaded {len(data)} valid redshift residuals from {input_path}")
    
    # Run analyses
    print("[INFO] Running bootstrap analysis...")
    bootstrap_result = bootstrap_analysis(
        data,
        n_resamples=args.bootstrap_samples
    )
    
    print("[INFO] Running jackknife analysis...")
    jackknife_result = jackknife_analysis(data)
    
    print("[INFO] Running outlier sensitivity analysis...")
    outlier_result = outlier_sensitivity(df, metric_col=args.metric)
    
    # Compile results
    output = {
        "input_file": str(input_path),
        "metric": args.metric,
        "n_samples": len(data),
        "bootstrap": bootstrap_result,
        "jackknife": jackknife_result,
        "outlier_sensitivity": outlier_result,
        "interpretation": interpret_results(bootstrap_result, jackknife_result, outlier_result),
    }
    
    # Print report
    print_report(output, verbose=args.verbose)
    
    # Save JSON
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        print(f"\n[INFO] Results saved to: {output_path}")
    
    return 0


def interpret_results(bootstrap, jackknife, outlier):
    """Generate interpretation text."""
    lines = []
    
    # Bootstrap CI width
    ci_width = bootstrap["ci_upper"] - bootstrap["ci_lower"]
    if ci_width < 0.005:
        lines.append(f"✓ Bootstrap CI is tight ({ci_width:.4f})")
    else:
        lines.append(f"⚠ Bootstrap CI is wide ({ci_width:.4f})")
    
    # Jackknife bias
    if abs(jackknife["bias_relative_pct"]) < 10:
        lines.append(f"✓ Jackknife bias is negligible ({jackknife['bias_relative_pct']:.2f}%)")
    else:
        lines.append(f"⚠ Jackknife bias is significant ({jackknife['bias_relative_pct']:.2f}%)")
    
    # Outlier sensitivity
    if abs(outlier["delta_pct"]) < 5:
        lines.append(f"✓ Robust to outliers (Δ = {outlier['delta_pct']:.2f}%)")
    else:
        lines.append(f"⚠ Sensitive to outliers (Δ = {outlier['delta_pct']:.2f}%)")
    
    return lines


def print_report(output, verbose=False):
    """Print formatted report."""
    bootstrap = output["bootstrap"]
    jackknife = output["jackknife"]
    outlier = output["outlier_sensitivity"]
    
    print("\n" + "=" * 80)
    print("Redshift Robustness Analysis")
    print("=" * 80)
    print(f"Input file: {output['input_file']}")
    print(f"Metric:     {output['metric']}")
    print(f"Samples:    {output['n_samples']}")
    
    print("\n" + "-" * 80)
    print("Bootstrap Analysis (1000 resamples):")
    print("-" * 80)
    print(f"  Mean(median |Δz|):  {bootstrap['mean']:.6f}")
    print(f"  Std(median |Δz|):   {bootstrap['std']:.6f}")
    print(f"  95% CI:             [{bootstrap['ci_lower']:.6f}, {bootstrap['ci_upper']:.6f}]")
    print(f"  CI Width:           {bootstrap['ci_upper'] - bootstrap['ci_lower']:.6f}")
    
    print("\n" + "-" * 80)
    print("Jackknife Analysis (leave-one-out):")
    print("-" * 80)
    print(f"  Full estimate:      {jackknife['full_estimate']:.6f}")
    print(f"  Jackknife mean:     {jackknife['jackknife_mean']:.6f}")
    print(f"  Bias:               {jackknife['bias']:.6f}")
    print(f"  Bias (relative):    {jackknife['bias_relative_pct']:.2f}%")
    print(f"  Std Error:          {jackknife['std_error']:.6f}")
    
    print("\n" + "-" * 80)
    print("Outlier Sensitivity (remove top 5%):")
    print("-" * 80)
    print(f"  Median (all):       {outlier['median_all']:.6f}")
    print(f"  Median (filtered):  {outlier['median_filtered']:.6f}")
    print(f"  Delta:              {outlier['delta']:.6f}")
    print(f"  Delta (%):          {outlier['delta_pct']:.2f}%")
    print(f"  Samples removed:    {outlier['n_removed']} / {outlier['n_all']}")
    
    print("\n" + "-" * 80)
    print("Interpretation:")
    print("-" * 80)
    for line in output["interpretation"]:
        print(f"  {line}")
    
    print("\n" + "=" * 80)
    
    if verbose:
        print("\nDetails:")
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    sys.exit(main())
