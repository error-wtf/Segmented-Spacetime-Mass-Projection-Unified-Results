#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ vs GR Core Models

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import numpy as np
from scipy.optimize import brentq

# Physical constants
G = 6.67430e-11  # m³/kg/s²
c = 299792458.0  # m/s
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ≈ 1.6180339887


def schwarzschild_rs(M):
    """
    Schwarzschild radius
    
    Args:
        M: Mass in kg
    
    Returns:
        r_s in meters
    """
    return 2 * G * M / (c**2)


def xi_exponential(r, rs, xi_max=0.802, phi=PHI):
    """
    Exponential segment density function
    
    Ξ(r) = Ξ_max(1 - exp(-φ * r/r_s))
    
    Args:
        r: Radial coordinate (array or scalar)
        rs: Schwarzschild radius
        xi_max: Maximum segment density (default 0.802)
        phi: Golden ratio (default PHI)
    
    Returns:
        Ξ(r) values
    """
    r = np.asarray(r)
    rs = float(rs)
    return xi_max * (1.0 - np.exp(-phi * r / rs))


def time_dilation_ssz(r, rs, xi_max=0.802, phi=PHI):
    """
    SSZ time dilation (relative clock rate)
    
    D_SSZ(r) = 1 / (1 + Ξ(r))
    
    Args:
        r: Radial coordinate (array or scalar)
        rs: Schwarzschild radius
        xi_max: Maximum segment density
        phi: Golden ratio
    
    Returns:
        D_SSZ(r) - relative time dilation (1 = no dilation)
    """
    xi = xi_exponential(r, rs, xi_max, phi)
    return 1.0 / (1.0 + xi)


def time_dilation_gr(r, rs):
    """
    GR Schwarzschild time dilation
    
    D_GR(r) = sqrt(1 - r_s/r) for r > r_s
    
    Args:
        r: Radial coordinate (array or scalar)
        rs: Schwarzschild radius
    
    Returns:
        D_GR(r) - Schwarzschild time dilation
    """
    r = np.asarray(r)
    rs = float(rs)
    
    # Mask for valid region (r > r_s)
    valid = r > rs
    result = np.zeros_like(r, dtype=float)
    result[valid] = np.sqrt(1.0 - rs / r[valid])
    result[~valid] = np.nan  # Undefined inside horizon
    
    return result


def find_intersection(rs, xi_max=0.802, phi=PHI, r_min=None, r_max=None):
    """
    Find intersection point where D_SSZ(r) = D_GR(r)
    
    Args:
        rs: Schwarzschild radius
        xi_max: Maximum segment density
        phi: Golden ratio
        r_min: Minimum search radius (default: 1.05 * rs)
        r_max: Maximum search radius (default: 10 * rs)
    
    Returns:
        dict with keys:
            - r_star: Intersection radius
            - r_over_rs: r*/r_s
            - D_star: Time dilation at intersection
            - xi_star: Ξ at intersection
    """
    if r_min is None:
        r_min = 1.05 * rs
    if r_max is None:
        r_max = 10.0 * rs
    
    def difference(r):
        """D_GR(r) - D_SSZ(r)"""
        d_gr = time_dilation_gr(r, rs)
        d_ssz = time_dilation_ssz(r, rs, xi_max, phi)
        return d_gr - d_ssz
    
    # Check if intersection exists in range
    f_min = difference(r_min)
    f_max = difference(r_max)
    
    if f_min * f_max > 0:
        raise ValueError(f"No intersection found in range [{r_min/rs:.2f}, {r_max/rs:.2f}] r_s")
    
    # Find root
    r_star = brentq(difference, r_min, r_max, xtol=1e-12)
    
    return {
        'r_star': r_star,
        'r_over_rs': r_star / rs,
        'D_star': time_dilation_gr(r_star, rs),
        'xi_star': xi_exponential(r_star, rs, xi_max, phi)
    }


def redshift_gr(r, rs):
    """
    GR gravitational redshift z = 1/D_GR - 1
    
    Args:
        r: Radial coordinate
        rs: Schwarzschild radius
    
    Returns:
        Redshift z
    """
    d_gr = time_dilation_gr(r, rs)
    return 1.0 / d_gr - 1.0


def redshift_ssz(r, rs, xi_max=0.802, phi=PHI):
    """
    SSZ gravitational redshift z = 1/D_SSZ - 1
    
    Args:
        r: Radial coordinate
        rs: Schwarzschild radius
        xi_max: Maximum segment density
        phi: Golden ratio
    
    Returns:
        Redshift z
    """
    d_ssz = time_dilation_ssz(r, rs, xi_max, phi)
    return 1.0 / d_ssz - 1.0
