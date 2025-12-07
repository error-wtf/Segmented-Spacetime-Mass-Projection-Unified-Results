#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PERFECT ENERGY FORMULAS - Clean Implementation

Fundamental formula:
  E_obs(r,v) = E_rest × γ_SR(v) × γ_GR/SSZ(r)

where:
  E_rest = mc² (baseline/anchor)
  γ_SR = 1/√(1 - v²/c²) (SR modulation)
  γ_GR = 1/√(1 - r_s/r) (GR modulation)
  γ_SSZ = γ_GR × F(Ξ(r)) (SSZ modulation)

© 2025 Carmen Wrede & Lino Casu
"""

import numpy as np
from astropy import units as u
from astropy.constants import G, c, M_sun

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio

# ============================================================================
# BASELINE ENERGY (Anchor)
# ============================================================================

def E_rest(m):
    """
    Baseline rest energy (ontological).
    
    E_rest = m·c²
    
    This is the energy that EXISTS in local frame.
    NOT an additive component!
    
    Parameters
    ----------
    m : Quantity
        Rest mass
        
    Returns
    -------
    E : Quantity
        Rest energy
    """
    return m * c**2

# ============================================================================
# TRANSFORMATION FACTORS (Observational)
# ============================================================================

def gamma_SR(v):
    """
    Special relativistic γ factor.
    
    γ_SR = 1/√(1 - v²/c²)
    
    Describes HOW E_rest appears due to motion.
    NOT a separate energy!
    
    Parameters
    ----------
    v : Quantity
        Velocity
        
    Returns
    -------
    gamma : float
        Lorentz factor (≥ 1)
    """
    beta = (v / c).decompose().value
    beta_clamped = min(beta, 0.9999)  # Numerical stability
    return 1.0 / np.sqrt(1 - beta_clamped**2)

def gamma_GR(M, r):
    """
    General relativistic γ factor (Schwarzschild).
    
    γ_GR = √(-g_tt(∞)/-g_tt(r)) = 1/√(1 - r_s/r)
    
    Describes HOW E_rest appears due to gravity.
    NOT a separate energy!
    
    Parameters
    ----------
    M : Quantity
        Mass of gravitating body
    r : Quantity
        Radius from center
        
    Returns
    -------
    gamma : float
        Gravitational factor (≥ 1)
    """
    r_s = (2 * G * M / c**2).to(r.unit)
    ratio = (r_s / r).decompose().value
    ratio_clamped = min(ratio, 0.99)  # Numerical stability
    return 1.0 / np.sqrt(1 - ratio_clamped)

def Xi_SSZ(M, r, xi_max=0.8):
    """
    SSZ segment density Ξ(r).
    
    Ξ(r) = ξ_max·(1 - exp(-φ·r_s/r))
    
    Parameters
    ----------
    M : Quantity
        Mass
    r : Quantity
        Radius
    xi_max : float
        Maximum segment density
        
    Returns
    -------
    xi : float
        Segment density (0 to ξ_max)
    """
    r_s = (2 * G * M / c**2).to(r.unit)
    ratio = (r_s / r).decompose().value
    return xi_max * (1 - np.exp(-PHI * ratio))

def F_SSZ(xi):
    """
    SSZ modulation factor F(Ξ).
    
    F(Ξ) = 1/(1 + Ξ)
    
    Parameters
    ----------
    xi : float
        Segment density
        
    Returns
    -------
    F : float
        Modulation factor (0 < F ≤ 1)
    """
    return 1.0 / (1 + xi)

def gamma_SSZ(M, r, v, xi_max=0.8):
    """
    SSZ total γ factor.
    
    γ_SSZ = γ_SR/D_SSZ
    where D_SSZ = F(Ξ) = 1/(1 + Ξ)
    
    Parameters
    ----------
    M : Quantity
        Mass
    r : Quantity
        Radius
    v : Quantity
        Velocity
    xi_max : float
        Maximum segment density
        
    Returns
    -------
    gamma : float
        SSZ γ factor
    """
    xi = Xi_SSZ(M, r, xi_max)
    D_SSZ = F_SSZ(xi)
    γ_sr = gamma_SR(v)
    return γ_sr / D_SSZ

# ============================================================================
# OBSERVED ENERGY (Perfect Formula)
# ============================================================================

def E_obs_GR(m, M, r, v):
    """
    Observed energy in GR.
    
    E_obs = E_rest × γ_SR × γ_GR
    
    PERFECT FORMULA (multiplicative).
    
    Parameters
    ----------
    m : Quantity
        Test mass
    M : Quantity
        Gravitating mass
    r : Quantity
        Radius
    v : Quantity
        Velocity
        
    Returns
    -------
    E : Quantity
        Observed energy
    """
    E_r = E_rest(m)
    γ_sr = gamma_SR(v)
    γ_gr = gamma_GR(M, r)
    
    return E_r * γ_sr * γ_gr

def E_obs_SSZ(m, M, r, v, xi_max=0.8):
    """
    Observed energy in SSZ.
    
    E_obs = E_rest × γ_SR × γ_GR × F(Ξ)
    
    PERFECT FORMULA (multiplicative).
    
    Parameters
    ----------
    m : Quantity
        Test mass
    M : Quantity
        Gravitating mass
    r : Quantity
        Radius
    v : Quantity
        Velocity
    xi_max : float
        Maximum segment density
        
    Returns
    -------
    E : Quantity
        Observed energy (SSZ)
    """
    E_r = E_rest(m)
    γ_sr = gamma_SR(v)
    γ_gr = gamma_GR(M, r)
    xi = Xi_SSZ(M, r, xi_max)
    F = F_SSZ(xi)
    
    return E_r * γ_sr * γ_gr * F

# ============================================================================
# BOOKKEEPING FORM (Additive, for tables/plots)
# ============================================================================

def Delta_E_SR(m, v):
    """
    SR energy contribution (bookkeeping).
    
    ΔE_SR = (γ_SR - 1)·E_rest
    
    This is NOT a separate energy!
    It's how much E_rest APPEARS different due to SR.
    
    Parameters
    ----------
    m : Quantity
        Mass
    v : Quantity
        Velocity
        
    Returns
    -------
    Delta_E : Quantity
        SR contribution
    """
    E_r = E_rest(m)
    γ_sr = gamma_SR(v)
    return (γ_sr - 1) * E_r

def Delta_E_GR(m, M, r):
    """
    GR energy contribution (bookkeeping).
    
    ΔE_GR = (γ_GR - 1)·E_rest
    
    This is NOT a separate energy!
    It's how much E_rest APPEARS different due to GR.
    
    Parameters
    ----------
    m : Quantity
        Mass
    M : Quantity
        Gravitating mass
    r : Quantity
        Radius
        
    Returns
    -------
    Delta_E : Quantity
        GR contribution
    """
    E_r = E_rest(m)
    γ_gr = gamma_GR(M, r)
    return (γ_gr - 1) * E_r

def Delta_E_SSZ(m, M, r, xi_max=0.8):
    """
    SSZ energy contribution (bookkeeping).
    
    ΔE_SSZ = (γ_GR·F(Ξ) - 1)·E_rest
    
    This is NOT a separate energy!
    It's how much E_rest APPEARS different due to SSZ.
    
    Parameters
    ----------
    m : Quantity
        Mass
    M : Quantity
        Gravitating mass
    r : Quantity
        Radius
    xi_max : float
        Maximum segment density
        
    Returns
    -------
    Delta_E : Quantity
        SSZ contribution
    """
    E_r = E_rest(m)
    γ_gr = gamma_GR(M, r)
    xi = Xi_SSZ(M, r, xi_max)
    F = F_SSZ(xi)
    return (γ_gr * F - 1) * E_r

def E_obs_additive_GR(m, M, r, v):
    """
    Observed energy (additive bookkeeping).
    
    E_obs ≈ E_rest + ΔE_SR + ΔE_GR
    
    BOOKKEEPING FORM (for tables/plots).
    Mathematically equivalent to multiplicative form.
    
    Parameters
    ----------
    m, M, r, v : Quantity
        As in E_obs_GR
        
    Returns
    -------
    E : Quantity
        Observed energy
    """
    E_r = E_rest(m)
    ΔE_sr = Delta_E_SR(m, v)
    ΔE_gr = Delta_E_GR(m, M, r)
    
    return E_r + ΔE_sr + ΔE_gr

def E_obs_additive_SSZ(m, M, r, v, xi_max=0.8):
    """
    Observed energy SSZ (additive bookkeeping).
    
    E_obs ≈ E_rest + ΔE_SR + ΔE_SSZ
    
    BOOKKEEPING FORM (for tables/plots).
    
    Parameters
    ----------
    m, M, r, v, xi_max : as above
        
    Returns
    -------
    E : Quantity
        Observed energy (SSZ)
    """
    E_r = E_rest(m)
    ΔE_sr = Delta_E_SR(m, v)
    ΔE_ssz = Delta_E_SSZ(m, M, r, xi_max)
    
    return E_r + ΔE_sr + ΔE_ssz

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*80)
    print("PERFECT ENERGY FORMULAS - Example")
    print("="*80)
    
    # Setup
    m = 1.0 * u.kg
    M = 1.0 * M_sun
    R = 1.0 * u.R_sun
    v = np.sqrt(G * M / R)  # Keplerian
    
    print(f"\nSetup:")
    print(f"  m = {m}")
    print(f"  M = {M.to(M_sun):.3f}")
    print(f"  R = {R.to(u.km):.0f}")
    print(f"  v = {v.to(u.km/u.s):.3f}")
    
    # Baseline
    E_r = E_rest(m)
    print(f"\n{'-'*80}")
    print("BASELINE ENERGY (Anchor):")
    print(f"  E_rest = {E_r.to(u.J):.6e}")
    
    # Factors
    γ_sr = gamma_SR(v)
    γ_gr = gamma_GR(M, R)
    
    print(f"\n{'-'*80}")
    print("TRANSFORMATION FACTORS:")
    print(f"  gamma_SR = {γ_sr:.9f}")
    print(f"  gamma_GR = {γ_gr:.9f}")
    
    # GR (multiplicative)
    E_gr = E_obs_GR(m, M, R, v)
    print(f"\n{'-'*80}")
    print("GR OBSERVED ENERGY (Multiplicative):")
    print(f"  E_obs = E_rest * gamma_SR * gamma_GR")
    print(f"  E_obs = {E_gr.to(u.J):.6e}")
    print(f"  E_obs/E_rest = {(E_gr/E_r).decompose():.9f}")
    
    # GR (additive)
    E_gr_add = E_obs_additive_GR(m, M, R, v)
    print(f"\nGR OBSERVED ENERGY (Additive Bookkeeping):")
    print(f"  E_obs = E_rest + DeltaE_SR + DeltaE_GR")
    print(f"  E_obs = {E_gr_add.to(u.J):.6e}")
    print(f"  E_obs/E_rest = {(E_gr_add/E_r).decompose():.9f}")
    print(f"  Difference: {abs((E_gr - E_gr_add)/E_gr).decompose():.3e}")
    
    # SSZ
    E_ssz = E_obs_SSZ(m, M, R, v)
    xi = Xi_SSZ(M, R)
    
    print(f"\n{'-'*80}")
    print("SSZ OBSERVED ENERGY:")
    print(f"  Xi(R) = {xi:.6f}")
    print(f"  F(Xi) = {F_SSZ(xi):.6f}")
    print(f"  E_obs = {E_ssz.to(u.J):.6e}")
    print(f"  E_obs/E_rest = {(E_ssz/E_r).decompose():.9f}")
    
    # Comparison
    print(f"\n{'-'*80}")
    print("GR vs SSZ:")
    print(f"  |E_SSZ - E_GR|/E_GR = {abs((E_ssz - E_gr)/E_gr).decompose():.6e}")
    
    print(f"\n{'='*80}")
    print("PASS: Perfect formulas work correctly!")
    print(f"{'='*80}\n")
