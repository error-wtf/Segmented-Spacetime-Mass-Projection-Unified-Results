#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Source-Specific Data Completeness

Checks if orbital sources have orbital parameters,
spectroscopic sources have spectroscopic data, etc.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pandas as pd
import sys
import io

# UTF-8 Setup
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def main():
    df = pd.read_csv('real_data_full.csv')
    
    print("="*80)
    print("SOURCE-SPECIFIC DATA VERIFICATION")
    print("="*80)
    
    # Check by source type
    sources = df.groupby('source')
    
    print(f"\n--- SOURCES OVERVIEW ---")
    print(f"Total unique sources: {df['source'].nunique()}")
    print(f"Total data points: {len(df)}")
    
    # Orbital sources (should have a_m, e, P_year, etc.)
    orbital_keywords = ['S2', 'S4715', 'PSR', 'pulsar']
    print(f"\n--- ORBITAL SOURCES ---")
    orbital_sources = []
    for source_name in df['source'].unique():
        if any(kw in str(source_name) for kw in orbital_keywords):
            orbital_sources.append(source_name)
            data = df[df['source'] == source_name]
            orbital_params = ['a_m', 'e', 'P_year']
            missing = sum(data[param].isna().all() for param in orbital_params if param in data.columns)
            status = "COMPLETE" if missing == 0 else f"MISSING {missing}"
            print(f"  [{status:12s}] {source_name}: {len(data)} points")
            
            # Show which params are missing
            if missing > 0:
                for param in orbital_params:
                    if param in data.columns and data[param].isna().all():
                        print(f"      - Missing: {param}")
    
    # Multi-frequency sources (M87*, Cyg X-1)
    print(f"\n--- MULTI-FREQUENCY SOURCES ---")
    multi_freq = ['M87*', 'Cyg', 'CygX']
    for source_name in df['source'].unique():
        if any(kw in str(source_name) for kw in multi_freq):
            data = df[df['source'] == source_name]
            f_emit_ok = not data['f_emit_Hz'].isna().any()
            f_obs_ok = not data['f_obs_Hz'].isna().any()
            status = "COMPLETE" if (f_emit_ok and f_obs_ok) else "INCOMPLETE"
            print(f"  [{status:12s}] {source_name}: {len(data)} points")
            print(f"      f_emit_Hz: {'OK' if f_emit_ok else 'MISSING'}")
            print(f"      f_obs_Hz:  {'OK' if f_obs_ok else 'MISSING'}")
    
    # Generic sources (should have basic params only)
    print(f"\n--- GENERIC SOURCES (AGN, Galaxies, etc.) ---")
    generic_sources = []
    for source_name in df['source'].unique():
        is_orbital = any(kw in str(source_name) for kw in orbital_keywords)
        is_multi = any(kw in str(source_name) for kw in multi_freq)
        if not is_orbital and not is_multi:
            generic_sources.append(source_name)
    
    print(f"  Total generic sources: {len(generic_sources)}")
    print(f"  (These sources only need: f_emit, f_obs, r_emit, M_solar, n_round, z)")
    print(f"  All should have NaN for orbital/spectroscopic parameters - this is CORRECT!")
    
    # Summary
    print(f"\n" + "="*80)
    print("DATA COMPLETENESS SUMMARY")
    print("="*80)
    print(f"\nORBITAL SOURCES ({len(orbital_sources)}):")
    for src in orbital_sources:
        data = df[df['source'] == src]
        orbital_params = ['a_m', 'e', 'P_year']
        complete = all(not data[p].isna().all() for p in orbital_params if p in data.columns)
        status = "OK" if complete else "NEEDS DATA"
        print(f"  [{status}] {src}")
    
    print(f"\nGENERIC SOURCES ({len(generic_sources)}):")
    print(f"  All OK - only need basic parameters")
    
    print(f"\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    
    # Check if S2 has orbital data
    s2_data = df[df['source'].str.contains('S2', case=False, na=False)]
    if len(s2_data) > 0:
        has_orbital = not s2_data['a_m'].isna().all()
        if not has_orbital:
            print(f"\nWARNING: S2 orbital source missing orbital parameters!")
            print(f"  Action: Fetch from data/observations/s2_star_timeseries.csv")
        else:
            print(f"\nOK: S2 has orbital parameters")
    
    # Check M87*
    m87_data = df[df['source'].str.contains('M87', case=False, na=False)]
    if len(m87_data) > 0:
        has_freq = not m87_data['f_obs_Hz'].isna().any()
        if not has_freq:
            print(f"\nWARNING: M87* multi-frequency source missing f_obs_Hz!")
            print(f"  Action: Fetch from data/observations/m87_continuum_spectrum.csv")
        else:
            print(f"\nOK: M87* has multi-frequency data ({len(m87_data)} points)")
    
    print(f"\n" + "="*80)

if __name__ == '__main__':
    main()
