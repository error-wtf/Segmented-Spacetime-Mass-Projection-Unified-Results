"""
Segmented Radiowave Propagation - Core Physics

Implements γ_seg(r) as discrete shell sequence with:
- Velocity evolution: v_k = v_{k-1} · q_k^{-α/2}
- Frequency shift: ν_out(r_k) = ν_in · γ_k^{-1/2}

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Optional


def compute_q_factor(
    T_curr: float,
    T_prev: float,
    n_curr: Optional[float] = None,
    n_prev: Optional[float] = None,
    beta: float = 1.0,
    eta: float = 0.0
) -> float:
    """
    Compute q_k = γ_k / γ_{k-1} proxy from temperature/density.
    
    q_k ≈ (T_k / T_{k-1})^β · (n_k / n_{k-1})^η
    
    Parameters:
    -----------
    T_curr : Temperature at shell k (K)
    T_prev : Temperature at shell k-1 (K)
    n_curr : Optional density at shell k (cm^-3)
    n_prev : Optional density at shell k-1 (cm^-3)
    beta : Temperature exponent (default 1.0)
    eta : Density exponent (default 0.0)
    
    Returns:
    --------
    q_k : Gamma ratio
    """
    if T_prev <= 0 or T_curr <= 0:
        raise ValueError(f"Invalid temperature: T_prev={T_prev}, T_curr={T_curr}")
    
    q = (T_curr / T_prev) ** beta
    
    if eta != 0.0 and n_curr is not None and n_prev is not None:
        if n_prev <= 0 or n_curr <= 0:
            raise ValueError(f"Invalid density: n_prev={n_prev}, n_curr={n_curr}")
        q *= (n_curr / n_prev) ** eta
    
    return q


def predict_velocity_profile(
    rings: np.ndarray,
    T: np.ndarray,
    v0: float,
    alpha: float = 1.0,
    n: Optional[np.ndarray] = None,
    beta: float = 1.0,
    eta: float = 0.0
) -> pd.DataFrame:
    """
    Predict velocity profile v(r) through segmented shells.
    
    v_k = v_{k-1} · q_k^{-α/2}
    
    Parameters:
    -----------
    rings : Ring/shell identifiers (arbitrary labels or radii)
    T : Temperature array (K) - same length as rings
    v0 : Initial velocity at first shell (km/s)
    alpha : Calibration parameter (default 1.0)
    n : Optional density array (cm^-3)
    beta : Temperature exponent (default 1.0)
    eta : Density exponent (default 0.0)
    
    Returns:
    --------
    DataFrame with columns: ring, T, n (if provided), q_k, v_pred
    """
    if len(rings) != len(T):
        raise ValueError(f"rings and T must have same length: {len(rings)} vs {len(T)}")
    
    if n is not None and len(n) != len(T):
        raise ValueError(f"n must have same length as T: {len(n)} vs {len(T)}")
    
    N = len(rings)
    q_vals = np.zeros(N)
    v_vals = np.zeros(N)
    
    # First shell
    q_vals[0] = 1.0
    v_vals[0] = v0
    
    # Propagate through shells
    for k in range(1, N):
        n_curr = n[k] if n is not None else None
        n_prev = n[k-1] if n is not None else None
        
        q_k = compute_q_factor(
            T[k], T[k-1],
            n_curr, n_prev,
            beta, eta
        )
        
        v_k = v_vals[k-1] * (q_k ** (-alpha / 2.0))
        
        q_vals[k] = q_k
        v_vals[k] = v_k
    
    # Build DataFrame
    data = {
        "ring": rings,
        "T": T,
        "q_k": q_vals,
        "v_pred": v_vals
    }
    
    if n is not None:
        data["n"] = n
    
    return pd.DataFrame(data)


def predict_frequency_track(
    nu_in: float,
    gamma_series: np.ndarray
) -> pd.Series:
    """
    Compute frequency evolution through shells.
    
    ν_out(r_k) = ν_in · γ_k^{-1/2}
    
    Parameters:
    -----------
    nu_in : Input frequency (Hz)
    gamma_series : Array of cumulative γ values per shell
    
    Returns:
    --------
    Series of output frequencies (Hz)
    """
    if np.any(gamma_series <= 0):
        raise ValueError("All gamma values must be positive")
    
    nu_out = nu_in * (gamma_series ** (-0.5))
    return pd.Series(nu_out, name="nu_out_Hz")


def compute_residuals(
    v_pred: np.ndarray,
    v_obs: np.ndarray
) -> dict:
    """
    Compute residuals and metrics between predicted and observed velocities.
    
    Returns:
    --------
    dict with keys: residuals (array), mae, rmse, max_abs_residual
    """
    residuals = v_pred - v_obs
    mae = np.mean(np.abs(residuals))
    rmse = np.sqrt(np.mean(residuals ** 2))
    max_abs = np.max(np.abs(residuals))
    
    return {
        "residuals": residuals,
        "mae": mae,
        "rmse": rmse,
        "max_abs_residual": max_abs
    }


def compute_cumulative_gamma(q_series: np.ndarray) -> np.ndarray:
    """
    Compute cumulative gamma values from q_k ratios.
    
    γ_k = ∏_{i=1}^{k} q_i
    
    Parameters:
    -----------
    q_series : Array of q_k values
    
    Returns:
    --------
    Cumulative gamma array
    """
    return np.cumprod(q_series)
