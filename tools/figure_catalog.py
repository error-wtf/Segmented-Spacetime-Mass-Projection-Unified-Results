#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figure Caption Catalog for SSZ Suite

Paper-ready captions for all generated figures.
Copy-paste directly into LaTeX/Markdown.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

# Complete caption catalog with LaTeX-ready descriptions
CAPTIONS = {
    "ringchain_v_vs_k":
        "Ring-Ketten-Propagation im SSZ-Feld. Die Umlaufgeschwindigkeit v_k steigt "
        "trotz fallender Temperatur über k und reproduziert die 14–16 km s⁻¹.",
    
    "gamma_log_vs_k":
        "Exponentielles Wachstum der kumulativen Zeitdichte γ entlang der Ringe – "
        "skaleninvariante Selbstorganisation des segmentierten Feldes.",
    
    "freqshift_vs_gamma":
        "Vorhersage des frequenzabhängigen Shifts ν_out(γ), der Radioemission in "
        "kühlen Zonen (Radio–Molekül-Overlap) erklärt.",
    
    "residuals_model_vs_obs":
        "Residuen zwischen SSZ-Modell und Beobachtung; geringe RMSE/MAE belegen die Anpassung.",
    
    "posterior_corner":
        "Posterior-Verteilungen von (α, β, η) mit 68/95%-Konfidenzintervallen.",
    
    "uncertainty_bands_v_vs_k":
        "Unsicherheitspropagation: 68%-Band für v_k nach Messfehlern in T, n, v0.",
    
    "line_ratios_vs_radius":
        "Vorhergesagte Linienverhältnisse (z.B. CO(2–1)/CO(3–2), NH₃(1,1)/(2,2)) "
        "als Funktion des Radius.",
    
    "radio_spectral_index":
        "Vorhersage des Radio-Spektralindex α_r in Abhängigkeit des γ-Feldes.",
    
    "model_compare_scores":
        "AIC/BIC/WAIC und RMSE: SSZ vs. Shock/PDR/GR(α=0) – ΔBIC ≫ 10 favorisiert SSZ.",
    
    "sweep_heatmap_alpha_beta":
        "Parameterlandschaft (α×β): Gütemaße zeigen robuste Plateaus und geringe Degeneranzen.",
    
    "lensing_deflection_map":
        "Effektiver Deflektionswinkel (Proxy) aus dem γ-Feld – unabhängiger SSZ-Test.",
    
    "stability_criteria":
        "Stabilitätskriterien ∂v/∂k, ∂²v/∂k² und Entropie-Proxy; markiert stabile Molekül-Zonen."
}


def get_caption(figure_name: str, object_name: str = None) -> str:
    """
    Get caption for a figure
    
    Args:
        figure_name: Name of figure (e.g., "ringchain_v_vs_k")
        object_name: Optional object name to prepend (e.g., "G79")
    
    Returns:
        str: Caption text
    
    Example:
        caption = get_caption("ringchain_v_vs_k", "G79")
        # → "G79: Ring-Ketten-Propagation..."
    """
    caption = CAPTIONS.get(figure_name, f"Figure: {figure_name}")
    
    if object_name:
        caption = f"{object_name}: {caption}"
    
    return caption


def list_all_figures():
    """List all available figure names"""
    return sorted(CAPTIONS.keys())
