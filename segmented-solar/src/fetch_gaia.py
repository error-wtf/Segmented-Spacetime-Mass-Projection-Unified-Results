"""
GAIA data fetching module for nearby stars.
Retrieves stellar positions, proper motions, and parallaxes from GAIA DR3.
"""

import pandas as pd
import numpy as np
from astroquery.gaia import Gaia
from astropy import units as u
from astropy.coordinates import SkyCoord
import os
from typing import Optional, Tuple

def query_gaia_stars(maxdist_pc: float = 30, 
                    gmag_max: float = 10,
                    cache_dir: str = "data/raw",
                    use_cache: bool = True) -> pd.DataFrame:
    """
    Query GAIA DR3 for nearby stars.
    
    Parameters:
    -----------
    maxdist_pc : float
        Maximum distance in parsecs
    gmag_max : float  
        Maximum G magnitude (brightness limit)
    cache_dir : str
        Directory to cache results
    use_cache : bool
        Whether to use cached results if available
        
    Returns:
    --------
    DataFrame with columns: source_id, ra, dec, parallax, pmra, pmdec, 
                           phot_g_mean_mag, dist_pc
    """
    
    cache_file = os.path.join(cache_dir, f"gaia_stars_d{maxdist_pc}_g{gmag_max}.csv")
    
    # Check cache first
    if use_cache and os.path.exists(cache_file):
        print(f"Loading cached GAIA data from {cache_file}")
        return pd.read_csv(cache_file)
    
    print(f"Querying GAIA DR3 for stars within {maxdist_pc} pc, G < {gmag_max}")
    
    # Set GAIA table
    Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
    
    # ADQL query for nearby bright stars
    query = f"""
    SELECT source_id, ra, dec, parallax, parallax_error,
           pmra, pmra_error, pmdec, pmdec_error,
           phot_g_mean_mag, bp_rp, teff_gspphot
    FROM gaiadr3.gaia_source
    WHERE parallax > {1000.0/maxdist_pc}
      AND parallax_over_error > 5
      AND phot_g_mean_mag < {gmag_max}
      AND pmra IS NOT NULL 
      AND pmdec IS NOT NULL
    ORDER BY phot_g_mean_mag ASC
    """
    
    try:
        # Launch asynchronous job
        job = Gaia.launch_job_async(query)
        table = job.get_results()
        
        # Convert to pandas DataFrame
        df = table.to_pandas()
        
        # Calculate distances
        df["dist_pc"] = 1000.0 / df["parallax"]
        
        # Filter out negative parallaxes (unphysical)
        df = df[df["parallax"] > 0].copy()
        
        print(f"Retrieved {len(df)} stars from GAIA DR3")
        
        # Cache results
        os.makedirs(cache_dir, exist_ok=True)
        df.to_csv(cache_file, index=False)
        print(f"Cached results to {cache_file}")
        
        return df
        
    except Exception as e:
        print(f"Error querying GAIA: {e}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            'source_id', 'ra', 'dec', 'parallax', 'parallax_error',
            'pmra', 'pmra_error', 'pmdec', 'pmdec_error', 
            'phot_g_mean_mag', 'bp_rp', 'teff_gspphot', 'dist_pc'
        ])

def gaia_to_cartesian(df: pd.DataFrame, epoch: str = "2025.0") -> np.ndarray:
    """
    Convert GAIA astrometric data to Cartesian coordinates.
    
    Parameters:
    -----------
    df : DataFrame
        GAIA data with ra, dec, parallax, pmra, pmdec columns
    epoch : str
        Epoch for proper motion correction (e.g., "2025.0")
        
    Returns:
    --------
    xyz : np.ndarray, shape (N, 3)
        Cartesian coordinates in AU (heliocentric)
    """
    
    if len(df) == 0:
        return np.empty((0, 3))
    
    # Create SkyCoord object
    coords = SkyCoord(
        ra=df['ra'].values * u.deg,
        dec=df['dec'].values * u.deg, 
        distance=(1000.0 / df['parallax'].values) * u.pc,
        pm_ra_cosdec=df['pmra'].fillna(0).values * u.mas/u.yr,
        pm_dec=df['pmdec'].fillna(0).values * u.mas/u.yr,
        obstime="J2016.0"  # GAIA DR3 reference epoch
    )
    
    # Apply proper motion to target epoch if specified
    if epoch != "2016.0":
        from astropy.time import Time
        target_time = Time(float(epoch), format='decimalyear')
        coords = coords.apply_space_motion(new_obstime=target_time)
    
    # Convert to Cartesian (heliocentric ecliptic)
    xyz_icrs = coords.cartesian
    
    # Convert to AU
    xyz = np.column_stack([
        xyz_icrs.x.to(u.AU).value,
        xyz_icrs.y.to(u.AU).value, 
        xyz_icrs.z.to(u.AU).value
    ])
    
    return xyz

def estimate_stellar_masses(df: pd.DataFrame) -> np.ndarray:
    """
    Estimate stellar masses from GAIA photometry.
    Uses empirical mass-luminosity relations.
    
    Parameters:
    -----------
    df : DataFrame
        GAIA data with phot_g_mean_mag, bp_rp columns
        
    Returns:
    --------
    masses : np.ndarray
        Estimated masses in solar masses
    """
    
    if len(df) == 0:
        return np.array([])
    
    # Use G magnitude and BP-RP color for mass estimation
    G = df['phot_g_mean_mag'].values
    bp_rp = df['bp_rp'].fillna(0.65).values  # Solar color as default
    
    # Absolute magnitude (distance modulus correction)
    dist_pc = df['dist_pc'].values
    M_G = G - 5 * np.log10(dist_pc) + 5
    
    # Empirical mass-luminosity relation (approximate)
    # Based on main sequence relations
    # M/M_sun ≈ (L/L_sun)^0.23 for M < M_sun
    # M/M_sun ≈ (L/L_sun)^0.6 for M > M_sun
    
    # Convert absolute G magnitude to luminosity
    M_G_sun = 4.67  # Solar absolute G magnitude
    log_L_ratio = -0.4 * (M_G - M_G_sun)
    L_ratio = 10**log_L_ratio
    
    # Mass-luminosity relation
    masses = np.where(
        L_ratio < 1.0,
        L_ratio**0.23,  # Low mass stars
        L_ratio**0.6    # High mass stars  
    )
    
    # Apply reasonable bounds
    masses = np.clip(masses, 0.08, 50.0)  # 0.08 to 50 solar masses
    
    return masses

def get_local_stellar_environment(maxdist_pc: float = 30, 
                                gmag_max: float = 10,
                                epoch: str = "2025.0") -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Get complete local stellar environment data.
    
    Returns:
    --------
    positions : np.ndarray, shape (N, 3)
        Stellar positions in AU
    masses : np.ndarray, shape (N,)
        Stellar masses in solar masses
    catalog : DataFrame
        Full GAIA catalog data
    """
    
    # Fetch GAIA data
    df = query_gaia_stars(maxdist_pc=maxdist_pc, gmag_max=gmag_max)
    
    if len(df) == 0:
        return np.empty((0, 3)), np.array([]), df
    
    # Convert to Cartesian coordinates
    positions = gaia_to_cartesian(df, epoch=epoch)
    
    # Estimate masses
    masses = estimate_stellar_masses(df)
    
    print(f"Processed {len(df)} stars:")
    print(f"  Distance range: {df['dist_pc'].min():.1f} - {df['dist_pc'].max():.1f} pc")
    print(f"  Mass range: {masses.min():.2f} - {masses.max():.2f} M_sun")
    
    return positions, masses, df

if __name__ == "__main__":
    # Test GAIA data fetching
    print("Testing GAIA data fetching...")
    
    positions, masses, catalog = get_local_stellar_environment(
        maxdist_pc=20, 
        gmag_max=8,
        epoch="2025.0"
    )
    
    print(f"\nRetrieved {len(catalog)} stars")
    if len(catalog) > 0:
        print(f"Brightest star: G = {catalog['phot_g_mean_mag'].min():.2f}")
        print(f"Nearest star: d = {catalog['dist_pc'].min():.2f} pc")
        print(f"Position range: ±{np.max(np.abs(positions)):.1f} AU")
    
    print("GAIA test complete!")
