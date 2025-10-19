"""
Segmented Spacetime Solar System Visualization Package

A 3D visualization framework for representing the Solar System embedded in
a segmented spacetime mesh based on the Casu & Wrede theoretical framework.
"""

__version__ = "1.0.0"
__author__ = "Segmented Spacetime Project"
__email__ = "contact@segmented-spacetime.org"

# Core modules
from .icosphere import build_icosphere, mesh_info
from .segments import SegmentedSpacetimeField, create_solar_system_field
from .coords import (
    orbital_elements_to_cartesian, 
    propagate_orbit,
    icrs_to_ecliptic,
    au_to_meters,
    meters_to_au,
    solar_masses_to_kg,
    kg_to_solar_masses
)
from .fetch_gaia import get_local_stellar_environment, query_gaia_stars
from .fetch_vizier import get_complete_solar_system, get_planetary_data
from .orbits import OrbitVisualizer, create_solar_system_orbits, generate_phi_spiral
from .viz_plotly import SegmentedSpacetimeVisualizer, create_interactive_dashboard

# Main application
from .app import SegmentedSolarApp, main

__all__ = [
    # Core classes
    'SegmentedSpacetimeField',
    'OrbitVisualizer', 
    'SegmentedSpacetimeVisualizer',
    'SegmentedSolarApp',
    
    # Mesh generation
    'build_icosphere',
    'mesh_info',
    
    # Field calculations
    'create_solar_system_field',
    
    # Coordinate transformations
    'orbital_elements_to_cartesian',
    'propagate_orbit',
    'icrs_to_ecliptic',
    'au_to_meters',
    'meters_to_au',
    'solar_masses_to_kg',
    'kg_to_solar_masses',
    
    # Data fetching
    'get_local_stellar_environment',
    'query_gaia_stars',
    'get_complete_solar_system',
    'get_planetary_data',
    
    # Orbit and visualization
    'create_solar_system_orbits',
    'generate_phi_spiral',
    'create_interactive_dashboard',
    
    # Main application
    'main'
]
