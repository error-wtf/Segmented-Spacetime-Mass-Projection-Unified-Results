"""
Segmented Radiowave Propagation Module

This module implements radiowave propagation through segmented spacetime shells
based on the γ_seg(r) formalism.

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from .seg_wave_propagation import (
    predict_velocity_profile,
    predict_frequency_track,
    compute_residuals,
    compute_q_factor,
    compute_cumulative_gamma
)
from .calib import fit_alpha
from .io import load_ring_data, load_sources_manifest, load_sources_config, save_results, save_report

__all__ = [
    "predict_velocity_profile",
    "predict_frequency_track",
    "compute_residuals",
    "compute_q_factor",
    "compute_cumulative_gamma",
    "fit_alpha",
    "load_ring_data",
    "load_sources_manifest",
    "load_sources_config",
    "save_results",
    "save_report",
]
