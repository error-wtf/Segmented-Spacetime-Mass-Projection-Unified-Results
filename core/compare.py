#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Comparison for SSZ Suite

Compare SSZ against baseline models (Shock, PDR, GR α=0).
Uses AIC, BIC, WAIC, RMSE, and effect sizes.

TODO: Implement baseline model predictions
- Current: Placeholder
- Needed: Physics for Shock/PDR/GR predictions

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import numpy as np
from typing import Dict, List
from tools.metrics import rmse, mae, aic, bic, cliffs_delta, log_likelihood_gaussian
from tools.io_utils import safe_write_csv, register_artifact


def compare_models(
    y_obs: np.ndarray,
    models: Dict[str, np.ndarray],
    metrics: List[str] = None,
    out_csv: str = "reports/compare/model_scores.csv",
    manifest_path: str = None
) -> Dict:
    """
    Compare multiple models using information criteria and fit metrics
    
    Args:
        y_obs: Observed values
        models: Dict of {model_name: y_pred}
            e.g., {"SSZ": [...], "Shock": [...], "PDR": [...]}
        metrics: List of metrics to compute
            Options: "rmse", "mae", "aic", "bic", "waic", "cliffs"
        out_csv: Output CSV path
        manifest_path: Optional manifest path
    
    Returns:
        dict: Comparison results
            {model_name: {metric: value}}
    
    Example:
        results = compare_models(
            y_obs=[1, 2, 3, 4],
            models={
                "SSZ": [1.1, 2.0, 2.9, 4.1],
                "GR": [0.9, 2.2, 3.1, 3.9]
            },
            metrics=["rmse", "aic", "bic"]
        )
    """
    if metrics is None:
        metrics = ["rmse", "mae", "aic", "bic"]
    
    n = len(y_obs)
    results = {}
    
    for model_name, y_pred in models.items():
        model_results = {}
        
        # Fit metrics
        if "rmse" in metrics:
            model_results["rmse"] = rmse(y_obs, y_pred)
        
        if "mae" in metrics:
            model_results["mae"] = mae(y_obs, y_pred)
        
        # Information criteria (requires log-likelihood)
        if "aic" in metrics or "bic" in metrics:
            # Assume Gaussian errors
            ll = log_likelihood_gaussian(y_obs, y_pred)
            
            # Assume k=3 parameters (α, β, η) for all models
            # TODO: Adjust based on actual model complexity
            k = 3
            
            if "aic" in metrics:
                model_results["aic"] = aic(ll, k)
            
            if "bic" in metrics:
                model_results["bic"] = bic(ll, k, n)
        
        results[model_name] = model_results
    
    # Effect sizes (pairwise comparisons)
    if "cliffs" in metrics and len(models) >= 2:
        model_names = list(models.keys())
        for i in range(len(model_names)):
            for j in range(i+1, len(model_names)):
                name1, name2 = model_names[i], model_names[j]
                residuals1 = y_obs - models[name1]
                residuals2 = y_obs - models[name2]
                delta = cliffs_delta(np.abs(residuals1), np.abs(residuals2))
                results[f"{name1}_vs_{name2}_delta"] = delta
    
    # Write CSV
    header = ["model"] + metrics
    rows = []
    for model_name, model_results in results.items():
        if "_vs_" not in model_name:  # Skip pairwise comparisons in table
            row = [model_name] + [model_results.get(m, np.nan) for m in metrics]
            rows.append(row)
    
    safe_write_csv(out_csv, header, rows)
    
    # Register in manifest
    if manifest_path:
        register_artifact(manifest_path, "compare_scores", out_csv, format="csv")
    
    return results


def predict_baseline_shock(T: np.ndarray, n: np.ndarray, v0: float) -> np.ndarray:
    """
    Predict velocities using Shock model
    
    Args:
        T, n: Temperature and density
        v0: Initial velocity
    
    Returns:
        np.ndarray: Predicted velocities
    
    TODO - IMPLEMENT:
        Shock model physics:
        - Jump conditions
        - Post-shock cooling
        - Velocity evolution
    
    Note:
        STUB - returns dummy predictions!
    """
    # PLACEHOLDER: Simple power-law
    n_rings = len(T)
    v_pred = v0 * (T / T[0]) ** 0.5  # Example: v ∝ √T
    return v_pred


def predict_baseline_pdr(T: np.ndarray, n: np.ndarray, v0: float) -> np.ndarray:
    """
    Predict velocities using PDR (Photo-Dissociation Region) model
    
    Args:
        T, n: Temperature and density
        v0: Initial velocity
    
    Returns:
        np.ndarray: Predicted velocities
    
    TODO - IMPLEMENT:
        PDR model physics:
        - UV heating
        - Chemical stratification
        - Pressure balance
    
    Note:
        STUB - returns dummy predictions!
    """
    # PLACEHOLDER: Isothermal expansion
    n_rings = len(T)
    v_pred = np.full(n_rings, v0)  # Constant velocity
    return v_pred


def predict_baseline_gr_alpha0(T: np.ndarray, n: np.ndarray, v0: float) -> np.ndarray:
    """
    Predict velocities using GR with α=0 (no SSZ field)
    
    Args:
        T, n: Temperature and density (unused in α=0 limit)
        v0: Initial velocity
    
    Returns:
        np.ndarray: Predicted velocities (constant = v0)
    
    Note:
        α=0 → No segment field → Classical limit
        All velocities = v0
    """
    n_rings = len(T)
    v_pred = np.full(n_rings, v0)
    return v_pred


def run_full_comparison(
    T: np.ndarray,
    n: np.ndarray,
    v_obs: np.ndarray,
    v0: float,
    v_ssz: np.ndarray,
    metrics: List[str] = None,
    out_csv: str = "reports/compare/model_scores.csv",
    manifest_path: str = None
) -> Dict:
    """
    Run full model comparison: SSZ vs. Shock vs. PDR vs. GR(α=0)
    
    Args:
        T, n: Input data
        v_obs: Observed velocities
        v0: Initial velocity
        v_ssz: SSZ model predictions
        metrics: Metrics to compute
        out_csv: Output CSV path
        manifest_path: Optional manifest path
    
    Returns:
        dict: Comparison results
    
    Example:
        results = run_full_comparison(
            T=T, n=n, v_obs=v_obs, v0=12.5,
            v_ssz=ssz_predictions,
            metrics=["rmse", "aic", "bic"]
        )
    """
    # Generate baseline predictions
    # TODO: Replace with actual physics
    models = {
        "SSZ": v_ssz,
        "Shock": predict_baseline_shock(T, n, v0),
        "PDR": predict_baseline_pdr(T, n, v0),
        "GR_alpha0": predict_baseline_gr_alpha0(T, n, v0)
    }
    
    return compare_models(v_obs, models, metrics, out_csv, manifest_path)
