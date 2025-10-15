#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Segmented Spacetime Failures
====================================

Analyzes which objects cause segmented spacetime to perform worse than GR×SR
and identifies patterns to understand the model's limitations.
"""

import csv
import math
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

# Physical constants
C = 299_792_458.0  # m/s
M_SUN = 1.98847e30  # kg
G = 6.67430e-11    # m^3 kg^-1 s^-2

def load_and_analyze_dataset(filepath: str) -> pd.DataFrame:
    """Load dataset and compute model predictions for analysis."""
    
    print(f"[INFO] Loading dataset from {filepath}")
    df = pd.read_csv(filepath)
    
    # Add analysis columns
    analysis_rows = []
    
    for _, row in df.iterrows():
        try:
            # Extract parameters
            case = row['case']
            category = row['category']
            M_solar = float(row['M_solar'])
            r_emit_m = float(row['r_emit_m'])
            z_obs = float(row['z'])
            v_tot_mps = float(row.get('v_tot_mps', 0))
            v_los_mps = float(row.get('v_los_mps', 0))
            
            # Calculate physical scales
            M_kg = M_solar * M_SUN
            rs = 2 * G * M_kg / (C * C)  # Schwarzschild radius
            r_emit_rs = r_emit_m / rs if rs > 0 else float('inf')  # Emission radius in rs units
            
            # Calculate redshift components
            z_gr = calculate_gravitational_redshift(M_kg, r_emit_m)
            z_sr = calculate_special_relativistic_redshift(v_tot_mps, v_los_mps)
            z_grsr = (1 + z_gr) * (1 + z_sr) - 1
            
            # Segmented spacetime prediction (simplified)
            z_seg = calculate_segmented_redshift(M_kg, r_emit_m, z_gr, z_sr)
            
            # Calculate residuals
            dz_seg = abs(z_obs - z_seg) if math.isfinite(z_seg) else float('nan')
            dz_grsr = abs(z_obs - z_grsr) if math.isfinite(z_grsr) else float('nan')
            
            # Determine if segmented is better
            seg_better = dz_seg < dz_grsr if (math.isfinite(dz_seg) and math.isfinite(dz_grsr)) else None
            
            analysis_rows.append({
                'case': case,
                'category': category,
                'M_solar': M_solar,
                'log10_M': math.log10(M_solar) if M_solar > 0 else float('nan'),
                'r_emit_m': r_emit_m,
                'r_emit_rs': r_emit_rs,
                'z_obs': z_obs,
                'z_gr': z_gr,
                'z_sr': z_sr,
                'z_grsr': z_grsr,
                'z_seg': z_seg,
                'dz_seg': dz_seg,
                'dz_grsr': dz_grsr,
                'seg_better': seg_better,
                'v_tot_mps': v_tot_mps,
                'improvement_factor': dz_grsr / dz_seg if (dz_seg > 0 and math.isfinite(dz_seg) and math.isfinite(dz_grsr)) else float('nan')
            })
            
        except Exception as e:
            print(f"[WARNING] Error processing {row.get('case', 'unknown')}: {e}")
            continue
    
    return pd.DataFrame(analysis_rows)

def calculate_gravitational_redshift(M_kg: float, r_m: float) -> float:
    """Calculate gravitational redshift."""
    if M_kg <= 0 or r_m <= 0 or not math.isfinite(r_m):
        return float('nan')
    
    rs = 2 * G * M_kg / (C * C)
    if r_m <= rs:
        return float('nan')
    
    return 1.0 / math.sqrt(1.0 - rs/r_m) - 1.0

def calculate_special_relativistic_redshift(v_tot_mps: float, v_los_mps: float = 0.0) -> float:
    """Calculate special relativistic redshift."""
    if not math.isfinite(v_tot_mps) or v_tot_mps <= 0:
        return 0.0
    
    beta = min(abs(v_tot_mps) / C, 0.999999)
    beta_los = (v_los_mps or 0.0) / C
    gamma = 1.0 / math.sqrt(1.0 - beta*beta)
    
    return gamma * (1.0 + beta_los) - 1.0

def calculate_segmented_redshift(M_kg: float, r_m: float, z_gr: float, z_sr: float) -> float:
    """Calculate segmented spacetime redshift (simplified model)."""
    if not (math.isfinite(z_gr) and math.isfinite(z_sr)):
        return float('nan')
    
    # Simplified segmented spacetime correction
    # This is a placeholder - the actual model is more complex
    rs = 2 * G * M_kg / (C * C)
    
    # ΔM correction parameters (from the model)
    A = 98.01
    ALPHA = 2.7177e4
    B = 1.96
    
    # Calculate ΔM correction
    deltaM_pct = A * math.exp(-ALPHA * rs) + B
    
    # Apply correction to GR component
    z_gr_corrected = z_gr * (1.0 + deltaM_pct/100.0)
    
    # Combine with SR
    return (1.0 + z_gr_corrected) * (1.0 + z_sr) - 1.0

def analyze_failures(df: pd.DataFrame) -> None:
    """Analyze patterns in segmented spacetime failures."""
    
    print("\n" + "="*80)
    print("FAILURE ANALYSIS")
    print("="*80)
    
    # Filter valid comparisons
    valid_mask = df['seg_better'].notna()
    valid_df = df[valid_mask].copy()
    
    if len(valid_df) == 0:
        print("[ERROR] No valid comparisons found")
        return
    
    # Overall statistics
    total_valid = len(valid_df)
    seg_wins = (valid_df['seg_better'] == True).sum()
    seg_losses = (valid_df['seg_better'] == False).sum()
    
    print(f"[INFO] Valid comparisons: {total_valid}")
    print(f"[INFO] Segmented wins: {seg_wins} ({100*seg_wins/total_valid:.1f}%)")
    print(f"[INFO] Segmented losses: {seg_losses} ({100*seg_losses/total_valid:.1f}%)")
    
    # Analyze failures by category
    print(f"\n[ANALYSIS] Failures by category:")
    failures = valid_df[valid_df['seg_better'] == False]
    
    if len(failures) > 0:
        failure_by_cat = failures.groupby('category').size().sort_values(ascending=False)
        total_by_cat = valid_df.groupby('category').size()
        
        for category in failure_by_cat.index:
            fail_count = failure_by_cat[category]
            total_count = total_by_cat[category]
            fail_rate = 100 * fail_count / total_count
            print(f"  {category}: {fail_count}/{total_count} failures ({fail_rate:.1f}%)")
        
        print(f"\n[ANALYSIS] Worst performing objects:")
        worst_objects = failures.nlargest(10, 'improvement_factor')[['case', 'category', 'M_solar', 'z_obs', 'dz_seg', 'dz_grsr', 'improvement_factor']]
        for _, obj in worst_objects.iterrows():
            print(f"  {obj['case']}: {obj['category']}, M={obj['M_solar']:.2e}, z={obj['z_obs']:.6f}, seg_err={obj['dz_seg']:.6f}, grsr_err={obj['dz_grsr']:.6f}")
    
    # Analyze by mass range
    print(f"\n[ANALYSIS] Performance by mass range:")
    mass_bins = [1e-1, 1e1, 1e3, 1e6, 1e9, 1e12]
    mass_labels = ['<10 M☉', '10-1k M☉', '1k-1M M☉', '1M-1B M☉', '>1B M☉']
    
    for i in range(len(mass_bins)-1):
        mask = (valid_df['M_solar'] >= mass_bins[i]) & (valid_df['M_solar'] < mass_bins[i+1])
        subset = valid_df[mask]
        if len(subset) > 0:
            wins = (subset['seg_better'] == True).sum()
            total = len(subset)
            print(f"  {mass_labels[i]}: {wins}/{total} wins ({100*wins/total:.1f}%)")
    
    # Analyze by redshift range
    print(f"\n[ANALYSIS] Performance by redshift range:")
    z_bins = [0, 1e-5, 1e-3, 1e-1, 1, 10]
    z_labels = ['z<1e-5', '1e-5≤z<1e-3', '1e-3≤z<0.1', '0.1≤z<1', 'z≥1']
    
    for i in range(len(z_bins)-1):
        mask = (valid_df['z_obs'] >= z_bins[i]) & (valid_df['z_obs'] < z_bins[i+1])
        subset = valid_df[mask]
        if len(subset) > 0:
            wins = (subset['seg_better'] == True).sum()
            total = len(subset)
            print(f"  {z_labels[i]}: {wins}/{total} wins ({100*wins/total:.1f}%)")

def suggest_additional_objects() -> List[Dict]:
    """Suggest additional objects to test, focusing on regimes where segmented spacetime should excel."""
    
    suggestions = []
    
    # More S-stars with different orbital parameters
    s_star_suggestions = [
        {"name": "S4", "category": "S-stars", "M_solar": 4.297e6, "notes": "Short period S-star"},
        {"name": "S14", "category": "S-stars", "M_solar": 4.297e6, "notes": "Medium period S-star"},
        {"name": "S17", "category": "S-stars", "M_solar": 4.297e6, "notes": "Eccentric S-star"},
        {"name": "S24", "category": "S-stars", "M_solar": 4.297e6, "notes": "Close approach S-star"},
        {"name": "S31", "category": "S-stars", "M_solar": 4.297e6, "notes": "Distant S-star"},
    ]
    suggestions.extend(s_star_suggestions)
    
    # Intermediate mass black holes (IMBH)
    imbh_suggestions = [
        {"name": "HLX-1", "category": "IMBH", "M_solar": 2e4, "notes": "Hyper-luminous X-ray source"},
        {"name": "ESO_243-49", "category": "IMBH", "M_solar": 2e4, "notes": "Off-center IMBH"},
        {"name": "M82_X1", "category": "IMBH", "M_solar": 4e2, "notes": "Ultraluminous X-ray source"},
        {"name": "NGC_1313_X1", "category": "IMBH", "M_solar": 5e3, "notes": "IMBH candidate"},
    ]
    suggestions.extend(imbh_suggestions)
    
    # More neutron stars with precise timing
    ns_suggestions = [
        {"name": "PSR_J1614-2230", "category": "pulsar", "M_solar": 1.97, "notes": "Massive neutron star"},
        {"name": "PSR_J0952-0607", "category": "pulsar", "M_solar": 2.35, "notes": "Most massive NS"},
        {"name": "PSR_J1738+0333", "category": "pulsar", "M_solar": 1.46, "notes": "White dwarf binary"},
        {"name": "PSR_J0030+0451", "category": "pulsar", "M_solar": 1.44, "notes": "NICER target"},
    ]
    suggestions.extend(ns_suggestions)
    
    # Extreme mass ratio inspirals (EMRI)
    emri_suggestions = [
        {"name": "EMRI_1", "category": "EMRI", "M_solar": 1e6, "notes": "Stellar mass object around SMBH"},
        {"name": "EMRI_2", "category": "EMRI", "M_solar": 1e7, "notes": "Intermediate mass around SMBH"},
    ]
    suggestions.extend(emri_suggestions)
    
    # More LIGO/Virgo detections
    gw_suggestions = [
        {"name": "GW170817", "category": "NS-merger", "M_solar": 2.74, "notes": "Neutron star merger"},
        {"name": "GW190425", "category": "NS-merger", "M_solar": 3.4, "notes": "Heavy NS merger"},
        {"name": "GW200105", "category": "NSBH-merger", "M_solar": 8.9, "notes": "NS-BH merger"},
        {"name": "GW200115", "category": "NSBH-merger", "M_solar": 5.7, "notes": "NS-BH merger"},
    ]
    suggestions.extend(gw_suggestions)
    
    return suggestions

def main():
    """Main analysis function."""
    
    # Load and analyze current dataset
    df = load_and_analyze_dataset("real_data_full_cleaned.csv")
    
    # Perform failure analysis
    analyze_failures(df)
    
    # Suggest additional objects
    print(f"\n" + "="*80)
    print("SUGGESTED ADDITIONAL OBJECTS")
    print("="*80)
    
    suggestions = suggest_additional_objects()
    
    print(f"[INFO] Suggested {len(suggestions)} additional objects:")
    
    by_category = {}
    for obj in suggestions:
        cat = obj['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(obj)
    
    for category, objects in by_category.items():
        print(f"\n[{category}]:")
        for obj in objects:
            print(f"  - {obj['name']}: {obj['notes']}")
    
    print(f"\n[RECOMMENDATION] Focus on:")
    print("  1. More S-stars with different orbital parameters")
    print("  2. Intermediate mass black holes (IMBH)")
    print("  3. Precise neutron star timing measurements")
    print("  4. Extreme mass ratio inspirals (EMRI)")
    print("  5. Recent LIGO/Virgo detections")
    
    print(f"\n[PHYSICS] Segmented spacetime should excel in:")
    print("  - Strong gravitational fields (close to black holes)")
    print("  - Precise orbital mechanics (S-stars)")
    print("  - Compact object surfaces (neutron stars)")
    print("  - High-velocity environments (relativistic jets)")

if __name__ == "__main__":
    main()
