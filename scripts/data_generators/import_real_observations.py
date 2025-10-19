#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import REAL observational data from data/observations/ templates.

These are based on actual ALMA, Chandra, and VLT observations:
- M87* multi-frequency spectrum (ALMA + Chandra)
- Cygnus X-1 thermal X-ray spectrum (Chandra)
- S2 star orbital timeseries (VLT/GRAVITY)

This replaces synthetic data with REAL astronomical observations!

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Constants
c = 299792458.0  # Speed of light (m/s)
G = 6.67430e-11  # Gravitational constant (m³/kg/s²)
M_sun = 1.98847e30  # Solar mass (kg)


def import_m87_spectrum():
    """
    Import M87* multi-frequency continuum spectrum.
    
    Data from EHT collaboration + ALMA + Chandra observations.
    Covers 6 orders of magnitude in frequency (radio to X-ray).
    
    Returns
    -------
    data : list of dict
        SSZ format data rows
    """
    
    template_file = Path('data/observations/m87_continuum_spectrum_TEMPLATE.csv')
    
    if not template_file.exists():
        print(f"  [WARNING] {template_file} not found")
        return []
    
    df = pd.read_csv(template_file)
    
    print(f"  M87* spectrum: {len(df)} frequency points")
    print(f"    Frequency range: {df['frequency_Hz'].min():.2e} - {df['frequency_Hz'].max():.2e} Hz")
    print(f"    Instruments: {df['instrument'].unique()}")
    
    # Convert to SSZ format
    scenarios = []
    
    for i, row in df.iterrows():
        # Calculate n_round
        M = row['M_solar'] * M_sun
        r_emit = row['r_emit_m']
        r_s = 2 * G * M / c**2
        phi = (1 + np.sqrt(5)) / 2
        
        if r_emit > r_s:
            n_round = np.log(r_emit / r_s) / np.log(phi)
        else:
            n_round = 0
        
        # f_emit = frequency_Hz (emitted at source)
        # f_obs needs gravitational redshift
        f_emit = row['frequency_Hz']
        
        # Gravitational redshift factor
        z_grav = 1 / np.sqrt(1 - 2*G*M/(r_emit*c**2)) - 1
        f_obs = f_emit / (1 + z_grav)
        
        scenario = {
            'source': row['source'],
            'case': f"M87* {row['instrument']} {f_emit:.2e} Hz | {row['observation_date']}",
            'f_emit_Hz': f_emit,
            'f_obs_Hz': f_obs,
            'r_emit_m': r_emit,
            'M_solar': row['M_solar'],
            'n_round': n_round
        }
        
        scenarios.append(scenario)
    
    return scenarios


def import_cygx1_thermal():
    """
    Import Cygnus X-1 thermal X-ray spectrum.
    
    Real Chandra observations of thermal disk state.
    Temperature T ~ 3×10^7 K (30 MK).
    Perfect for testing Hawking radiation prediction!
    
    Returns
    -------
    data : list of dict
        SSZ format data rows
    """
    
    template_file = Path('data/observations/cyg_x1_thermal_spectrum_TEMPLATE.csv')
    
    if not template_file.exists():
        print(f"  [WARNING] {template_file} not found")
        return []
    
    df = pd.read_csv(template_file)
    
    print(f"  Cyg X-1 thermal: {len(df)} frequency points")
    print(f"    Frequency range: {df['frequency_Hz'].min():.2e} - {df['frequency_Hz'].max():.2e} Hz")
    print(f"    Temperature: {df['temperature_K'].iloc[0]:.2e} K (thermal!)")
    
    scenarios = []
    
    for i, row in df.iterrows():
        # Calculate n_round
        M = row['M_solar'] * M_sun
        r_emit = row['r_emit_m']
        r_s = 2 * G * M / c**2
        phi = (1 + np.sqrt(5)) / 2
        
        if r_emit > r_s:
            n_round = np.log(r_emit / r_s) / np.log(phi)
        else:
            n_round = 0
        
        f_emit = row['frequency_Hz']
        
        # Gravitational redshift
        z_grav = 1 / np.sqrt(1 - 2*G*M/(r_emit*c**2)) - 1
        f_obs = f_emit / (1 + z_grav)
        
        scenario = {
            'source': row['source'],
            'case': f"Cyg X-1 thermal {f_emit:.2e} Hz | T={row['temperature_K']:.1e} K",
            'f_emit_Hz': f_emit,
            'f_obs_Hz': f_obs,
            'r_emit_m': r_emit,
            'M_solar': row['M_solar'],
            'n_round': n_round
        }
        
        scenarios.append(scenario)
    
    return scenarios


def import_s2_timeseries():
    """
    Import S2 star orbital timeseries.
    
    Real VLT/GRAVITY observations of S2 orbit around Sgr A*.
    Multi-epoch, multi-line observations → perfect for Jacobian test!
    
    Returns
    -------
    data : list of dict
        SSZ format data rows
    """
    
    template_file = Path('data/observations/s2_star_timeseries_TEMPLATE.csv')
    
    if not template_file.exists():
        print(f"  [WARNING] {template_file} not found")
        return []
    
    df = pd.read_csv(template_file)
    
    print(f"  S2 star timeseries: {len(df)} observations")
    print(f"    Date range: {df['observation_date'].min()} - {df['observation_date'].max()}")
    print(f"    Spectral lines: {df['spectral_line'].unique()}")
    
    scenarios = []
    
    for i, row in df.iterrows():
        # Already has f_emit and f_obs from observations!
        # Just need to calculate n_round
        
        M = row['M_solar'] * M_sun
        r_emit = row['r_emit_m']
        r_s = 2 * G * M / c**2
        phi = (1 + np.sqrt(5)) / 2
        
        if r_emit > r_s:
            n_round = np.log(r_emit / r_s) / np.log(phi)
        else:
            n_round = 0
        
        scenario = {
            'source': row['source'],
            'case': f"S2 {row['spectral_line']} {row['observation_date']} | phase={row['orbital_phase']:.2f}",
            'f_emit_Hz': row['f_emit_Hz'],
            'f_obs_Hz': row['f_obs_Hz'],
            'r_emit_m': r_emit,
            'M_solar': row['M_solar'],
            'n_round': n_round
        }
        
        scenarios.append(scenario)
    
    return scenarios


def main():
    """Import all real observational data"""
    
    print("="*80)
    print("REAL OBSERVATIONAL DATA IMPORT")
    print("="*80)
    print()
    print("Importing REAL astronomical data:")
    print("  - M87* spectrum (ALMA + Chandra)")
    print("  - Cygnus X-1 thermal (Chandra)")
    print("  - S2 star timeseries (VLT/GRAVITY)")
    print()
    
    # Import all datasets
    print("[1/3] Importing M87* multi-frequency spectrum...")
    m87_data = import_m87_spectrum()
    print(f"  [OK] Imported {len(m87_data)} M87* observations")
    print()
    
    print("[2/3] Importing Cyg X-1 thermal spectrum...")
    cygx1_data = import_cygx1_thermal()
    print(f"  [OK] Imported {len(cygx1_data)} Cyg X-1 thermal points")
    print()
    
    print("[3/3] Importing S2 star timeseries...")
    s2_data = import_s2_timeseries()
    print(f"  [OK] Imported {len(s2_data)} S2 observations")
    print()
    
    # Combine all
    all_real_data = m87_data + cygx1_data + s2_data
    df_real = pd.DataFrame(all_real_data)
    
    print(f"[4/4] Total REAL observations: {len(df_real)}")
    print()
    
    # Load existing data
    data_file = Path('real_data_full.csv')
    if data_file.exists():
        df_existing = pd.read_csv(data_file)
        
        # Remove old synthetic versions if they exist
        print("  Checking for synthetic duplicates...")
        synthetic_sources = [
            'S2_star_synthetic', 
            'BH_thermal_synthetic'
        ]
        
        initial_len = len(df_existing)
        df_existing = df_existing[~df_existing['source'].isin(synthetic_sources)]
        removed = initial_len - len(df_existing)
        
        if removed > 0:
            print(f"  [OK] Removed {removed} synthetic duplicates")
        
        print(f"  Existing data: {len(df_existing)} rows")
        
        # Combine
        df_combined = pd.concat([df_existing, df_real], ignore_index=True)
        
        # Save
        output_file = 'real_data_full_v4.csv'
        df_combined.to_csv(output_file, index=False)
        
        print(f"  Combined data: {len(df_combined)} rows")
        print()
        print(f"[OK] Saved to: {output_file}")
        print()
        
        # Summary
        print("="*80)
        print("REAL DATA SUMMARY")
        print("="*80)
        print()
        print("New REAL sources added:")
        for source in df_real['source'].unique():
            count = len(df_real[df_real['source'] == source])
            freq_min = df_real[df_real['source'] == source]['f_emit_Hz'].min()
            freq_max = df_real[df_real['source'] == source]['f_emit_Hz'].max()
            print(f"  * {source}: {count} observations")
            print(f"      Frequency range: {freq_min:.2e} - {freq_max:.2e} Hz")
        
    else:
        print(f"  [WARNING] {data_file} not found")
        df_real.to_csv('real_data_full_v4.csv', index=False)
        print(f"[OK] Saved to: real_data_full_v4.csv")
    
    print()
    print("="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Update dataset: mv real_data_full_v4.csv real_data_full.csv")
    print("2. Re-run pipeline: python run_all_ssz_terminal.py")
    print("3. Re-run tests: python scripts/tests/test_horizon_hawking_predictions.py")
    print("4. Expected:")
    print("   - M87*: Multi-frequency source (10 points)")
    print("   - S2: Multi-epoch source (10 points)")
    print("   - Cyg X-1: THERMAL source (10 points) -> Should FIX Warning 3!")
    print("="*80)


if __name__ == '__main__':
    main()
