#!/usr/bin/env python3
"""
Fetch Real Astronomical Data for Energy Framework Testing
Downloads real observations from GAIA, SIMBAD, and NED

Authors: Carmen Wrede & Lino Casu
License: ANTI-CAPITALIST SOFTWARE LICENSE v1.4
Date: 2025-12-07
"""

import numpy as np
import pandas as pd
from pathlib import Path
import time

# Try to import astroquery
try:
    from astroquery.gaia import Gaia
    from astroquery.simbad import Simbad
    from astroquery.ned import Ned
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    ASTROQUERY_AVAILABLE = True
except ImportError:
    print("[WARNING] astroquery not installed. Install with: pip install astroquery")
    ASTROQUERY_AVAILABLE = False

# Physical constants
c = 299792458.0  # m/s
G = 6.67430e-11  # m^3 kg^-1 s^-2
M_sun = 1.989e30  # kg
R_sun = 6.96e8    # m

def fetch_gaia_stars(n_stars=100):
    """Fetch real star data from GAIA DR3"""
    
    if not ASTROQUERY_AVAILABLE:
        print("[ERROR] astroquery required for GAIA access")
        return pd.DataFrame()
    
    print(f"[GAIA] Fetching {n_stars} stars from GAIA DR3...")
    
    # Query GAIA for stars with complete data
    query = f"""
    SELECT TOP {n_stars}
        source_id, ra, dec, parallax, phot_g_mean_mag, 
        radial_velocity, teff_gspphot, radius_gspphot, mass_flame
    FROM gaiadr3.gaia_source
    WHERE parallax > 1.0
        AND phot_g_mean_mag < 12
        AND radial_velocity IS NOT NULL
        AND teff_gspphot IS NOT NULL
        AND radius_gspphot IS NOT NULL
        AND mass_flame IS NOT NULL
    ORDER BY RANDOM()
    """
    
    try:
        job = Gaia.launch_job_async(query)
        results = job.get_results()
        
        # Convert to pandas
        df = results.to_pandas()
        
        # Add metadata
        df['source'] = 'GAIA_DR3'
        df['type'] = 'star'
        
        print(f"[GAIA] Retrieved {len(df)} stars")
        return df
        
    except Exception as e:
        print(f"[ERROR] GAIA query failed: {e}")
        return pd.DataFrame()


def fetch_simbad_objects(object_types=['Star', 'WD', 'NS', 'BH'], n_per_type=25):
    """Fetch real objects from SIMBAD"""
    
    if not ASTROQUERY_AVAILABLE:
        print("[ERROR] astroquery required for SIMBAD access")
        return pd.DataFrame()
    
    print(f"[SIMBAD] Fetching objects from SIMBAD...")
    
    # Configure SIMBAD
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('otype', 'rv_value', 'plx', 'flux(V)')
    
    all_data = []
    
    for obj_type in object_types:
        print(f"  Fetching {obj_type}...")
        try:
            # Query by object type
            result = custom_simbad.query_criteria(
                otype=obj_type,
                nbRef='>10',  # Well-studied objects
                max_rows=n_per_type
            )
            
            if result is not None:
                df = result.to_pandas()
                df['object_type'] = obj_type
                df['source'] = 'SIMBAD'
                all_data.append(df)
                print(f"    Retrieved {len(df)} {obj_type} objects")
                
        except Exception as e:
            print(f"    [WARNING] Failed to fetch {obj_type}: {e}")
        
        time.sleep(1)  # Rate limiting
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        print(f"[SIMBAD] Total: {len(combined)} objects")
        return combined
    else:
        return pd.DataFrame()


def fetch_ned_galaxies(n_galaxies=50):
    """Fetch galaxy data from NED"""
    
    if not ASTROQUERY_AVAILABLE:
        print("[ERROR] astroquery required for NED access")
        return pd.DataFrame()
    
    print(f"[NED] Fetching {n_galaxies} galaxies from NED...")
    
    try:
        # Query for well-known galaxies
        result = Ned.query_refcode('2006AJ....131.1163S')  # Nearby galaxies catalog
        
        if result is not None:
            df = result.to_pandas()
            df = df.head(n_galaxies)  # Limit to n_galaxies
            df['source'] = 'NED'
            df['type'] = 'galaxy'
            
            print(f"[NED] Retrieved {len(df)} galaxies")
            return df
        else:
            print("[NED] No results")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"[ERROR] NED query failed: {e}")
        return pd.DataFrame()


def create_fallback_dataset():
    """Create dataset from well-known astronomical objects (no API needed)"""
    
    print("[FALLBACK] Creating dataset from well-known objects...")
    
    # Well-known objects with published data
    objects = [
        # Stars
        {'name': 'Sun', 'type': 'star', 'mass_msun': 1.0, 'radius_rsun': 1.0, 'source': 'Published'},
        {'name': 'Sirius A', 'type': 'star', 'mass_msun': 2.063, 'radius_rsun': 1.711, 'source': 'Published'},
        {'name': 'Proxima Centauri', 'type': 'star', 'mass_msun': 0.122, 'radius_rsun': 0.154, 'source': 'Published'},
        {'name': 'Betelgeuse', 'type': 'red_giant', 'mass_msun': 16.5, 'radius_rsun': 764, 'source': 'Published'},
        
        # White Dwarfs
        {'name': 'Sirius B', 'type': 'white_dwarf', 'mass_msun': 1.018, 'radius_rsun': 0.0084, 'source': 'Published'},
        {'name': '40 Eridani B', 'type': 'white_dwarf', 'mass_msun': 0.573, 'radius_rsun': 0.014, 'source': 'Published'},
        
        # Neutron Stars
        {'name': 'PSR J0348+0432', 'type': 'neutron_star', 'mass_msun': 2.01, 'radius_rsun': 1.4e-5, 'source': 'Published'},
        {'name': 'PSR J0740+6620', 'type': 'neutron_star', 'mass_msun': 2.08, 'radius_rsun': 1.5e-5, 'source': 'Published'},
        
        # Black Holes (stellar)
        {'name': 'Cygnus X-1', 'type': 'stellar_bh', 'mass_msun': 21.2, 'radius_rsun': 6.2e-5, 'source': 'Published'},
        {'name': 'GRO J1655-40', 'type': 'stellar_bh', 'mass_msun': 6.3, 'radius_rsun': 1.9e-5, 'source': 'Published'},
        
        # Supermassive Black Holes
        {'name': 'Sgr A*', 'type': 'smbh', 'mass_msun': 4.297e6, 'radius_rsun': 0.127, 'source': 'Published'},
        {'name': 'M87*', 'type': 'smbh', 'mass_msun': 6.5e9, 'radius_rsun': 192, 'source': 'Published'},
        {'name': 'M31 BH', 'type': 'smbh', 'mass_msun': 1.4e8, 'radius_rsun': 4.1, 'source': 'Published'},
    ]
    
    df = pd.DataFrame(objects)
    
    # Calculate physical properties
    df['mass_kg'] = df['mass_msun'] * M_sun
    df['radius_m'] = df['radius_rsun'] * R_sun
    df['schwarzschild_radius_m'] = 2 * G * df['mass_kg'] / c**2
    df['R_over_rs'] = df['radius_m'] / df['schwarzschild_radius_m']
    
    print(f"[FALLBACK] Created dataset with {len(df)} well-known objects")
    return df


def fetch_complete_dataset(use_api=True):
    """Fetch complete astronomical dataset"""
    
    print("="*80)
    print("FETCHING REAL ASTRONOMICAL DATA")
    print("="*80)
    print("")
    
    all_datasets = []
    
    if use_api and ASTROQUERY_AVAILABLE:
        # Try to fetch from APIs
        print("Attempting to fetch from astronomical databases...")
        print("")
        
        # GAIA stars
        gaia_data = fetch_gaia_stars(n_stars=50)
        if not gaia_data.empty:
            all_datasets.append(gaia_data)
        
        # SIMBAD objects
        simbad_data = fetch_simbad_objects(n_per_type=10)
        if not simbad_data.empty:
            all_datasets.append(simbad_data)
        
        # NED galaxies
        ned_data = fetch_ned_galaxies(n_galaxies=20)
        if not ned_data.empty:
            all_datasets.append(ned_data)
    
    # Always include fallback dataset with well-known objects
    fallback = create_fallback_dataset()
    all_datasets.append(fallback)
    
    # Combine all datasets
    if len(all_datasets) > 0:
        combined = pd.concat(all_datasets, ignore_index=True)
        print("")
        print("="*80)
        print(f"TOTAL: {len(combined)} real astronomical objects fetched")
        print("="*80)
        return combined
    else:
        print("[ERROR] No data could be fetched")
        return pd.DataFrame()


def save_dataset(df, filename="data/real_astronomical_data.csv"):
    """Save dataset to CSV"""
    
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    print("")
    print("="*80)
    print(f"SAVING DATASET: {filepath}")
    print("="*80)
    
    df.to_csv(filepath, index=False)
    
    file_size = filepath.stat().st_size
    
    print(f"[OK] Dataset saved!")
    print(f"     File: {filepath.resolve()}")
    print(f"     Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"     Objects: {len(df)}")
    print("")
    
    # Print breakdown
    if 'type' in df.columns:
        print("Breakdown by type:")
        for obj_type in df['type'].unique():
            count = len(df[df['type'] == obj_type])
            print(f"  {obj_type:15s}: {count:4d} objects")
    
    if 'source' in df.columns:
        print("")
        print("Breakdown by source:")
        for source in df['source'].unique():
            count = len(df[df['source'] == source])
            print(f"  {source:15s}: {count:4d} objects")
    
    print("="*80)
    return filepath


if __name__ == "__main__":
    print("")
    print("="*80)
    print("REAL ASTRONOMICAL DATA FETCHER")
    print("="*80)
    print("Purpose: Fetch real astronomical objects for energy framework")
    print("Sources: GAIA DR3, SIMBAD, NED, Published catalogs")
    print("")
    
    # Check if astroquery is available
    if not ASTROQUERY_AVAILABLE:
        print("[WARNING] astroquery not installed")
        print("          Will use fallback dataset with well-known objects")
        print("          Install with: pip install astroquery")
        print("")
        use_api = False
    else:
        print("[OK] astroquery available - will fetch from APIs")
        print("")
        use_api = True
    
    # Fetch data
    df = fetch_complete_dataset(use_api=use_api)
    
    if not df.empty:
        # Save dataset
        filepath = save_dataset(df)
        
        print("")
        print("[SUCCESS] Real astronomical data fetched and saved!")
        print(f"          Use this file for energy framework testing")
        print(f"          File: {filepath}")
    else:
        print("[ERROR] Failed to fetch data")
        exit(1)
