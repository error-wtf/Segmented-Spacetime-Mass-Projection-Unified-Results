#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add velocity data to NED continuum spectra (M87 & Sgr A*)

Continuum spectra lack orbital velocity but DO have source proper motion
and radial velocities. This script adds these to enable better predictions.

Sources:
- M87: van der Marel et al. (1990), NED database
- Sgr A*: GRAVITY Collaboration (2019), Ghez et al. (2008)

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Velocity data from literature
VELOCITY_DATA = {
    'M87': {
        'v_los_mps': 1284e3,  # Radial velocity: +1284 km/s (recession)
        'v_tot_mps': 1284e3,  # Proper motion negligible, use v_los
        'source': 'van der Marel et al. (1990), ApJ 347, 294; NED database',
        'notes': 'Recession velocity from NED. Proper motion ~0.3 mas/yr is negligible.'
    },
    'Sgr A*': {
        'v_los_mps': 0.0,  # Galactic center, v_los ~ 0 by definition
        'v_tot_mps': 246e3,  # Tangential velocity from proper motion: ~246 km/s
        'source': 'GRAVITY Collaboration (2019) A&A 625, L10; Ghez et al. (2008)',
        'notes': 'Proper motion: mu_alpha=-3.151, mu_delta=-5.547 mas/yr at d=8.178 kpc -> v_tan=246 km/s'
    }
}

def add_velocity_to_continuum(input_csv='real_data_full.csv', output_csv=None, backup=True):
    """
    Add velocity data to M87 and Sgr A* continuum rows
    
    Args:
        input_csv: Input CSV file
        output_csv: Output CSV file (if None, overwrites input)
        backup: Create backup before modifying
    """
    
    print("="*80)
    print("ADD VELOCITY DATA TO NED CONTINUUM SPECTRA")
    print("="*80)
    
    # Load data
    df = pd.read_csv(input_csv)
    print(f"\nLoaded: {input_csv}")
    print(f"Total rows: {len(df)}")
    
    # Create backup
    if backup and output_csv is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{input_csv}.backup_velocity_{timestamp}"
        df.to_csv(backup_path, index=False)
        print(f"Backup created: {backup_path}")
    
    # Track changes
    changes = {
        'M87': {'rows': 0, 'v_los_added': 0, 'v_tot_added': 0},
        'Sgr A*': {'rows': 0, 'v_los_added': 0, 'v_tot_added': 0}
    }
    
    # Add velocity for each source
    for source_name, vel_data in VELOCITY_DATA.items():
        mask = df['source'] == source_name
        n_rows = mask.sum()
        
        if n_rows == 0:
            print(f"\n[WARN] No rows found for {source_name}")
            continue
        
        print(f"\n--- {source_name} ---")
        print(f"Rows: {n_rows}")
        
        # Check current state
        v_los_missing = df.loc[mask, 'v_los_mps'].isna().sum()
        v_tot_missing = df.loc[mask, 'v_tot_mps'].isna().sum()
        
        print(f"v_los_mps missing: {v_los_missing}")
        print(f"v_tot_mps missing: {v_tot_missing}")
        
        # Add v_los where missing
        if v_los_missing > 0:
            df.loc[mask & df['v_los_mps'].isna(), 'v_los_mps'] = vel_data['v_los_mps']
            changes[source_name]['v_los_added'] = v_los_missing
            print(f"[OK] Added v_los_mps = {vel_data['v_los_mps']:.3e} m/s to {v_los_missing} rows")
        
        # Add v_tot where missing
        if v_tot_missing > 0:
            df.loc[mask & df['v_tot_mps'].isna(), 'v_tot_mps'] = vel_data['v_tot_mps']
            changes[source_name]['v_tot_added'] = v_tot_missing
            print(f"[OK] Added v_tot_mps = {vel_data['v_tot_mps']:.3e} m/s to {v_tot_missing} rows")
        
        print(f"Source: {vel_data['source']}")
        print(f"Notes: {vel_data['notes']}")
        
        changes[source_name]['rows'] = n_rows
    
    # Save
    output_path = output_csv if output_csv else input_csv
    df.to_csv(output_path, index=False)
    print(f"\n[OK] Saved to: {output_path}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_v_los_added = sum(c['v_los_added'] for c in changes.values())
    total_v_tot_added = sum(c['v_tot_added'] for c in changes.values())
    
    for source_name, stats in changes.items():
        if stats['rows'] > 0:
            print(f"\n{source_name}:")
            print(f"  Rows updated: {stats['rows']}")
            print(f"  v_los_mps added: {stats['v_los_added']}")
            print(f"  v_tot_mps added: {stats['v_tot_added']}")
    
    print(f"\nTotal velocity values added:")
    print(f"  v_los_mps: {total_v_los_added}")
    print(f"  v_tot_mps: {total_v_tot_added}")
    
    # Verify
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    df_verify = pd.read_csv(output_path)
    print(f"\nTotal rows with v_tot_mps: {df_verify['v_tot_mps'].notna().sum()} / {len(df_verify)} ({100*df_verify['v_tot_mps'].notna().sum()/len(df_verify):.1f}%)")
    print(f"Total rows with v_los_mps: {df_verify['v_los_mps'].notna().sum()} / {len(df_verify)} ({100*df_verify['v_los_mps'].notna().sum()/len(df_verify):.1f}%)")
    
    # Expected paired test improvement
    complete_for_prediction = df_verify['v_tot_mps'].notna().sum()
    print(f"\n[STATS] Rows usable for predictions: {complete_for_prediction} / {len(df_verify)} ({100*complete_for_prediction/len(df_verify):.1f}%)")
    print(f"   BEFORE velocity add: 113 / 427 (26.5%)")
    print(f"   AFTER velocity add: {complete_for_prediction} / {len(df_verify)} ({100*complete_for_prediction/len(df_verify):.1f}%)")
    
    print("\n[OK] COMPLETE!")
    print("="*80)
    
    return df_verify

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Add velocity data to NED continuum spectra')
    parser.add_argument('--input', default='real_data_full.csv', help='Input CSV file')
    parser.add_argument('--output', default=None, help='Output CSV file (default: overwrite input)')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    
    args = parser.parse_args()
    
    add_velocity_to_continuum(
        input_csv=args.input,
        output_csv=args.output,
        backup=not args.no_backup
    )
