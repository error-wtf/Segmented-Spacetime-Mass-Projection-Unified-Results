#!/usr/bin/env python3
"""
Identify the EXACT failing object and propose solutions
Run perfect_paired_test logic but output detailed per-object results
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Physical constants
C = 299792458
G = 6.67430e-11
M_SUN = 1.98847e30
PHI = (1 + 5**0.5) / 2

# Load data
csv_file = Path("data") / "real_data_emission_lines_clean.csv"
df = pd.read_csv(csv_file)

print("="*80)
print("FINDING THE FAILING OBJECT(S)")
print("="*80)
print(f"\nTotal objects: {len(df)}")

# Simplified classification
def classify_regime(r_m, M_kg):
    r_s = 2 * G * M_kg / (C**2)
    x = r_m / r_s
    
    if 2.0 <= x <= 3.0:
        return "Photon Sphere", x
    elif 3.0 < x <= 10.0:
        return "Strong Field", x
    else:
        return "Other", x

# Simplified SEG vs GR comparison (using classical GR for baseline)
results = []

for idx, row in df.iterrows():
    case = row.get('case', f'Object_{idx}')
    M_solar = row.get('M_solar', np.nan)
    r_emit_m = row.get('r_emit_m', np.nan)
    z_obs = row.get('z', np.nan)
    z_geom_hint = row.get('z_geom_hint', None)
    
    if pd.isna(M_solar) or pd.isna(r_emit_m) or pd.isna(z_obs):
        continue
    
    M_kg = M_solar * M_SUN
    r_s = 2 * G * M_kg / (C**2)
    x = r_emit_m / r_s
    
    regime, x_val = classify_regime(r_emit_m, M_kg)
    
    # Classical GR redshift
    if x > 1.0:
        z_gr = 1.0 / np.sqrt(1 - 1.0/x) - 1.0
    else:
        z_gr = np.nan
    
    # SEG redshift (simplified - just using z_geom_hint if available)
    if z_geom_hint is not None and not pd.isna(z_geom_hint):
        z_seg = z_geom_hint
    else:
        z_seg = z_gr  # Fallback
    
    # Errors
    error_gr = abs(z_gr - z_obs) if not np.isnan(z_gr) else np.nan
    error_seg = abs(z_seg - z_obs) if not np.isnan(z_seg) else np.nan
    
    # Winner
    if not np.isnan(error_gr) and not np.isnan(error_seg):
        winner = "SEG" if error_seg < error_gr else "GR"
    else:
        winner = "N/A"
    
    results.append({
        'case': case,
        'regime': regime,
        'x': x_val,
        'M_solar': M_solar,
        'z_obs': z_obs,
        'z_gr': z_gr,
        'z_seg': z_seg,
        'error_gr': error_gr,
        'error_seg': error_seg,
        'winner': winner
    })

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Filter by regime
print("\n" + "="*80)
print("PHOTON SPHERE RESULTS:")
print("="*80)
photon_sphere = results_df[results_df['regime'] == 'Photon Sphere']
print(f"\nTotal: {len(photon_sphere)}")
print(f"SEG wins: {(photon_sphere['winner'] == 'SEG').sum()}")
print(f"GR wins: {(photon_sphere['winner'] == 'GR').sum()}")

print("\n" + "="*80)
print("STRONG FIELD RESULTS:")
print("="*80)
strong_field = results_df[results_df['regime'] == 'Strong Field']
print(f"\nTotal: {len(strong_field)}")
print(f"SEG wins: {(strong_field['winner'] == 'SEG').sum()}")
print(f"GR wins: {(strong_field['winner'] == 'GR').sum()}")

# Show GR wins in Strong Field (these are the failures!)
gr_wins_strong = strong_field[strong_field['winner'] == 'GR']
if len(gr_wins_strong) > 0:
    print("\n" + "-"*80)
    print("OBJECTS WHERE GR WINS (FAILURES):")
    print("-"*80)
    for idx, row in gr_wins_strong.iterrows():
        print(f"\n{row['case']}:")
        print(f"  Regime: {row['regime']}")
        print(f"  x = {row['x']:.3f} r_s")
        print(f"  M = {row['M_solar']:.2e} M_sun")
        print(f"  z_obs = {row['z_obs']:.6f}")
        print(f"  z_GR = {row['z_gr']:.6f} (error: {row['error_gr']:.6e})")
        print(f"  z_SEG = {row['z_seg']:.6f} (error: {row['error_seg']:.6e})")
        print(f"  Δerror = {row['error_seg'] - row['error_gr']:.6e} (SEG worse by this much)")

# Save results for further analysis
results_df.to_csv('analysis_results.csv', index=False)
print("\n" + "="*80)
print("Results saved to: analysis_results.csv")
print("="*80)
