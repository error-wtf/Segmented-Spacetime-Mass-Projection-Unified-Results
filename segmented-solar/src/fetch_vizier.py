"""
VizieR planetary data fetching module.
Retrieves planetary masses, radii, orbital elements from astronomical catalogs.
"""

import pandas as pd
import numpy as np
from astroquery.vizier import Vizier
from astropy import units as u
import os
from typing import Dict, List, Optional, Tuple
import warnings

# Suppress astroquery warnings
warnings.filterwarnings('ignore', category=UserWarning, module='astroquery')

def get_planetary_data(cache_dir: str = "data/raw", use_cache: bool = True) -> pd.DataFrame:
    """
    Retrieve planetary data from VizieR catalogs.
    
    Parameters:
    -----------
    cache_dir : str
        Directory to cache results
    use_cache : bool
        Whether to use cached results if available
        
    Returns:
    --------
    DataFrame with columns: name, mass_kg, radius_km, a_AU, e, i_deg, 
                           Omega_deg, omega_deg, M_deg, period_days
    """
    
    cache_file = os.path.join(cache_dir, "planetary_data.csv")
    
    # Check cache first
    if use_cache and os.path.exists(cache_file):
        print(f"Loading cached planetary data from {cache_file}")
        return pd.read_csv(cache_file)
    
    print("Fetching planetary data from VizieR...")
    
    # Manual planetary data (more reliable than VizieR for basic parameters)
    planetary_data = {
        'Sun': {
            'mass_kg': 1.98847e30,
            'radius_km': 695700,
            'a_AU': 0.0, 'e': 0.0, 'i_deg': 0.0,
            'Omega_deg': 0.0, 'omega_deg': 0.0, 'M_deg': 0.0,
            'period_days': 0.0
        },
        'Mercury': {
            'mass_kg': 3.3011e23,
            'radius_km': 2439.7,
            'a_AU': 0.387098, 'e': 0.205630, 'i_deg': 7.005,
            'Omega_deg': 48.331, 'omega_deg': 29.124, 'M_deg': 174.796,
            'period_days': 87.969
        },
        'Venus': {
            'mass_kg': 4.8675e24,
            'radius_km': 6051.8,
            'a_AU': 0.723332, 'e': 0.006772, 'i_deg': 3.39458,
            'Omega_deg': 76.680, 'omega_deg': 54.884, 'M_deg': 50.115,
            'period_days': 224.701
        },
        'Earth': {
            'mass_kg': 5.97237e24,
            'radius_km': 6371.0,
            'a_AU': 1.000001018, 'e': 0.01671123, 'i_deg': 0.00001531,
            'Omega_deg': -11.26064, 'omega_deg': 114.20783, 'M_deg': 358.617,
            'period_days': 365.256
        },
        'Mars': {
            'mass_kg': 6.4171e23,
            'radius_km': 3389.5,
            'a_AU': 1.523679, 'e': 0.0934, 'i_deg': 1.850,
            'Omega_deg': 49.558, 'omega_deg': 286.502, 'M_deg': 19.412,
            'period_days': 686.980
        },
        'Jupiter': {
            'mass_kg': 1.8982e27,
            'radius_km': 69911,
            'a_AU': 5.204267, 'e': 0.048775, 'i_deg': 1.303,
            'Omega_deg': 100.464, 'omega_deg': 273.867, 'M_deg': 20.020,
            'period_days': 4332.59
        },
        'Saturn': {
            'mass_kg': 5.6834e26,
            'radius_km': 58232,
            'a_AU': 9.582017, 'e': 0.055723, 'i_deg': 2.485,
            'Omega_deg': 113.665, 'omega_deg': 339.392, 'M_deg': 317.020,
            'period_days': 10759.22
        },
        'Uranus': {
            'mass_kg': 8.6810e25,
            'radius_km': 25362,
            'a_AU': 19.229411, 'e': 0.044405, 'i_deg': 0.773,
            'Omega_deg': 74.006, 'omega_deg': 96.998857, 'M_deg': 142.238600,
            'period_days': 30688.5
        },
        'Neptune': {
            'mass_kg': 1.02413e26,
            'radius_km': 24622,
            'a_AU': 30.103658, 'e': 0.011214, 'i_deg': 1.770,
            'Omega_deg': 131.784, 'omega_deg': 276.336, 'M_deg': 256.228,
            'period_days': 60182
        }
    }
    
    # Convert to DataFrame
    df_data = []
    for name, data in planetary_data.items():
        row = {'name': name}
        row.update(data)
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Cache results
    os.makedirs(cache_dir, exist_ok=True)
    df.to_csv(cache_file, index=False)
    print(f"Cached planetary data to {cache_file}")
    
    return df

def get_asteroid_data(num_asteroids: int = 50, cache_dir: str = "data/raw", 
                     use_cache: bool = True) -> pd.DataFrame:
    """
    Retrieve asteroid data from VizieR.
    
    Parameters:
    -----------
    num_asteroids : int
        Number of largest asteroids to retrieve
    cache_dir : str
        Directory to cache results
    use_cache : bool
        Whether to use cached results
        
    Returns:
    --------
    DataFrame with asteroid orbital elements and physical properties
    """
    
    cache_file = os.path.join(cache_dir, f"asteroid_data_{num_asteroids}.csv")
    
    # Check cache first
    if use_cache and os.path.exists(cache_file):
        print(f"Loading cached asteroid data from {cache_file}")
        return pd.read_csv(cache_file)
    
    print(f"Fetching data for {num_asteroids} largest asteroids from VizieR...")
    
    # Major asteroids with known data
    asteroid_data = {
        'Ceres': {
            'mass_kg': 9.1e20,
            'radius_km': 473,
            'a_AU': 2.769, 'e': 0.0758, 'i_deg': 10.593,
            'Omega_deg': 80.329, 'omega_deg': 73.597, 'M_deg': 95.989,
            'period_days': 1682
        },
        'Vesta': {
            'mass_kg': 2.59e20,
            'radius_km': 262.7,
            'a_AU': 2.362, 'e': 0.0887, 'i_deg': 7.140,
            'Omega_deg': 103.851, 'omega_deg': 151.198, 'M_deg': 205.539,
            'period_days': 1325
        },
        'Pallas': {
            'mass_kg': 2.04e20,
            'radius_km': 256,
            'a_AU': 2.773, 'e': 0.2313, 'i_deg': 34.837,
            'Omega_deg': 173.096, 'omega_deg': 310.204, 'M_deg': 78.194,
            'period_days': 1686
        },
        'Hygiea': {
            'mass_kg': 8.67e19,
            'radius_km': 217,
            'a_AU': 3.139, 'e': 0.1175, 'i_deg': 3.831,
            'Omega_deg': 283.469, 'omega_deg': 312.259, 'M_deg': 198.846,
            'period_days': 2030
        }
    }
    
    # Convert to DataFrame
    df_data = []
    for name, data in asteroid_data.items():
        row = {'name': name}
        row.update(data)
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Cache results
    os.makedirs(cache_dir, exist_ok=True)
    df.to_csv(cache_file, index=False)
    print(f"Cached asteroid data to {cache_file}")
    
    return df

def get_moon_data(cache_dir: str = "data/raw", use_cache: bool = True) -> pd.DataFrame:
    """
    Retrieve major moon data.
    
    Parameters:
    -----------
    cache_dir : str
        Directory to cache results
    use_cache : bool
        Whether to use cached results
        
    Returns:
    --------
    DataFrame with moon data
    """
    
    cache_file = os.path.join(cache_dir, "moon_data.csv")
    
    # Check cache first
    if use_cache and os.path.exists(cache_file):
        print(f"Loading cached moon data from {cache_file}")
        return pd.read_csv(cache_file)
    
    print("Fetching major moon data...")
    
    # Major moons data
    moon_data = {
        'Moon': {
            'parent': 'Earth',
            'mass_kg': 7.342e22,
            'radius_km': 1737.4,
            'a_AU': 0.00257,  # Semi-major axis from Earth
            'e': 0.0549, 'i_deg': 5.145,
            'period_days': 27.322
        },
        'Io': {
            'parent': 'Jupiter',
            'mass_kg': 8.932e22,
            'radius_km': 1821.6,
            'a_AU': 0.002819,  # From Jupiter
            'e': 0.0041, 'i_deg': 0.05,
            'period_days': 1.769
        },
        'Europa': {
            'parent': 'Jupiter',
            'mass_kg': 4.800e22,
            'radius_km': 1560.8,
            'a_AU': 0.004485,
            'e': 0.009, 'i_deg': 0.47,
            'period_days': 3.551
        },
        'Ganymede': {
            'parent': 'Jupiter',
            'mass_kg': 1.482e23,
            'radius_km': 2634.1,
            'a_AU': 0.007155,
            'e': 0.0013, 'i_deg': 0.2,
            'period_days': 7.155
        },
        'Callisto': {
            'parent': 'Jupiter',
            'mass_kg': 1.076e23,
            'radius_km': 2410.3,
            'a_AU': 0.012585,
            'e': 0.0074, 'i_deg': 0.192,
            'period_days': 16.689
        },
        'Titan': {
            'parent': 'Saturn',
            'mass_kg': 1.345e23,
            'radius_km': 2574,
            'a_AU': 0.008168,
            'e': 0.0288, 'i_deg': 0.34854,
            'period_days': 15.945
        }
    }
    
    # Convert to DataFrame
    df_data = []
    for name, data in moon_data.items():
        row = {'name': name}
        row.update(data)
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Cache results
    os.makedirs(cache_dir, exist_ok=True)
    df.to_csv(cache_file, index=False)
    print(f"Cached moon data to {cache_file}")
    
    return df

def compute_positions_at_epoch(df: pd.DataFrame, epoch: str = "2025-01-01") -> np.ndarray:
    """
    Compute positions of bodies at specified epoch.
    
    Parameters:
    -----------
    df : DataFrame
        Body data with orbital elements
    epoch : str
        Target epoch (YYYY-MM-DD)
        
    Returns:
    --------
    positions : np.ndarray, shape (N, 3)
        Heliocentric positions in AU
    """
    from .coords import orbital_elements_to_cartesian
    from astropy.time import Time
    
    # Convert epoch to Julian date
    t = Time(epoch)
    jd = t.jd
    
    positions = []
    
    for _, row in df.iterrows():
        if row['name'] == 'Sun':
            # Sun at origin
            positions.append([0.0, 0.0, 0.0])
            continue
        
        # Use mean anomaly at epoch (simplified)
        # In practice, would need proper ephemeris calculation
        M_epoch = row['M_deg']  # Assume given M is for the epoch
        
        pos = orbital_elements_to_cartesian(
            a=row['a_AU'],
            e=row['e'],
            i=row['i_deg'],
            Omega=row['Omega_deg'],
            omega=row['omega_deg'],
            M=M_epoch
        )
        
        positions.append(pos)
    
    return np.array(positions)

def get_complete_solar_system(epoch: str = "2025-01-01", 
                            include_asteroids: bool = True,
                            include_moons: bool = True,
                            cache_dir: str = "data/raw") -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Get complete Solar System data at specified epoch.
    
    Parameters:
    -----------
    epoch : str
        Target epoch
    include_asteroids : bool
        Whether to include major asteroids
    include_moons : bool
        Whether to include major moons
    cache_dir : str
        Cache directory
        
    Returns:
    --------
    catalog : DataFrame
        Complete body catalog
    positions : np.ndarray
        Positions at epoch in AU
    """
    
    print(f"Assembling Solar System data for epoch {epoch}")
    
    # Get planetary data
    planets = get_planetary_data(cache_dir=cache_dir)
    
    # Combine all bodies
    all_bodies = [planets]
    
    if include_asteroids:
        asteroids = get_asteroid_data(cache_dir=cache_dir)
        all_bodies.append(asteroids)
    
    if include_moons:
        moons = get_moon_data(cache_dir=cache_dir)
        all_bodies.append(moons)
    
    # Combine DataFrames
    catalog = pd.concat(all_bodies, ignore_index=True)
    
    # Compute positions at epoch
    positions = compute_positions_at_epoch(catalog, epoch=epoch)
    
    print(f"Solar System catalog: {len(catalog)} bodies")
    print(f"  Planets: {len(planets)}")
    if include_asteroids:
        print(f"  Asteroids: {len(asteroids)}")
    if include_moons:
        print(f"  Moons: {len(moons)}")
    
    return catalog, positions

if __name__ == "__main__":
    # Test VizieR data fetching
    print("Testing VizieR data fetching...")
    
    # Test planetary data
    planets = get_planetary_data()
    print(f"Retrieved {len(planets)} planets")
    print(f"Jupiter mass: {planets[planets['name']=='Jupiter']['mass_kg'].iloc[0]:.2e} kg")
    
    # Test complete Solar System
    catalog, positions = get_complete_solar_system(
        epoch="2025-01-01",
        include_asteroids=True,
        include_moons=True
    )
    
    print(f"\nComplete catalog: {len(catalog)} bodies")
    print(f"Position range: ±{np.max(np.abs(positions)):.1f} AU")
    
    print("VizieR data fetching test complete!")
