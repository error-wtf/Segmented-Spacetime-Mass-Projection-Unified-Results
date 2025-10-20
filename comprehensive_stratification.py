#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Stratification Analysis - 3 Dimensions

Performs paired test with THREE stratification dimensions:
1. By radius (photon sphere, very close, weak field, etc.)
2. By data type (NED vs non-NED sources  
3. By completeness (100% complete data vs partial data)

This provides the COMPLETE picture of where SEG works and where it doesn't.
"""
import pandas as pd
import numpy as np
import subprocess
import json
from pathlib import Path

print("="*80)
print("COMPREHENSIVE STRATIFICATION ANALYSIS - 3 DIMENSIONS")
print("="*80)
print()

# Load data
data_file = Path("data/real_data_emission_lines.csv")
if not data_file.exists():
    print(f"ERROR: {data_file} not found!")
    exit(1)

df = pd.read_csv(data_file)
print(f"Loaded {len(df)} emission-line observations")
print()

# Calculate field parameters
G = 6.67430e-11
c = 2.99792458e8
M_sun_kg = 1.989e30

df['M_kg'] = df['M_solar'] * M_sun_kg
df['r_s'] = 2 * G * df['M_kg'] / (c**2)
df['r_over_rs'] = df['r_emit_m'] / df['r_s']

# Check completeness
required_cols = ['M_solar', 'r_emit_m', 'v_tot_mps', 'z']
df['complete'] = df[required_cols].notna().all(axis=1)

# Identify NED-origin objects
ned_keywords = ['M87', 'NGC', 'Sgr', 'SgrA', 'Cygnus', 'Centaurus']
df['is_ned'] = df['case'].astype(str).str.contains('|'.join(ned_keywords), case=False, na=False)

def paired_test(subset_df, name):
    """Perform paired test on subset"""
    valid = subset_df.dropna(subset=['abs_seg', 'abs_grsr'])
    n = len(valid)
    seg_wins = valid['seg_better'].sum()
    
    if n == 0:
        return None
    
    win_pct = (seg_wins / n) * 100
    
    # Binomial test
    if n > 0:
        p_value = stats.binom_test(seg_wins, n, 0.5, alternative='two-sided')
    else:
        p_value = 1.0
    
    return {
        'name': name,
        'n': n,
        'seg_wins': seg_wins,
        'win_pct': win_pct,
        'p_value': p_value,
        'significant': p_value < 0.05
    }

print("="*80)
print("DIMENSION 1: STRATIFICATION BY RADIUS")
print("="*80)
print()

radius_strata = {
    'Very Close (r<2)': df[df['r_over_rs'] < 2],
    'Photon Sphere (r=2-3)': df[(df['r_over_rs'] >= 2) & (df['r_over_rs'] < 3)],
    'Moderate (r=3-5)': df[(df['r_over_rs'] >= 3) & (df['r_over_rs'] < 5)],
    'Intermediate (r=5-10)': df[(df['r_over_rs'] >= 5) & (df['r_over_rs'] < 10)],
    'Weak Field (r>=10)': df[df['r_over_rs'] >= 10],
    'FULL DATASET': df
}

radius_results = []
for name, subset in radius_strata.items():
    result = paired_test(subset, name)
    if result:
        radius_results.append(result)
        sig = "YES (p<0.05)" if result['significant'] else "No (p>=0.05)"
        print(f"{name:25} | n={result['n']:3d} | SEG wins: {result['seg_wins']:3d}/{result['n']:3d} ({result['win_pct']:5.1f}%) | p={result['p_value']:.4f} | Sig: {sig}")

print()
print("="*80)
print("DIMENSION 2: STRATIFICATION BY DATA SOURCE")
print("="*80)
print()

# Identify NED sources (continuum originally from NED)
# For emission lines, we check object names that might be from NED
ned_keywords = ['M87', 'NGC', 'Sgr', 'SgrA', 'Cygnus', 'Centaurus']
df['is_ned_origin'] = df['object'].str.contains('|'.join(ned_keywords), case=False, na=False)

source_strata = {
    'NED-origin objects': df[df['is_ned_origin'] == True],
    'Non-NED objects': df[df['is_ned_origin'] == False],
    'FULL DATASET': df
}

source_results = []
for name, subset in source_strata.items():
    result = paired_test(subset, name)
    if result:
        source_results.append(result)
        sig = "YES (p<0.05)" if result['significant'] else "No (p>=0.05)"
        print(f"{name:25} | n={result['n']:3d} | SEG wins: {result['seg_wins']:3d}/{result['n']:3d} ({result['win_pct']:5.1f}%) | p={result['p_value']:.4f} | Sig: {sig}")

print()
print("="*80)
print("DIMENSION 3: STRATIFICATION BY DATA COMPLETENESS")
print("="*80)
print()

# Check completeness
required_cols = ['M_solar', 'r_emit_m', 'v_tot_mps', 'z', 'abs_seg', 'abs_grsr']
df['complete'] = df[required_cols].notna().all(axis=1)

completeness_strata = {
    '100% Complete Data': df[df['complete'] == True],
    'Partial Data': df[df['complete'] == False],
    'FULL DATASET': df
}

completeness_results = []
for name, subset in completeness_strata.items():
    result = paired_test(subset, name)
    if result:
        completeness_results.append(result)
        sig = "YES (p<0.05)" if result['significant'] else "No (p>=0.05)"
        print(f"{name:25} | n={result['n']:3d} | SEG wins: {result['seg_wins']:3d}/{result['n']:3d} ({result['win_pct']:5.1f}%) | p={result['p_value']:.4f} | Sig: {sig}")

print()
print("="*80)
print("CROSS-STRATIFICATION: Radius × Completeness")
print("="*80)
print()

# Most important: Photon sphere with complete data
photon_sphere = df[(df['r_over_rs'] >= 2) & (df['r_over_rs'] < 3)]
ps_complete = photon_sphere[photon_sphere['complete'] == True]
ps_result = paired_test(ps_complete, "Photon Sphere + 100% Complete")
if ps_result:
    sig = "YES (p<0.05)" if ps_result['significant'] else "No (p>=0.05)"
    print(f"Photon Sphere (100% complete): n={ps_result['n']:3d} | SEG wins: {ps_result['seg_wins']:3d}/{ps_result['n']:3d} ({ps_result['win_pct']:5.1f}%) | p={ps_result['p_value']:.4f} | Sig: {sig}")

# Very close with complete data
very_close = df[df['r_over_rs'] < 2]
vc_complete = very_close[very_close['complete'] == True]
vc_result = paired_test(vc_complete, "Very Close + 100% Complete")
if vc_result:
    sig = "YES (p<0.05)" if vc_result['significant'] else "No (p>=0.05)"
    print(f"Very Close (100% complete):   n={vc_result['n']:3d} | SEG wins: {vc_result['seg_wins']:3d}/{vc_result['n']:3d} ({vc_result['win_pct']:5.1f}%) | p={vc_result['p_value']:.4f} | Sig: {sig}")

print()
print("="*80)
print("SUMMARY REPORT")
print("="*80)
print()

# Save results
results = {
    'radius': radius_results,
    'source': source_results,
    'completeness': completeness_results,
    'cross_stratification': {
        'photon_sphere_complete': ps_result,
        'very_close_complete': vc_result
    }
}

output_file = Path("reports/comprehensive_stratification_results.json")
output_file.parent.mkdir(exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {output_file}")
print()

print("KEY FINDINGS:")
print()
print("1. RADIUS STRATIFICATION:")
for r in radius_results:
    if r['name'] != 'FULL DATASET':
        status = "DOMINATES" if r['win_pct'] > 70 else "FAILS" if r['win_pct'] < 30 else "COMPARABLE"
        print(f"   {r['name']:25} → {status:12} ({r['win_pct']:5.1f}% wins, p={r['p_value']:.4f})")

print()
print("2. DATA SOURCE:")
for r in source_results:
    if r['name'] != 'FULL DATASET':
        status = "BETTER" if r['win_pct'] > 55 else "WORSE" if r['win_pct'] < 45 else "COMPARABLE"
        print(f"   {r['name']:25} → {status:12} ({r['win_pct']:5.1f}% wins)")

print()
print("3. COMPLETENESS:")
for r in completeness_results:
    if r['name'] != 'FULL DATASET':
        status = "BETTER" if r['win_pct'] > 55 else "WORSE" if r['win_pct'] < 45 else "COMPARABLE"
        print(f"   {r['name']:25} → {status:12} ({r['win_pct']:5.1f}% wins)")

print()
print("="*80)
print("Analysis complete!")
print("="*80)
