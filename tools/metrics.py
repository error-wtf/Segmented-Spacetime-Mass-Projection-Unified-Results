#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Statistical Metrics for SSZ Suite - Model Comparison & Validation

Implements standard metrics for model selection:
- RMSE, MAE (goodness of fit)
- AIC, BIC, WAIC (information criteria)
- Cliff's Delta (effect size)

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import math
import numpy as np
from typing import Union, List


def rmse(y_obs: Union[List, np.ndarray], y_pred: Union[List, np.ndarray]) -> float:
    """
    Root Mean Square Error
    
    Args:
        y_obs: Observed values
        y_pred: Predicted values
    
    Returns:
        float: RMSE value
    
    Formula:
        RMSE = sqrt(mean((y_obs - y_pred)^2))
    
    Interpretation:
        - Lower is better
        - Same units as y
        - Sensitive to outliers
    """
    y_obs = np.asarray(y_obs)
    y_pred = np.asarray(y_pred)
    return float(np.sqrt(np.mean((y_obs - y_pred) ** 2)))


def mae(y_obs: Union[List, np.ndarray], y_pred: Union[List, np.ndarray]) -> float:
    """
    Mean Absolute Error
    
    Args:
        y_obs: Observed values
        y_pred: Predicted values
    
    Returns:
        float: MAE value
    
    Formula:
        MAE = mean(|y_obs - y_pred|)
    
    Interpretation:
        - Lower is better
        - Same units as y
        - Robust to outliers (compared to RMSE)
    """
    y_obs = np.asarray(y_obs)
    y_pred = np.asarray(y_pred)
    return float(np.mean(np.abs(y_obs - y_pred)))


def mape(y_obs: Union[List, np.ndarray], y_pred: Union[List, np.ndarray]) -> float:
    """
    Mean Absolute Percentage Error
    
    Args:
        y_obs: Observed values
        y_pred: Predicted values
    
    Returns:
        float: MAPE value (as percentage)
    
    Warning:
        - Undefined if any y_obs == 0
        - Asymmetric (over-prediction penalized more than under-prediction)
    """
    y_obs = np.asarray(y_obs)
    y_pred = np.asarray(y_pred)
    
    # Avoid division by zero
    mask = y_obs != 0
    if not np.any(mask):
        return np.nan
    
    return float(100 * np.mean(np.abs((y_obs[mask] - y_pred[mask]) / y_obs[mask])))


def r_squared(y_obs: Union[List, np.ndarray], y_pred: Union[List, np.ndarray]) -> float:
    """
    Coefficient of Determination (R²)
    
    Args:
        y_obs: Observed values
        y_pred: Predicted values
    
    Returns:
        float: R² value
    
    Formula:
        R² = 1 - SS_res / SS_tot
        where SS_res = sum((y_obs - y_pred)^2)
              SS_tot = sum((y_obs - mean(y_obs))^2)
    
    Interpretation:
        - Range: (-∞, 1]
        - 1 = perfect fit
        - 0 = model no better than mean
        - <0 = model worse than mean
    """
    y_obs = np.asarray(y_obs)
    y_pred = np.asarray(y_pred)
    
    ss_res = np.sum((y_obs - y_pred) ** 2)
    ss_tot = np.sum((y_obs - np.mean(y_obs)) ** 2)
    
    if ss_tot == 0:
        return np.nan
    
    return float(1 - ss_res / ss_tot)


def aic(log_likelihood: float, k: int) -> float:
    """
    Akaike Information Criterion
    
    Args:
        log_likelihood: Log-likelihood of model
        k: Number of parameters
    
    Returns:
        float: AIC value
    
    Formula:
        AIC = 2k - 2*log(L)
    
    Interpretation:
        - Lower is better
        - Penalizes model complexity (number of parameters)
        - Assumes large sample size
    """
    return 2 * k - 2 * log_likelihood


def aicc(log_likelihood: float, k: int, n: int) -> float:
    """
    Corrected Akaike Information Criterion (for small samples)
    
    Args:
        log_likelihood: Log-likelihood of model
        k: Number of parameters
        n: Sample size
    
    Returns:
        float: AICc value
    
    Formula:
        AICc = AIC + 2k(k+1)/(n-k-1)
    
    Note:
        Use when n/k < 40
    """
    aic_val = aic(log_likelihood, k)
    
    if n - k - 1 <= 0:
        return np.inf  # Invalid (too many parameters)
    
    correction = 2 * k * (k + 1) / (n - k - 1)
    return aic_val + correction


def bic(log_likelihood: float, k: int, n: int) -> float:
    """
    Bayesian Information Criterion
    
    Args:
        log_likelihood: Log-likelihood of model
        k: Number of parameters
        n: Sample size
    
    Returns:
        float: BIC value
    
    Formula:
        BIC = log(n)*k - 2*log(L)
    
    Interpretation:
        - Lower is better
        - Stronger penalty for complexity than AIC
        - ΔBIC > 10: Strong evidence against higher BIC model
    """
    if n <= 0:
        return np.nan
    
    return math.log(n) * k - 2 * log_likelihood


def waic(log_pointwise_pred_density: np.ndarray) -> dict:
    """
    Watanabe-Akaike Information Criterion
    
    Args:
        log_pointwise_pred_density: Log pointwise predictive density
                                    Shape: (n_samples, n_observations)
    
    Returns:
        dict: WAIC components
            - waic: WAIC value
            - lppd: Log pointwise predictive density
            - p_waic: Effective number of parameters
    
    Note:
        Requires posterior samples (MCMC or Bootstrap)
    """
    log_ppd = np.asarray(log_pointwise_pred_density)
    
    # Log pointwise predictive density (lppd)
    lppd = np.sum(np.log(np.mean(np.exp(log_ppd), axis=0)))
    
    # Effective number of parameters (variance of log densities)
    p_waic = np.sum(np.var(log_ppd, axis=0))
    
    # WAIC
    waic_val = -2 * (lppd - p_waic)
    
    return {
        "waic": float(waic_val),
        "lppd": float(lppd),
        "p_waic": float(p_waic)
    }


def cliffs_delta(x: Union[List, np.ndarray], y: Union[List, np.ndarray]) -> float:
    """
    Cliff's Delta (non-parametric effect size)
    
    Args:
        x: First sample
        y: Second sample
    
    Returns:
        float: Cliff's delta value
    
    Formula:
        δ = (# pairs where x > y - # pairs where x < y) / (nx * ny)
    
    Interpretation:
        - Range: [-1, 1]
        - |δ| < 0.147: negligible
        - |δ| < 0.330: small
        - |δ| < 0.474: medium
        - |δ| ≥ 0.474: large
        - Positive: x tends to be larger than y
        - Negative: x tends to be smaller than y
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    # Count comparisons
    gt = 0  # x > y
    lt = 0  # x < y
    eq = 0  # x == y
    
    for xi in x:
        for yi in y:
            if xi > yi:
                gt += 1
            elif xi < yi:
                lt += 1
            else:
                eq += 1
    
    total = gt + lt + eq
    
    if total == 0:
        return 0.0
    
    return (gt - lt) / total


def cohens_d(x: Union[List, np.ndarray], y: Union[List, np.ndarray]) -> float:
    """
    Cohen's d (parametric effect size)
    
    Args:
        x: First sample
        y: Second sample
    
    Returns:
        float: Cohen's d value
    
    Formula:
        d = (mean(x) - mean(y)) / pooled_std
    
    Interpretation:
        - |d| < 0.2: small effect
        - |d| < 0.5: medium effect
        - |d| ≥ 0.8: large effect
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    nx = len(x)
    ny = len(y)
    
    if nx < 2 or ny < 2:
        return np.nan
    
    # Pooled standard deviation
    pooled_std = np.sqrt(((nx - 1) * np.var(x, ddof=1) + 
                          (ny - 1) * np.var(y, ddof=1)) / (nx + ny - 2))
    
    if pooled_std == 0:
        return np.nan
    
    return (np.mean(x) - np.mean(y)) / pooled_std


def relative_difference(y_obs: Union[List, np.ndarray], 
                        y_pred: Union[List, np.ndarray]) -> np.ndarray:
    """
    Relative difference (element-wise)
    
    Args:
        y_obs: Observed values
        y_pred: Predicted values
    
    Returns:
        np.ndarray: Relative differences
    
    Formula:
        rel_diff = (y_pred - y_obs) / y_obs
    
    Note:
        Returns NaN where y_obs == 0
    """
    y_obs = np.asarray(y_obs)
    y_pred = np.asarray(y_pred)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        return (y_pred - y_obs) / y_obs


def log_likelihood_gaussian(y_obs: Union[List, np.ndarray], 
                            y_pred: Union[List, np.ndarray],
                            sigma: float = None) -> float:
    """
    Log-likelihood assuming Gaussian errors
    
    Args:
        y_obs: Observed values
        y_pred: Predicted values
        sigma: Standard deviation (if None, estimate from residuals)
    
    Returns:
        float: Log-likelihood value
    
    Formula:
        log L = -n/2 * log(2π) - n/2 * log(σ²) - sum((y_obs - y_pred)^2) / (2σ²)
    """
    y_obs = np.asarray(y_obs)
    y_pred = np.asarray(y_pred)
    residuals = y_obs - y_pred
    n = len(y_obs)
    
    # Estimate sigma from residuals if not provided
    if sigma is None:
        sigma = np.std(residuals, ddof=1)
    
    if sigma <= 0:
        return -np.inf
    
    # Log-likelihood
    ll = -n / 2 * np.log(2 * np.pi)
    ll -= n / 2 * np.log(sigma ** 2)
    ll -= np.sum(residuals ** 2) / (2 * sigma ** 2)
    
    return float(ll)


def model_comparison(y_obs: Union[List, np.ndarray],
                    models: dict,
                    metrics: List[str] = None) -> dict:
    """
    Compare multiple models using multiple metrics
    
    Args:
        y_obs: Observed values
        models: Dict of {model_name: y_pred}
        metrics: List of metrics to compute (default: all)
    
    Returns:
        dict: Comparison results
    
    Example:
        results = model_comparison(
            y_obs=[1, 2, 3, 4],
            models={
                "SSZ": [1.1, 2.0, 2.9, 4.1],
                "GR": [0.9, 2.2, 3.1, 3.9]
            },
            metrics=["rmse", "mae", "r2"]
        )
    """
    if metrics is None:
        metrics = ["rmse", "mae", "r2"]
    
    y_obs = np.asarray(y_obs)
    results = {}
    
    for model_name, y_pred in models.items():
        y_pred = np.asarray(y_pred)
        model_results = {}
        
        for metric in metrics:
            if metric.lower() == "rmse":
                model_results["rmse"] = rmse(y_obs, y_pred)
            elif metric.lower() == "mae":
                model_results["mae"] = mae(y_obs, y_pred)
            elif metric.lower() in ["r2", "r_squared"]:
                model_results["r2"] = r_squared(y_obs, y_pred)
            elif metric.lower() == "mape":
                model_results["mape"] = mape(y_obs, y_pred)
        
        results[model_name] = model_results
    
    return results
