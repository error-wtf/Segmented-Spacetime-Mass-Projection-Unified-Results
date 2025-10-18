"""
Orbital mechanics and visualization module.
Handles Keplerian orbit propagation and φ-spiral clock generation.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import pandas as pd
from .coords import orbital_elements_to_cartesian, propagate_orbit

# Golden ratio φ
PHI = (1.0 + np.sqrt(5.0)) / 2.0

def generate_orbit_points(a: float, e: float, i: float, Omega: float, omega: float, 
                         M0: float, num_points: int = 400, 
                         time_span_days: float = None) -> np.ndarray:
    """
    Generate orbit trajectory points.
    
    Parameters:
    -----------
    a, e, i, Omega, omega : float
        Orbital elements (angles in degrees)
    M0 : float
        Mean anomaly at epoch (degrees)
    num_points : int
        Number of points along orbit
    time_span_days : float, optional
        Time span to cover (defaults to full period)
        
    Returns:
    --------
    orbit_points : np.ndarray, shape (N, 3)
        Orbit trajectory in AU
    """
    
    # Calculate orbital period if not specified
    if time_span_days is None:
        # Kepler's third law: P² ∝ a³ (P in years, a in AU)
        period_years = a**(3/2)
        time_span_days = period_years * 365.25
    
    # Time points
    times = np.linspace(0, time_span_days, num_points)
    
    # Propagate orbit
    orbit_points = propagate_orbit(a, e, i, Omega, omega, M0, times)
    
    return orbit_points

def generate_phi_spiral(center: np.ndarray, radius: float, tau_local: float,
                       num_turns: float = 3.0, points_per_turn: int = 50) -> np.ndarray:
    """
    Generate φ-spiral "Normaluhr" clock around a celestial body.
    
    Parameters:
    -----------
    center : np.ndarray, shape (3,)
        Center position in AU
    radius : float
        Spiral radius in AU
    tau_local : float
        Local time dilation factor
    num_turns : float
        Number of spiral turns
    points_per_turn : int
        Points per spiral turn
        
    Returns:
    --------
    spiral_points : np.ndarray, shape (N, 3)
        Spiral trajectory points
    """
    
    total_points = int(num_turns * points_per_turn)
    
    # Parameter along spiral
    t = np.linspace(0, num_turns * 2 * np.pi, total_points)
    
    # φ-based spiral (logarithmic spiral with golden ratio)
    # r(θ) = r₀ * φ^(θ/π) 
    r = radius * PHI**(t / np.pi) / PHI**(num_turns * 2)
    
    # Modulate by time dilation (slower time = tighter spiral)
    r *= tau_local
    
    # Spiral coordinates in local plane
    x_spiral = r * np.cos(t)
    y_spiral = r * np.sin(t)
    z_spiral = np.zeros_like(t)
    
    # Translate to body center
    spiral_points = np.column_stack([x_spiral, y_spiral, z_spiral])
    spiral_points += center[None, :]
    
    return spiral_points

class OrbitVisualizer:
    """
    Handles orbit visualization and φ-spiral clock generation.
    """
    
    def __init__(self):
        self.orbits = {}
        self.spirals = {}
        
    def add_orbit(self, name: str, orbital_elements: Dict, 
                  color: str = "white", width: float = 2.0,
                  num_points: int = 400) -> None:
        """
        Add orbit trajectory for visualization.
        
        Parameters:
        -----------
        name : str
            Body name
        orbital_elements : dict
            Dictionary with keys: a, e, i, Omega, omega, M
        color : str
            Orbit line color
        width : float
            Line width
        num_points : int
            Number of trajectory points
        """
        
        # Generate orbit points
        points = generate_orbit_points(
            a=orbital_elements['a'],
            e=orbital_elements['e'],
            i=orbital_elements['i'],
            Omega=orbital_elements['Omega'],
            omega=orbital_elements['omega'],
            M0=orbital_elements['M'],
            num_points=num_points
        )
        
        self.orbits[name] = {
            'points': points,
            'color': color,
            'width': width,
            'elements': orbital_elements
        }
        
    def add_phi_spiral(self, name: str, center: np.ndarray, 
                      body_radius_au: float, tau_local: float,
                      color: str = "gold", width: float = 1.0) -> None:
        """
        Add φ-spiral clock around a body.
        
        Parameters:
        -----------
        name : str
            Body name
        center : np.ndarray
            Body center position
        body_radius_au : float
            Body radius in AU
        tau_local : float
            Local time dilation factor
        color : str
            Spiral color
        width : float
            Line width
        """
        
        # Spiral radius proportional to body size
        spiral_radius = max(body_radius_au * 5, 0.01)  # At least 0.01 AU
        
        # Generate spiral
        points = generate_phi_spiral(
            center=center,
            radius=spiral_radius,
            tau_local=tau_local,
            num_turns=PHI * 2,  # φ-based number of turns
            points_per_turn=30
        )
        
        self.spirals[name] = {
            'points': points,
            'color': color,
            'width': width,
            'tau': tau_local,
            'radius': spiral_radius
        }
        
    def get_orbit_traces(self) -> List[Dict]:
        """
        Get orbit traces for plotting.
        
        Returns:
        --------
        traces : list
            List of trace dictionaries for plotting
        """
        traces = []
        
        for name, orbit in self.orbits.items():
            points = orbit['points']
            
            trace = {
                'type': 'scatter3d',
                'mode': 'lines',
                'x': points[:, 0],
                'y': points[:, 1], 
                'z': points[:, 2],
                'line': {
                    'color': orbit['color'],
                    'width': orbit['width']
                },
                'name': f"{name} orbit",
                'showlegend': True
            }
            traces.append(trace)
            
        return traces
    
    def get_spiral_traces(self) -> List[Dict]:
        """
        Get φ-spiral traces for plotting.
        
        Returns:
        --------
        traces : list
            List of spiral trace dictionaries
        """
        traces = []
        
        for name, spiral in self.spirals.items():
            points = spiral['points']
            
            trace = {
                'type': 'scatter3d',
                'mode': 'lines',
                'x': points[:, 0],
                'y': points[:, 1],
                'z': points[:, 2],
                'line': {
                    'color': spiral['color'],
                    'width': spiral['width']
                },
                'name': f"{name} φ-clock",
                'showlegend': True
            }
            traces.append(trace)
            
        return traces

def create_solar_system_orbits(catalog: pd.DataFrame, positions: np.ndarray,
                              field_calculator=None) -> OrbitVisualizer:
    """
    Create orbit visualizer for Solar System.
    
    Parameters:
    -----------
    catalog : DataFrame
        Body catalog with orbital elements
    positions : np.ndarray
        Current positions at epoch
    field_calculator : SegmentedSpacetimeField, optional
        Field calculator for time dilation
        
    Returns:
    --------
    visualizer : OrbitVisualizer
        Configured orbit visualizer
    """
    
    visualizer = OrbitVisualizer()
    
    # Color scheme for planets
    planet_colors = {
        'Mercury': 'gray',
        'Venus': 'orange', 
        'Earth': 'blue',
        'Mars': 'red',
        'Jupiter': 'brown',
        'Saturn': 'gold',
        'Uranus': 'cyan',
        'Neptune': 'darkblue'
    }
    
    # Add orbits for planets
    for i, row in catalog.iterrows():
        name = row['name']
        
        if name == 'Sun':
            continue  # Sun doesn't have an orbit
            
        # Skip moons for now (would need parent-relative orbits)
        if 'parent' in row and pd.notna(row['parent']):
            continue
            
        # Orbital elements
        elements = {
            'a': row['a_AU'],
            'e': row['e'],
            'i': row['i_deg'],
            'Omega': row['Omega_deg'],
            'omega': row['omega_deg'],
            'M': row['M_deg']
        }
        
        # Color
        color = planet_colors.get(name, 'white')
        
        # Line width based on mass
        mass_ratio = row['mass_kg'] / 5.97237e24  # Relative to Earth
        width = max(1.0, min(4.0, 1.0 + np.log10(mass_ratio)))
        
        visualizer.add_orbit(name, elements, color=color, width=width)
        
        # Add φ-spiral clock if field calculator available
        if field_calculator is not None:
            position = positions[i]
            
            # Calculate local time dilation
            N_local = field_calculator.compute_segment_density(position.reshape(1, -1))[0]
            tau_local = field_calculator.compute_time_dilation(np.array([N_local]))[0]
            
            # Body radius in AU
            radius_au = row['radius_km'] / 149597870.7  # km to AU
            
            visualizer.add_phi_spiral(
                name, 
                center=position,
                body_radius_au=radius_au,
                tau_local=tau_local,
                color='gold'
            )
    
    return visualizer

def compute_orbital_resonances(catalog: pd.DataFrame) -> Dict[str, Dict]:
    """
    Compute orbital resonances between bodies.
    
    Parameters:
    -----------
    catalog : DataFrame
        Body catalog with periods
        
    Returns:
    --------
    resonances : dict
        Dictionary of resonance relationships
    """
    
    resonances = {}
    
    # Get planets with periods
    planets = catalog[catalog['period_days'] > 0].copy()
    
    for i, body1 in planets.iterrows():
        for j, body2 in planets.iterrows():
            if i >= j:
                continue
                
            P1, P2 = body1['period_days'], body2['period_days']
            
            # Check for simple integer ratios
            ratio = P2 / P1  # Outer to inner period ratio
            
            # Check ratios up to 5:1
            for n in range(1, 6):
                for m in range(1, 6):
                    expected_ratio = n / m
                    
                    if abs(ratio - expected_ratio) / expected_ratio < 0.05:  # 5% tolerance
                        resonance_key = f"{body1['name']}-{body2['name']}"
                        resonances[resonance_key] = {
                            'ratio': f"{n}:{m}",
                            'actual_ratio': ratio,
                            'expected_ratio': expected_ratio,
                            'deviation': abs(ratio - expected_ratio) / expected_ratio
                        }
                        break
                else:
                    continue
                break
    
    return resonances

if __name__ == "__main__":
    # Test orbit calculations
    print("Testing orbit calculations...")
    
    # Test Earth orbit
    earth_orbit = generate_orbit_points(
        a=1.0, e=0.0167, i=0.0, Omega=0.0, omega=0.0, M0=0.0,
        num_points=100
    )
    
    print(f"Earth orbit: {len(earth_orbit)} points")
    print(f"Orbit radii: {np.min(np.linalg.norm(earth_orbit, axis=1)):.3f} - "
          f"{np.max(np.linalg.norm(earth_orbit, axis=1)):.3f} AU")
    
    # Test φ-spiral
    spiral = generate_phi_spiral(
        center=np.array([1.0, 0.0, 0.0]),
        radius=0.01,
        tau_local=0.8,
        num_turns=2.0
    )
    
    print(f"φ-spiral: {len(spiral)} points")
    
    # Test orbit visualizer
    visualizer = OrbitVisualizer()
    
    earth_elements = {
        'a': 1.0, 'e': 0.0167, 'i': 0.0,
        'Omega': 0.0, 'omega': 0.0, 'M': 0.0
    }
    
    visualizer.add_orbit("Earth", earth_elements, color="blue")
    visualizer.add_phi_spiral("Earth", np.array([1.0, 0.0, 0.0]), 0.0000426, 0.9)
    
    orbit_traces = visualizer.get_orbit_traces()
    spiral_traces = visualizer.get_spiral_traces()
    
    print(f"Generated {len(orbit_traces)} orbit traces, {len(spiral_traces)} spiral traces")
    
    print("Orbit calculations test complete!")
