#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time-Series Data Loader for SSZ Theory Predictions Tests

Loads orbital time-series data (e.g., S2 star observations)
for Information Preservation (Jacobian reconstruction) tests.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pandas as pd
from pathlib import Path
import numpy as np

def load_s2_timeseries(csv_path):
    """
    Load S2 star time-series data for Jacobian reconstruction.
    
    Parameters
    ----------
    csv_path : str or Path
        Path to CSV file with S2 observations
    
    Returns
    -------
    dict
        Dictionary with source names as keys, DataFrames as values
        Only includes sources with ≥3 observations
    
    Required CSV Columns
    -------------------
    - source : str - Source identifier
    - f_emit_Hz : float - Rest-frame frequency
    - f_obs_Hz : float - Observed frequency
    - r_emit_m : float - Emission radius
    - M_solar : float - Central mass in solar masses
    
    Optional Columns
    ---------------
    - observation_date : str - ISO date or MJD
    - orbital_phase : float - 0-1
    - v_los_mps : float - Line-of-sight velocity
    - spectral_line : str - Line identifier (e.g., 'H-alpha')
    
    Example
    -------
    >>> sources = load_s2_timeseries('data/observations/s2_star_timeseries.csv')
    >>> print(f"Loaded {len(sources)} sources")
    >>> for name, df in sources.items():
    ...     print(f"{name}: {len(df)} observations")
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Load data
    df = pd.read_csv(csv_path)
    
    # Validate required columns
    required = ['source', 'f_emit_Hz', 'f_obs_Hz', 'r_emit_m', 'M_solar']
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Filter and group
    sources = {}
    for source, group in df.groupby('source'):
        # Need at least 3 observations for Jacobian
        if len(group) >= 3:
            # Sort by orbital phase if available, else by r_emit_m
            if 'orbital_phase' in group.columns:
                group = group.sort_values('orbital_phase')
            else:
                group = group.sort_values('r_emit_m')
            
            sources[source] = group.reset_index(drop=True)
    
    return sources


def validate_timeseries(df):
    """
    Validate time-series data for Jacobian reconstruction.
    
    Checks:
    - Sufficient variation in f_emit_Hz
    - Monotonic orbital progression (if phase available)
    - No duplicate observations
    - Finite values
    
    Parameters
    ----------
    df : DataFrame
        Single-source time-series data
    
    Returns
    -------
    dict
        Validation results with bool flags and statistics
    """
    results = {}
    
    # Check f_emit variation
    f_emit_unique = df['f_emit_Hz'].nunique()
    f_emit_std = df['f_emit_Hz'].std()
    results['sufficient_f_emit_variation'] = (f_emit_unique >= 2 and f_emit_std > 1e6)
    results['f_emit_unique_count'] = f_emit_unique
    results['f_emit_std'] = f_emit_std
    
    # Check for duplicates
    duplicates = df.duplicated(subset=['f_emit_Hz', 'f_obs_Hz']).sum()
    results['has_duplicates'] = (duplicates > 0)
    results['duplicate_count'] = duplicates
    
    # Check monotonicity (if orbital_phase available)
    if 'orbital_phase' in df.columns:
        phases = df['orbital_phase'].values
        is_monotonic = np.all(np.diff(phases) >= 0)
        results['orbital_phase_monotonic'] = is_monotonic
    else:
        results['orbital_phase_monotonic'] = None
    
    # Check finite values
    finite_check = df[['f_emit_Hz', 'f_obs_Hz', 'r_emit_m']].apply(lambda x: np.isfinite(x).all())
    results['all_finite'] = finite_check.all()
    results['finite_by_column'] = finite_check.to_dict()
    
    # Overall pass/fail
    results['valid_for_jacobian'] = (
        results['sufficient_f_emit_variation'] and
        not results['has_duplicates'] and
        results['all_finite']
    )
    
    return results


def print_timeseries_summary(sources_dict):
    """
    Print summary statistics for loaded time-series data.
    
    Parameters
    ----------
    sources_dict : dict
        Output from load_s2_timeseries()
    """
    print("="*80)
    print("TIME-SERIES DATA SUMMARY")
    print("="*80)
    print(f"Total sources loaded: {len(sources_dict)}")
    print()
    
    for source, df in sources_dict.items():
        print(f"Source: {source}")
        print(f"  Observations: {len(df)}")
        
        # Check validation
        validation = validate_timeseries(df)
        status = "✅ VALID" if validation['valid_for_jacobian'] else "❌ INVALID"
        print(f"  Status: {status}")
        
        # Frequency stats
        f_emit_range = df['f_emit_Hz'].max() - df['f_emit_Hz'].min()
        f_obs_range = df['f_obs_Hz'].max() - df['f_obs_Hz'].min()
        print(f"  f_emit range: {f_emit_range:.4e} Hz ({validation['f_emit_unique_count']} unique)")
        print(f"  f_obs range: {f_obs_range:.4e} Hz")
        
        # Radius stats
        r_min = df['r_emit_m'].min()
        r_max = df['r_emit_m'].max()
        print(f"  r_emit range: {r_min:.4e} - {r_max:.4e} m")
        
        if validation['has_duplicates']:
            print(f"  ⚠️  Warning: {validation['duplicate_count']} duplicate observations")
        
        if not validation['sufficient_f_emit_variation']:
            print(f"  ⚠️  Warning: Insufficient f_emit variation (need multiple emission lines)")
        
        print()
    
    print("="*80)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python load_timeseries.py <path_to_csv>")
        print("\nExample:")
        print("  python load_timeseries.py data/observations/s2_star_timeseries.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    try:
        sources = load_s2_timeseries(csv_path)
        print_timeseries_summary(sources)
        
        # Additional details
        total_obs = sum(len(df) for df in sources.values())
        print(f"Total observations across all sources: {total_obs}")
        
        # Validation summary
        valid_count = sum(1 for df in sources.values() if validate_timeseries(df)['valid_for_jacobian'])
        print(f"Sources valid for Jacobian reconstruction: {valid_count}/{len(sources)}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
