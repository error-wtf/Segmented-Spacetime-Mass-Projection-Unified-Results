#!/usr/bin/env python3
"""
Analyze the ONE missing win in Strong Field regime
Find exactly which object is failing and why
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Load data
csv_file = Path("data") / "real_data_emission_lines_clean.csv"
df = pd.read_csv(csv_file)

print("="*80)
print("ANALYZING THE MISSING WIN")
print("="*80)
print(f"\nTotal objects: {len(df)}")

# Physical constants
C = 299792458  # m/s
G = 6.67430e-11
M_SUN = 1.98847e30

# Classify by regime
def classify_regime(r_m, M_msun, v_mps=None):
    r_s = 2 * G * M_msun * M_SUN / (C**2)
    x = r_m / r_s
    
    if x < 1.5:
        regime = "Very Close"
    elif 1.5 <= x < 2.0:
        regime = "Near Horizon"
    elif 2.0 <= x <= 3.0:
        regime = "Photon Sphere"
    elif 3.0 < x <= 10.0:
        regime = "Strong Field"
    else:
        regime = "Weak Field"
    
    # High velocity bonus
    if v_mps is not None and abs(v_mps) > 0.05 * C:
        regime += " + High Velocity"
    
    return regime, x

# Add regime classification
regimes = []
x_values = []

for idx, row in df.iterrows():
    r_m = row.get('r_m', np.nan)
    M_msun = row.get('M_msun', np.nan)
    v_tot = row.get('v_tot_mps', np.nan)
    
    if pd.notna(r_m) and pd.notna(M_msun):
        regime, x = classify_regime(r_m, M_msun, v_tot if pd.notna(v_tot) else None)
        regimes.append(regime)
        x_values.append(x)
    else:
        regimes.append("Unknown")
        x_values.append(np.nan)

df['regime'] = regimes
df['x_rs'] = x_values

# Count by regime
print("\nREGIME BREAKDOWN:")
print("-"*80)
regime_counts = df['regime'].value_counts()
for regime, count in regime_counts.items():
    print(f"  {regime}: {count}")

# Show Strong Field objects specifically
print("\n" + "="*80)
print("STRONG FIELD OBJECTS (r = 3-10 r_s)")
print("="*80)

strong_field = df[df['regime'] == 'Strong Field'].copy()
print(f"\nTotal Strong Field objects: {len(strong_field)}")
print(f"Expected: 35/36 wins (one failure)")

# Show key parameters for strong field
if len(strong_field) > 0:
    print("\nKEY PARAMETERS:")
    print("-"*80)
    cols_to_show = ['object_name', 'x_rs', 'M_msun', 'v_los_mps', 'v_tot_mps', 'z_obs']
    available_cols = [c for c in cols_to_show if c in strong_field.columns]
    
    # Sort by x (radius)
    strong_field_sorted = strong_field.sort_values('x_rs')
    
    for idx, row in strong_field_sorted.iterrows():
        obj_name = row.get('object_name', f'Object {idx}')
        x = row.get('x_rs', np.nan)
        M = row.get('M_msun', np.nan)
        v_los = row.get('v_los_mps', np.nan)
        v_tot = row.get('v_tot_mps', np.nan)
        z_obs = row.get('z_obs', np.nan)
        
        print(f"\n{obj_name}:")
        print(f"  x = {x:.3f} r_s")
        print(f"  M = {M:.2e} M_sun")
        print(f"  v_los = {v_los:.1f} m/s" if pd.notna(v_los) else "  v_los = N/A")
        print(f"  v_tot = {v_tot:.1f} m/s" if pd.notna(v_tot) else "  v_tot = N/A")
        print(f"  z_obs = {z_obs:.6f}" if pd.notna(z_obs) else "  z_obs = N/A")

print("\n" + "="*80)
print("To find the exact failing object, need to run perfect_paired_test.py")
print("and check which Strong Field object has SEG error > GR error")
print("="*80)
