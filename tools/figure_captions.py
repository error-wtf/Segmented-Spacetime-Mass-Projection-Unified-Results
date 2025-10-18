#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figure Captions for SSZ Suite Paper Exports

Paper-ready captions for all generated plots.
Carmen can copy these directly into LaTeX/Word.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

# Object-specific captions (use {obj} placeholder for object name)
OBJECT_CAPTIONS = {
    "ringchain_v_vs_k": (
        "Ring-chain propagation in the SSZ field. "
        "Orbital velocity (v_k) increases despite falling temperature over ring index (k), "
        "reproducing observed flat rotation curves (14–16 km s⁻¹)."
    ),
    
    "gamma_log_vs_k": (
        "Exponential growth of cumulative time-density (γ) along rings, "
        "demonstrating scale-invariant self-organization of the segmented field."
    ),
    
    "freqshift_vs_gamma": (
        "Prediction of frequency-dependent shift ν_out(γ), "
        "explaining radio emission in cool zones (radio–molecular overlap)."
    ),
    
    "residuals_model_vs_obs": (
        "Deviations between SSZ model and observed velocities/line strengths; "
        "low RMSE/MAE confirms the fit quality."
    ),
    
    "posterior_corner": (
        "Posterior distributions of key factors (α, β, η) "
        "with confidence intervals (68/95 %)."
    ),
    
    "uncertainty_bands_v_vs_k": (
        "Uncertainty propagation: 68% band for v_k "
        "after measurement errors in T, n, v₀."
    ),
    
    "line_ratios_vs_radius": (
        "Predicted line ratios (e.g., CO(2–1)/CO(3–2), NH₃(1,1)/(2,2)) "
        "as a function of radius—observational test."
    ),
    
    "radio_spectral_index": (
        "Prediction of radio spectral index (α_r) "
        "as a function of the γ-field."
    ),
}

# Shared/comparison captions (cross-object)
SHARED_CAPTIONS = {
    "model_compare_scores": (
        "AIC/BIC/WAIC and RMSE comparison: SSZ vs. Shock/PDR/GR(α=0). "
        "ΔBIC ≫ 10 strongly favors SSZ."
    ),
    
    "sweep_heatmap_alpha_beta": (
        "Parameter landscape: goodness-of-fit scores over α×β "
        "show robust plateaus and low degeneracies."
    ),
    
    "lensing_deflection_map": (
        "Effective deflection angle from the γ-field (proxy), "
        "independent SSZ test."
    ),
    
    "stability_criteria": (
        "Stability criteria (∂v/∂k, ∂²v/∂k², entropy proxy); "
        "marks stable molecular zones."
    ),
}


def get_caption(figure_name, object_name=None):
    """
    Get caption for a figure
    
    Args:
        figure_name: Name without prefix (e.g., "ringchain_v_vs_k")
        object_name: Object name (e.g., "G79") or None for shared figures
    
    Returns:
        str: Caption text
    """
    if object_name:
        # Object-specific caption
        caption = OBJECT_CAPTIONS.get(figure_name, "")
        return caption.format(obj=object_name) if "{obj}" in caption else caption
    else:
        # Shared caption
        return SHARED_CAPTIONS.get(figure_name, "")


def format_caption_for_latex(caption, label):
    """
    Format caption for LaTeX figure environment
    
    Args:
        caption: Caption text
        label: LaTeX label (e.g., "fig:G79_velocity")
    
    Returns:
        str: LaTeX-formatted caption
    """
    return f"\\caption{{{caption}\\label{{{label}}}}}"


def format_caption_for_markdown(caption, figure_path):
    """
    Format caption for Markdown
    
    Args:
        caption: Caption text
        figure_path: Path to figure file
    
    Returns:
        str: Markdown-formatted caption
    """
    return f"![{caption}]({figure_path})"


# Full catalog with categories (for documentation)
CATALOG = {
    "object_specific": {
        "velocity_propagation": {
            "figures": ["ringchain_v_vs_k", "uncertainty_bands_v_vs_k"],
            "description": "Velocity evolution along ring chain with SSZ field effects"
        },
        "time_density": {
            "figures": ["gamma_log_vs_k"],
            "description": "Cumulative time-density field growth"
        },
        "spectral_predictions": {
            "figures": ["freqshift_vs_gamma", "line_ratios_vs_radius", "radio_spectral_index"],
            "description": "Observable predictions for line emission and radio continuum"
        },
        "model_validation": {
            "figures": ["residuals_model_vs_obs", "posterior_corner"],
            "description": "Model fit quality and parameter constraints"
        },
    },
    "shared": {
        "model_comparison": {
            "figures": ["model_compare_scores"],
            "description": "SSZ vs. alternative models (Shock, PDR, GR)"
        },
        "parameter_space": {
            "figures": ["sweep_heatmap_alpha_beta"],
            "description": "Grid sweeps over parameter space"
        },
        "additional_tests": {
            "figures": ["lensing_deflection_map", "stability_criteria"],
            "description": "Independent tests and stability analysis"
        },
    }
}
