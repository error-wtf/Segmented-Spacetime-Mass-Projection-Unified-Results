#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stratified Paired Test - Separate analysis by field strength and velocity

Tests hypothesis: SEG wins in strong field + high velocity, 
gets diluted by photon sphere region (r=2-3 r_s, low v)
"""
import pandas as pd
import numpy as np
import subprocess
import json
from pathlib import Path
from scipy import stats

print("="*80)
print("STRATIFIED PAIRED TEST ANALYSIS")
print("="*80)

# Load data
df = pd.read_csv('data/real_data_emission_lines.csv')

# Calculate field strength
G = 6.67430e-11
c = 2.99792458e8
M_sun_kg = 1.989e30

df['M_kg'] = df['M_solar'] * M_sun_kg
df['r_s'] = 2 * G * df['M_kg'] / (c**2)
df['r_over_rs'] = df['r_emit_m'] / df['r_s']
df['v_over_c'] = df['v_tot_mps'] / c if 'v_tot_mps' in df.columns else 0

print(f"\nTotal dataset: {len(df)} observations")

# Define strata
photon_sphere = (df['r_over_rs'] >= 2) & (df['r_over_rs'] <= 3) & (df['v_over_c'] < 0.01)
strong_high_v = (df['r_over_rs'] < 2) | ((df['r_over_rs'] < 3) & (df['v_over_c'] >= 0.05))
weak_field = df['r_over_rs'] > 10

print("\nStrata definition:")
print(f"  Photon sphere (2 < r/rs < 3, v < 1%c): {photon_sphere.sum()} obs")
print(f"  Strong field + high v (r < 2 OR v > 5%c): {strong_high_v.sum()} obs")
print(f"  Weak field (r > 10 rs): {weak_field.sum()} obs")
print(f"  Other: {len(df) - photon_sphere.sum() - strong_high_v.sum() - weak_field.sum()} obs")

# Function to run paired test on subset
def run_paired_test(data_subset, label):
    """Run paired test on a data subset"""
    print(f"\n{'='*80}")
    print(f"PAIRED TEST: {label}")
    print(f"{'='*80}")
    
    if len(data_subset) == 0:
        print("  No data in this stratum")
        return None
    
    print(f"  Sample size: {len(data_subset)}")
    
    # Save subset to temp file
    temp_file = Path('temp_subset.csv')
    data_subset.to_csv(temp_file, index=False)
    
    # Run paired test
    cmd = [
        'python', 'segspace_all_in_one_extended.py',
        '--outdir', 'agent_out_temp',
        'eval-redshift',
        '--csv', str(temp_file),
        '--paired-stats',
        '--mode', 'hybrid'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              encoding='utf-8', errors='replace', timeout=60)
        
        # Read results
        result_file = Path('agent_out_temp/reports/redshift_paired_stats.json')
        if result_file.exists():
            with open(result_file) as f:
                stats_data = json.load(f)
            
            n_pairs = stats_data.get('N_pairs', 0)
            n_seg_better = stats_data.get('N_Seg_better', 0)
            share = stats_data.get('share_Seg_better', 0)
            p_value = stats_data.get('binom_two_sided_p', 1.0)
            
            print(f"  SEG wins: {n_seg_better}/{n_pairs} ({share*100:.1f}%)")
            print(f"  p-value: {p_value:.4f}")
            
            if p_value < 0.05:
                print(f"  [SIGNIFICANT] (p < 0.05)")
            elif p_value < 0.10:
                print(f"  [Marginally significant] (p < 0.10)")
            else:
                print(f"  [Not significant] (p >= 0.10)")
            
            # Cleanup
            temp_file.unlink(missing_ok=True)
            
            return {
                'n_pairs': n_pairs,
                'n_seg_better': n_seg_better,
                'share': share,
                'p_value': p_value,
                'label': label
            }
        else:
            print("  [ERROR] Could not read results")
            temp_file.unlink(missing_ok=True)
            return None
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        temp_file.unlink(missing_ok=True)
        return None

# Run stratified tests
results = []

# 1. Full dataset (baseline)
result = run_paired_test(df, "FULL DATASET (baseline)")
if result:
    results.append(result)

# 2. Photon sphere region (the problematic 46%)
result = run_paired_test(df[photon_sphere], "PHOTON SPHERE (2 < r/rs < 3, v < 1%c)")
if result:
    results.append(result)

# 3. WITHOUT photon sphere
result = run_paired_test(df[~photon_sphere], "WITHOUT PHOTON SPHERE")
if result:
    results.append(result)

# 4. Strong field + high velocity
result = run_paired_test(df[strong_high_v], "STRONG FIELD + HIGH VELOCITY")
if result:
    results.append(result)

# 5. Weak field
result = run_paired_test(df[weak_field], "WEAK FIELD (r > 10 rs)")
if result:
    results.append(result)

# 6. Very close (r < 2 rs)
very_close = df[df['r_over_rs'] < 2]
result = run_paired_test(very_close, "VERY CLOSE (r < 2 rs)")
if result:
    results.append(result)

# 7. High velocity (v > 5% c)
if 'v_over_c' in df.columns:
    high_v = df[df['v_over_c'] >= 0.05]
    result = run_paired_test(high_v, "HIGH VELOCITY (v > 5%c)")
    if result:
        results.append(result)

# Summary
print(f"\n{'='*80}")
print("SUMMARY OF STRATIFIED RESULTS")
print(f"{'='*80}\n")

if results:
    summary_df = pd.DataFrame(results)
    print(summary_df.to_string(index=False))
    
    print(f"\n{'='*80}")
    print("KEY INSIGHTS")
    print(f"{'='*80}\n")
    
    # Find best and worst strata
    best = summary_df.loc[summary_df['share'].idxmax()]
    worst = summary_df.loc[summary_df['share'].idxmin()]
    
    print(f"Best performance: {best['label']}")
    print(f"  SEG wins: {best['n_seg_better']}/{best['n_pairs']} ({best['share']*100:.1f}%)")
    print(f"  p-value: {best['p_value']:.4f}")
    
    print(f"\nWorst performance: {worst['label']}")
    print(f"  SEG wins: {worst['n_seg_better']}/{worst['n_pairs']} ({worst['share']*100:.1f}%)")
    print(f"  p-value: {worst['p_value']:.4f}")
    
    print(f"\n{'='*80}")
    print("HYPOTHESIS TEST")
    print(f"{'='*80}\n")
    
    print("HYPOTHESIS: Removing photon sphere region improves SEG performance")
    
    full_result = next((r for r in results if r['label'] == "FULL DATASET (baseline)"), None)
    without_ps = next((r for r in results if r['label'] == "WITHOUT PHOTON SPHERE"), None)
    
    if full_result and without_ps:
        print(f"\nFull dataset:          {full_result['share']*100:.1f}% (p={full_result['p_value']:.4f})")
        print(f"Without photon sphere: {without_ps['share']*100:.1f}% (p={without_ps['p_value']:.4f})")
        
        improvement = (without_ps['share'] - full_result['share']) * 100
        print(f"\nImprovement: {improvement:+.1f} percentage points")
        
        if without_ps['p_value'] < full_result['p_value']:
            print("[OK] p-value improved (more significant without photon sphere)")
        else:
            print("[NOTE] p-value did not improve")
    
print("\n" + "="*80)
print("Analysis complete!")
print("="*80)
