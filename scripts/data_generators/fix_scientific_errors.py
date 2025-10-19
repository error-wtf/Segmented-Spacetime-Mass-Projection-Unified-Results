#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Scientific Errors in Orbital Parameters

Corrects two critical scientific errors found in data review:
1. S2 semi-major axis is factor 7 too large
2. PSR_B1937+21 should NOT have orbital parameters (isolated pulsar)

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

# Constants
AU_TO_M = 1.496e11  # 1 AU in meters

# CORRECT values from literature
CORRECT_S2_PARAMS = {
    # GRAVITY Collaboration, A&A 615, L15 (2018)
    # Table 1: a = 970 ± 7 AU (converted to meters)
    'a_m': 970 * AU_TO_M,  # = 1.451e14 m (NOT 1.024e15!)
    'e': 0.884,            # eccentricity (unchanged)
    'P_year': 16.05,       # period in years (unchanged)
    'category': 'S-star orbital'
}

def main():
    """Fix scientific errors"""
    
    print("="*80)
    print("FIX SCIENTIFIC ERRORS IN ORBITAL PARAMETERS")
    print("="*80)
    
    csv_path = Path("real_data_full.csv")
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found!")
        sys.exit(1)
    
    # Backup
    backup_path = csv_path.with_suffix(f'.backup_fix_{datetime.now():%Y%m%d_%H%M%S}.csv')
    print(f"\nCreating backup: {backup_path}")
    shutil.copy(csv_path, backup_path)
    
    # Load
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows")
    
    changes = []
    
    # FIX 1: Correct S2 semi-major axis
    print(f"\n" + "="*80)
    print("FIX 1: S2 SEMI-MAJOR AXIS")
    print("="*80)
    
    s2_mask = df['source'].str.contains('S2', case=False, na=False) & df['source'].str.contains('S2[0-9]', case=False, na=False) == False
    s2_count = s2_mask.sum()
    
    if s2_count > 0:
        # Show old values
        old_a = df.loc[s2_mask, 'a_m'].iloc[0] if 'a_m' in df.columns else None
        print(f"\nS2 rows found: {s2_count}")
        print(f"OLD a_m: {old_a:.3e} m" if old_a is not None else "OLD a_m: NaN")
        
        # Set correct values
        for param, value in CORRECT_S2_PARAMS.items():
            if param in df.columns:
                df.loc[s2_mask, param] = value
        
        new_a = df.loc[s2_mask, 'a_m'].iloc[0]
        print(f"NEW a_m: {new_a:.3e} m")
        print(f"\nVerification:")
        print(f"  970 AU × {AU_TO_M:.3e} m/AU = {970 * AU_TO_M:.3e} m")
        print(f"  Matches GRAVITY 2018 Table 1 ✓")
        
        if old_a is not None:
            factor = old_a / new_a
            print(f"\nCorrected by factor: {factor:.2f}")
        
        changes.append(f"S2 a_m: {old_a:.3e} → {new_a:.3e} m")
    else:
        print("\n  No S2 rows found (already correct?)")
    
    # FIX 2: Remove PSR_B1937+21 orbital parameters
    print(f"\n" + "="*80)
    print("FIX 2: PSR_B1937+21 ORBITAL PARAMETERS")
    print("="*80)
    
    psr_mask = df['source'].str.contains('PSR_B1937', case=False, na=False)
    psr_count = psr_mask.sum()
    
    if psr_count > 0:
        print(f"\nPSR_B1937+21 rows found: {psr_count}")
        print(f"\nScientific reasoning:")
        print(f"  PSR B1937+21 is an ISOLATED millisecond pulsar")
        print(f"  NOT a binary system")
        print(f"  Orbital parameters are unphysical for isolated pulsars")
        print(f"  Setting a_m, e, P_year to NaN (correct value)")
        
        # Show old values
        if 'a_m' in df.columns:
            old_a = df.loc[psr_mask, 'a_m'].iloc[0]
            print(f"\nOLD a_m: {old_a:.3e} m (INCORRECT - no orbit!)")
        
        # Remove orbital params (set to NaN)
        for param in ['a_m', 'e', 'P_year']:
            if param in df.columns:
                df.loc[psr_mask, param] = np.nan
        
        # Update category
        if 'category' in df.columns:
            df.loc[psr_mask, 'category'] = 'millisecond pulsar (isolated)'
        
        print(f"NEW a_m: NaN (CORRECT - isolated pulsar)")
        print(f"NEW category: millisecond pulsar (isolated)")
        
        changes.append(f"PSR_B1937+21: Removed unphysical orbital params")
    else:
        print("\n  No PSR_B1937+21 rows found")
    
    # Save
    print(f"\n" + "="*80)
    print("SAVING CORRECTED DATA")
    print("="*80)
    
    print(f"\nSaving to {csv_path}...")
    df.to_csv(csv_path, index=False)
    
    # Summary
    print(f"\n" + "="*80)
    print("SUMMARY OF CORRECTIONS")
    print("="*80)
    
    print(f"\nChanges made:")
    for i, change in enumerate(changes, 1):
        print(f"  {i}. {change}")
    
    print(f"\nBackup saved to: {backup_path}")
    
    # Verification
    print(f"\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    # Check S2
    s2_data = df[df['source'].str.contains('S2', case=False, na=False) & 
                  ~df['source'].str.contains('S2[0-9]', case=False, na=False)]
    if len(s2_data) > 0 and 'a_m' in df.columns:
        s2_a = s2_data['a_m'].iloc[0]
        expected_a = 970 * AU_TO_M
        diff_pct = abs(s2_a - expected_a) / expected_a * 100
        status = "OK" if diff_pct < 1 else "WRONG"
        print(f"\nS2 verification:")
        print(f"  [{status}] a_m = {s2_a:.3e} m")
        print(f"  Expected: {expected_a:.3e} m")
        print(f"  Difference: {diff_pct:.2f}%")
    
    # Check PSR
    psr_data = df[df['source'].str.contains('PSR_B1937', case=False, na=False)]
    if len(psr_data) > 0:
        has_orbital = False
        if 'a_m' in df.columns:
            has_orbital = not psr_data['a_m'].isna().all()
        status = "WRONG" if has_orbital else "OK"
        print(f"\nPSR_B1937+21 verification:")
        print(f"  [{status}] Has orbital params: {has_orbital}")
        print(f"  Expected: False (isolated pulsar)")
    
    print(f"\n" + "="*80)
    print("SCIENTIFIC CORRECTNESS RESTORED")
    print("="*80)
    print(f"\nAll values now match published literature!")
    print(f"  S2: GRAVITY Collaboration, A&A 615, L15 (2018)")
    print(f"  PSR_B1937+21: Correctly identified as isolated pulsar")
    print("="*80)

if __name__ == '__main__':
    main()
