#!/usr/bin/env python3
"""
Process ESO GRAVITY FITS files to CSV for SEG validation.

Usage:
    python scripts/process_eso_fits_to_csv.py --fits-dir data/raw_fetch/eso_fits --output data/emission_lines.csv

This script is the KEY PROCESSING STEP after downloading FITS files from ESO.
It extracts spectra, identifies emission lines, and creates the validation CSV.

See docs/MANUAL_ESO_DATA_ACQUISITION_GUIDE.md for complete workflow.
"""

import argparse
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from astropy.io import fits
from scipy.signal import find_peaks

# Physical constants
G = 6.67430e-11
c = 299792458.0
M_sun = 1.98847e30
PHI = (1 + np.sqrt(5)) / 2

# Rest wavelengths (nm)
REST_LINES = {
    'Br_gamma': 2166.0,
    'He_I': 2058.0,
    'Pa_alpha': 1876.0,
}

def extract_spectrum(fits_file):
    """Extract wavelength and flux from FITS."""
    try:
        with fits.open(fits_file) as hdul:
            hdr = hdul[0].header
            target = hdr.get('OBJECT', 'Unknown')
            obs_date = hdr.get('DATE-OBS', 'Unknown')
            
            # Find spectrum extension
            for i, hdu in enumerate(hdul):
                if hdu.data is not None and len(hdu.data.shape) > 0:
                    data = hdu.data
                    h = hdu.header
                    
                    # Extract wavelength
                    if hasattr(data.dtype, 'names') and 'WAVE' in data.dtype.names:
                        wave = data['WAVE']
                    else:
                        crval = h.get('CRVAL1', 0)
                        cdelt = h.get('CDELT1', 1)
                        naxis = h.get('NAXIS1', len(data))
                        wave = crval + np.arange(naxis) * cdelt
                    
                    # Extract flux
                    if hasattr(data.dtype, 'names') and 'FLUX' in data.dtype.names:
                        flux = data['FLUX']
                    else:
                        flux = data
                    
                    # Convert to nm if needed
                    if np.median(wave) < 10:
                        wave = wave * 1000
                    elif np.median(wave) > 10000:
                        wave = wave / 10
                    
                    return {
                        'target': target,
                        'date': obs_date,
                        'wavelength': wave.flatten(),
                        'flux': flux.flatten(),
                        'file': fits_file.name
                    }
    except Exception as e:
        print(f"Error {fits_file.name}: {e}")
    return None

def find_lines(wavelength, flux):
    """Find emission peaks."""
    flux_clean = np.nan_to_num(flux, 0)
    if len(flux_clean) == 0:
        return [], []
    flux_norm = (flux_clean - np.min(flux_clean)) / (np.max(flux_clean) - np.min(flux_clean) + 1e-10)
    peaks, _ = find_peaks(flux_norm, prominence=0.1, width=3)
    return wavelength[peaks], flux[peaks]

def match_line(obs_wave, tolerance=10.0):
    """Match observed wavelength to known line."""
    for name, rest_wave in REST_LINES.items():
        z = (obs_wave - rest_wave) / rest_wave
        if abs(obs_wave - rest_wave * (1 + z)) < tolerance:
            return name, rest_wave, z
    return None, None, None

def seg_prediction(M_solar, r_m, v_los, v_tot):
    """Calculate SEG z_geom_hint."""
    M_kg = M_solar * M_sun
    r_s = 2 * G * M_kg / (c**2)
    delta_M = 98.01 * np.exp(-2.7177e4 * r_s) + 1.96
    M_eff = M_kg * delta_M
    beta = 2 * G * M_eff / (r_m * c**2)
    z_grav = (1 - beta * PHI / 2)**(-0.5) - 1
    gamma = 1 / np.sqrt(1 - (v_tot / c)**2)
    z_kin = (1 + v_los / c) * gamma - 1
    return z_grav + z_kin

def main():
    parser = argparse.ArgumentParser(description='Process ESO FITS to CSV')
    parser.add_argument('--fits-dir', required=True, help='Directory with FITS files')
    parser.add_argument('--output', required=True, help='Output CSV file')
    parser.add_argument('--params', help='JSON file with stellar parameters')
    args = parser.parse_args()
    
    fits_dir = Path(args.fits_dir)
    if not fits_dir.exists():
        print(f"Error: {fits_dir} not found")
        return 1
    
    # Load parameters if provided
    params = {}
    if args.params:
        with open(args.params) as f:
            params = json.load(f)
    
    print(f"Processing FITS files from {fits_dir}...")
    
    all_lines = []
    for fits_file in sorted(fits_dir.glob('*.fits')):
        print(f"  {fits_file.name}")
        spectrum = extract_spectrum(fits_file)
        if not spectrum:
            continue
        
        peak_waves, peak_fluxes = find_lines(spectrum['wavelength'], spectrum['flux'])
        print(f"    Found {len(peak_waves)} peaks")
        
        for obs_wave in peak_waves:
            line_name, rest_wave, z = match_line(obs_wave)
            if line_name:
                # Get parameters for this target
                target_params = params.get(spectrum['target'], {})
                
                row = {
                    'case': f"{spectrum['target']}_{spectrum['date']}",
                    'target': spectrum['target'],
                    'obs_date': spectrum['date'],
                    'line_name': line_name,
                    'lambda_rest_nm': rest_wave,
                    'lambda_obs_nm': obs_wave,
                    'z': z,
                    'M_solar': target_params.get('M_solar'),
                    'a_m': target_params.get('a_m'),
                    'e': target_params.get('e'),
                    'r_emit_m': target_params.get('r_emit_m'),
                    'v_los_mps': target_params.get('v_los_mps'),
                    'v_tot_mps': target_params.get('v_tot_mps'),
                }
                
                # Calculate SEG prediction if parameters available
                if all(row.get(k) for k in ['M_solar', 'r_emit_m', 'v_los_mps', 'v_tot_mps']):
                    row['z_geom_hint'] = seg_prediction(
                        row['M_solar'], row['r_emit_m'], 
                        row['v_los_mps'], row['v_tot_mps']
                    )
                
                all_lines.append(row)
                print(f"      {line_name}: λ={obs_wave:.2f}nm, z={z:.6f}")
    
    df = pd.DataFrame(all_lines)
    df.to_csv(args.output, index=False)
    print(f"\n✅ Created {args.output} with {len(df)} emission lines")
    return 0

if __name__ == '__main__':
    sys.exit(main())
