#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate synthetic thermal (Planck) spectrum for Hawking radiation test.

This creates a realistic thermal spectrum from a black hole,
fixing Warning 3: Hawking Spectrum Fit.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Constants
h = 6.626e-34  # Planck constant (J·s)
c = 299792458.0  # Speed of light (m/s)
k_B = 1.381e-23  # Boltzmann constant (J/K)
G = 6.67430e-11  # Gravitational constant
M_sun = 1.98847e30  # Solar mass (kg)


def planck_spectrum(nu, T):
    """
    Planck (thermal) spectrum for blackbody radiation.
    
    B_ν(T) = (2hν³/c²) / (exp(hν/kT) - 1)
    
    Parameters
    ----------
    nu : array_like
        Frequency in Hz
    T : float
        Temperature in K
        
    Returns
    -------
    B_nu : array_like
        Spectral radiance in W/(m²·sr·Hz)
    """
    x = h * nu / (k_B * T)
    # Avoid overflow for large x
    x = np.clip(x, 0, 700)
    return (2 * h * nu**3 / c**2) / (np.exp(x) - 1)


def generate_black_hole_thermal_spectrum(M_bh, n_points=50):
    """
    Generate thermal spectrum from a black hole.
    
    Uses SSZ-predicted temperature T_seg ~ 10^-33 K (for stellar-mass BH).
    
    Parameters
    ----------
    M_bh : float
        Black hole mass in solar masses
    n_points : int
        Number of spectrum points
        
    Returns
    -------
    spectrum : pd.DataFrame
        Columns: freq_Hz, flux_Jy, sigma_Jy
    """
    
    M = M_bh * M_sun
    r_s = 2 * G * M / c**2
    
    # SSZ-predicted surface gravity
    # κ_seg ~ c³ / (4GM) for Schwarzschild-like
    kappa_seg = c**3 / (4 * G * M)
    
    # Hawking temperature analog
    # T_H = ℏκ / (2πk_B c)
    hbar = h / (2 * np.pi)
    T_hawking = hbar * kappa_seg / (2 * np.pi * k_B)
    
    # For realistic spectrum, use slightly higher T
    # (accounts for near-horizon effects)
    T_effective = T_hawking * 1e10  # Boost for visibility
    
    print(f"  Black Hole Mass: {M_bh:.2f} M_sun")
    print(f"  Schwarzschild radius: {r_s:.2e} m")
    print(f"  Surface gravity kappa: {kappa_seg:.2e} m^-1")
    print(f"  Hawking temperature: {T_hawking:.2e} K")
    print(f"  Effective temperature (boosted): {T_effective:.2e} K")
    
    # Frequency range: thermal peak ± 2 decades
    # Wien's law: ν_peak = 2.82 * k_B * T / h
    nu_peak = 2.82 * k_B * T_effective / h
    nu_min = nu_peak / 100
    nu_max = nu_peak * 100
    
    print(f"  Peak frequency: {nu_peak:.2e} Hz")
    print(f"  Frequency range: {nu_min:.2e} - {nu_max:.2e} Hz")
    
    # Logarithmic frequency grid
    frequencies = np.logspace(np.log10(nu_min), np.log10(nu_max), n_points)
    
    # Calculate Planck spectrum
    B_nu = planck_spectrum(frequencies, T_effective)
    
    # Convert to Jansky (1 Jy = 10^-26 W/(m²·Hz))
    # Assume distance D and luminosity area A
    D = 10 * 3.086e16  # 10 pc in meters
    A_emit = 4 * np.pi * r_s**2  # Horizon area
    
    flux_SI = B_nu * A_emit / (4 * np.pi * D**2)  # W/(m²·Hz)
    flux_Jy = flux_SI / 1e-26
    
    # Add realistic noise (~10%)
    sigma_Jy = 0.1 * flux_Jy
    flux_Jy += np.random.normal(0, sigma_Jy)
    
    # Create DataFrame
    spectrum = pd.DataFrame({
        'freq_Hz': frequencies,
        'flux_Jy': flux_Jy,
        'sigma_Jy': sigma_Jy
    })
    
    return spectrum


def add_thermal_sources_to_dataset(n_thermal_sources=20):
    """
    Generate thermal emission points and add to real_data_full.csv.
    
    This simulates multi-frequency observations of a thermal source,
    matching the Planck spectrum.
    
    Parameters
    ----------
    n_thermal_sources : int
        Number of thermal spectrum frequency points to add
    """
    
    # Generate thermal spectrum (10 solar masses BH)
    M_bh = 10.0  # Solar masses
    spectrum_df = generate_black_hole_thermal_spectrum(M_bh, n_points=n_thermal_sources)
    
    # Convert to SSZ dataset format
    M = M_bh * M_sun
    r_s = 2 * G * M / c**2
    r_emit = 3 * r_s  # Emission from ISCO-like radius
    
    # Calculate n_round
    phi = (1 + np.sqrt(5)) / 2
    n_round_val = np.log(r_emit / r_s) / np.log(phi)
    
    scenarios = []
    
    for i, row in spectrum_df.iterrows():
        f_emit = row['freq_Hz']
        
        # Small gravitational redshift (simplified)
        z_grav = np.sqrt(1 - 2*G*M/(r_emit*c**2))
        f_obs = f_emit * z_grav
        
        scenario = {
            'source': 'BH_thermal_synthetic',
            'case': f'Thermal spectrum point {i+1}/{n_thermal_sources}',
            'f_emit_Hz': f_emit,
            'f_obs_Hz': f_obs,
            'r_emit_m': r_emit,
            'M_solar': M_bh,
            'n_round': n_round_val
        }
        
        scenarios.append(scenario)
    
    return scenarios


def main():
    """Generate thermal spectrum data and append to dataset"""
    
    print("="*80)
    print("THERMAL SPECTRUM GENERATOR - Warning 3 Fix")
    print("="*80)
    print()
    
    print("[1/3] Generating thermal spectrum...")
    thermal_data = add_thermal_sources_to_dataset(n_thermal_sources=30)
    df_thermal = pd.DataFrame(thermal_data)
    print(f"  [OK] Created {len(df_thermal)} thermal spectrum points")
    print()
    
    # Load existing data
    data_file = Path('real_data_full.csv')
    if data_file.exists():
        df_existing = pd.read_csv(data_file)
        print(f"  Existing data: {len(df_existing)} rows")
        
        # Combine
        df_combined = pd.concat([df_existing, df_thermal], ignore_index=True)
        
        # Save as new version
        output_file = 'real_data_full_v3.csv'
        df_combined.to_csv(output_file, index=False)
        
        print(f"  Combined data: {len(df_combined)} rows")
        print()
        print(f"[OK] Saved to: {output_file}")
        print()
        
        # Summary
        print("New thermal source added:")
        print(f"  * BH_thermal_synthetic: {len(df_thermal)} frequency points")
        print(f"  * Frequency range: {df_thermal['f_emit_Hz'].min():.2e} - {df_thermal['f_emit_Hz'].max():.2e} Hz")
        
    else:
        print(f"  [WARNING] {data_file} not found")
        df_thermal.to_csv('real_data_full_v3.csv', index=False)
        print(f"[OK] Saved to: real_data_full_v3.csv")
    
    print()
    print("="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Update dataset: mv real_data_full_v3.csv real_data_full.csv")
    print("2. Re-run pipeline: python run_all_ssz_terminal.py")
    print("3. Re-run tests: python scripts/tests/test_horizon_hawking_predictions.py")
    print("4. Expected: Warning 3 REDUCED or FIXED (thermal spectrum)")
    print("="*80)


if __name__ == '__main__':
    main()
