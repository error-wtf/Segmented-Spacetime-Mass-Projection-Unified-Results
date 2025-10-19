#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch M87 Continuum Spectrum from NED (NASA/IPAC Extragalactic Database)

Downloads photometry data for M87 (or other sources) from NED and converts
to CSV format compatible with test_hawking_spectrum_continuum.py

Requires: astroquery
Install: pip install astroquery

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import argparse
import sys
import os
import numpy as np
import pandas as pd

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


def main():
    """
    Fetch continuum spectrum from NED
    
    Usage:
        python fetch_m87_spectrum.py --name M87 --minGHz 30 --maxGHz 1000
        python fetch_m87_spectrum.py --name "Sgr A*" --out sgra_spectrum.csv
    """
    ap = argparse.ArgumentParser(
        description='Fetch continuum spectrum from NED (NASA/IPAC Extragalactic Database)'
    )
    ap.add_argument('--name', type=str, default='M87',
                    help='Source name (default: M87)')
    ap.add_argument('--minGHz', type=float, default=30.0,
                    help='Minimum frequency in GHz (default: 30)')
    ap.add_argument('--maxGHz', type=float, default=1000.0,
                    help='Maximum frequency in GHz (default: 1000)')
    ap.add_argument('--out', type=str, default='m87_spectrum.csv',
                    help='Output CSV file (default: m87_spectrum.csv)')
    ap.add_argument('--M_solar', type=float, default=6.5e9,
                    help='Black hole mass in solar masses (default: 6.5e9 for M87*)')
    ap.add_argument('--r_emit_m', type=float, default=1.2e13,
                    help='Emission radius in meters (default: 1.2e13 for M87*)')
    args = ap.parse_args()

    print(f"Fetching photometry data for {args.name} from NED...")
    
    try:
        from astroquery.ned import Ned
    except ImportError:
        print("ERROR: astroquery not installed!")
        print("Install with: pip install astroquery")
        sys.exit(1)
    
    try:
        # Query NED for photometry
        tab = Ned.get_table(args.name, table='photometry')
        df = tab.to_pandas()
        df.columns = [c.lower() for c in df.columns]
        
        print(f"Downloaded {len(df)} photometry points from NED")
        
    except Exception as e:
        print(f"ERROR querying NED: {e}")
        sys.exit(1)

    # Extract frequency in Hz
    if 'frequency' in df.columns:
        freq = pd.to_numeric(df['frequency'], errors='coerce')
    else:
        # Try wavelength (Angstrom -> m) -> Hz
        c = 299792458.0  # m/s
        wl = pd.to_numeric(df.get('wavelength'), errors='coerce')
        if wl is None:
            raise RuntimeError('No frequency or wavelength column found in NED data')
        wl_m = wl * 1e-10  # Angstrom to meters
        freq = c / wl_m
    
    df['freq_Hz'] = freq

    # Extract flux in Jy (prefer direct Jy columns)
    jy_cols = [c for c in df.columns if ('flux' in c and 'jy' in c)]
    if not jy_cols and 'flux density' in df.columns:
        jy_cols = ['flux density']
    if not jy_cols:
        print("Available columns:", df.columns.tolist())
        raise RuntimeError('No Jy flux column detected. Inspect NED columns for this target.')

    flux = pd.to_numeric(df[jy_cols[0]], errors='coerce')

    # Extract uncertainty (Jy) — try to find or assume 10%
    sig_cols = [c for c in df.columns if (('uncert' in c or 'error' in c) and 'jy' in c)]
    if sig_cols:
        sigma = pd.to_numeric(df[sig_cols[0]], errors='coerce')
    else:
        print("No uncertainty column found, assuming 10% error")
        sigma = 0.1 * flux

    # Build output DataFrame
    out = pd.DataFrame({
        'source': args.name,
        'frequency_Hz': df['freq_Hz'],
        'flux_density_Jy': flux,
        'flux_error_Jy': sigma,
        'M_solar': args.M_solar,
        'r_emit_m': args.r_emit_m,
        'instrument': df.get('refcode', 'NED'),  # Reference code as instrument
        'observation_date': df.get('published', 'unknown')
    })
    
    # Clean data
    out = out.dropna(subset=['frequency_Hz', 'flux_density_Jy', 'flux_error_Jy'])
    
    # Filter by frequency range
    freq_min = args.minGHz * 1e9
    freq_max = args.maxGHz * 1e9
    out = out[(out['frequency_Hz'] >= freq_min) & (out['frequency_Hz'] <= freq_max)]
    
    # Filter positive fluxes
    out = out[(out['flux_density_Jy'] > 0) & (out['flux_error_Jy'] > 0)]
    
    # Sort by frequency
    out = out.sort_values('frequency_Hz')
    
    # Save
    out.to_csv(args.out, index=False)
    
    print(f"\n✅ Success!")
    print(f"   Wrote {len(out)} data points to {args.out}")
    print(f"   Frequency range: {out['frequency_Hz'].min():.3e} - {out['frequency_Hz'].max():.3e} Hz")
    print(f"   Flux range: {out['flux_density_Jy'].min():.3e} - {out['flux_density_Jy'].max():.3e} Jy")
    print(f"\n📊 To test with Hawking spectrum analysis:")
    print(f"   python scripts/tests/test_hawking_spectrum_continuum.py")


if __name__ == '__main__':
    main()
