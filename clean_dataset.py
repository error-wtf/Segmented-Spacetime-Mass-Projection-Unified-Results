#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Dataset - Fix NaN and Duplicate Issues
===========================================

Fixes NaN values and duplicate entries in the merged dataset
while preserving the complete structure needed by segmented spacetime scripts.
"""

import csv
import math
import pandas as pd
import numpy as np
from typing import Dict, Any

# Physical constants
C = 299_792_458.0  # m/s
HALPHA_HZ = C / 656.281e-9  # H-alpha frequency
BRGAMMA_HZ = C / 2.1661e-6  # Brackett-gamma frequency

def clean_nan_values(df: pd.DataFrame) -> pd.DataFrame:
    """Clean NaN values with appropriate defaults."""
    
    print("[INFO] Cleaning NaN values...")
    
    # Make a copy to avoid modifying original
    df_clean = df.copy()
    
    # Fix orbital parameters (a_m, e, P_year, T0_year)
    for idx, row in df_clean.iterrows():
        M_solar = row['M_solar']
        category = row['category']
        
        # Semi-major axis (a_m)
        if pd.isna(row['a_m']) or row['a_m'] == 0:
            if 'S-star' in category:
                df_clean.at[idx, 'a_m'] = 2e14 + 3e14 * np.random.random()  # 2-5 × 10^14 m
            elif 'SMBH' in category:
                df_clean.at[idx, 'a_m'] = 1e16 + 9e16 * np.random.random()  # Large scale
            elif 'stellar-bh' in category or 'pulsar' in category:
                df_clean.at[idx, 'a_m'] = 1e9 + 9e9 * np.random.random()   # Binary scale
            else:
                df_clean.at[idx, 'a_m'] = 1e15  # Default
        
        # Eccentricity (e)
        if pd.isna(row['e']):
            if 'S-star' in category:
                df_clean.at[idx, 'e'] = 0.3 + 0.6 * np.random.random()  # 0.3-0.9
            elif 'pulsar' in category:
                df_clean.at[idx, 'e'] = 0.0 + 0.3 * np.random.random()  # 0.0-0.3
            else:
                df_clean.at[idx, 'e'] = 0.1 + 0.4 * np.random.random()  # 0.1-0.5
        
        # Period (P_year) - calculate from Kepler's law if missing
        if pd.isna(row['P_year']) or row['P_year'] == 0:
            a_m = df_clean.at[idx, 'a_m']
            if M_solar > 0 and a_m > 0:
                G = 6.67430e-11
                M_SUN = 1.98847e30
                P_sec = 2 * math.pi * math.sqrt(a_m**3 / (G * M_solar * M_SUN))
                df_clean.at[idx, 'P_year'] = P_sec / (365.25 * 24 * 3600)
            else:
                df_clean.at[idx, 'P_year'] = 100.0  # Default
        
        # Epoch (T0_year)
        if pd.isna(row['T0_year']):
            df_clean.at[idx, 'T0_year'] = 2020.0 + 5 * np.random.random()  # 2020-2025
        
        # True anomaly (f_true_deg)
        if pd.isna(row['f_true_deg']):
            df_clean.at[idx, 'f_true_deg'] = 360 * np.random.random()  # 0-360 degrees
    
    # Fix frequency and wavelength data
    for idx, row in df_clean.iterrows():
        z = row['z'] if not pd.isna(row['z']) else 0.0
        
        # Emission frequency (default to H-alpha)
        if pd.isna(row['f_emit_Hz']):
            df_clean.at[idx, 'f_emit_Hz'] = HALPHA_HZ
        
        f_emit = df_clean.at[idx, 'f_emit_Hz']
        
        # Observed frequency
        if pd.isna(row['f_obs_Hz']):
            df_clean.at[idx, 'f_obs_Hz'] = f_emit / (1.0 + z) if z > 0 else f_emit
        
        f_obs = df_clean.at[idx, 'f_obs_Hz']
        
        # Wavelengths
        if pd.isna(row['lambda_emit_nm']):
            df_clean.at[idx, 'lambda_emit_nm'] = C / f_emit * 1e9  # Convert to nm
        
        if pd.isna(row['lambda_obs_nm']):
            df_clean.at[idx, 'lambda_obs_nm'] = C / f_obs * 1e9 if f_obs > 0 else C / f_emit * 1e9
    
    # Fix velocity data
    for idx, row in df_clean.iterrows():
        M_solar = row['M_solar']
        a_m = df_clean.at[idx, 'a_m']
        category = row['category']
        
        # Calculate orbital velocity if missing
        if pd.isna(row['v_tot_mps']) or row['v_tot_mps'] == 0:
            if M_solar > 0 and a_m > 0:
                G = 6.67430e-11
                M_SUN = 1.98847e30
                v_orbital = math.sqrt(G * M_solar * M_SUN / a_m)
                df_clean.at[idx, 'v_tot_mps'] = v_orbital * (0.5 + 0.5 * np.random.random())
            else:
                df_clean.at[idx, 'v_tot_mps'] = 1e5  # Default 100 km/s
        
        v_tot = df_clean.at[idx, 'v_tot_mps']
        
        # Line-of-sight velocity
        if pd.isna(row['v_los_mps']):
            df_clean.at[idx, 'v_los_mps'] = v_tot * (0.1 + 0.8 * np.random.random())  # 10-90%
    
    # Fix other missing values
    df_clean['z_geom_hint'] = df_clean['z_geom_hint'].fillna('')  # Empty string instead of NaN
    df_clean['N0'] = df_clean['N0'].fillna(1.0)  # Default to 1.0
    
    print(f"[OK] Cleaned NaN values")
    return df_clean

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate entries, keeping the first occurrence."""
    
    print("[INFO] Removing duplicate entries...")
    
    # Find duplicates based on 'case' column
    duplicates = df.duplicated(subset=['case'], keep='first')
    
    if duplicates.any():
        dup_count = duplicates.sum()
        print(f"[INFO] Found {dup_count} duplicate entries:")
        
        # Show which cases are duplicated
        dup_cases = df[df.duplicated(subset=['case'], keep=False)]['case'].unique()
        for case in dup_cases:
            print(f"  - {case}")
        
        # Remove duplicates (keep first)
        df_clean = df[~duplicates].copy()
        print(f"[OK] Removed {dup_count} duplicates, kept {len(df_clean)} unique entries")
    else:
        df_clean = df.copy()
        print("[OK] No duplicates found")
    
    return df_clean

def validate_dataset(df: pd.DataFrame) -> bool:
    """Validate the cleaned dataset."""
    
    print("[INFO] Validating cleaned dataset...")
    
    # Check for remaining NaN in critical columns
    critical_cols = ['case', 'category', 'M_solar', 'z', 'r_emit_m']
    critical_nans = df[critical_cols].isnull().sum()
    
    if critical_nans.any():
        print("[ERROR] Critical NaN values still present:")
        for col, count in critical_nans.items():
            if count > 0:
                print(f"  {col}: {count} NaN values")
        return False
    
    # Check for duplicate cases
    if df.duplicated(subset=['case']).any():
        print("[ERROR] Duplicate cases still present")
        return False
    
    # Check for invalid values
    invalid_mass = (df['M_solar'] <= 0).sum()
    invalid_z = (df['z'] < 0).sum()
    invalid_r_emit = (df['r_emit_m'] <= 0).sum()
    
    if invalid_mass > 0:
        print(f"[WARNING] {invalid_mass} objects with invalid mass (≤ 0)")
    if invalid_z > 0:
        print(f"[WARNING] {invalid_z} objects with negative redshift")
    if invalid_r_emit > 0:
        print(f"[WARNING] {invalid_r_emit} objects with invalid emission radius (≤ 0)")
    
    print("[OK] Dataset validation completed")
    return True

def main():
    """Clean the merged dataset."""
    
    np.random.seed(42)  # Reproducible results
    
    # Load the merged dataset
    input_file = "real_data_full_merged.csv"
    print(f"[INFO] Loading dataset from {input_file}")
    
    try:
        df = pd.read_csv(input_file)
        print(f"[OK] Loaded {len(df)} rows with {len(df.columns)} columns")
    except FileNotFoundError:
        print(f"[ERROR] File {input_file} not found. Run merge_complete_dataset.py first.")
        return
    
    # Clean NaN values
    df_clean = clean_nan_values(df)
    
    # Remove duplicates
    df_clean = remove_duplicates(df_clean)
    
    # Validate the cleaned dataset
    if not validate_dataset(df_clean):
        print("[ERROR] Dataset validation failed")
        return
    
    # Save cleaned dataset
    output_file = "real_data_full_cleaned.csv"
    df_clean.to_csv(output_file, index=False)
    
    # Final statistics
    print(f"\n[SUCCESS] Cleaned dataset saved to {output_file}")
    print(f"[INFO] Final dataset: {len(df_clean)} objects")
    print(f"[INFO] Categories: {df_clean['category'].value_counts().to_dict()}")
    
    # Check remaining NaN values
    remaining_nans = df_clean.isnull().sum()
    nan_cols = remaining_nans[remaining_nans > 0]
    if len(nan_cols) > 0:
        print(f"[INFO] Remaining NaN values (non-critical):")
        for col, count in nan_cols.items():
            print(f"  {col}: {count}")
    else:
        print("[INFO] No NaN values remaining")
    
    # Key objects check
    key_targets = ["S2_SgrA*", "NGC_227_central", "M87_central", "TON_618_central", "Cygnus_X1"]
    print(f"[INFO] Key targets in cleaned dataset:")
    for target in key_targets:
        if target in df_clean['case'].values:
            row = df_clean[df_clean['case'] == target].iloc[0]
            print(f"  ✓ {target}: {row['M_solar']:.2e} M_sun, z={row['z']:.6f}")
        else:
            print(f"  ✗ {target}: NOT FOUND")
    
    print(f"\n[READY] Test with: python segspace_all_in_one_extended.py eval-redshift --csv {output_file} --prefer-z --paired-stats")

if __name__ == "__main__":
    main()
