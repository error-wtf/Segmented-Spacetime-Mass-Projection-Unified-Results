#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fill Missing Columns in real_data_full.csv

Fills critical NaN values with calculated/derived values to ensure
all tests can run without data quality warnings.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io
from datetime import datetime

# UTF-8 Setup for Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
C_LIGHT = 299792458.0  # m/s
G = 6.67430e-11  # m³/(kg·s²)
M_SUN = 1.98847e30  # kg

def calculate_n_round(M_solar, r_emit_m):
    """
    Calculate segment count n_round
    
    Based on SSZ theory: n_round = φ-lattice structure around mass
    """
    if pd.isna(M_solar) or pd.isna(r_emit_m):
        return np.nan
    
    if r_emit_m <= 0 or M_solar <= 0:
        return np.nan
    
    # Schwarzschild radius
    r_s = 2 * G * (M_solar * M_SUN) / (C_LIGHT ** 2)
    
    # Segment count based on φ-lattice
    # n_round ~ (r / r_s)^(1/φ) for r > r_s
    if r_emit_m > r_s:
        n = (r_emit_m / r_s) ** (1 / PHI)
        return np.round(n)
    else:
        # Inside horizon: fixed segments
        return 1.0

def calculate_redshift_from_frequencies(f_emit, f_obs):
    """Calculate redshift from frequency shift"""
    if pd.isna(f_emit) or pd.isna(f_obs):
        return np.nan
    
    if f_obs <= 0:
        return np.nan
    
    return (f_emit - f_obs) / f_obs

def calculate_redshift_from_velocity(v_los_mps):
    """Calculate redshift from line-of-sight velocity (non-relativistic)"""
    if pd.isna(v_los_mps):
        return np.nan
    
    return v_los_mps / C_LIGHT

def fill_f_obs_from_z(f_emit, z):
    """Calculate f_obs from f_emit and z"""
    if pd.isna(f_emit) or pd.isna(z):
        return np.nan
    
    return f_emit / (1 + z)

def main():
    """Main data cleaning function"""
    
    print("="*80)
    print("FILL MISSING COLUMNS IN real_data_full.csv")
    print("="*80)
    
    # Load data
    csv_path = Path("real_data_full.csv")
    if not csv_path.exists():
        print(f"❌ ERROR: {csv_path} not found!")
        sys.exit(1)
    
    # Create backup
    backup_path = csv_path.with_suffix(f'.backup_{datetime.now():%Y%m%d_%H%M%S}.csv')
    print(f"\n📁 Creating backup: {backup_path}")
    import shutil
    shutil.copy(csv_path, backup_path)
    
    # Load data
    df = pd.read_csv(csv_path)
    print(f"\n📊 Loaded {len(df)} rows")
    
    # Initial NaN count
    initial_nan = df.isnull().sum().sum()
    print(f"   Initial NaN count: {initial_nan}")
    
    # Track changes
    changes = {}
    
    # 1. Fill n_round (CRITICAL for SSZ!)
    if 'n_round' in df.columns:
        nan_before = df['n_round'].isna().sum()
        if nan_before > 0:
            print(f"\n🔧 Filling n_round ({nan_before} NaN)...")
            
            for idx, row in df.iterrows():
                if pd.isna(row['n_round']):
                    n = calculate_n_round(row['M_solar'], row['r_emit_m'])
                    if not pd.isna(n):
                        df.at[idx, 'n_round'] = n
            
            nan_after = df['n_round'].isna().sum()
            filled = nan_before - nan_after
            changes['n_round'] = filled
            print(f"   ✓ Filled {filled} values")
    
    # 2. Fill z from frequencies (if both available)
    if 'z' in df.columns and 'f_emit_Hz' in df.columns and 'f_obs_Hz' in df.columns:
        nan_before = df['z'].isna().sum()
        if nan_before > 0:
            print(f"\n🔧 Filling z from frequencies ({nan_before} NaN)...")
            
            for idx, row in df.iterrows():
                if pd.isna(row['z']) and not pd.isna(row['f_emit_Hz']) and not pd.isna(row['f_obs_Hz']):
                    z = calculate_redshift_from_frequencies(row['f_emit_Hz'], row['f_obs_Hz'])
                    if not pd.isna(z):
                        df.at[idx, 'z'] = z
            
            nan_after = df['z'].isna().sum()
            filled = nan_before - nan_after
            changes['z_from_freq'] = filled
            print(f"   ✓ Filled {filled} values")
    
    # 3. Fill f_obs_Hz from z and f_emit (if z available)
    if 'f_obs_Hz' in df.columns and 'f_emit_Hz' in df.columns and 'z' in df.columns:
        nan_before = df['f_obs_Hz'].isna().sum()
        if nan_before > 0:
            print(f"\n🔧 Filling f_obs_Hz from z ({nan_before} NaN)...")
            
            for idx, row in df.iterrows():
                if pd.isna(row['f_obs_Hz']) and not pd.isna(row['f_emit_Hz']) and not pd.isna(row['z']):
                    f_obs = fill_f_obs_from_z(row['f_emit_Hz'], row['z'])
                    if not pd.isna(f_obs):
                        df.at[idx, 'f_obs_Hz'] = f_obs
            
            nan_after = df['f_obs_Hz'].isna().sum()
            filled = nan_before - nan_after
            changes['f_obs_Hz'] = filled
            print(f"   ✓ Filled {filled} values")
    
    # 4. Fill z from v_los (if frequency-based z failed)
    if 'z' in df.columns and 'v_los_mps' in df.columns:
        nan_before = df['z'].isna().sum()
        if nan_before > 0:
            print(f"\n🔧 Filling remaining z from v_los ({nan_before} NaN)...")
            
            for idx, row in df.iterrows():
                if pd.isna(row['z']) and not pd.isna(row['v_los_mps']):
                    z = calculate_redshift_from_velocity(row['v_los_mps'])
                    if not pd.isna(z):
                        df.at[idx, 'z'] = z
            
            nan_after = df['z'].isna().sum()
            filled = nan_before - nan_after
            changes['z_from_vlos'] = filled
            print(f"   ✓ Filled {filled} values")
    
    # Final NaN count
    final_nan = df.isnull().sum().sum()
    total_filled = initial_nan - final_nan
    
    # Save cleaned data
    print(f"\n💾 Saving cleaned data to {csv_path}...")
    df.to_csv(csv_path, index=False)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Initial NaN count: {initial_nan}")
    print(f"Final NaN count:   {final_nan}")
    print(f"Total filled:      {total_filled}")
    print(f"\nChanges by column:")
    for col, count in changes.items():
        print(f"  {col}: {count} values")
    
    # Remaining critical NaN
    critical_cols = ['f_emit_Hz', 'f_obs_Hz', 'r_emit_m', 'M_solar', 'n_round']
    print(f"\nRemaining NaN in critical columns:")
    for col in critical_cols:
        if col in df.columns:
            nan_count = df[col].isna().sum()
            status = "✅" if nan_count == 0 else "⚠️"
            print(f"  {status} {col}: {nan_count}")
    
    print(f"\n📁 Backup saved to: {backup_path}")
    print(f"✅ Cleaned data saved to: {csv_path}")
    print("="*80)

if __name__ == '__main__':
    main()
