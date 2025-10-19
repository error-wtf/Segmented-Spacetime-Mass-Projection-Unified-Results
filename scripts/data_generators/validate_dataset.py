#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dataset Validation Tool

Validates that a CSV dataset meets SSZ pipeline requirements.
Use before integrating external datasets.

Usage:
    python scripts/data_generators/validate_dataset.py --csv external_data.csv
    python scripts/data_generators/validate_dataset.py --csv real_data_full.csv --strict

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pandas as pd
import numpy as np
import argparse
import sys
import os

# UTF-8 Setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        import io
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Critical columns (MUST exist and be filled for all rows)
CRITICAL_COLUMNS = [
    'source',      # Source name
    'f_emit_Hz',   # Emitted frequency
    'f_obs_Hz',    # Observed frequency  
    'r_emit_m',    # Emission radius
    'M_solar',     # Mass in solar masses
    'n_round',     # Segment count
    'z'            # Redshift
]

# Recommended columns (should exist but NaN is OK where not applicable)
RECOMMENDED_COLUMNS = [
    'case',        # Case/observation description
    'category',    # Source category
]

# Optional columns (nice to have, NaN is OK)
OPTIONAL_COLUMNS = [
    'a_m',         # Semi-major axis (orbital sources only)
    'e',           # Eccentricity (orbital sources only)
    'P_year',      # Orbital period (orbital sources only)
    'v_los_mps',   # Line-of-sight velocity (Doppler sources only)
    'v_tot_mps',   # Total velocity (motion sources only)
]

def validate_dataset(csv_path, strict=False):
    """
    Validate dataset against SSZ pipeline requirements
    
    Parameters:
        csv_path: Path to CSV file
        strict: If True, also validate recommended columns
    
    Returns:
        bool: True if valid, False otherwise
    """
    
    print("="*80)
    print("SSZ DATASET VALIDATION")
    print("="*80)
    print(f"\nFile: {csv_path}")
    print(f"Strict mode: {strict}")
    
    # Load CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"\n✓ Loaded successfully")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
    except Exception as e:
        print(f"\n✗ ERROR loading CSV: {e}")
        return False
    
    # Track validation status
    errors = []
    warnings = []
    
    # ===== 1. CRITICAL COLUMNS =====
    print(f"\n{'='*80}")
    print("1. CRITICAL COLUMNS (MUST exist and be filled)")
    print(f"{'='*80}")
    
    for col in CRITICAL_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing critical column: {col}")
            print(f"✗ {col}: MISSING")
        else:
            null_count = df[col].isna().sum()
            if null_count > 0:
                errors.append(f"Critical column {col} has {null_count} NaN values")
                print(f"✗ {col}: {null_count}/{len(df)} NaN ({null_count/len(df)*100:.1f}%)")
            else:
                print(f"✓ {col}: {len(df)}/{len(df)} filled (100%)")
    
    # ===== 2. RECOMMENDED COLUMNS =====
    print(f"\n{'='*80}")
    print("2. RECOMMENDED COLUMNS (should exist, NaN OK)")
    print(f"{'='*80}")
    
    for col in RECOMMENDED_COLUMNS:
        if col not in df.columns:
            msg = f"Missing recommended column: {col}"
            if strict:
                errors.append(msg)
                print(f"✗ {col}: MISSING (strict mode)")
            else:
                warnings.append(msg)
                print(f"⚠ {col}: MISSING (recommended)")
        else:
            null_count = df[col].isna().sum()
            print(f"✓ {col}: exists ({len(df) - null_count}/{len(df)} filled)")
    
    # ===== 3. OPTIONAL COLUMNS =====
    print(f"\n{'='*80}")
    print("3. OPTIONAL COLUMNS (nice to have)")
    print(f"{'='*80}")
    
    optional_found = []
    for col in OPTIONAL_COLUMNS:
        if col in df.columns:
            null_count = df[col].isna().sum()
            optional_found.append(col)
            print(f"✓ {col}: exists ({len(df) - null_count}/{len(df)} filled)")
    
    if len(optional_found) == 0:
        print("  (none found - OK for minimal datasets)")
    
    # ===== 4. DATA VALIDATION =====
    print(f"\n{'='*80}")
    print("4. DATA VALIDATION")
    print(f"{'='*80}")
    
    # Check frequencies are positive
    if 'f_obs_Hz' in df.columns:
        if (df['f_obs_Hz'] <= 0).any():
            errors.append("f_obs_Hz contains non-positive values")
            print(f"✗ f_obs_Hz: has non-positive values")
        else:
            print(f"✓ f_obs_Hz: all positive")
    
    # Check masses are positive
    if 'M_solar' in df.columns:
        if (df['M_solar'] <= 0).any():
            errors.append("M_solar contains non-positive values")
            print(f"✗ M_solar: has non-positive values")
        else:
            print(f"✓ M_solar: all positive")
    
    # Check redshift reasonable (-1 < z for non-relativistic)
    if 'z' in df.columns:
        if (df['z'] < -1).any():
            errors.append("z contains extremely negative values (z < -1)")
            print(f"✗ z: has z < -1 (unphysical)")
        elif (df['z'] < 0).any():
            neg_count = (df['z'] < 0).sum()
            warnings.append(f"{neg_count} sources have blueshift (z < 0)")
            print(f"⚠ z: {neg_count} blueshifts (z < 0, OK for approaching sources)")
        else:
            print(f"✓ z: all non-negative (redshift only)")
    
    # Check eccentricity if present (0 <= e < 1)
    if 'e' in df.columns:
        e_valid = df['e'].dropna()
        if len(e_valid) > 0:
            if ((e_valid < 0) | (e_valid >= 1)).any():
                warnings.append("e (eccentricity) has values outside [0, 1)")
                print(f"⚠ e: has values outside [0, 1)")
            else:
                print(f"✓ e: all in valid range [0, 1)")
    
    # ===== 5. STATISTICS =====
    print(f"\n{'='*80}")
    print("5. DATASET STATISTICS")
    print(f"{'='*80}")
    
    print(f"\nTotal rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Critical columns: {sum(col in df.columns for col in CRITICAL_COLUMNS)}/{len(CRITICAL_COLUMNS)}")
    print(f"Recommended columns: {sum(col in df.columns for col in RECOMMENDED_COLUMNS)}/{len(RECOMMENDED_COLUMNS)}")
    print(f"Optional columns: {len(optional_found)}/{len(OPTIONAL_COLUMNS)}")
    
    # Unique sources
    if 'source' in df.columns:
        print(f"Unique sources: {df['source'].nunique()}")
    
    # Frequency range
    if 'f_obs_Hz' in df.columns:
        print(f"Frequency range: {df['f_obs_Hz'].min():.2e} - {df['f_obs_Hz'].max():.2e} Hz")
    
    # Mass range
    if 'M_solar' in df.columns:
        print(f"Mass range: {df['M_solar'].min():.2e} - {df['M_solar'].max():.2e} M☉")
    
    # ===== 6. SUMMARY =====
    print(f"\n{'='*80}")
    print("6. VALIDATION SUMMARY")
    print(f"{'='*80}")
    
    if len(errors) == 0 and len(warnings) == 0:
        print(f"\n✅ DATASET VALID!")
        print(f"   All critical requirements met")
        print(f"   Ready for SSZ pipeline")
        return True
    
    elif len(errors) == 0:
        print(f"\n⚠️  DATASET USABLE (with warnings)")
        print(f"   All critical requirements met")
        print(f"   {len(warnings)} warnings (can be ignored)")
        
        print(f"\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
        
        print(f"\n✓ Can be used in SSZ pipeline")
        print(f"  (Warnings are for optimal usage, not blockers)")
        return True
    
    else:
        print(f"\n✗ DATASET INVALID!")
        print(f"   {len(errors)} errors found")
        
        print(f"\nErrors:")
        for e in errors:
            print(f"  - {e}")
        
        if len(warnings) > 0:
            print(f"\nWarnings:")
            for w in warnings:
                print(f"  - {w}")
        
        print(f"\n✗ Cannot be used in SSZ pipeline until fixed")
        return False

def main():
    """Main validation workflow"""
    
    parser = argparse.ArgumentParser(
        description='Validate dataset against SSZ pipeline requirements'
    )
    parser.add_argument('--csv', required=True,
                        help='Path to CSV file to validate')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode (also validate recommended columns)')
    args = parser.parse_args()
    
    # Validate
    valid = validate_dataset(args.csv, strict=args.strict)
    
    # Exit code
    sys.exit(0 if valid else 1)

if __name__ == '__main__':
    main()
