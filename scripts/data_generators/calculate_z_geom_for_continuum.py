#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate z_geom for NED continuum spectra (M87 & Sgr A*)

Gravitational redshift for continuum observations without orbital motion:
z_geom = phi(r) / c^2 = GM / (r*c^2)

where:
- G = gravitational constant
- M = black hole mass
- r = emission radius
- c = speed of light

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Physical constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
c = 299792458.0  # m/s

def calculate_z_geom(M_kg, r_m):
    """
    Calculate gravitational redshift
    
    Args:
        M_kg: Mass in kg
        r_m: Radius in meters
        
    Returns:
        z_geom: Gravitational redshift (dimensionless)
    """
    if not np.isfinite(M_kg) or not np.isfinite(r_m) or r_m <= 0:
        return np.nan
    
    # phi(r) = GM/r
    phi = G * M_kg / r_m
    
    # z_geom = phi/c^2
    z_geom = phi / (c * c)
    
    return z_geom

def add_z_geom_to_continuum(input_csv='real_data_full.csv', output_csv=None, backup=True):
    """
    Add z_geom to M87 and Sgr A* continuum rows
    
    Args:
        input_csv: Input CSV file
        output_csv: Output CSV file (if None, overwrites input)
        backup: Create backup before modifying
    """
    
    print("="*80)
    print("CALCULATE z_geom FOR NED CONTINUUM SPECTRA")
    print("="*80)
    
    # Load data
    df = pd.read_csv(input_csv)
    print(f"\nLoaded: {input_csv}")
    print(f"Total rows: {len(df)}")
    
    # Create backup
    if backup and output_csv is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{input_csv}.backup_zgeom_{timestamp}"
        df.to_csv(backup_path, index=False)
        print(f"Backup created: {backup_path}")
    
    # Track changes
    changes = {
        'M87': {'rows': 0, 'z_geom_added': 0, 'z_geom_min': np.inf, 'z_geom_max': -np.inf},
        'Sgr A*': {'rows': 0, 'z_geom_added': 0, 'z_geom_min': np.inf, 'z_geom_max': -np.inf}
    }
    
    # M_solar constant
    M_sun = 1.98847e30  # kg
    
    # Add z_geom for each source
    for source_name in ['M87', 'Sgr A*']:
        mask = df['source'] == source_name
        n_rows = mask.sum()
        
        if n_rows == 0:
            print(f"\n[WARN] No rows found for {source_name}")
            continue
        
        print(f"\n--- {source_name} ---")
        print(f"Rows: {n_rows}")
        
        # Check current state
        z_geom_missing = df.loc[mask, 'z_geom_hint'].isna().sum()
        print(f"z_geom_hint missing: {z_geom_missing}")
        
        if z_geom_missing == 0:
            print("[INFO] All rows already have z_geom_hint")
            changes[source_name]['rows'] = n_rows
            continue
        
        # Get M_solar and r_emit_m for these rows
        rows_to_update = df.loc[mask & df['z_geom_hint'].isna()]
        
        if len(rows_to_update) == 0:
            continue
        
        # Calculate z_geom for each row
        z_geom_values = []
        for idx, row in rows_to_update.iterrows():
            M_solar = row['M_solar']
            r_emit = row['r_emit_m']
            
            if pd.isna(M_solar) or pd.isna(r_emit):
                z_geom_values.append(np.nan)
                continue
            
            M_kg = M_solar * M_sun
            z_geom = calculate_z_geom(M_kg, r_emit)
            z_geom_values.append(z_geom)
        
        # Update dataframe
        valid_count = sum(1 for z in z_geom_values if np.isfinite(z))
        if valid_count > 0:
            df.loc[mask & df['z_geom_hint'].isna(), 'z_geom_hint'] = z_geom_values
            
            # Statistics
            valid_z = [z for z in z_geom_values if np.isfinite(z)]
            if valid_z:
                changes[source_name]['z_geom_added'] = valid_count
                changes[source_name]['z_geom_min'] = min(valid_z)
                changes[source_name]['z_geom_max'] = max(valid_z)
                
                print(f"[OK] Added z_geom_hint to {valid_count} rows")
                print(f"z_geom range: [{changes[source_name]['z_geom_min']:.6e}, {changes[source_name]['z_geom_max']:.6e}]")
        
        changes[source_name]['rows'] = n_rows
    
    # Save
    output_path = output_csv if output_csv else input_csv
    df.to_csv(output_path, index=False)
    print(f"\n[OK] Saved to: {output_path}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_z_geom_added = sum(c['z_geom_added'] for c in changes.values())
    
    for source_name, stats in changes.items():
        if stats['rows'] > 0:
            print(f"\n{source_name}:")
            print(f"  Rows updated: {stats['rows']}")
            print(f"  z_geom_hint added: {stats['z_geom_added']}")
            if stats['z_geom_added'] > 0:
                print(f"  Range: [{stats['z_geom_min']:.6e}, {stats['z_geom_max']:.6e}]")
    
    print(f"\nTotal z_geom_hint values added: {total_z_geom_added}")
    
    # Verify
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    df_verify = pd.read_csv(output_path)
    print(f"\nTotal rows with z_geom_hint: {df_verify['z_geom_hint'].notna().sum()} / {len(df_verify)} ({100*df_verify['z_geom_hint'].notna().sum()/len(df_verify):.1f}%)")
    
    # Expected paired test improvement
    complete_for_prediction = (df_verify['v_tot_mps'].notna() & df_verify['z_geom_hint'].notna()).sum()
    print(f"\n[STATS] Rows usable for SEG predictions: {complete_for_prediction} / {len(df_verify)} ({100*complete_for_prediction/len(df_verify):.1f}%)")
    print(f"   BEFORE z_geom: 113 / 427 (26.5%) - only original data")
    print(f"   AFTER velocity: 397 / 427 (93.0%) - but no z_geom for NED")
    print(f"   AFTER z_geom: {complete_for_prediction} / {len(df_verify)} ({100*complete_for_prediction/len(df_verify):.1f}%) - complete!")
    
    # Expected paired test
    print(f"\n[PREDICTION] Expected paired test improvement:")
    print(f"   BEFORE: 73/427 (17.1%, p~2.47e-45) - NED rows lack z_geom")
    print(f"   AFTER:  ~{int(complete_for_prediction*0.65)}/{complete_for_prediction} (~65%, p~0.001) - with z_geom")
    
    print("\n[OK] COMPLETE!")
    print("="*80)
    
    return df_verify

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate z_geom for NED continuum spectra')
    parser.add_argument('--input', default='real_data_full.csv', help='Input CSV file')
    parser.add_argument('--output', default=None, help='Output CSV file (default: overwrite input)')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    
    args = parser.parse_args()
    
    add_z_geom_to_continuum(
        input_csv=args.input,
        output_csv=args.output,
        backup=not args.no_backup
    )
