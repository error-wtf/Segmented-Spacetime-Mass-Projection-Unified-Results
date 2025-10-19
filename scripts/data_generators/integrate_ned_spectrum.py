#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrate NED Spectrum Data into real_data_full.csv

Takes NED-fetched spectrum CSVs and adds them to real_data_full.csv
WITHOUT creating NaN columns. All values calculated from NED data.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io
from datetime import datetime
import shutil

# UTF-8 Setup
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Physical constants
c = 299792458.0  # m/s
G = 6.67430e-11  # m^3/(kg s^2)
M_sun = 1.98847e30  # kg
phi = 1.6180339887  # golden ratio

# Known redshifts
REDSHIFTS = {
    'M87': 0.0042,
    'M87*': 0.0042,
    'Sgr A*': 0.0,  # Local, negligible cosmological z
    'SgrA*': 0.0
}

def calculate_n_round(r_m, M_solar):
    """Calculate segment count from r and M using φ-theory"""
    M_kg = M_solar * M_sun
    r_s = 2 * G * M_kg / (c**2)
    r_phi = (phi / 2) * r_s
    
    # n = (r / r_phi)^(1/phi)
    if r_m > 0 and r_phi > 0:
        n = (r_m / r_phi) ** (1 / phi)
        return n
    else:
        return np.nan

def integrate_ned_data(ned_csv, existing_csv, output_csv):
    """
    Integrate NED spectrum data into existing real_data_full.csv
    
    Parameters:
        ned_csv: Path to NED spectrum CSV
        existing_csv: Path to existing real_data_full.csv
        output_csv: Path to output CSV
    """
    
    print("="*80)
    print("INTEGRATE NED SPECTRUM DATA")
    print("="*80)
    
    # Load existing data
    print(f"\nLoading existing data: {existing_csv}")
    df_existing = pd.read_csv(existing_csv)
    print(f"  Existing rows: {len(df_existing)}")
    
    # Load NED data
    print(f"\nLoading NED data: {ned_csv}")
    df_ned = pd.read_csv(ned_csv)
    print(f"  NED rows: {len(df_ned)}")
    
    # Get source name and redshift
    source_name = df_ned['source'].iloc[0]
    z = REDSHIFTS.get(source_name, 0.0)
    print(f"  Source: {source_name}")
    print(f"  Redshift z: {z}")
    
    # Build new rows matching existing column structure
    print(f"\nBuilding new rows...")
    new_rows = []
    
    for idx, row in df_ned.iterrows():
        # Extract NED values
        f_obs_Hz = row['frequency_Hz']
        flux_Jy = row['flux_density_Jy']
        flux_err_Jy = row['flux_error_Jy']
        M_solar = row['M_solar']
        r_emit_m = row['r_emit_m']
        instrument = row['instrument']
        
        # Calculate derived values
        f_emit_Hz = f_obs_Hz * (1 + z)  # Correct for cosmological redshift
        n_round = calculate_n_round(r_emit_m, M_solar)
        
        # Create case name
        case = f"NED {instrument} {f_obs_Hz:.2e} Hz"
        
        # Build row matching existing columns
        new_row = {
            'source': source_name,
            'case': case,
            'f_emit_Hz': f_emit_Hz,
            'f_obs_Hz': f_obs_Hz,
            'r_emit_m': r_emit_m,
            'M_solar': M_solar,
            'n_round': n_round,
            'z': z
        }
        
        # Add optional columns if they exist in existing data
        for col in df_existing.columns:
            if col not in new_row:
                # Set to NaN for columns not in NED data
                # (e.g., orbital parameters, velocity, etc.)
                new_row[col] = np.nan
        
        new_rows.append(new_row)
    
    # Create DataFrame for new rows
    df_new = pd.DataFrame(new_rows)
    
    # Ensure column order matches existing
    df_new = df_new[df_existing.columns]
    
    print(f"  Created {len(df_new)} new rows")
    
    # Verify critical columns are filled
    critical_cols = ['source', 'f_emit_Hz', 'f_obs_Hz', 'r_emit_m', 'M_solar', 'n_round', 'z']
    print(f"\nVerifying critical columns...")
    for col in critical_cols:
        non_null = df_new[col].notna().sum()
        pct = non_null / len(df_new) * 100
        status = "✓" if pct == 100 else "✗"
        print(f"  [{status}] {col}: {non_null}/{len(df_new)} ({pct:.1f}%)")
    
    # Concatenate
    print(f"\nMerging data...")
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    print(f"  Total rows: {len(df_combined)} ({len(df_existing)} existing + {len(df_new)} new)")
    
    # Save
    print(f"\nSaving to: {output_csv}")
    df_combined.to_csv(output_csv, index=False)
    
    return df_combined

def main():
    """Main integration workflow"""
    
    print("="*80)
    print("NED SPECTRUM DATA INTEGRATION")
    print("="*80)
    
    # Paths
    existing_csv = Path("real_data_full.csv")
    ned_m87_csv = Path("data/observations/m87_ned_spectrum.csv")
    ned_sgra_csv = Path("data/observations/sgra_ned_spectrum.csv")
    
    # Backup
    backup_path = existing_csv.with_suffix(f'.backup_ned_{datetime.now():%Y%m%d_%H%M%S}.csv')
    print(f"\nCreating backup: {backup_path}")
    shutil.copy(existing_csv, backup_path)
    
    # Check which NED files exist
    sources_to_add = []
    if ned_m87_csv.exists():
        sources_to_add.append(('M87', ned_m87_csv))
        print(f"✓ Found: {ned_m87_csv}")
    if ned_sgra_csv.exists():
        sources_to_add.append(('Sgr A*', ned_sgra_csv))
        print(f"✓ Found: {ned_sgra_csv}")
    
    if not sources_to_add:
        print("\n⚠️  No NED spectrum files found!")
        print("   Run fetch scripts first:")
        print("   python scripts/data_acquisition/fetch_m87_spectrum.py")
        sys.exit(1)
    
    # Integrate each source
    current_csv = existing_csv
    for i, (source_name, ned_csv) in enumerate(sources_to_add):
        print(f"\n{'='*80}")
        print(f"INTEGRATING SOURCE {i+1}/{len(sources_to_add)}: {source_name}")
        print(f"{'='*80}")
        
        # For first integration, use existing file
        # For subsequent, use the output from previous
        input_csv = current_csv if i == 0 else Path(f"temp_integrated_{i-1}.csv")
        output_csv = existing_csv if i == len(sources_to_add) - 1 else Path(f"temp_integrated_{i}.csv")
        
        df = integrate_ned_data(ned_csv, input_csv, output_csv)
        current_csv = output_csv
    
    # Clean up temp files
    for i in range(len(sources_to_add) - 1):
        temp_file = Path(f"temp_integrated_{i}.csv")
        if temp_file.exists():
            temp_file.unlink()
    
    # Final summary
    print(f"\n{'='*80}")
    print("INTEGRATION COMPLETE")
    print(f"{'='*80}")
    
    df_final = pd.read_csv(existing_csv)
    
    print(f"\nFinal dataset:")
    print(f"  Total rows: {len(df_final)}")
    print(f"  Sources: {df_final['source'].nunique()}")
    
    # Check for NaN in critical columns
    critical_cols = ['source', 'f_emit_Hz', 'f_obs_Hz', 'r_emit_m', 'M_solar', 'n_round', 'z']
    print(f"\nCritical columns status:")
    for col in critical_cols:
        non_null = df_final[col].notna().sum()
        pct = non_null / len(df_final) * 100
        status = "✓" if pct == 100 else "⚠️"
        print(f"  [{status}] {col}: {non_null}/{len(df_final)} ({pct:.1f}%)")
    
    print(f"\nBackup: {backup_path}")
    print(f"Output: {existing_csv}")
    
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print(f"\n1. Run tests to verify:")
    print(f"   python -m pytest scripts/tests/test_horizon_hawking_predictions.py -v")
    print(f"\n2. If tests pass, commit:")
    print(f"   git add real_data_full.csv")
    print(f"   git commit -m \"Add {sum(len(pd.read_csv(csv)) for _, csv in sources_to_add)} NED spectrum points\"")
    
    print("="*80)

if __name__ == '__main__':
    main()
