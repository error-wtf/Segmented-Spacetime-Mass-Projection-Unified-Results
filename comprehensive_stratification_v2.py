#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Stratification Analysis - 3 Dimensions

Performs paired test with THREE stratification dimensions:
1. By radius (photon sphere, very close, moderate, weak field)
2. By data type (NED-origin vs non-NED objects)
3. By completeness (100% complete vs partial data)

Uses segspace_all_in_one_extended.py for each stratified subset.
"""
import pandas as pd
import subprocess
import json
from pathlib import Path

print("="*80)
print("COMPREHENSIVE STRATIFICATION ANALYSIS - 3 DIMENSIONS")
print("="*80)
print()

# Load data
df = pd.read_csv('data/real_data_emission_lines.csv')

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

print(f"Total dataset: {len(df)} observations")
print(f"Complete data: {df['complete'].sum()} ({df['complete'].sum()/len(df)*100:.1f}%)")
print(f"NED-origin: {df['is_ned'].sum()} ({df['is_ned'].sum()/len(df)*100:.1f}%)")
print()

def run_paired_test(subset_df, label, outdir='agent_out_strat'):
    """Run paired test on a subset"""
    if len(subset_df) == 0:
        return None
    
    # Save subset to temp file
    temp_file = Path('temp_stratified_subset.csv')
    subset_df.to_csv(temp_file, index=False)
    
    # Run paired test
    cmd = [
        'python', 'segspace_all_in_one_extended.py',
        '--outdir', outdir,
        'eval-redshift',
        '--csv', str(temp_file),
        '--paired-stats',
        '--mode', 'hybrid'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              encoding='utf-8', errors='replace', timeout=60)
        
        # Read results
        result_file = Path(f'{outdir}/reports/redshift_paired_stats.json')
        if result_file.exists():
            with open(result_file) as f:
                stats_data = json.load(f)
            
            n_pairs = stats_data.get('N_pairs', 0)
            n_seg_better = stats_data.get('N_Seg_better', 0)
            share = stats_data.get('share_Seg_better', 0)
            p_value = stats_data.get('binom_two_sided_p', 1.0)
            
            temp_file.unlink(missing_ok=True)
            
            return {
                'label': label,
                'n': n_pairs,
                'seg_wins': n_seg_better,
                'win_pct': share * 100,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
    except Exception as e:
        print(f"  ERROR in {label}: {e}")
        temp_file.unlink(missing_ok=True)
        return None

# ==============================================================================
# DIMENSION 1: BY RADIUS
# ==============================================================================
print("="*80)
print("DIMENSION 1: STRATIFICATION BY RADIUS")
print("="*80)
print()

radius_strata = {
    'Very Close (r<2 r_s)': df[df['r_over_rs'] < 2],
    'Photon Sphere (r=2-3 r_s)': df[(df['r_over_rs'] >= 2) & (df['r_over_rs'] < 3)],
    'Moderate (r=3-5 r_s)': df[(df['r_over_rs'] >= 3) & (df['r_over_rs'] < 5)],
    'Intermediate (r=5-10 r_s)': df[(df['r_over_rs'] >= 5) & (df['r_over_rs'] < 10)],
    'Weak Field (r>=10 r_s)': df[df['r_over_rs'] >= 10],
}

radius_results = []
for name, subset in radius_strata.items():
    print(f"\n{name}: {len(subset)} observations")
    result = run_paired_test(subset, name)
    if result:
        radius_results.append(result)
        sig = "✓ YES" if result['significant'] else "  No"
        print(f"  Result: {result['seg_wins']}/{result['n']} ({result['win_pct']:.1f}%) | p={result['p_value']:.4f} | Sig: {sig}")

# ==============================================================================
# DIMENSION 2: BY DATA SOURCE
# ==============================================================================
print()
print("="*80)
print("DIMENSION 2: STRATIFICATION BY DATA SOURCE")
print("="*80)
print()

source_strata = {
    'NED-origin objects': df[df['is_ned'] == True],
    'Non-NED objects': df[df['is_ned'] == False],
}

source_results = []
for name, subset in source_strata.items():
    print(f"\n{name}: {len(subset)} observations")
    result = run_paired_test(subset, name)
    if result:
        source_results.append(result)
        sig = "✓ YES" if result['significant'] else "  No"
        print(f"  Result: {result['seg_wins']}/{result['n']} ({result['win_pct']:.1f}%) | p={result['p_value']:.4f} | Sig: {sig}")

# ==============================================================================
# DIMENSION 3: BY COMPLETENESS
# ==============================================================================
print()
print("="*80)
print("DIMENSION 3: STRATIFICATION BY DATA COMPLETENESS")
print("="*80)
print()

completeness_strata = {
    '100% Complete Data': df[df['complete'] == True],
    'Partial Data': df[df['complete'] == False],
}

completeness_results = []
for name, subset in completeness_strata.items():
    print(f"\n{name}: {len(subset)} observations")
    result = run_paired_test(subset, name)
    if result:
        completeness_results.append(result)
        sig = "✓ YES" if result['significant'] else "  No"
        print(f"  Result: {result['seg_wins']}/{result['n']} ({result['win_pct']:.1f}%) | p={result['p_value']:.4f} | Sig: {sig}")

# ==============================================================================
# CROSS-STRATIFICATION: Key combinations
# ==============================================================================
print()
print("="*80)
print("CROSS-STRATIFICATION: Key Combinations")
print("="*80)
print()

# Photon sphere + complete
ps_complete = df[(df['r_over_rs'] >= 2) & (df['r_over_rs'] < 3) & (df['complete'] == True)]
print(f"\nPhoton Sphere + 100% Complete: {len(ps_complete)} observations")
ps_result = run_paired_test(ps_complete, "Photon Sphere + Complete")
if ps_result:
    sig = "✓ YES" if ps_result['significant'] else "  No"
    print(f"  Result: {ps_result['seg_wins']}/{ps_result['n']} ({ps_result['win_pct']:.1f}%) | p={ps_result['p_value']:.4f} | Sig: {sig}")

# Very close + complete
vc_complete = df[(df['r_over_rs'] < 2) & (df['complete'] == True)]
print(f"\nVery Close + 100% Complete: {len(vc_complete)} observations")
vc_result = run_paired_test(vc_complete, "Very Close + Complete")
if vc_result:
    sig = "✓ YES" if vc_result['significant'] else "  No"
    print(f"  Result: {vc_result['seg_wins']}/{vc_result['n']} ({vc_result['win_pct']:.1f}%) | p={vc_result['p_value']:.4f} | Sig: {sig}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print()
print("="*80)
print("SUMMARY: COMPREHENSIVE STRATIFICATION RESULTS")
print("="*80)
print()

print("1. BY RADIUS:")
for r in radius_results:
    status = "DOMINATES" if r['win_pct'] > 70 else "FAILS" if r['win_pct'] < 30 else "COMPARABLE"
    print(f"   {r['label']:30} → {status:12} ({r['win_pct']:5.1f}%, p={r['p_value']:.4f})")

print()
print("2. BY DATA SOURCE:")
for r in source_results:
    status = "BETTER" if r['win_pct'] > 55 else "WORSE" if r['win_pct'] < 45 else "COMPARABLE"
    print(f"   {r['label']:30} → {status:12} ({r['win_pct']:5.1f}%, p={r['p_value']:.4f})")

print()
print("3. BY COMPLETENESS:")
for r in completeness_results:
    status = "BETTER" if r['win_pct'] > 55 else "WORSE" if r['win_pct'] < 45 else "COMPARABLE"
    print(f"   {r['label']:30} → {status:12} ({r['win_pct']:5.1f}%, p={r['p_value']:.4f})")

# Save results
all_results = {
    'radius': radius_results,
    'source': source_results,
    'completeness': completeness_results,
    'cross_stratification': {
        'photon_sphere_complete': ps_result,
        'very_close_complete': vc_result
    }
}

output_file = Path('reports/comprehensive_stratification_results.json')
output_file.parent.mkdir(exist_ok=True, parents=True)
with open(output_file, 'w') as f:
    json.dump(all_results, f, indent=2)

print()
print(f"Results saved to: {output_file}")
print()
print("="*80)
print("Analysis complete!")
print("="*80)
