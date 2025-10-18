"""
Calibration Module for Segmented Radiowave Propagation

Implements α parameter fitting to minimize prediction errors.

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from __future__ import annotations
import numpy as np
from scipy.optimize import minimize_scalar
from typing import Optional, Tuple

from .seg_wave_propagation import predict_velocity_profile, compute_residuals


def fit_alpha(
    rings: np.ndarray,
    T: np.ndarray,
    v0: float,
    v_obs: np.ndarray,
    n: Optional[np.ndarray] = None,
    beta: float = 1.0,
    eta: float = 0.0,
    alpha_bounds: Tuple[float, float] = (0.1, 3.0)
) -> Tuple[float, dict]:
    """
    Fit optimal α parameter to minimize RMSE against observed velocities.
    
    Parameters:
    -----------
    rings : Ring/shell identifiers
    T : Temperature array (K)
    v0 : Initial velocity (km/s)
    v_obs : Observed velocities (km/s) - same length as rings
    n : Optional density array (cm^-3)
    beta : Temperature exponent (default 1.0)
    eta : Density exponent (default 0.0)
    alpha_bounds : Search bounds for α (default [0.1, 3.0])
    
    Returns:
    --------
    alpha_hat : Optimal α value
    metrics : dict with 'alpha', 'rmse', 'mae', 'max_abs_residual'
    """
    if len(rings) != len(v_obs):
        raise ValueError(f"rings and v_obs must have same length: {len(rings)} vs {len(v_obs)}")
    
    def objective(alpha: float) -> float:
        """RMSE objective to minimize"""
        try:
            df = predict_velocity_profile(
                rings, T, v0,
                alpha=alpha,
                n=n,
                beta=beta,
                eta=eta
            )
            v_pred = df["v_pred"].values
            metrics = compute_residuals(v_pred, v_obs)
            return metrics["rmse"]
        except Exception:
            # Return large penalty for invalid parameters
            return 1e10
    
    # Bounded scalar optimization
    result = minimize_scalar(
        objective,
        bounds=alpha_bounds,
        method='bounded'
    )
    
    alpha_hat = result.x
    rmse_final = result.fun
    
    # Compute final metrics with optimal α
    df_final = predict_velocity_profile(
        rings, T, v0,
        alpha=alpha_hat,
        n=n,
        beta=beta,
        eta=eta
    )
    
    v_pred_final = df_final["v_pred"].values
    final_metrics = compute_residuals(v_pred_final, v_obs)
    
    return alpha_hat, {
        "alpha": alpha_hat,
        "rmse": final_metrics["rmse"],
        "mae": final_metrics["mae"],
        "max_abs_residual": final_metrics["max_abs_residual"]
    }


def evaluate_alpha_grid(
    rings: np.ndarray,
    T: np.ndarray,
    v0: float,
    v_obs: np.ndarray,
    alpha_grid: np.ndarray,
    n: Optional[np.ndarray] = None,
    beta: float = 1.0,
    eta: float = 0.0
) -> dict:
    """
    Evaluate RMSE across a grid of α values for visualization.
    
    Returns:
    --------
    dict with 'alpha_values' and 'rmse_values' arrays
    """
    rmse_values = []
    
    for alpha in alpha_grid:
        try:
            df = predict_velocity_profile(
                rings, T, v0,
                alpha=alpha,
                n=n,
                beta=beta,
                eta=eta
            )
            v_pred = df["v_pred"].values
            metrics = compute_residuals(v_pred, v_obs)
            rmse_values.append(metrics["rmse"])
        except Exception:
            rmse_values.append(np.nan)
    
    return {
        "alpha_values": alpha_grid,
        "rmse_values": np.array(rmse_values)
    }
