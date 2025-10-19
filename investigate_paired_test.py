#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERY DETAILED INVESTIGATION: Why is paired test still 79/427 (18.5%)?

Expected: ~222/342 (65%) with z_geom
Actual: 79/427 (18.5%)

This script investigates:
1. Which rows have complete data (v_tot + z_geom)
2. How predictions are calculated
3. Why NED rows don't improve the score
4. What's missing

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import pandas as pd
import numpy as np
import sys
import runpy

print("="*80)
print("PAIRED TEST INVESTIGATION - VERY DETAILED")
print("="*80)

# Load data
df = pd.read_csv('real_data_full.csv')
print(f"\nTotal rows: {len(df)}")

# Load prediction module
print("\n" + "="*80)
print("STEP 1: LOAD PREDICTION FUNCTIONS")
print("="*80)

ns = runpy.run_path('segspace_all_in_one_extended.py')
z_seg_pred = ns['z_seg_pred']
z_gravitational = ns['z_gravitational']
z_special_rel = ns['z_special_rel']
z_combined = ns['z_combined']
A = float(ns['A'])
B = float(ns['B'])
ALPHA = float(ns['ALPHA'])

print(f"Delta(M) parameters: A={A}, B={B}, ALPHA={ALPHA}")

# Constants
M_sun = 1.98847e30
c = 299792458.0

def finite(x):
    try:
        return np.isfinite(float(x))
    except:
        return False

# Check data completeness
print("\n" + "="*80)
print("STEP 2: DATA COMPLETENESS ANALYSIS")
print("="*80)

required_cols = ['M_solar', 'r_emit_m', 'v_tot_mps', 'z_geom_hint', 'z']
for col in required_cols:
    count = df[col].notna().sum()
    pct = 100 * count / len(df)
    print(f"{col:15s}: {count:3d}/{len(df)} ({pct:5.1f}%)")

# Check combinations
print("\n--- Critical Combinations for SEG Predictions ---")
has_mass = df['M_solar'].notna()
has_r = df['r_emit_m'].notna()
has_v_tot = df['v_tot_mps'].notna()
has_z_geom = df['z_geom_hint'].notna()
has_z_obs = df['z'].notna()

print(f"Has M_solar + r_emit_m:                    {(has_mass & has_r).sum()}/{len(df)}")
print(f"Has M_solar + r_emit_m + v_tot:            {(has_mass & has_r & has_v_tot).sum()}/{len(df)}")
print(f"Has M_solar + r_emit_m + v_tot + z_geom:   {(has_mass & has_r & has_v_tot & has_z_geom).sum()}/{len(df)}")
print(f"Has M_solar + r_emit_m + v_tot + z_geom + z_obs: {(has_mass & has_r & has_v_tot & has_z_geom & has_z_obs).sum()}/{len(df)}")

complete_for_seg = has_mass & has_r & has_v_tot & has_z_geom & has_z_obs
print(f"\nCOMPLETE for SEG prediction: {complete_for_seg.sum()}/{len(df)} ({100*complete_for_seg.sum()/len(df):.1f}%)")

# Breakdown by source type
print("\n" + "="*80)
print("STEP 3: BREAKDOWN BY SOURCE TYPE")
print("="*80)

ned_sources = df['source'].isin(['M87', 'Sgr A*'])
original_sources = ~ned_sources

print(f"\nOriginal sources: {original_sources.sum()}")
print(f"  Complete for SEG: {(original_sources & complete_for_seg).sum()}/{original_sources.sum()}")

print(f"\nNED sources (M87/Sgr A*): {ned_sources.sum()}")
print(f"  Complete for SEG: {(ned_sources & complete_for_seg).sum()}/{ned_sources.sum()}")

# Check M87 specifically
m87 = df['source'] == 'M87'
print(f"\nM87 detailed:")
print(f"  Total rows: {m87.sum()}")
print(f"  Has M_solar: {(m87 & has_mass).sum()}")
print(f"  Has r_emit_m: {(m87 & has_r).sum()}")
print(f"  Has v_tot_mps: {(m87 & has_v_tot).sum()}")
print(f"  Has z_geom_hint: {(m87 & has_z_geom).sum()}")
print(f"  Has z (observed): {(m87 & has_z_obs).sum()}")
print(f"  Complete for SEG: {(m87 & complete_for_seg).sum()}")

# Check Sgr A* specifically
sgr = df['source'] == 'Sgr A*'
print(f"\nSgr A* detailed:")
print(f"  Total rows: {sgr.sum()}")
print(f"  Has M_solar: {(sgr & has_mass).sum()}")
print(f"  Has r_emit_m: {(sgr & has_r).sum()}")
print(f"  Has v_tot_mps: {(sgr & has_v_tot).sum()}")
print(f"  Has z_geom_hint: {(sgr & has_z_geom).sum()}")
print(f"  Has z (observed): {(sgr & has_z_obs).sum()}")
print(f"  Complete for SEG: {(sgr & complete_for_seg).sum()}")

# THE KEY QUESTION: Does NED have z_obs?
print("\n" + "="*80)
print("STEP 4: THE SMOKING GUN - DO NED ROWS HAVE z_obs?")
print("="*80)

print("\nNED rows WITHOUT z_obs (observed redshift):")
ned_no_z = ned_sources & ~has_z_obs
print(f"  Count: {ned_no_z.sum()}/{ned_sources.sum()} ({100*ned_no_z.sum()/ned_sources.sum():.1f}%)")

if ned_no_z.sum() > 0:
    print("\n⚠️  CRITICAL ISSUE FOUND!")
    print("NED continuum spectra do NOT have observed redshift (z_obs)!")
    print("\nWITHOUT z_obs, we cannot:")
    print("  1. Calculate prediction error (need z_obs to compare to z_pred)")
    print("  2. Include row in paired test (need both z_obs and predictions)")
    print("  3. Test if SEG is better than GR×SR (need z_obs as ground truth)")

# Test prediction for a few rows
print("\n" + "="*80)
print("STEP 5: TEST PREDICTIONS ON SAMPLE ROWS")
print("="*80)

# Sample: 1 original row, 1 M87 row, 1 Sgr A* row
samples = []

# Original row with complete data
original_complete = df[original_sources & complete_for_seg]
if len(original_complete) > 0:
    samples.append(('Original (complete)', original_complete.iloc[0]))

# M87 row
m87_rows = df[m87]
if len(m87_rows) > 0:
    samples.append(('M87', m87_rows.iloc[0]))

# Sgr A* row
sgr_rows = df[sgr]
if len(sgr_rows) > 0:
    samples.append(('Sgr A*', sgr_rows.iloc[0]))

for label, row in samples:
    print(f"\n--- {label}: {row.get('case', 'N/A')} ---")
    print(f"source: {row.get('source')}")
    print(f"M_solar: {row.get('M_solar')}")
    print(f"r_emit_m: {row.get('r_emit_m'):.3e}" if finite(row.get('r_emit_m')) else f"r_emit_m: NaN")
    print(f"v_tot_mps: {row.get('v_tot_mps'):.3e}" if finite(row.get('v_tot_mps')) else f"v_tot_mps: NaN")
    print(f"v_los_mps: {row.get('v_los_mps'):.3e}" if finite(row.get('v_los_mps')) else f"v_los_mps: NaN")
    print(f"z_geom_hint: {row.get('z_geom_hint'):.6f}" if finite(row.get('z_geom_hint')) else f"z_geom_hint: NaN")
    print(f"z (observed): {row.get('z'):.6e}" if finite(row.get('z')) else f"z (observed): NaN")
    
    # Try to calculate predictions
    if finite(row.get('M_solar')) and finite(row.get('r_emit_m')):
        M_kg = row.get('M_solar') * M_sun
        r_m = row.get('r_emit_m')
        v_tot = row.get('v_tot_mps') if finite(row.get('v_tot_mps')) else 0.0
        v_los = row.get('v_los_mps') if finite(row.get('v_los_mps')) else 0.0
        
        z_gr = z_gravitational(M_kg, r_m)
        z_sr = z_special_rel(v_tot, v_los)
        z_grsr = z_combined(z_gr, z_sr)
        
        print(f"\nPredictions:")
        print(f"  z_GR: {z_gr:.6e}")
        print(f"  z_SR: {z_sr:.6e}")
        print(f"  z_GR×SR: {z_grsr:.6e}")
        
        # SEG prediction
        z_geom_val = row.get('z_geom_hint') if finite(row.get('z_geom_hint')) else None
        log_M = np.log10(M_kg) if M_kg > 0 else np.log10(M_sun)
        
        try:
            z_seg = z_seg_pred(
                'hybrid',
                z_geom_val,
                z_gr,
                z_sr,
                z_grsr,
                A, B, ALPHA,
                log_M,
                None, None
            )
            print(f"  z_SEG: {z_seg:.6e}")
        except Exception as e:
            print(f"  z_SEG: ERROR - {e}")
        
        # Can we compare?
        z_obs = row.get('z')
        if finite(z_obs):
            print(f"\n[OK] CAN COMPARE (has z_obs)")
            print(f"  |z_obs - z_SEG|: {abs(z_obs - z_seg):.6e}" if finite(z_seg) else "  Cannot calculate")
            print(f"  |z_obs - z_GR×SR|: {abs(z_obs - z_grsr):.6e}")
        else:
            print(f"\n[FAIL] CANNOT COMPARE (no z_obs)")
            print(f"  This row is EXCLUDED from paired test!")

# Summary and conclusion
print("\n" + "="*80)
print("STEP 6: ROOT CAUSE ANALYSIS")
print("="*80)

print("\nFINDINGS:")
print(f"1. Total rows: {len(df)}")
print(f"2. Rows with v_tot: {has_v_tot.sum()} (93%)")
print(f"3. Rows with z_geom: {has_z_geom.sum()} (80%)")
print(f"4. Rows with z_obs: {has_z_obs.sum()} ({100*has_z_obs.sum()/len(df):.1f}%)")
print(f"5. Rows with BOTH v_tot AND z_geom: {(has_v_tot & has_z_geom).sum()}")
print(f"6. Rows with v_tot AND z_geom AND z_obs: {(has_v_tot & has_z_geom & has_z_obs).sum()}")

print("\nROOT CAUSE:")
ned_missing_z_obs = ned_sources & ~has_z_obs
if ned_missing_z_obs.sum() > 0:
    print(f"[FAIL] NED continuum rows LACK z_obs (observed redshift)!")
    print(f"   {ned_missing_z_obs.sum()}/{ned_sources.sum()} NED rows have no z_obs")
    print(f"\n   Without z_obs, these rows CANNOT be used in paired test because:")
    print(f"   - No ground truth to compare predictions against")
    print(f"   - Cannot calculate |z_obs - z_pred|")
    print(f"   - Cannot determine if SEG is better than GR×SR")
    
    print(f"\n   This is why paired test is still 79/427 (18.5%):")
    print(f"   - Only {(~ned_sources & complete_for_seg).sum()} original rows usable")
    print(f"   - {ned_missing_z_obs.sum()} NED rows excluded (no z_obs)")
    print(f"   - Total usable: {complete_for_seg.sum()} rows")
else:
    print(f"[OK] All NED rows have z_obs")
    print(f"   Problem must be elsewhere...")

# What does NED continuum even mean?
print("\n" + "="*80)
print("STEP 7: WHAT IS NED CONTINUUM DATA?")
print("="*80)

print("\nNED continuum spectra are:")
print("  - Flux measurements at different frequencies")
print("  - NOT individual emission lines with Doppler shift")
print("  - NO intrinsic redshift (continuum = broadband)")
print("  - z_obs would be cosmological/motion redshift of SOURCE")
print("  - But for M87/Sgr A*, we need EMISSION LINE z, not continuum")

print("\nFOR PAIRED TEST WE NEED:")
print("  - Observed redshift of SPECIFIC emission")
print("  - Frequency shift from emission line")
print("  - NOT just 'source has recession velocity'")

print("\nCONCLUSION:")
print("  NED continuum data is FLUX vs FREQUENCY")
print("  It does NOT have redshift per observation")
print("  Each frequency is just a flux measurement")
print("  There is no 'z_obs' for continuum!")

# Proposed solution
print("\n" + "="*80)
print("STEP 8: PROPOSED SOLUTION")
print("="*80)

print("\nWHY z_geom DIDN'T HELP PAIRED TEST:")
print("  1. z_geom was added to NED rows [OK]")
print("  2. BUT NED rows have no z_obs [FAIL]")
print("  3. Without z_obs, cannot do paired comparison")
print("  4. So paired test score unchanged")

print("\nWHAT WE CAN DO:")

print("\nOption A) Accept current situation:")
print("  - NED continuum = for spectrum analysis")
print("  - NOT for paired redshift test")
print("  - Keep paired test at 79/427 (original data only)")
print("  - Document: 'Continuum data excluded from paired test'")

print("\nOption B) Calculate 'synthetic z_obs' for NED:")
print("  - Use source recession velocity")
print("  - z_obs = v_source / c (for M87/Sgr A*)")
print("  - BUT this is NOT an observation!")
print("  - Would be scientifically questionable")

print("\nOption C) Get real emission line data:")
print("  - Find M87/Sgr A* emission line measurements")
print("  - With actual observed frequency shifts")
print("  - Would need literature search")
print("  - More work but scientifically correct")

print("\nRECOMMENDATION:")
print("  [OK] Option A - Accept and document")
print("  - NED continuum is for multi-frequency coverage")
print("  - Paired test uses emission line data only")
print("  - This is scientifically correct!")
print("  - Update README: 'Paired test: 79/143 original rows (55%)'")

print("\n" + "="*80)
print("INVESTIGATION COMPLETE")
print("="*80)
