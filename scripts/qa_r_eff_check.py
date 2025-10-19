#!/usr/bin/env python3
"""
r_eff Quality Assurance Check

Validates effective radii (r_eff) in SSZ analysis outputs and flags suspicious values.

Usage:
    python scripts/qa_r_eff_check.py --input data.csv --output qa_report.csv
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Plausibility limits (SI units: meters)
OBJECT_CLASS_LIMITS = {
    "pulsar": {"min": 1e4, "max": 5e4, "expected": 1.5e4},  # ~10-50 km
    "neutron_star": {"min": 1e4, "max": 5e4, "expected": 1.5e4},
    "black_hole": {"min": 3e3, "max": 1e10, "expected": 1e6},  # Stellar to SMBH
    "white_dwarf": {"min": 5e6, "max": 2e7, "expected": 1e7},  # ~5000-20000 km
    "main_sequence": {"min": 5e8, "max": 2e9, "expected": 7e8},  # ~0.5-2 R_☉
    "giant": {"min": 5e10, "max": 5e11, "expected": 1e11},  # 50-500 R_☉
    "galaxy": {"min": 1e19, "max": 1e22, "expected": 1e20},  # kpc scale
    "default": {"min": 1e3, "max": 1e23, "expected": 1e9},  # Very permissive
}


def classify_object(row):
    """
    Classify object based on name patterns or explicit type column.
    
    Args:
        row: pandas DataFrame row
        
    Returns:
        str: Object class ("pulsar", "black_hole", etc.)
    """
    name = str(row.get("object", row.get("name", ""))).lower()
    obj_type = str(row.get("type", "")).lower()
    
    # Explicit type
    if "pulsar" in obj_type or "psr" in obj_type:
        return "pulsar"
    if "neutron" in obj_type or "ns" in obj_type:
        return "neutron_star"
    if "black hole" in obj_type or "bh" in obj_type:
        return "black_hole"
    if "white dwarf" in obj_type or "wd" in obj_type:
        return "white_dwarf"
    if "giant" in obj_type:
        return "giant"
    if "galaxy" in obj_type or "gal" in obj_type:
        return "galaxy"
    
    # Name patterns
    if "psr" in name or "pulsar" in name:
        return "pulsar"
    if "grs" in name or "cyg" in name or "lmc" in name:
        return "black_hole"  # Common BH binary patterns
    if "sgr a" in name or "m87" in name or "ngc" in name:
        return "black_hole"  # SMBH
    if "proxima" in name or "barnard" in name or "alpha cen" in name:
        return "main_sequence"  # Close stars
    
    return "default"


def check_r_eff(df, strict_mode=False):
    """
    Check r_eff values for plausibility.
    
    Args:
        df: pandas DataFrame with "r_eff" column
        strict_mode: If True, use tighter limits
        
    Returns:
        DataFrame with QA flags
    """
    qa_df = df.copy()
    qa_df["obj_class"] = qa_df.apply(classify_object, axis=1)
    qa_df["qa_flag"] = "PASS"
    qa_df["qa_reason"] = ""
    qa_df["expected_range"] = ""
    
    for idx, row in qa_df.iterrows():
        r_eff = row.get("r_eff", np.nan)
        obj_class = row["obj_class"]
        
        # Skip if r_eff is missing or NaN
        if pd.isna(r_eff) or r_eff <= 0:
            qa_df.at[idx, "qa_flag"] = "MISSING"
            qa_df.at[idx, "qa_reason"] = "r_eff is NaN or ≤0"
            continue
        
        # Get limits for object class
        limits = OBJECT_CLASS_LIMITS.get(obj_class, OBJECT_CLASS_LIMITS["default"])
        min_r, max_r, expected = limits["min"], limits["max"], limits["expected"]
        
        # Format expected range
        qa_df.at[idx, "expected_range"] = f"{min_r:.2e} - {max_r:.2e} m"
        
        # Check plausibility
        if r_eff < min_r:
            qa_df.at[idx, "qa_flag"] = "TOO_SMALL"
            qa_df.at[idx, "qa_reason"] = f"r_eff={r_eff:.2e} < min={min_r:.2e} for {obj_class}"
        elif r_eff > max_r:
            qa_df.at[idx, "qa_flag"] = "TOO_LARGE"
            qa_df.at[idx, "qa_reason"] = f"r_eff={r_eff:.2e} > max={max_r:.2e} for {obj_class}"
        elif strict_mode:
            # Additional check: more than 10× off from expected
            if r_eff < expected / 10 or r_eff > expected * 10:
                qa_df.at[idx, "qa_flag"] = "SUSPICIOUS"
                qa_df.at[idx, "qa_reason"] = f"r_eff={r_eff:.2e} unusual for {obj_class} (exp={expected:.2e})"
    
    return qa_df


def print_summary(qa_df):
    """Print QA summary statistics."""
    print("\n" + "="*80)
    print("QA SUMMARY")
    print("="*80)
    
    total = len(qa_df)
    passed = (qa_df["qa_flag"] == "PASS").sum()
    missing = (qa_df["qa_flag"] == "MISSING").sum()
    too_small = (qa_df["qa_flag"] == "TOO_SMALL").sum()
    too_large = (qa_df["qa_flag"] == "TOO_LARGE").sum()
    suspicious = (qa_df["qa_flag"] == "SUSPICIOUS").sum()
    
    print(f"Total objects:    {total}")
    print(f"PASS:             {passed:4d} ({100*passed/total:5.1f}%)")
    print(f"MISSING:          {missing:4d} ({100*missing/total:5.1f}%)")
    print(f"TOO_SMALL:        {too_small:4d} ({100*too_small/total:5.1f}%)")
    print(f"TOO_LARGE:        {too_large:4d} ({100*too_large/total:5.1f}%)")
    print(f"SUSPICIOUS:       {suspicious:4d} ({100*suspicious/total:5.1f}%)")
    
    print("\n" + "-"*80)
    print("QA FLAGS BY OBJECT CLASS")
    print("-"*80)
    
    for obj_class in qa_df["obj_class"].unique():
        subset = qa_df[qa_df["obj_class"] == obj_class]
        flagged = subset[subset["qa_flag"] != "PASS"]
        print(f"{obj_class:20s}: {len(subset):4d} total, {len(flagged):4d} flagged")
    
    print("="*80 + "\n")


def main():
    ap = argparse.ArgumentParser(description="QA check for r_eff values")
    ap.add_argument("--input", "-i", required=True, help="Input CSV file")
    ap.add_argument("--output", "-o", required=True, help="Output QA report CSV")
    ap.add_argument("--strict", action="store_true", help="Enable strict mode")
    ap.add_argument("--suspects-only", action="store_true", help="Output only flagged rows")
    args = ap.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        sys.exit(f"ERROR: Input file not found: {input_path}")
    
    print(f"[INFO] Reading input: {input_path}")
    df = pd.read_csv(input_path)
    
    if "r_eff" not in df.columns:
        sys.exit("ERROR: Input CSV must have 'r_eff' column")
    
    print(f"[INFO] Loaded {len(df)} objects")
    
    # Run QA check
    qa_df = check_r_eff(df, strict_mode=args.strict)
    
    # Print summary
    print_summary(qa_df)
    
    # Output
    if args.suspects_only:
        qa_df = qa_df[qa_df["qa_flag"] != "PASS"]
        print(f"[INFO] Writing {len(qa_df)} flagged objects to {output_path}")
    else:
        print(f"[INFO] Writing all {len(qa_df)} objects to {output_path}")
    
    qa_df.to_csv(output_path, index=False)
    print(f"[OK] QA report written: {output_path}")
    
    # Exit code based on QA results
    failed = len(qa_df[qa_df["qa_flag"] != "PASS"])
    if failed > 0:
        print(f"\n[WARN] {failed} objects flagged for review")
        return 1
    else:
        print("\n[OK] All objects passed QA")
        return 0


if __name__ == "__main__":
    sys.exit(main())
