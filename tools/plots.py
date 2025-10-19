#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot Utilities for SSZ Suite - Paper-Ready Figures

Generates publication-quality plots with consistent formatting:
- PNG (600 DPI) for drafts
- SVG (vector) for print/publishers
- Standard dimensions (160mm 2-column, 84mm 1-column)
- Minimal styling (neutral, no custom colors)

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import math
import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


def _ensure_dir(p):
    """Create directory if it doesn't exist"""
    Path(p).mkdir(parents=True, exist_ok=True)


def _fig_size(width_mm=160, aspect=0.62):
    """
    Calculate figure size in inches for Matplotlib
    
    Args:
        width_mm: Width in millimeters (160mm = 2-column, 84mm = 1-column)
        aspect: Height/Width ratio (0.62 ≈ golden ratio inverse)
    
    Returns:
        (width_inches, height_inches)
    """
    width_in = width_mm / 25.4  # mm to inches
    height_in = max(2.0, width_in * aspect)  # Minimum 2 inches height
    return (width_in, height_in)


def save_figure(fig, basepath, formats=("png", "svg"), dpi=300):
    """
    Save figure in multiple formats with consistent settings
    
    Args:
        fig: Matplotlib figure object
        basepath: Path without extension (e.g., "reports/figures/G79/fig_G79_velocity")
        formats: Tuple of formats ("png", "svg", "pdf")
        dpi: DPI for raster formats (300 for standard, 600 for high-quality)
    
    Returns:
        List of saved file paths
    """
    _ensure_dir(Path(basepath).parent)
    saved_paths = []
    
    for ext in formats:
        out = f"{basepath}.{ext}"
        if ext.lower() == "png":
            fig.savefig(out, dpi=dpi, bbox_inches="tight", facecolor='white', edgecolor='none')
        else:
            # Vector formats (SVG, PDF)
            fig.savefig(out, bbox_inches="tight", facecolor='white', edgecolor='none')
        saved_paths.append(out)
    
    plt.close(fig)
    return saved_paths


def plot_line(x, y, xlabel, ylabel, title, basepath, 
              formats=("png", "svg"), dpi=300, width_mm=160, 
              yerr=None, label=None):
    """
    Create line plot with optional error bars
    
    Args:
        x, y: Data arrays
        xlabel, ylabel: Axis labels
        title: Plot title
        basepath: Output path without extension
        formats: Output formats
        dpi: DPI for PNG
        width_mm: Figure width in millimeters
        yerr: Optional error bars (1D array or tuple (lower, upper))
        label: Optional legend label
    
    Returns:
        List of saved file paths
    """
    _ensure_dir(Path(basepath).parent)
    fig = plt.figure(figsize=_fig_size(width_mm))
    ax = fig.add_subplot(111)
    
    if yerr is not None:
        ax.errorbar(x, y, yerr=yerr, marker="o", linestyle="-", capsize=3, label=label)
    else:
        ax.plot(x, y, marker="o", linestyle="-", label=label)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, which="both", alpha=0.3, linestyle=":")
    
    if label:
        ax.legend(loc="best", framealpha=0.9)
    
    return save_figure(fig, basepath, formats=formats, dpi=dpi)


def plot_scatter(x, y, xlabel, ylabel, title, basepath,
                 formats=("png", "svg"), dpi=300, width_mm=160,
                 xerr=None, yerr=None, label=None):
    """
    Create scatter plot with optional error bars
    
    Args:
        x, y: Data arrays
        xlabel, ylabel: Axis labels
        title: Plot title
        basepath: Output path without extension
        formats: Output formats
        dpi: DPI for PNG
        width_mm: Figure width in millimeters
        xerr, yerr: Optional error bars
        label: Optional legend label
    
    Returns:
        List of saved file paths
    """
    _ensure_dir(Path(basepath).parent)
    fig = plt.figure(figsize=_fig_size(width_mm))
    ax = fig.add_subplot(111)
    
    if xerr is not None or yerr is not None:
        ax.errorbar(x, y, xerr=xerr, yerr=yerr, fmt="o", capsize=3, label=label)
    else:
        ax.scatter(x, y, s=16, label=label)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, which="both", alpha=0.3, linestyle=":")
    
    if label:
        ax.legend(loc="best", framealpha=0.9)
    
    return save_figure(fig, basepath, formats=formats, dpi=dpi)


def plot_heatmap(Z, x, y, xlabel, ylabel, title, basepath,
                 formats=("png", "svg"), dpi=300, width_mm=160,
                 cmap="viridis", cbar_label="score"):
    """
    Create heatmap (2D color plot)
    
    Args:
        Z: 2D array (shape: len(y) x len(x))
        x, y: 1D arrays for axis coordinates
        xlabel, ylabel: Axis labels
        title: Plot title
        basepath: Output path without extension
        formats: Output formats
        dpi: DPI for PNG
        width_mm: Figure width in millimeters
        cmap: Colormap name
        cbar_label: Colorbar label
    
    Returns:
        List of saved file paths
    """
    _ensure_dir(Path(basepath).parent)
    fig = plt.figure(figsize=_fig_size(width_mm, aspect=0.8))
    ax = fig.add_subplot(111)
    
    # Create mesh grid for imshow
    im = ax.imshow(Z, origin="lower", aspect="auto",
                   extent=[min(x), max(x), min(y), max(y)],
                   cmap=cmap, interpolation='nearest')
    
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(cbar_label)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    
    return save_figure(fig, basepath, formats=formats, dpi=dpi)


def plot_corner(samples, param_names, title, basepath,
                formats=("png", "svg"), dpi=300, width_mm=160):
    """
    Create corner plot (posterior distributions)
    
    Requires: corner package (pip install corner)
    
    Args:
        samples: 2D array (N_samples x N_params)
        param_names: List of parameter names
        title: Plot title
        basepath: Output path without extension
        formats: Output formats
        dpi: DPI for PNG
        width_mm: Figure width in millimeters
    
    Returns:
        List of saved file paths
    """
    try:
        import corner
    except ImportError:
        raise ImportError("corner package required: pip install corner")
    
    _ensure_dir(Path(basepath).parent)
    fig = corner.corner(samples, labels=param_names, 
                        quantiles=[0.16, 0.5, 0.84],
                        show_titles=True, title_fmt=".3f",
                        title_kwargs={"fontsize": 10})
    fig.suptitle(title, y=1.02)
    
    return save_figure(fig, basepath, formats=formats, dpi=dpi)


def plot_residuals(y_obs, y_pred, xlabel, basepath,
                   formats=("png", "svg"), dpi=300, width_mm=160):
    """
    Create residual plot (obs vs pred + residuals)
    
    Args:
        y_obs: Observed values
        y_pred: Predicted values
        xlabel: X-axis label (e.g., "Ring index k")
        basepath: Output path without extension
        formats: Output formats
        dpi: DPI for PNG
        width_mm: Figure width in millimeters
    
    Returns:
        List of saved file paths
    """
    _ensure_dir(Path(basepath).parent)
    
    residuals = np.array(y_obs) - np.array(y_pred)
    x = np.arange(len(y_obs))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=_fig_size(width_mm, aspect=0.8),
                                    sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    
    # Top: Observed vs Predicted
    ax1.plot(x, y_obs, 'o', label='Observed', markersize=6)
    ax1.plot(x, y_pred, 's', label='Predicted', markersize=4)
    ax1.set_ylabel('Value')
    ax1.legend(loc='best', framealpha=0.9)
    ax1.grid(True, which='both', alpha=0.3, linestyle=':')
    
    # Bottom: Residuals
    ax2.plot(x, residuals, 'o', markersize=4, color='red')
    ax2.axhline(0, color='black', linestyle='--', linewidth=1)
    ax2.set_xlabel(xlabel)
    ax2.set_ylabel('Residual')
    ax2.grid(True, which='both', alpha=0.3, linestyle=':')
    
    fig.suptitle('Model vs. Observation', y=0.995)
    plt.tight_layout()
    
    return save_figure(fig, basepath, formats=formats, dpi=dpi)


def plot_uncertainty_bands(x, y, y_lower, y_upper, xlabel, ylabel, title, basepath,
                           formats=("png", "svg"), dpi=300, width_mm=160,
                           band_label="68% CI"):
    """
    Create plot with uncertainty bands
    
    Args:
        x: X-axis data
        y: Central values (e.g., median)
        y_lower, y_upper: Lower/upper bounds
        xlabel, ylabel: Axis labels
        title: Plot title
        basepath: Output path without extension
        formats: Output formats
        dpi: DPI for PNG
        width_mm: Figure width in millimeters
        band_label: Label for uncertainty band
    
    Returns:
        List of saved file paths
    """
    _ensure_dir(Path(basepath).parent)
    fig = plt.figure(figsize=_fig_size(width_mm))
    ax = fig.add_subplot(111)
    
    ax.plot(x, y, 'o-', label='Central', linewidth=2)
    ax.fill_between(x, y_lower, y_upper, alpha=0.3, label=band_label)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, which='both', alpha=0.3, linestyle=':')
    
    return save_figure(fig, basepath, formats=formats, dpi=dpi)
