"""
Coordinate transformation utilities for astronomical data.
Handles conversions between different reference frames and units.
"""

import numpy as np
from astropy.coordinates import SkyCoord, ICRS, HeliocentricEclipticIAU76
from astropy import units as u
from astropy.time import Time
import pandas as pd
from typing import Tuple, Optional

# Physical constants
AU = 1.495978707e11  # meters
SOLAR_MASS = 1.98847e30  # kg
EARTH_MASS = 5.97237e24  # kg
JUPITER_MASS = 1.89813e27  # kg

def icrs_to_ecliptic(ra: np.ndarray, dec: np.ndarray, distance: np.ndarray) -> np.ndarray:
    """
    Convert ICRS coordinates to heliocentric ecliptic.
    
    Parameters:
    -----------
    ra, dec : array-like
        Right ascension and declination in degrees
    distance : array-like  
        Distance in parsecs
        
    Returns:
    --------
    xyz_ecliptic : np.ndarray, shape (N, 3)
        Ecliptic coordinates in AU
    """
    
    # Create ICRS coordinate object
    coords_icrs = SkyCoord(
        ra=ra * u.deg,
        dec=dec * u.deg,
        distance=distance * u.pc,
        frame=ICRS()
    )
    
    # Transform to heliocentric ecliptic
    coords_ecliptic = coords_icrs.transform_to(HeliocentricEclipticIAU76())
    
    # Extract Cartesian coordinates in AU
    xyz = np.column_stack([
        coords_ecliptic.cartesian.x.to(u.AU).value,
        coords_ecliptic.cartesian.y.to(u.AU).value,
        coords_ecliptic.cartesian.z.to(u.AU).value
    ])
    
    return xyz

def orbital_elements_to_cartesian(a: float, e: float, i: float, 
                                Omega: float, omega: float, M: float,
                                epoch: Optional[str] = None) -> np.ndarray:
    """
    Convert Keplerian orbital elements to Cartesian coordinates.
    
    Parameters:
    -----------
    a : float
        Semi-major axis in AU
    e : float  
        Eccentricity
    i : float
        Inclination in degrees
    Omega : float
        Longitude of ascending node in degrees
    omega : float
        Argument of periapsis in degrees  
    M : float
        Mean anomaly in degrees
    epoch : str, optional
        Epoch for the elements
        
    Returns:
    --------
    xyz : np.ndarray, shape (3,)
        Position vector in AU (heliocentric ecliptic)
    """
    
    # Convert angles to radians
    i_rad = np.radians(i)
    Omega_rad = np.radians(Omega)
    omega_rad = np.radians(omega)
    M_rad = np.radians(M)
    
    # Solve Kepler's equation for eccentric anomaly E
    E = solve_kepler_equation(M_rad, e)
    
    # True anomaly
    nu = 2 * np.arctan2(
        np.sqrt(1 + e) * np.sin(E/2),
        np.sqrt(1 - e) * np.cos(E/2)
    )
    
    # Distance
    r = a * (1 - e * np.cos(E))
    
    # Position in orbital plane
    x_orb = r * np.cos(nu)
    y_orb = r * np.sin(nu)
    z_orb = 0.0
    
    # Rotation matrices
    cos_Omega, sin_Omega = np.cos(Omega_rad), np.sin(Omega_rad)
    cos_omega, sin_omega = np.cos(omega_rad), np.sin(omega_rad)
    cos_i, sin_i = np.cos(i_rad), np.sin(i_rad)
    
    # Combined rotation matrix (orbital plane to ecliptic)
    R11 = cos_Omega * cos_omega - sin_Omega * sin_omega * cos_i
    R12 = -cos_Omega * sin_omega - sin_Omega * cos_omega * cos_i
    R13 = sin_Omega * sin_i
    
    R21 = sin_Omega * cos_omega + cos_Omega * sin_omega * cos_i
    R22 = -sin_Omega * sin_omega + cos_Omega * cos_omega * cos_i
    R23 = -cos_Omega * sin_i
    
    R31 = sin_omega * sin_i
    R32 = cos_omega * sin_i
    R33 = cos_i
    
    # Transform to ecliptic coordinates
    x = R11 * x_orb + R12 * y_orb + R13 * z_orb
    y = R21 * x_orb + R22 * y_orb + R23 * z_orb
    z = R31 * x_orb + R32 * y_orb + R33 * z_orb
    
    return np.array([x, y, z])

def solve_kepler_equation(M: float, e: float, tol: float = 1e-12) -> float:
    """
    Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E.
    Uses Newton-Raphson iteration.
    
    Parameters:
    -----------
    M : float
        Mean anomaly in radians
    e : float
        Eccentricity
    tol : float
        Convergence tolerance
        
    Returns:
    --------
    E : float
        Eccentric anomaly in radians
    """
    
    # Initial guess
    E = M if e < 0.8 else np.pi
    
    # Newton-Raphson iteration
    for _ in range(50):  # Max iterations
        f = E - e * np.sin(E) - M
        df = 1 - e * np.cos(E)
        
        dE = f / df
        E -= dE
        
        if abs(dE) < tol:
            break
    
    return E

def propagate_orbit(a: float, e: float, i: float, Omega: float, omega: float, 
                   M0: float, epoch_days: np.ndarray, mu: float = 1.0) -> np.ndarray:
    """
    Propagate orbit over time using mean motion.
    
    Parameters:
    -----------
    a, e, i, Omega, omega : float
        Orbital elements
    M0 : float
        Mean anomaly at epoch in degrees
    epoch_days : array-like
        Time points in days from epoch
    mu : float
        Standard gravitational parameter (GM) in AU³/day²
        Default is for Sun: μ = 1.0 in these units
        
    Returns:
    --------
    positions : np.ndarray, shape (N, 3)
        Position vectors over time in AU
    """
    
    # Mean motion (radians per day)
    n = np.sqrt(mu / a**3)
    
    # Mean anomaly over time
    M = np.radians(M0) + n * epoch_days
    
    # Calculate positions for each time point
    positions = []
    for M_t in M:
        xyz = orbital_elements_to_cartesian(a, e, i, Omega, omega, np.degrees(M_t))
        positions.append(xyz)
    
    return np.array(positions)

def au_to_meters(au_coords: np.ndarray) -> np.ndarray:
    """Convert coordinates from AU to meters."""
    return au_coords * AU

def meters_to_au(meter_coords: np.ndarray) -> np.ndarray:
    """Convert coordinates from meters to AU."""
    return meter_coords / AU

def solar_masses_to_kg(solar_masses: np.ndarray) -> np.ndarray:
    """Convert masses from solar masses to kg."""
    return solar_masses * SOLAR_MASS

def kg_to_solar_masses(kg_masses: np.ndarray) -> np.ndarray:
    """Convert masses from kg to solar masses."""
    return kg_masses / SOLAR_MASS

def distance_3d(pos1: np.ndarray, pos2: np.ndarray) -> np.ndarray:
    """
    Calculate 3D distances between points.
    
    Parameters:
    -----------
    pos1, pos2 : np.ndarray
        Position arrays, shape (..., 3)
        
    Returns:
    --------
    distances : np.ndarray
        Euclidean distances
    """
    return np.linalg.norm(pos1 - pos2, axis=-1)

def spherical_to_cartesian(r: np.ndarray, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """
    Convert spherical to Cartesian coordinates.
    
    Parameters:
    -----------
    r : array-like
        Radial distance
    theta : array-like  
        Polar angle (0 to π) in radians
    phi : array-like
        Azimuthal angle (0 to 2π) in radians
        
    Returns:
    --------
    xyz : np.ndarray, shape (..., 3)
        Cartesian coordinates
    """
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)  
    z = r * np.cos(theta)
    
    return np.column_stack([x, y, z])

def cartesian_to_spherical(xyz: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert Cartesian to spherical coordinates.
    
    Parameters:
    -----------
    xyz : np.ndarray, shape (..., 3)
        Cartesian coordinates
        
    Returns:
    --------
    r, theta, phi : np.ndarray
        Spherical coordinates (r, polar angle, azimuthal angle)
    """
    x, y, z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(z / (r + 1e-15))  # Avoid division by zero
    phi = np.arctan2(y, x)
    
    return r, theta, phi

if __name__ == "__main__":
    # Test coordinate transformations
    print("Testing coordinate transformations...")
    
    # Test orbital elements to Cartesian (Earth-like orbit)
    earth_pos = orbital_elements_to_cartesian(
        a=1.0, e=0.0167, i=0.0, Omega=0.0, omega=0.0, M=0.0
    )
    print(f"Earth position at perihelion: {earth_pos} AU")
    
    # Test orbit propagation
    times = np.linspace(0, 365.25, 100)  # One year
    earth_orbit = propagate_orbit(
        a=1.0, e=0.0167, i=0.0, Omega=0.0, omega=0.0, M0=0.0, 
        epoch_days=times
    )
    
    orbit_radii = np.linalg.norm(earth_orbit, axis=1)
    print(f"Earth orbit radii: {orbit_radii.min():.3f} - {orbit_radii.max():.3f} AU")
    
    print("Coordinate transformation tests complete!")
