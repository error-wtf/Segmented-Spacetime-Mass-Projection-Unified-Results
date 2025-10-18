#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extended Ring Metrics & Statistics for SSZ Pipeline

Provides:
- compute_ring_metrics: Calculate γ, Δv, E_k from ring data
- export_ring_metrics_csv: Write metrics to CSV
- correlation_summary: Compute fit quality statistics
- residuals: Calculate model-observation differences

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from pathlib import Path
import csv
import numpy as np


def _safe_dir(p: Path):
    """Ensure parent directory exists."""
    p.parent.mkdir(parents=True, exist_ok=True)


def _write_csv(path, header, rows):
    """Write CSV file with UTF-8 encoding."""
    path = Path(path)
    _safe_dir(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return str(path)


def _pearson(x, y):
    """Calculate Pearson correlation coefficient."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2:
        return float("nan")
    cx = x - x.mean()
    cy = y - y.mean()
    denom = np.sqrt((cx**2).sum()) * np.sqrt((cy**2).sum())
    return float((cx * cy).sum() / denom) if denom > 0 else float("nan")


def compute_ring_metrics(k, T, n, v, q=None, gamma=None, mass_proxy=1.0):
    """
    Calculate extended ring metrics: γ, Δv, E_k.
    
    Parameters:
    -----------
    k : array
        Ring indices
    T : array
        Temperatures [K]
    n : array
        Densities [cm^-3]
    v : array
        Velocities [km/s]
    q : array, optional
        Temperature ratios. If None, calculated from T.
    gamma : array, optional
        Cumulative time-density. If None, calculated as cumprod(q).
    mass_proxy : float
        Normalization for energy calculation
        
    Returns:
    --------
    dict with keys: k, T, n, v, q, gamma, log_gamma, dv, E
    """
    k = np.asarray(k, dtype=float)
    T = np.asarray(T, dtype=float)
    n = np.asarray(n, dtype=float)
    v = np.asarray(v, dtype=float)

    # q from temperature ratios if not provided
    if q is None:
        q = np.ones_like(T)
        if len(T) > 1:
            q[1:] = T[1:] / T[:-1]
    else:
        q = np.asarray(q, dtype=float)

    # gamma from cumulative product if not provided
    if gamma is None:
        gamma = np.cumprod(q)
    else:
        gamma = np.asarray(gamma, dtype=float)

    # Velocity differences
    dv = np.zeros_like(v)
    if len(v) > 1:
        dv[:-1] = v[1:] - v[:-1]

    # Segment energy (normalized)
    Ek = 0.5 * mass_proxy * (v**2)

    metrics = {
        "k": k,
        "T": T,
        "n": n,
        "v": v,
        "q": q,
        "gamma": gamma,
        "log_gamma": np.log(np.clip(gamma, 1e-20, None)),
        "dv": dv,
        "E": Ek
    }
    return metrics


def export_ring_metrics_csv(obj_name, metrics, outdir="reports/data"):
    """
    Export ring metrics to CSV file.
    
    Parameters:
    -----------
    obj_name : str
        Object name (e.g., "G79", "CygnusX")
    metrics : dict
        Dictionary from compute_ring_metrics()
    outdir : str
        Output directory
        
    Returns:
    --------
    str : Path to created CSV file
    """
    out = Path(outdir) / f"{obj_name}_ring_metrics.csv"
    header = ["k", "T[K]", "n[cm^-3]", "v[km_s]", "q_k", "gamma", 
              "log_gamma", "delta_v", "E[arb]"]
    rows = list(zip(
        metrics["k"], metrics["T"], metrics["n"], metrics["v"],
        metrics["q"], metrics["gamma"], metrics["log_gamma"],
        metrics["dv"], metrics["E"]
    ))
    return _write_csv(out, header, rows)


def correlation_summary(obj_name, metrics, v_obs=None, outdir="reports/stats"):
    """
    Calculate and export correlation statistics.
    
    Parameters:
    -----------
    obj_name : str
        Object name
    metrics : dict
        Dictionary from compute_ring_metrics()
    v_obs : array, optional
        Observed velocities for residual calculation
    outdir : str
        Output directory
        
    Returns:
    --------
    str : Path to created CSV file
    """
    out = Path(outdir) / f"{obj_name}_fit_summary.csv"
    v = metrics["v"]
    T = metrics["T"]
    n = metrics["n"]
    
    # Correlations
    corr_vT = _pearson(v, T)
    corr_vn = _pearson(v, n)
    
    # Residuals if observations provided
    mae = rmse = maxabs = float("nan")
    if v_obs is not None:
        v_obs = np.asarray(v_obs, dtype=float)
        m = min(len(v), len(v_obs))
        res = v[:m] - v_obs[:m]
        mae = float(np.mean(np.abs(res)))
        rmse = float(np.sqrt(np.mean(res**2)))
        maxabs = float(np.max(np.abs(res)))
    
    header = ["r(v,T)", "r(v,n)", "MAE[km_s]", "RMSE[km_s]", "MaxAbsRes[km_s]"]
    rows = [(corr_vT, corr_vn, mae, rmse, maxabs)]
    return _write_csv(out, header, rows)


def residuals(v, v_obs):
    """
    Calculate residuals between model and observations.
    
    Parameters:
    -----------
    v : array
        Model velocities
    v_obs : array
        Observed velocities
        
    Returns:
    --------
    array : Residuals (v - v_obs)
    """
    v = np.asarray(v, dtype=float)
    v_obs = np.asarray(v_obs, dtype=float)
    m = min(len(v), len(v_obs))
    return v[:m] - v_obs[:m]
