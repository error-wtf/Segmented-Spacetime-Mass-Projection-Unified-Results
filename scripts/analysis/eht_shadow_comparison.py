#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EHT Shadow Comparison: SSZ vs. GR vs. Observations

Compares SSZ predictions (~5-6% offset) against EHT Collaboration data
for Sgr A* and M87* shadow measurements.

References:
- EHT Collaboration 2022 (Sgr A*): ApJ Letters 930
- EHT Collaboration 2019 (M87*): ApJ Letters 875
"""

import argparse
import sys
from pathlib import Path
import json
import numpy as np
from scipy.stats import chi2

# EHT Published Data (angular sizes in microarcseconds)
EHT_DATA = {
    "Sgr_A": {
        "name": "Sagittarius A*",
        "obs_shadow_uas": 51.8,
        "obs_error_uas": 8.6,
        "distance_kpc": 8.127,
        "mass_msun": 4.15e6,
        "gr_prediction_uas": 51.8,
        "ssz_prediction_uas": 54.9,  # +6.0% from GR
        "ssz_r_rs": 3.18,  # vs. GR: 3.00
        "gr_r_rs": 3.00,
    },
    "M87": {
        "name": "M87*",
        "obs_shadow_uas": 39.0,
        "obs_error_uas": 8.0,
        "distance_mpc": 16.9,
        "mass_msun": 6.5e9,
        "gr_prediction_uas": 42.0,
        "ssz_prediction_uas": 44.5,  # +6.0% from GR
        "ssz_r_rs": 3.18,
        "gr_r_rs": 3.00,
    },
}


def compute_chi2(prediction, observation, error):
    """Compute χ² for a single measurement."""
    return ((prediction - observation) / error) ** 2


def compute_p_value(chi2_value, dof):
    """Compute p-value from χ² statistic."""
    return 1 - chi2.cdf(chi2_value, df=dof)


def analyze_object(name, data):
    """Analyze single object (Sgr A* or M87*)."""
    obs = data["obs_shadow_uas"]
    err = data["obs_error_uas"]
    ssz = data["ssz_prediction_uas"]
    gr = data["gr_prediction_uas"]
    
    chi2_ssz = compute_chi2(ssz, obs, err)
    chi2_gr = compute_chi2(gr, obs, err)
    
    residual_ssz = ssz - obs
    residual_gr = gr - obs
    
    sigma_ssz = residual_ssz / err
    sigma_gr = residual_gr / err
    
    return {
        "object": data["name"],
        "obs_uas": float(obs),
        "err_uas": float(err),
        "ssz_pred_uas": float(ssz),
        "gr_pred_uas": float(gr),
        "residual_ssz_uas": float(residual_ssz),
        "residual_gr_uas": float(residual_gr),
        "sigma_ssz": float(sigma_ssz),
        "sigma_gr": float(sigma_gr),
        "chi2_ssz": float(chi2_ssz),
        "chi2_gr": float(chi2_gr),
        "ssz_in_1sigma": bool(abs(sigma_ssz) < 1.0),
        "gr_in_1sigma": bool(abs(sigma_gr) < 1.0),
    }


def main():
    ap = argparse.ArgumentParser(
        description="EHT shadow comparison: SSZ vs. GR"
    )
    ap.add_argument("--output", "-o", type=str, default=None,
                    help="Output JSON file")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Verbose output")
    args = ap.parse_args()
    
    results = {}
    
    # Analyze each object
    for key, data in EHT_DATA.items():
        result = analyze_object(key, data)
        results[key] = result
    
    # Combined χ²
    chi2_ssz_total = sum(r["chi2_ssz"] for r in results.values())
    chi2_gr_total = sum(r["chi2_gr"] for r in results.values())
    
    dof = len(EHT_DATA)
    p_ssz = compute_p_value(chi2_ssz_total, dof)
    p_gr = compute_p_value(chi2_gr_total, dof)
    
    # Summary
    summary = {
        "chi2_ssz_total": float(chi2_ssz_total),
        "chi2_gr_total": float(chi2_gr_total),
        "dof": dof,
        "p_value_ssz": float(p_ssz),
        "p_value_gr": float(p_gr),
        "ssz_consistent": p_ssz > 0.05,
        "gr_consistent": p_gr > 0.05,
        "delta_chi2": float(chi2_ssz_total - chi2_gr_total),
    }
    
    output = {
        "summary": summary,
        "objects": results,
        "interpretation": interpret_results(summary, results),
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


def interpret_results(summary, objects):
    """Generate interpretation text."""
    lines = []
    
    if summary["ssz_consistent"]:
        lines.append("✓ SSZ is statistically consistent with EHT data (p > 0.05)")
    else:
        lines.append("✗ SSZ is inconsistent with EHT data (p < 0.05)")
    
    if summary["gr_consistent"]:
        lines.append("✓ GR is statistically consistent with EHT data (p > 0.05)")
    else:
        lines.append("✗ GR is inconsistent with EHT data (p < 0.05)")
    
    # Per-object
    for key, obj in objects.items():
        if obj["ssz_in_1sigma"]:
            lines.append(f"✓ {obj['object']}: SSZ within 1σ of observation")
        else:
            lines.append(f"⚠ {obj['object']}: SSZ at {obj['sigma_ssz']:.2f}σ from observation")
    
    # Model comparison
    if summary["delta_chi2"] < 0:
        lines.append(f"→ SSZ has lower χ² than GR by {-summary['delta_chi2']:.3f}")
    elif summary["delta_chi2"] > 0:
        lines.append(f"→ GR has lower χ² than SSZ by {summary['delta_chi2']:.3f}")
    else:
        lines.append("→ SSZ and GR have equal χ²")
    
    return lines


def print_report(output, verbose=False):
    """Print formatted report."""
    summary = output["summary"]
    objects = output["objects"]
    
    print("\n" + "=" * 80)
    print("EHT Shadow Comparison: SSZ vs. GR")
    print("=" * 80)
    
    print("\nPer-Object Results:")
    print("-" * 80)
    for key, obj in objects.items():
        print(f"\n{obj['object']}:")
        print(f"  Observed:       {obj['obs_uas']:6.1f} ± {obj['err_uas']:5.1f} μas")
        print(f"  SSZ Prediction: {obj['ssz_pred_uas']:6.1f} μas  (Δ = {obj['residual_ssz_uas']:+6.1f} μas, {obj['sigma_ssz']:+5.2f}σ)")
        print(f"  GR Prediction:  {obj['gr_pred_uas']:6.1f} μas  (Δ = {obj['residual_gr_uas']:+6.1f} μas, {obj['sigma_gr']:+5.2f}σ)")
        print(f"  χ²(SSZ):        {obj['chi2_ssz']:6.3f}")
        print(f"  χ²(GR):         {obj['chi2_gr']:6.3f}")
        
        if obj['ssz_in_1sigma']:
            print("  Status:         ✓ SSZ within 1σ")
        else:
            print(f"  Status:         ⚠ SSZ at {abs(obj['sigma_ssz']):.2f}σ")
    
    print("\n" + "-" * 80)
    print("Combined Statistics:")
    print("-" * 80)
    print(f"χ²(SSZ):     {summary['chi2_ssz_total']:6.3f}  (dof = {summary['dof']})")
    print(f"χ²(GR):      {summary['chi2_gr_total']:6.3f}  (dof = {summary['dof']})")
    print(f"p(SSZ):      {summary['p_value_ssz']:6.4f}")
    print(f"p(GR):       {summary['p_value_gr']:6.4f}")
    print(f"Δχ²:         {summary['delta_chi2']:+6.3f}  (SSZ - GR)")
    
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
