#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hawking Proxy Fit - Standalone BIC-based Spectrum Analysis

Simplified tool for fitting thermal (Planck-like) vs non-thermal (power-law)
models to continuum spectra, using SSZ-derived κ_seg for temperature seed.

Usage:
    python hawking_proxy_fit.py --spectrum m87_spectrum.csv --ssz ssz_config.json
    
Requires:
    - Spectrum CSV (from fetch_m87_spectrum.py or similar)
    - SSZ config JSON (with kappa_seg_per_m)

Outputs:
    - Markdown report with BIC comparison
    - PNG plot (log-log spectrum + fits)

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import argparse
import json
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

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


def planck_nu(nu, T, A):
    """
    Planck spectrum: I_ν = A · (2hν³/c²) / (exp(hν/kT) - 1)
    
    Parameters:
        nu: Frequency (Hz)
        T: Temperature (K)
        A: Amplitude normalization
    
    Returns:
        Intensity (arbitrary units, typically Jy)
    """
    h = 6.62607015e-34  # Planck constant (J·s)
    k = 1.380649e-23    # Boltzmann constant (J/K)
    c = 299792458.0     # Speed of light (m/s)
    
    x = h * nu / (k * T)
    x = np.clip(x, 1e-9, 1e3)  # Prevent overflow/underflow
    
    return A * (2 * h * nu**3 / c**2) / (np.expm1(x))


def powerlaw(nu, A, alpha):
    """
    Power-law spectrum: F_ν = A · (ν/ν₀)^α
    
    Parameters:
        nu: Frequency (Hz)
        A: Amplitude at reference frequency (100 GHz)
        alpha: Spectral index
    
    Returns:
        Flux density (Jy)
    """
    return A * (nu / 1e11)**alpha


def bic(y, yfit, npar, sigma):
    """
    Bayesian Information Criterion
    
    BIC = k·ln(n) + χ²
    
    where k = number of parameters, n = number of data points
    
    Lower BIC = better model (penalizes complexity)
    """
    chi2 = np.sum(((y - yfit) / sigma)**2)
    n = len(y)
    return npar * np.log(n) + chi2


def main():
    """
    Main analysis routine
    
    1. Load spectrum data
    2. Load SSZ config (for κ_seg)
    3. Fit thermal (Planck) model
    4. Fit non-thermal (power-law) model
    5. Compare via ΔBIC
    6. Generate report + plot
    """
    ap = argparse.ArgumentParser(
        description='Fit thermal vs non-thermal models to continuum spectrum'
    )
    ap.add_argument('--spectrum', default='m87_spectrum.csv',
                    help='Input spectrum CSV (freq_Hz, flux_Jy, sigma_Jy)')
    ap.add_argument('--ssz', default='ssz_config.json',
                    help='SSZ configuration JSON (must contain kappa_seg_per_m)')
    ap.add_argument('--C', type=float, default=1e30,
                    help='Temperature seed factor: T_seed = C * |κ_seg| (default: 1e30)')
    ap.add_argument('--out', default='hawking_fit_report.md',
                    help='Output report file (Markdown)')
    ap.add_argument('--plot', default='hawking_fit_plot.png',
                    help='Output plot file (PNG)')
    args = ap.parse_args()

    # Load spectrum data
    print(f"Loading spectrum: {args.spectrum}")
    try:
        obs = pd.read_csv(args.spectrum)
    except FileNotFoundError:
        print(f"ERROR: Spectrum file not found: {args.spectrum}")
        print(f"Generate one with: python scripts/data_acquisition/fetch_m87_spectrum.py")
        sys.exit(1)
    
    # Validate columns
    required = ['freq_Hz', 'flux_Jy', 'sigma_Jy']
    missing = [col for col in required if col not in obs.columns]
    if missing:
        # Try alternative column names
        if 'frequency_Hz' in obs.columns:
            obs['freq_Hz'] = obs['frequency_Hz']
        if 'flux_density_Jy' in obs.columns:
            obs['flux_Jy'] = obs['flux_density_Jy']
        if 'flux_error_Jy' in obs.columns:
            obs['sigma_Jy'] = obs['flux_error_Jy']
        
        # Re-check
        missing = [col for col in required if col not in obs.columns]
        if missing:
            print(f"ERROR: Missing columns: {missing}")
            print(f"Available columns: {obs.columns.tolist()}")
            sys.exit(1)
    
    print(f"  Loaded {len(obs)} data points")
    print(f"  Frequency range: {obs['freq_Hz'].min():.3e} - {obs['freq_Hz'].max():.3e} Hz")

    # Load SSZ config
    print(f"Loading SSZ config: {args.ssz}")
    try:
        cfg = json.load(open(args.ssz, 'r', encoding='utf-8'))
    except FileNotFoundError:
        print(f"WARNING: SSZ config not found: {args.ssz}")
        print(f"Using default kappa_seg = 1e-13 m⁻¹")
        cfg = {'kappa_seg_per_m': 1e-13}

    kappa = abs(cfg.get('kappa_seg_per_m', 1e-13))
    T_seed = args.C * kappa
    
    print(f"  κ_seg = {kappa:.6e} m⁻¹")
    print(f"  T_seed = C × |κ_seg| = {args.C:.3e} × {kappa:.3e} = {T_seed:.6e} K")

    # Fit thermal (Planck-like) model
    print("\nFitting thermal (Planck) model...")
    try:
        p_seg, _ = curve_fit(
            planck_nu, obs['freq_Hz'], obs['flux_Jy'],
            sigma=obs['sigma_Jy'],
            p0=[T_seed, np.nanmedian(obs['flux_Jy'])],
            maxfev=20000,
            bounds=([1e-35, 0], [1e10, np.inf])
        )
        y_seg = planck_nu(obs['freq_Hz'], *p_seg)
        BIC_seg = bic(obs['flux_Jy'], y_seg, 2, obs['sigma_Jy'])
        
        print(f"  T_fit = {p_seg[0]:.6e} K")
        print(f"  A_fit = {p_seg[1]:.6e}")
        print(f"  BIC = {BIC_seg:.3f}")
        
        thermal_success = True
    except Exception as e:
        print(f"  FAILED: {e}")
        thermal_success = False
        BIC_seg = np.inf

    # Fit power-law model
    print("\nFitting power-law model...")
    try:
        p_pow, _ = curve_fit(
            powerlaw, obs['freq_Hz'], obs['flux_Jy'],
            sigma=obs['sigma_Jy'],
            p0=[np.nanmedian(obs['flux_Jy']), -0.7],
            maxfev=20000,
            bounds=([0, -10], [np.inf, 10])
        )
        y_pow = powerlaw(obs['freq_Hz'], *p_pow)
        BIC_pow = bic(obs['flux_Jy'], y_pow, 2, obs['sigma_Jy'])
        
        print(f"  A_fit = {p_pow[0]:.6e}")
        print(f"  α_fit = {p_pow[1]:.3f}")
        print(f"  BIC = {BIC_pow:.3f}")
        
        powerlaw_success = True
    except Exception as e:
        print(f"  FAILED: {e}")
        powerlaw_success = False
        BIC_pow = np.inf

    # ΔBIC comparison
    dBIC = BIC_pow - BIC_seg
    
    print(f"\n{'='*60}")
    print(f"ΔBIC = BIC_powerlaw - BIC_thermal = {dBIC:.3f}")
    if dBIC > 10:
        print("✅ Strong evidence for thermal model (ΔBIC > 10)")
        preference = "thermal"
    elif dBIC > 2:
        print("✅ Positive evidence for thermal model (ΔBIC > 2)")
        preference = "thermal"
    elif dBIC < -10:
        print("⚠️  Strong evidence for power-law model (ΔBIC < -10)")
        preference = "power-law"
    elif dBIC < -2:
        print("⚠️  Positive evidence for power-law model (ΔBIC < -2)")
        preference = "power-law"
    else:
        print("ℹ️  No strong preference (|ΔBIC| < 2)")
        preference = "inconclusive"
    print(f"{'='*60}")

    # Generate plot
    print(f"\nGenerating plot: {args.plot}")
    nu = obs['freq_Hz'].values
    nu_grid = np.logspace(np.log10(nu.min()), np.log10(nu.max()), 400)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data
    ax.errorbar(nu, obs['flux_Jy'], yerr=obs['sigma_Jy'],
                fmt='o', label='Observed data', color='black', alpha=0.7)
    
    # Fits
    if thermal_success:
        ax.plot(nu_grid, planck_nu(nu_grid, *p_seg),
                label=f'Thermal (Planck-like) | BIC={BIC_seg:.1f}',
                color='red', linewidth=2)
    
    if powerlaw_success:
        ax.plot(nu_grid, powerlaw(nu_grid, *p_pow),
                label=f'Power-law (α={p_pow[1]:.2f}) | BIC={BIC_pow:.1f}',
                color='blue', linewidth=2, linestyle='--')
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Flux density (Jy)', fontsize=12)
    ax.set_title(f'Hawking Proxy Fit | ΔBIC = {dBIC:.1f} ({preference})', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(args.plot, dpi=160)
    print(f"  Saved: {args.plot}")

    # Generate report
    print(f"\nGenerating report: {args.out}")
    lines = []
    lines.append('# Hawking Proxy Fit Report')
    lines.append('')
    lines.append('## SSZ Configuration')
    lines.append(f'- κ_seg (abs): {kappa:.6e} m⁻¹')
    lines.append(f'- T_seed = C × |κ_seg|, C = {args.C:.3e} → {T_seed:.6e} K')
    lines.append('')
    lines.append('## Data')
    lines.append(f'- Spectrum file: `{args.spectrum}`')
    lines.append(f'- Data points: {len(obs)}')
    lines.append(f'- Frequency range: {obs["freq_Hz"].min():.3e} - {obs["freq_Hz"].max():.3e} Hz')
    lines.append(f'- Flux range: {obs["flux_Jy"].min():.3e} - {obs["flux_Jy"].max():.3e} Jy')
    lines.append('')
    lines.append('## Best-fit Parameters')
    
    if thermal_success:
        lines.append(f'**Thermal (Planck-like):**')
        lines.append(f'- T = {p_seg[0]:.6e} K')
        lines.append(f'- A = {p_seg[1]:.6e}')
        lines.append(f'- BIC = {BIC_seg:.3f}')
    else:
        lines.append(f'**Thermal (Planck-like):** FAILED')
    
    lines.append('')
    
    if powerlaw_success:
        lines.append(f'**Power-law:**')
        lines.append(f'- A = {p_pow[0]:.6e}')
        lines.append(f'- α = {p_pow[1]:.3f}')
        lines.append(f'- BIC = {BIC_pow:.3f}')
    else:
        lines.append(f'**Power-law:** FAILED')
    
    lines.append('')
    lines.append('## Model Comparison')
    lines.append(f'- BIC(thermal) = {BIC_seg:.3f}')
    lines.append(f'- BIC(power-law) = {BIC_pow:.3f}')
    lines.append(f'- **ΔBIC = BIC_powerlaw - BIC_thermal = {dBIC:.3f}**')
    lines.append('')
    
    if dBIC > 10:
        lines.append('### Interpretation: ✅ **Strong evidence for thermal model**')
        lines.append('ΔBIC > 10 indicates the thermal (Planck-like) spectrum is strongly preferred.')
    elif dBIC > 2:
        lines.append('### Interpretation: ✅ **Positive evidence for thermal model**')
        lines.append('ΔBIC > 2 indicates the thermal model is preferred.')
    elif dBIC < -10:
        lines.append('### Interpretation: ⚠️  **Strong evidence for power-law model**')
        lines.append('ΔBIC < -10 indicates the power-law spectrum is strongly preferred.')
    elif dBIC < -2:
        lines.append('### Interpretation: ⚠️  **Positive evidence for power-law model**')
        lines.append('ΔBIC < -2 indicates the power-law model is preferred.')
    else:
        lines.append('### Interpretation: ℹ️  **No strong preference**')
        lines.append('|ΔBIC| < 2 indicates both models fit equally well.')
    
    lines.append('')
    lines.append('## Plot')
    lines.append(f'![Spectrum fit]({args.plot})')
    lines.append('')
    lines.append('---')
    lines.append('**Generated by:** `hawking_proxy_fit.py`  ')
    lines.append('**© 2025 Carmen Wrede, Lino Casu**  ')
    lines.append('**Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4**')
    
    open(args.out, 'w', encoding='utf-8').write('\n'.join(lines))
    print(f"  Saved: {args.out}")
    
    print("\n✅ Analysis complete!")
    print(f"   Report: {args.out}")
    print(f"   Plot: {args.plot}")


if __name__ == '__main__':
    main()
