"""
Segmented spacetime field calculations.
Implements the φ-based segment density, time dilation, and refractive index fields
according to the Casu & Wrede theoretical framework.
"""

import numpy as np
from numba import jit, prange
from typing import Dict, List, Tuple, Optional
import warnings

# Golden ratio φ = (1 + √5)/2
PHI = (1.0 + np.sqrt(5.0)) / 2.0

def logistic(x: np.ndarray, steepness: float = 1.0) -> np.ndarray:
    """
    Logistic function for smooth saturation.
    
    Parameters:
    -----------
    x : np.ndarray
        Input values
    steepness : float
        Controls transition sharpness
        
    Returns:
    --------
    np.ndarray
        Logistic function values
    """
    return 1.0 / (1.0 + np.exp(-steepness * x))

@jit(nopython=True, parallel=True)
def kernel_soft_power_numba(distances: np.ndarray, M: float, r0: float, 
                           p: float, r_nb: float, delta: float) -> np.ndarray:
    """
    Optimized kernel computation using Numba.
    
    K_i(r) = (M / (r + r0)^p) * σ((r_nb - r)/δ)
    
    where σ is the logistic function for natural boundary saturation.
    """
    result = np.zeros_like(distances)
    
    for i in prange(len(distances)):
        r = distances[i]
        
        # Power-law component with softening
        power_term = M / (r + r0)**p
        
        # Natural boundary saturation
        boundary_arg = (r_nb - r) / delta
        # Manual logistic to avoid function calls in numba
        if boundary_arg > 50:
            saturation = 1.0
        elif boundary_arg < -50:
            saturation = 0.0
        else:
            saturation = 1.0 / (1.0 + np.exp(-boundary_arg))
        
        result[i] = power_term * saturation
    
    return result

def kernel_soft_power(distances: np.ndarray, M: float, r0: float, 
                     p: float, r_nb: float, delta: float) -> np.ndarray:
    """
    Softened power-law kernel with natural boundary saturation.
    
    Parameters:
    -----------
    distances : np.ndarray
        Distances from source
    M : float
        Mass parameter (scaled)
    r0 : float
        Softening radius
    p : float
        Power-law index (typically 1.5-2.5)
    r_nb : float
        Natural boundary radius
    delta : float
        Boundary transition width
        
    Returns:
    --------
    np.ndarray
        Kernel values
    """
    return kernel_soft_power_numba(distances, M, r0, p, r_nb, delta)

class SegmentedSpacetimeField:
    """
    Segmented spacetime field calculator implementing the Casu & Wrede model.
    """
    
    def __init__(self, params: Dict):
        """
        Initialize field calculator.
        
        Parameters:
        -----------
        params : dict
            Field parameters including:
            - p: power-law index
            - N_bg: background segment density  
            - N_max: maximum segment density
            - alpha: time dilation coupling
            - kappa: refractive index coupling
        """
        self.params = params
        self.bodies = []
        
        # Default parameters
        self.p = params.get('p', 2.0)
        self.N_bg = params.get('N_bg', 0.0)
        self.N_max = params.get('N_max', 5.0)
        self.alpha = params.get('alpha', 1.0)
        self.kappa = params.get('kappa', 0.015)
        
    def add_body(self, position: np.ndarray, mass_scaled: float, gamma: float,
                r0: float, r_nb: float, delta: float, name: str = ""):
        """
        Add a gravitating body to the field.
        
        Parameters:
        -----------
        position : np.ndarray, shape (3,)
            Body position in AU
        mass_scaled : float
            Scaled mass parameter
        gamma : float
            Coupling strength
        r0 : float
            Softening radius in AU
        r_nb : float
            Natural boundary radius in AU
        delta : float
            Boundary transition width in AU
        name : str
            Body identifier
        """
        body = {
            'name': name,
            'position': np.array(position),
            'mass_scaled': mass_scaled,
            'gamma': gamma,
            'r0': r0,
            'r_nb': r_nb,
            'delta': delta
        }
        self.bodies.append(body)
        
    def compute_segment_density(self, vertices: np.ndarray) -> np.ndarray:
        """
        Compute segment density field N(x) at mesh vertices.
        
        N(x) = N_bg + Σ_i γ_i * K_i(||x - x_i||)
        
        Parameters:
        -----------
        vertices : np.ndarray, shape (N, 3)
            Mesh vertex positions
            
        Returns:
        --------
        N : np.ndarray, shape (N,)
            Segment density values
        """
        N = np.full(len(vertices), self.N_bg)
        
        for body in self.bodies:
            # Calculate distances from body
            distances = np.linalg.norm(vertices - body['position'][None, :], axis=1)
            
            # Compute kernel contribution
            kernel_values = kernel_soft_power(
                distances, 
                body['mass_scaled'], 
                body['r0'],
                self.p, 
                body['r_nb'], 
                body['delta']
            )
            
            # Add weighted contribution
            N += body['gamma'] * kernel_values
        
        # Apply saturation
        N = np.clip(N, 0.0, self.N_max)
        
        return N
    
    def compute_time_dilation(self, N: np.ndarray) -> np.ndarray:
        """
        Compute time dilation field τ(x) from segment density.
        
        τ(x) = φ^(-α * N(x))
        
        Parameters:
        -----------
        N : np.ndarray
            Segment density values
            
        Returns:
        --------
        tau : np.ndarray
            Time dilation factors (τ < 1 means slower time)
        """
        return PHI ** (-self.alpha * N)
    
    def compute_refractive_index(self, N: np.ndarray) -> np.ndarray:
        """
        Compute effective refractive index n(x) from segment density.
        
        n(x) = 1 + κ * N(x)
        
        Parameters:
        -----------
        N : np.ndarray
            Segment density values
            
        Returns:
        --------
        n : np.ndarray
            Refractive index values (n > 1)
        """
        return 1.0 + self.kappa * N
    
    def compute_all_fields(self, vertices: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute all field quantities at mesh vertices.
        
        Parameters:
        -----------
        vertices : np.ndarray, shape (N, 3)
            Mesh vertex positions
            
        Returns:
        --------
        N, tau, n : tuple of np.ndarray
            Segment density, time dilation, and refractive index
        """
        N = self.compute_segment_density(vertices)
        tau = self.compute_time_dilation(N)
        n = self.compute_refractive_index(N)
        
        return N, tau, n
    
    def field_gradient(self, vertices: np.ndarray, field: str = 'N', 
                      h: float = 0.01) -> np.ndarray:
        """
        Compute field gradient using finite differences.
        
        Parameters:
        -----------
        vertices : np.ndarray, shape (N, 3)
            Evaluation points
        field : str
            Field to compute gradient for ('N', 'tau', 'n')
        h : float
            Finite difference step size in AU
            
        Returns:
        --------
        gradient : np.ndarray, shape (N, 3)
            Field gradient vectors
        """
        gradients = np.zeros_like(vertices)
        
        for i in range(3):  # x, y, z components
            # Forward and backward points
            vertices_plus = vertices.copy()
            vertices_minus = vertices.copy()
            vertices_plus[:, i] += h
            vertices_minus[:, i] -= h
            
            # Compute field values
            if field == 'N':
                field_plus = self.compute_segment_density(vertices_plus)
                field_minus = self.compute_segment_density(vertices_minus)
            elif field == 'tau':
                N_plus = self.compute_segment_density(vertices_plus)
                N_minus = self.compute_segment_density(vertices_minus)
                field_plus = self.compute_time_dilation(N_plus)
                field_minus = self.compute_time_dilation(N_minus)
            elif field == 'n':
                N_plus = self.compute_segment_density(vertices_plus)
                N_minus = self.compute_segment_density(vertices_minus)
                field_plus = self.compute_refractive_index(N_plus)
                field_minus = self.compute_refractive_index(N_minus)
            else:
                raise ValueError(f"Unknown field: {field}")
            
            # Central difference
            gradients[:, i] = (field_plus - field_minus) / (2 * h)
        
        return gradients

def create_solar_system_field(epoch: str = "2025-01-01") -> SegmentedSpacetimeField:
    """
    Create a segmented spacetime field for the Solar System.
    
    Parameters:
    -----------
    epoch : str
        Epoch for planetary positions
        
    Returns:
    --------
    field : SegmentedSpacetimeField
        Configured field calculator
    """
    
    # Field parameters (tunable)
    params = {
        'p': 2.0,           # Power-law index
        'N_bg': 0.0,        # Background density
        'N_max': 5.0,       # Maximum density
        'alpha': 1.0,       # Time dilation coupling
        'kappa': 0.015      # Refractive index coupling
    }
    
    field = SegmentedSpacetimeField(params)
    
    # Add Sun
    field.add_body(
        position=np.array([0.0, 0.0, 0.0]),
        mass_scaled=1.0,
        gamma=1.0,
        r0=0.00465,  # ~Solar radius in AU
        r_nb=0.02,   # Natural boundary
        delta=0.004, # Transition width
        name="Sun"
    )
    
    # Add major planets (approximate positions for demo)
    planets = [
        {"name": "Mercury", "pos": [0.39, 0.0, 0.0], "mass": 0.0553, "r0": 0.0000163},
        {"name": "Venus", "pos": [0.72, 0.0, 0.0], "mass": 0.815, "r0": 0.0000405},
        {"name": "Earth", "pos": [1.0, 0.0, 0.0], "mass": 1.0, "r0": 0.0000426},
        {"name": "Mars", "pos": [1.52, 0.0, 0.0], "mass": 0.107, "r0": 0.0000227},
        {"name": "Jupiter", "pos": [5.2, 0.0, 0.0], "mass": 317.8, "r0": 0.000477},
        {"name": "Saturn", "pos": [9.5, 0.0, 0.0], "mass": 95.2, "r0": 0.000403},
        {"name": "Uranus", "pos": [19.2, 0.0, 0.0], "mass": 14.5, "r0": 0.000171},
        {"name": "Neptune", "pos": [30.1, 0.0, 0.0], "mass": 17.1, "r0": 0.000165}
    ]
    
    for planet in planets:
        # Scale mass relative to Earth
        mass_scaled = planet["mass"] / 333000  # Earth masses to solar masses
        
        field.add_body(
            position=np.array(planet["pos"]),
            mass_scaled=mass_scaled,
            gamma=1.0,
            r0=planet["r0"],
            r_nb=planet["r0"] * 4,  # Natural boundary ~4x radius
            delta=planet["r0"] * 0.8,  # Transition width
            name=planet["name"]
        )
    
    return field

if __name__ == "__main__":
    # Test segmented spacetime field
    print("Testing segmented spacetime field calculations...")
    
    # Create test field
    field = create_solar_system_field()
    
    # Test points along x-axis
    test_points = np.array([
        [0.1, 0.0, 0.0],   # Near Sun
        [1.0, 0.0, 0.0],   # Earth orbit
        [5.2, 0.0, 0.0],   # Jupiter orbit
        [30.0, 0.0, 0.0],  # Neptune orbit
        [100.0, 0.0, 0.0]  # Outer system
    ])
    
    # Compute fields
    N, tau, n = field.compute_all_fields(test_points)
    
    print("\nField values at test points:")
    print("Distance (AU) | N(x)   | τ(x)   | n(x)")
    print("-" * 40)
    
    for i, point in enumerate(test_points):
        r = np.linalg.norm(point)
        print(f"{r:8.1f}      | {N[i]:.3f} | {tau[i]:.3f} | {n[i]:.4f}")
    
    # Test gradient computation
    grad_N = field.field_gradient(test_points[:2], field='N')
    print(f"\nGradient ∇N at Earth orbit: {grad_N[1]}")
    
    print("Segmented spacetime field test complete!")
