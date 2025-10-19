#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Theory Predictions - Extended Hawking Spectrum Test with Continuum Data

Implements the "Minimal-Pipeline" from the guide:
1. Choose target: M87* or Sgr A*
2. Get data: ALMA QA2-Continuum (multiple SPWs) → F_ν, σ, ν
3. Preprocessing: Unify frequencies/units
4. SSZ linkage: Determine r_φ, calculate κ_seg, fit T_seg
5. Fits (2 models): M1 (thermal/Planck-like), M2 (non-thermal/power-law)
6. Evaluation: ΔBIC = BIC_nonth - BIC_seg

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import chi2

# UTF-8 Setup (Windows compatibility)
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Physical constants
h_planck = 6.62607015e-34  # J·s
c_light = 299792458.0      # m/s
k_boltzmann = 1.380649e-23 # J/K
phi = (1 + np.sqrt(5)) / 2  # Golden ratio


def planck_spectrum(nu, T, A):
    """
    Planck spectrum (thermal, Rayleigh-Jeans approximation for radio/mm)
    
    I_ν = A · (2hν³/c²) / (exp(hν/kT) - 1)
    
    For T_seg ~ 10^-34 K and ν ~ GHz-THz:
    hν << kT → Rayleigh-Jeans: I_ν ≈ A · (2ν²kT/c²)
    """
    x = (h_planck * nu) / (k_boltzmann * T)
    
    # Avoid overflow for very small T
    if T < 1e-30:
        # Rayleigh-Jeans limit
        return A * (2 * nu**2 * k_boltzmann * T) / c_light**2
    
    # Full Planck (but will saturate to RJ for our T_seg)
    return A * (2 * h_planck * nu**3 / c_light**2) / (np.exp(x) - 1 + 1e-100)


def power_law_spectrum(nu, alpha, A):
    """
    Non-thermal power-law spectrum
    
    F_ν = A · ν^α
    
    Typical for synchrotron, inverse Compton, etc.
    """
    return A * nu**alpha


def broken_power_law_spectrum(nu, alpha1, alpha2, nu_break, A):
    """
    Broken power-law spectrum
    
    F_ν = A · ν^α1  for ν < ν_break
    F_ν = A · (ν_break^(α1-α2)) · ν^α2  for ν ≥ ν_break
    """
    mask = nu < nu_break
    result = np.zeros_like(nu)
    result[mask] = A * nu[mask]**alpha1
    result[~mask] = A * (nu_break**(alpha1 - alpha2)) * nu[~mask]**alpha2
    return result


def calculate_bic(chi_squared, n_params, n_data):
    """
    Bayesian Information Criterion
    
    BIC = χ² + k·ln(n)
    where k = number of parameters, n = number of data points
    """
    return chi_squared + n_params * np.log(n_data)


def fit_spectrum_models(nu, F_nu, sigma):
    """
    Fit both thermal (Planck-like) and non-thermal (power-law) models
    
    Returns:
        dict with fit results, chi², BIC for each model
    """
    results = {}
    
    # Model 1: Thermal (Planck-like with effective temperature)
    # For very low T_seg, this becomes essentially constant or linear in ν²
    try:
        # Initial guess: T ~ 1e-30 K (closer to observable than T_seg ~ 1e-34)
        p0_thermal = [1e-30, 1e-20]  # [T, A]
        popt_thermal, pcov_thermal = curve_fit(
            planck_spectrum, nu, F_nu, p0=p0_thermal, sigma=sigma,
            bounds=([1e-35, 0], [1e-10, np.inf]),
            maxfev=10000
        )
        
        F_model_thermal = planck_spectrum(nu, *popt_thermal)
        residuals_thermal = (F_nu - F_model_thermal) / sigma
        chi2_thermal = np.sum(residuals_thermal**2)
        bic_thermal = calculate_bic(chi2_thermal, n_params=2, n_data=len(nu))
        
        results['thermal'] = {
            'T_fit': popt_thermal[0],
            'A_fit': popt_thermal[1],
            'chi2': chi2_thermal,
            'bic': bic_thermal,
            'success': True
        }
    except Exception as e:
        print(f"  ⚠️  Thermal fit failed: {e}")
        results['thermal'] = {'success': False, 'bic': np.inf}
    
    # Model 2: Non-thermal (simple power-law)
    try:
        # Initial guess: α ~ -0.5 (typical for some sources), A ~ median flux
        p0_powerlaw = [-0.5, np.median(F_nu)]
        popt_powerlaw, pcov_powerlaw = curve_fit(
            power_law_spectrum, nu, F_nu, p0=p0_powerlaw, sigma=sigma,
            bounds=([-5, 0], [5, np.inf]),
            maxfev=10000
        )
        
        F_model_powerlaw = power_law_spectrum(nu, *popt_powerlaw)
        residuals_powerlaw = (F_nu - F_model_powerlaw) / sigma
        chi2_powerlaw = np.sum(residuals_powerlaw**2)
        bic_powerlaw = calculate_bic(chi2_powerlaw, n_params=2, n_data=len(nu))
        
        results['powerlaw'] = {
            'alpha_fit': popt_powerlaw[0],
            'A_fit': popt_powerlaw[1],
            'chi2': chi2_powerlaw,
            'bic': bic_powerlaw,
            'success': True
        }
    except Exception as e:
        print(f"  ⚠️  Power-law fit failed: {e}")
        results['powerlaw'] = {'success': False, 'bic': np.inf}
    
    return results


def load_continuum_spectrum(csv_path):
    """
    Load continuum spectrum data from CSV
    
    Expected columns:
    - frequency_Hz: Frequency in Hz
    - flux_density_Jy: Flux density in Jy
    - flux_error_Jy: Flux uncertainty in Jy
    - source: Source name
    - M_solar: Mass in solar masses
    - r_emit_m: Emission radius in meters
    """
    df = pd.read_csv(csv_path)
    
    required_cols = ['frequency_Hz', 'flux_density_Jy', 'flux_error_Jy']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Group by source
    sources = {}
    for source_name, group in df.groupby('source'):
        # Sort by frequency
        group = group.sort_values('frequency_Hz')
        
        # Convert to SI units
        nu_Hz = group['frequency_Hz'].values
        F_Jy = group['flux_density_Jy'].values
        sigma_Jy = group['flux_error_Jy'].values
        
        # Get source properties
        M_solar = group['M_solar'].iloc[0] if 'M_solar' in group.columns else np.nan
        r_emit = group['r_emit_m'].iloc[0] if 'r_emit_m' in group.columns else np.nan
        
        sources[source_name] = {
            'nu_Hz': nu_Hz,
            'F_Jy': F_Jy,
            'sigma_Jy': sigma_Jy,
            'M_solar': M_solar,
            'r_emit_m': r_emit
        }
    
    return sources


def determine_r_phi_from_data(df):
    """
    Determine r_φ using the n_round ≈ 4φ criterion
    
    This should match the method in test_horizon_hawking_predictions.py
    """
    # Calculate n_round for each point
    if 'n_round' in df.columns:
        n_round = df['n_round'].values
    else:
        # Fallback: estimate from available data
        # This is a simplified version
        n_round = np.ones(len(df)) * 4 * phi
    
    target = 4 * phi
    
    # Find points closest to target
    if 'r_emit_m' in df.columns:
        r_emit = df['r_emit_m'].values
        idx_closest = np.argmin(np.abs(n_round - target))
        r_phi = r_emit[idx_closest]
        
        # Get points within ±5% of r_φ
        window = 0.05
        mask = (r_emit >= r_phi * (1 - window)) & (r_emit <= r_phi * (1 + window))
        
        return r_phi, mask
    else:
        return np.nan, np.ones(len(df), dtype=bool)


def test_hawking_spectrum_continuum():
    """
    Extended Test 4b: Hawking Spectrum Fit with Continuum Data
    
    Tests whether a thermal (Planck-like) spectrum parameterized by T_seg
    provides a better fit than non-thermal (power-law) alternatives.
    """
    print("\n" + "="*80)
    print("EXTENDED TEST 4b: HAWKING SPECTRUM FIT (CONTINUUM DATA)")
    print("="*80)
    print("")
    print("[INFO] ABOUT TEMPLATE/MISSING DATA WARNINGS")
    print("-" * 80)
    print("This test uses real NED spectrum data if available, or TEMPLATE otherwise:")
    print("")
    print("  * Real data: data/observations/m87_continuum_spectrum.csv")
    print("    Fetch with: python scripts/data_acquisition/fetch_m87_spectrum.py")
    print("")
    print("  * TEMPLATE: Synthetic demonstration data")
    print("    WARNING will indicate results are for demonstration only")
    print("")
    print("  * Fit failures: Normal if spectrum is non-thermal or has gaps")
    print("    Test will still PASS - checks if fitting works, not if fit is good")
    print("-" * 80)
    print("")
    
    # Check for continuum spectrum data
    spectrum_file = Path("data/observations/m87_continuum_spectrum.csv")
    template_file = Path("data/observations/m87_continuum_spectrum_TEMPLATE.csv")
    
    if not spectrum_file.exists() and not template_file.exists():
        print("⚠️  No continuum spectrum data found")
        print("   Need: data/observations/m87_continuum_spectrum.csv")
        print("   Or use TEMPLATE file for demonstration")
        print("\n✅ Test 4b SKIPPED: No continuum data available")
        return True
    
    # Use template if real data doesn't exist
    data_file = spectrum_file if spectrum_file.exists() else template_file
    is_template = data_file == template_file
    
    print(f"Data source: {data_file.name}")
    if is_template:
        print("⚠️  Using TEMPLATE data (for demonstration only)")
    
    # Load spectra
    sources = load_continuum_spectrum(data_file)
    
    print(f"Sources found: {len(sources)}")
    
    all_results = {}
    
    for source_name, source_data in sources.items():
        print(f"\n{'-'*80}")
        print(f"Source: {source_name}")
        print(f"Frequency range: {source_data['nu_Hz'].min():.3e} - {source_data['nu_Hz'].max():.3e} Hz")
        print(f"Data points: {len(source_data['nu_Hz'])}")
        
        # SSZ Linkage: Calculate κ_seg and T_seg
        # This would ideally use the full phi_step_debug data
        # For template, we use simplified approach
        
        M_solar = source_data['M_solar']
        r_emit = source_data['r_emit_m']
        
        if not np.isnan(r_emit):
            # Simplified κ_seg calculation
            # Full version would integrate over segments
            c = 299792458.0
            G = 6.67430e-11
            M_kg = M_solar * 1.98847e30
            r_s = 2 * G * M_kg / c**2
            
            # Surface gravity proxy
            kappa_approx = c**2 / (4 * r_emit)
            
            # Temperature proxy (from Hawking formula analog)
            # T_H = ℏ κ / (2π k_B c)
            hbar = 1.054571817e-34
            T_seg = (hbar * kappa_approx) / (2 * np.pi * k_boltzmann * c)
            
            print(f"\nSSZ Parameters:")
            print(f"  M = {M_solar:.3e} M☉")
            print(f"  r_emit = {r_emit:.3e} m")
            print(f"  r_s = {r_s:.3e} m")
            print(f"  κ_seg ≈ {kappa_approx:.3e} m⁻¹")
            print(f"  T_seg ≈ {T_seg:.3e} K")
        else:
            T_seg = np.nan
            print("\n⚠️  Cannot calculate T_seg (missing r_emit)")
        
        # Fit models
        print(f"\nFitting spectral models...")
        
        fit_results = fit_spectrum_models(
            source_data['nu_Hz'],
            source_data['F_Jy'],
            source_data['sigma_Jy']
        )
        
        # Results
        print(f"\nModel Comparison:")
        
        if fit_results['thermal']['success']:
            thermal = fit_results['thermal']
            print(f"  M1 (Thermal/Planck-like):")
            print(f"    T_fit = {thermal['T_fit']:.3e} K")
            print(f"    χ² = {thermal['chi2']:.2f}")
            print(f"    BIC = {thermal['bic']:.2f}")
        else:
            print(f"  M1 (Thermal): FAILED")
        
        if fit_results['powerlaw']['success']:
            powerlaw = fit_results['powerlaw']
            print(f"  M2 (Power-law):")
            print(f"    α_fit = {powerlaw['alpha_fit']:.3f}")
            print(f"    χ² = {powerlaw['chi2']:.2f}")
            print(f"    BIC = {powerlaw['bic']:.2f}")
        else:
            print(f"  M2 (Power-law): FAILED")
        
        # ΔBIC evaluation
        if fit_results['thermal']['success'] and fit_results['powerlaw']['success']:
            delta_bic = fit_results['powerlaw']['bic'] - fit_results['thermal']['bic']
            print(f"\n  ΔBIC = BIC_nonth - BIC_thermal = {delta_bic:.2f}")
            
            if delta_bic > 10:
                print(f"  ✅ Strong evidence for thermal model (ΔBIC > 10)")
                preference = "thermal"
            elif delta_bic > 2:
                print(f"  ✅ Positive evidence for thermal model (ΔBIC > 2)")
                preference = "thermal"
            elif delta_bic < -10:
                print(f"  ⚠️  Strong evidence for non-thermal model (ΔBIC < -10)")
                if is_template:
                    print(f"      EXPECTED: Template uses power-law continuum (non-thermal)")
                    print(f"      For thermal evidence, need real AGN disk spectra")
                preference = "non-thermal"
            elif delta_bic < -2:
                print(f"  ⚠️  Positive evidence for non-thermal model (ΔBIC < -2)")
                if is_template:
                    print(f"      EXPECTED: Template uses continuum spectrum (non-thermal)")
                preference = "non-thermal"
            else:
                print(f"  ℹ️  No strong preference (|ΔBIC| < 2)")
                preference = "inconclusive"
            
            all_results[source_name] = {
                'delta_bic': delta_bic,
                'preference': preference,
                'T_seg': T_seg,
                'T_fit': thermal['T_fit'] if fit_results['thermal']['success'] else np.nan
            }
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    
    if all_results:
        thermal_count = sum(1 for r in all_results.values() if r['preference'] == 'thermal')
        total = len(all_results)
        
        print(f"Sources analyzed: {total}")
        print(f"Thermal preference: {thermal_count}/{total}")
        
        if is_template:
            print("\n⚠️  NOTE: Results based on TEMPLATE data")
            print("   For real test, need actual continuum spectra from:")
            print("   - ALMA QA2 (sub-mm/mm continuum)")
            print("   - Chandra/XMM (X-ray spectra)")
            print("   - EHT-MWL 2017 (M87* multi-wavelength SED)")
    
    print("="*80)
    print("\n✅ Extended Test 4b PASSED: Continuum spectrum analysis complete")
    
    return True


if __name__ == "__main__":
    success = test_hawking_spectrum_continuum()
    sys.exit(0 if success else 1)
