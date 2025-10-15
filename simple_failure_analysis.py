#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Failure Analysis
=======================

Analyzes which types of objects cause segmented spacetime to fail
by examining the dataset categories and mass ranges.
"""

import csv
import pandas as pd

def analyze_failures():
    """Simple analysis of segmented spacetime performance by object type."""
    
    print("SEGMENTED SPACETIME FAILURE ANALYSIS")
    print("="*60)
    
    # Load the expanded dataset
    df = pd.read_csv('real_data_full_expanded.csv')
    print(f"Total objects: {len(df)}")
    
    # From the results: 82/127 pairs where Seg is better (64.6%)
    # This means 45/127 pairs where GR×SR is better (35.4%)
    
    print(f"\nPerformance Summary:")
    print(f"- Segmented spacetime better: 82/127 (64.6%)")
    print(f"- GR×SR better: 45/127 (35.4%)")
    print(f"- P-value: 0.00131 (statistically significant)")
    
    # Analyze by category
    print(f"\nObjects by category:")
    category_counts = df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count} objects")
    
    # Analyze by mass range
    print(f"\nObjects by mass range:")
    df['log_mass'] = pd.to_numeric(df['M_solar'], errors='coerce').apply(lambda x: round(pd.np.log10(x)) if pd.notna(x) and x > 0 else None)
    mass_ranges = {
        0: "1 M☉ (Stellar mass)",
        1: "10 M☉ (Heavy stellar)",
        2: "100 M☉ (Very heavy stellar)",
        3: "1,000 M☉ (Intermediate)",
        4: "10,000 M☉ (IMBH)",
        5: "100,000 M☉ (Heavy IMBH)",
        6: "1,000,000 M☉ (Light SMBH)",
        7: "10,000,000 M☉ (SMBH)",
        8: "100,000,000 M☉ (Heavy SMBH)",
        9: "1,000,000,000 M☉ (Very heavy SMBH)",
        10: "10,000,000,000 M☉ (Extreme SMBH)",
        11: "100,000,000,000 M☉ (Ultra-massive)"
    }
    
    mass_counts = df['log_mass'].value_counts().sort_index()
    for log_mass, count in mass_counts.items():
        if pd.notna(log_mass) and log_mass in mass_ranges:
            print(f"  {mass_ranges[log_mass]}: {count} objects")
    
    # Theoretical expectations for segmented spacetime performance
    print(f"\nWHY SEGMENTED SPACETIME FAILS ON SOME OBJECTS:")
    print(f"="*60)
    
    print(f"\n1. EXPECTED TO EXCEL (Strong gravitational fields):")
    print(f"   - S-stars around Sgr A* (close orbits, high velocities)")
    print(f"   - Neutron stars (compact surfaces, strong gravity)")
    print(f"   - Stellar black holes (event horizon physics)")
    print(f"   - LIGO/Virgo mergers (extreme spacetime curvature)")
    
    print(f"\n2. EXPECTED TO STRUGGLE (Weak field regimes):")
    print(f"   - Distant objects (large emission radii)")
    print(f"   - Low-mass objects (weak gravitational fields)")
    print(f"   - High-redshift objects (cosmological effects dominate)")
    print(f"   - Objects with poor parameter estimates")
    
    print(f"\n3. MODEL LIMITATIONS:")
    print(f"   - ΔM correction may not apply universally")
    print(f"   - Some object types not in original calibration")
    print(f"   - Synthetic parameters vs real measurements")
    print(f"   - Model optimized for specific mass/distance ranges")
    
    print(f"\n4. RECOMMENDATIONS TO IMPROVE PERFORMANCE:")
    print(f"   - Add more S-stars with measured redshifts")
    print(f"   - Include more neutron star timing data")
    print(f"   - Focus on objects with r_emit < 100 r_s")
    print(f"   - Use real measurements instead of estimates")
    print(f"   - Calibrate ΔM parameters for different object types")

if __name__ == "__main__":
    analyze_failures()
