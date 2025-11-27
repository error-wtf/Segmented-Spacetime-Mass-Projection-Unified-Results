#!/usr/bin/env python3
"""
Modified perfect_paired_test to show DETAILED per-object results
Identify the exact failing object and analyze why
"""
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

import numpy as np
import pandas as pd
from pathlib import Path

# Import the original functions from perfect_paired_test
C = 299792458
G = 6.67430e-11
PHI = (1 + 5**0.5) / 2
M_SUN = 1.98847e30

# Simplified regime classification
def classify_regime_simple(r_m, M_msun, v_mps=None):
    r_s = 2 * G * M_msun * M_SUN / (C**2)
    x = r_m / r_s
    
    if 2.0 <= x <= 3.0:
        regime = "Photon Sphere"
    elif 3.0 < x <= 10.0:
        regime = "Strong Field"
    else:
        regime = "Other"
    
    if v_mps is not None and abs(v_mps) > 0.05 * C:
        regime += " + High Velocity"
    
    return regime, x

# Load data
csv_file = Path("data") / "real_data_emission_lines_clean.csv"
df = pd.read_csv(csv_file)

print("="*80)
print("DETAILED PER-OBJECT ANALYSIS")
print("="*80)

# We need to convert the data format
# M_solar → M_msun, r_emit_m → r_m
results = []

for idx, row in df.iterrows():
    case = row.get('case', f'Object_{idx}')
    M_solar = row.get('M_solar', np.nan)
    r_emit_m = row.get('r_emit_m', np.nan)
    z_obs = row.get('z', np.nan)
    v_los_mps = row.get('v_los_mps', 0)
    v_tot_mps = row.get('v_tot_mps', None)
    z_geom_hint = row.get('z_geom_hint', None)
    
    if pd.isna(M_solar) or pd.isna(r_emit_m) or pd.isna(z_obs):
        continue
    
    M_msun = M_solar
    r_m = r_emit_m
    M_kg = M_msun * M_SUN
    r_s = 2 * G * M_kg / (C**2)
    x = r_m / r_s
    
    # Classify regime
    v_tot = v_tot_mps if pd.notna(v_tot_mps) else None
    regime, x_val = classify_regime_simple(r_m, M_msun, v_tot)
    
    # Classical GR
    if x > 1.0:
        z_gr_grav = 1.0 / np.sqrt(1 - 1.0/x) - 1.0
    else:
        z_gr_grav = np.nan
    
    # SR component (if velocity available)
    if v_tot is not None and v_tot > 0:
        beta_tot = min(abs(v_tot) / C, 0.999999)
        beta_los = v_los_mps / C
        gamma = 1.0 / np.sqrt(1.0 - beta_tot**2)
        z_sr = gamma * (1.0 + beta_los) - 1.0
    else:
        z_sr = 0.0
    
    # Combined GR×SR
    z_grsr = (1.0 + z_gr_grav) * (1.0 + z_sr) - 1.0
    
    # SEG (using z_geom_hint if available, else GR)
    if z_geom_hint is not None and not pd.isna(z_geom_hint):
        z_seg_grav = z_geom_hint
    else:
        z_seg_grav = z_gr_grav
    
    z_seg = (1.0 + z_seg_grav) * (1.0 + z_sr) - 1.0
    
    # Errors
    error_gr = abs(z_grsr - z_obs)
    error_seg = abs(z_seg - z_obs)
    
    # Winner
    winner = "SEG" if error_seg < error_gr else "GR"
    
    results.append({
        'case': case,
        'regime': regime,
        'x': x_val,
        'M_msun': M_msun,
        'r_m': r_m,
        'v_tot': v_tot if v_tot else 0,
        'z_obs': z_obs,
        'z_grsr': z_grsr,
        'z_seg': z_seg,
        'error_gr': error_gr,
        'error_seg': error_seg,
        'winner': winner,
        'margin': error_seg - error_gr
    })

results_df = pd.DataFrame(results)

# Analyze by regime
print("\n" + "="*80)
print("PHOTON SPHERE (2-3 r_s):")
print("="*80)
photon = results_df[results_df['regime'].str.contains('Photon Sphere', na=False)]
print(f"Total: {len(photon)}")
seg_wins_photon = (photon['winner'] == 'SEG').sum()
print(f"SEG wins: {seg_wins_photon}/{len(photon)} ({100*seg_wins_photon/len(photon) if len(photon) > 0 else 0:.1f}%)")

print("\n" + "="*80)
print("STRONG FIELD (3-10 r_s):")
print("="*80)
strong = results_df[results_df['regime'].str.contains('Strong Field', na=False)]
print(f"Total: {len(strong)}")
seg_wins_strong = (strong['winner'] == 'SEG').sum()
print(f"SEG wins: {seg_wins_strong}/{len(strong)} ({100*seg_wins_strong/len(strong) if len(strong) > 0 else 0:.1f}%)")

# Show failures
failures_strong = strong[strong['winner'] == 'GR']
if len(failures_strong) > 0:
    print("\n" + "-"*80)
    print("FAILING OBJECTS (GR WINS):")
    print("-"*80)
    for idx, row in failures_strong.iterrows():
        print(f"\n{row['case']}:")
        print(f"  x = {row['x']:.4f} r_s")
        print(f"  M = {row['M_msun']:.3e} M_sun")
        print(f"  v_tot = {row['v_tot']:.1f} m/s")
        print(f"  z_obs = {row['z_obs']:.8f}")
        print(f"  z_GR×SR = {row['z_grsr']:.8f} (error: {row['error_gr']:.8e})")
        print(f"  z_SEG   = {row['z_seg']:.8f} (error: {row['error_seg']:.8e})")
        print(f"  Margin: SEG worse by {row['margin']:.8e}")

# Overall
print("\n" + "="*80)
print("OVERALL:")
print("="*80)
total_wins = (results_df['winner'] == 'SEG').sum()
print(f"SEG wins: {total_wins}/{len(results_df)} ({100*total_wins/len(results_df):.1f}%)")

# Save
results_df.to_csv('detailed_results.csv', index=False)
print(f"\nDetailed results saved to: detailed_results.csv")
print("="*80)
