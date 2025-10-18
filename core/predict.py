#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Observable Predictions for SSZ Suite

Predict line ratios and radio spectral index from γ-field.

TODO: Implement actual excitation physics
- Current: Placeholder
- Needed: Map γ → T_ex → line ratios

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import numpy as np
from typing import Dict, List
from tools.io_utils import safe_write_csv, register_artifact


def predict_line_ratios(
    gamma: np.ndarray,
    radius: np.ndarray,
    lines: List[str] = None,
    out_csv: str = "reports/pred/line_ratios.csv",
    manifest_path: str = None
) -> Dict:
    """
    Predict molecular line intensity ratios from γ-field
    
    Args:
        gamma: Segment field strength (γ)
        radius: Radial positions [pc]
        lines: List of line transitions
            Options: "co21", "co32", "nh3_11", "nh3_22", "cii"
        out_csv: Output CSV path
        manifest_path: Optional manifest path
    
    Returns:
        dict: Line ratio predictions
            {line_pair: ratio_array}
    
    TODO - IMPLEMENT:
        1. Map γ → excitation temperature T_ex
        2. For each molecular transition:
           - Compute level populations (LTE or non-LTE)
           - Calculate line intensities
        3. Compute ratios:
           - CO(2-1)/CO(3-2)
           - NH₃(1,1)/NH₃(2,2)
           - [CII]/CO ratios
    
    Physics:
        - γ affects local kinetic temperature
        - Temperature affects excitation
        - Excitation determines line ratios
    
    Note:
        STUB - returns dummy ratios!
    """
    if lines is None:
        lines = ["co21", "co32", "nh3_11", "nh3_22"]
    
    n_points = len(gamma)
    
    # TODO: REPLACE THIS PLACEHOLDER!
    # Map γ → line ratios using real excitation physics
    
    # Dummy line intensities
    intensities = {
        "co21": 1.0 / gamma,  # PLACEHOLDER: I ∝ 1/γ
        "co32": 0.5 / gamma,
        "nh3_11": 0.8 / gamma,
        "nh3_22": 0.4 / gamma,
        "cii": 2.0 / gamma
    }
    
    # Compute ratios
    ratios = {
        "co21_co32": intensities["co21"] / intensities["co32"],
        "nh3_11_nh3_22": intensities["nh3_11"] / intensities["nh3_22"],
        "cii_co21": intensities["cii"] / intensities["co21"]
    }
    
    # Write CSV
    header = ["radius_pc", "gamma"] + list(ratios.keys())
    rows = []
    for i in range(n_points):
        row = [radius[i], gamma[i]] + [ratios[key][i] for key in ratios.keys()]
        rows.append(row)
    
    safe_write_csv(out_csv, header, rows)
    
    # Register in manifest
    if manifest_path:
        register_artifact(manifest_path, "predict_lines", out_csv, format="csv")
    
    return ratios


def predict_radio_spectral_index(
    gamma: np.ndarray,
    frequency: np.ndarray = None,
    out_csv: str = "reports/pred/radio_slope.csv",
    manifest_path: str = None
) -> Dict:
    """
    Predict radio spectral index α_r from γ-field
    
    Args:
        gamma: Segment field strength (γ)
        frequency: Frequency grid [GHz] (optional)
        out_csv: Output CSV path
        manifest_path: Optional manifest path
    
    Returns:
        dict: Radio predictions
            - alpha_r: Spectral index (S_ν ∝ ν^α_r)
            - flux_density: Predicted flux at each frequency
    
    TODO - IMPLEMENT:
        1. Map γ → electron temperature T_e
        2. Compute emission measure EM
        3. Calculate free-free emission:
           S_ν ∝ ν^α_r with α_r = f(T_e, EM)
        4. Account for synchrotron contribution if needed
    
    Physics:
        - γ-field affects plasma conditions
        - T_e determines spectral index
        - α_r ≈ -0.1 (thermal) to -0.7 (non-thermal)
    
    Note:
        STUB - returns dummy spectral index!
    """
    if frequency is None:
        frequency = np.array([1.4, 5.0, 10.0])  # GHz
    
    n_points = len(gamma)
    
    # TODO: REPLACE THIS PLACEHOLDER!
    # Map γ → α_r using real plasma physics
    
    # Dummy spectral index
    alpha_r = -0.1 - 0.2 * (1 - gamma)  # PLACEHOLDER: α_r ∈ [-0.3, -0.1]
    
    # Dummy flux density
    flux_1p4GHz = 100.0 * gamma  # mJy at 1.4 GHz
    
    # Write CSV
    header = ["gamma", "alpha_r", "flux_1.4GHz_mJy"]
    rows = []
    for i in range(n_points):
        rows.append([gamma[i], alpha_r[i], flux_1p4GHz[i]])
    
    safe_write_csv(out_csv, header, rows)
    
    # Register in manifest
    if manifest_path:
        register_artifact(manifest_path, "radio_slope", out_csv, format="csv")
    
    return {
        "alpha_r": alpha_r,
        "flux_1.4GHz": flux_1p4GHz
    }


def predict_frequency_shift(
    gamma: np.ndarray,
    nu_in: float = 1e12,
    out_csv: str = "reports/pred/freq_shift.csv",
    manifest_path: str = None
) -> np.ndarray:
    """
    Predict frequency shift ν_out(γ)
    
    Args:
        gamma: Segment field strength (γ)
        nu_in: Input frequency [Hz]
        out_csv: Output CSV path
        manifest_path: Optional manifest path
    
    Returns:
        np.ndarray: Output frequencies ν_out [Hz]
    
    Formula:
        ν_out = ν_in × γ^(-1/2)
    
    Physics:
        - Photons redshift in segment field
        - Explains radio-molecular overlap
    """
    nu_out = nu_in * gamma ** (-0.5)
    
    # Write CSV
    header = ["gamma", "nu_in_Hz", "nu_out_Hz", "redshift_z"]
    rows = []
    for i in range(len(gamma)):
        z = (nu_in - nu_out[i]) / nu_out[i]
        rows.append([gamma[i], nu_in, nu_out[i], z])
    
    safe_write_csv(out_csv, header, rows)
    
    # Register in manifest
    if manifest_path:
        register_artifact(manifest_path, "freq_shift", out_csv, format="csv")
    
    return nu_out
