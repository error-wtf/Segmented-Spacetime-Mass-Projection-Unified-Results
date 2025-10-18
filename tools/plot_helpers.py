#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compact Plot Helpers for SSZ Suite

Convenience wrappers around tools/plots.py for quick figure generation.
These are the "copy-paste-ready" functions from Lino's snippet.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tools.plots import _ensure_dir, _fig_size, save_figure


def line(x, y, xlab, ylab, title, base, formats=("png", "svg"), dpi=600, width_mm=160):
    """
    Compact line plot
    
    Example:
        paths = line([1,2,3], [10,11,12], "x", "y", "Title", "reports/fig_test")
    """
    _ensure_dir(Path(base).parent)
    fig = plt.figure(figsize=_fig_size(width_mm))
    ax = fig.add_subplot(111)
    ax.plot(x, y, marker="o")
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    return save_figure(fig, base, formats, dpi)


def scatter(x, y, xlab, ylab, title, base, formats=("png", "svg"), dpi=600, width_mm=160):
    """
    Compact scatter plot
    
    Example:
        paths = scatter([1,2,3], [10,11,12], "x", "y", "Title", "reports/fig_test")
    """
    _ensure_dir(Path(base).parent)
    fig = plt.figure(figsize=_fig_size(width_mm))
    ax = fig.add_subplot(111)
    ax.scatter(x, y, s=16)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    return save_figure(fig, base, formats, dpi)


def heatmap(Z, x, y, xlab, ylab, title, base, formats=("png", "svg"), dpi=600, width_mm=160):
    """
    Compact heatmap
    
    Args:
        Z: 2D array (values)
        x, y: 1D arrays (axis values)
    
    Example:
        import numpy as np
        Z = np.random.rand(10, 10)
        paths = heatmap(Z, range(10), range(10), "x", "y", "Heatmap", "reports/fig_heat")
    """
    import numpy as np
    _ensure_dir(Path(base).parent)
    fig = plt.figure(figsize=_fig_size(width_mm, aspect=0.8))
    ax = fig.add_subplot(111)
    im = ax.imshow(Z, origin="lower", aspect="auto",
                   extent=[min(x), max(x), min(y), max(y)])
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("score")
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    return save_figure(fig, base, formats, dpi)
