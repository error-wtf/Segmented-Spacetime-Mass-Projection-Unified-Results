"""
Visualization Module for Segmented Radiowave Propagation

Simple plotting utilities (optional, requires matplotlib).

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from __future__ import annotations
import numpy as np
from pathlib import Path
from typing import Optional

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def plot_velocity_comparison(
    rings: np.ndarray,
    v_pred: np.ndarray,
    v_obs: Optional[np.ndarray] = None,
    output_path: Optional[str | Path] = None,
    title: str = "Velocity Profile Comparison"
) -> None:
    """
    Plot predicted vs observed velocity profiles.
    
    Parameters:
    -----------
    rings : Ring/shell identifiers
    v_pred : Predicted velocities (km/s)
    v_obs : Optional observed velocities (km/s)
    output_path : Optional path to save PNG
    title : Plot title
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for plotting. Install with: pip install matplotlib")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(rings, v_pred, 'b-o', label='SSZ Prediction', linewidth=2, markersize=6)
    
    if v_obs is not None:
        ax.plot(rings, v_obs, 'ro', label='Observed', markersize=8, alpha=0.7)
        
        # Plot residuals as error bars
        residuals = v_pred - v_obs
        ax.errorbar(rings, v_obs, yerr=np.abs(residuals), 
                   fmt='none', ecolor='gray', alpha=0.3, capsize=4)
    
    ax.set_xlabel('Ring / Shell', fontsize=12)
    ax.set_ylabel('Velocity (km/s)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_alpha_scan(
    alpha_values: np.ndarray,
    rmse_values: np.ndarray,
    alpha_opt: Optional[float] = None,
    output_path: Optional[str | Path] = None
) -> None:
    """
    Plot RMSE vs α parameter scan.
    
    Parameters:
    -----------
    alpha_values : Array of α values
    rmse_values : Array of RMSE values
    alpha_opt : Optional optimal α to mark
    output_path : Optional path to save PNG
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for plotting. Install with: pip install matplotlib")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(alpha_values, rmse_values, 'b-', linewidth=2)
    ax.scatter(alpha_values, rmse_values, c='blue', s=40, alpha=0.6)
    
    if alpha_opt is not None:
        ax.axvline(alpha_opt, color='red', linestyle='--', linewidth=2, 
                  label=f'α_opt = {alpha_opt:.3f}')
        ax.legend(fontsize=11)
    
    ax.set_xlabel('α Parameter', fontsize=12)
    ax.set_ylabel('RMSE (km/s)', fontsize=12)
    ax.set_title('Parameter Calibration: RMSE vs α', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved: {output_path}")
    else:
        plt.show()
    
    plt.close()
