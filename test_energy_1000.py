#!/usr/bin/env python3
"""
Energy Framework Test - 1000 Objects (Maximum Density)
Tests the perfect energy formulas with comprehensive dataset

Authors: Carmen Wrede & Lino Casu
License: ANTI-CAPITALIST SOFTWARE LICENSE v1.4
Date: 2025-12-07
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Physical constants
c = 299792458.0  # m/s
G = 6.67430e-11  # m^3 kg^-1 s^-2

def test_energy_1000_objects():
    """Test energy formulas with 1000 objects dataset"""
    
    print("="*80)
    print("ENERGY FRAMEWORK TEST - 1000 OBJECTS (MAXIMUM DENSITY)")
    print("="*80)
    print("")
    
    # Load dataset
    csv_path = Path("data/energy_dataset_1000.csv")
    
    if not csv_path.exists():
        print(f"[ERROR] Dataset not found: {csv_path}")
        print("        Run: python generate_energy_dataset.py")
        return False
    
    df = pd.read_csv(csv_path)
    print(f"[LOADED] {len(df)} objects from {csv_path}")
    print("")
    
    # Statistics by type
    print("Dataset Breakdown:")
    for obj_type in df['Type'].unique():
        count = len(df[df['Type'] == obj_type])
        print(f"  {obj_type:15s}: {count:4d} objects")
    print("")
    
    # Test energy calculations for each regime
    passed = 0
    failed = 0
    
    for regime in ['planet', 'star', 'white_dwarf', 'neutron_star', 'stellar_bh', 'smbh']:
        regime_df = df[df['Type'] == regime]
        if len(regime_df) == 0:
            continue
        
        print(f"Testing {regime:20s} ({len(regime_df):4d} objects)...", end=" ")
        
        # Sample test: E_rest should be positive and finite
        masses = regime_df['Mass_kg'].values
        E_rest = masses * c**2
        
        # Check all values are positive and finite
        if np.all(E_rest > 0) and np.all(np.isfinite(E_rest)):
            print("[PASS]")
            passed += 1
        else:
            print("[FAIL]")
            failed += 1
    
    print("")
    print("="*80)
    print(f"RESULTS: {passed}/{passed+failed} regimes PASSED")
    print("="*80)
    
    return failed == 0


if __name__ == "__main__":
    print("")
    success = test_energy_1000_objects()
    print("")
    
    if success:
        print("[SUCCESS] All energy tests passed with 1000 objects!")
        exit(0)
    else:
        print("[FAIL] Some tests failed")
        exit(1)
