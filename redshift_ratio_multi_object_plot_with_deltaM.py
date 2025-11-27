#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redshift Ratio & Segment Density Diagnostics WITH ΔM correction (φ/2-BLC).

This is a DIAGNOSTIC TOOL for computing:
- Redshift z_total = (f_emit - f_obs) / f_obs
- Segment density N_seg ≈ z_total
- Δm correction via φ/2-BLC formula

This script does NOT compute bound energy in the paper's sense!
For true bound energy see: bound_energy.py (E = α·m_bound·c²)

© 2025 Carmen Wrede & Lino Casu – All rights reserved.
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys

# Set non-interactive backend for pipeline execution
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

from decimal import Decimal, getcontext
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# UTF-8 encoding for Windows (prevents UnicodeEncodeError)
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Precision
getcontext().prec = 80

# Physical constants
c = Decimal("299792458")  # Speed of light (m/s)
G = Decimal("6.67430e-11")  # Gravitational constant
h = Decimal("6.62607015e-34")  # Planck constant

# φ/2-BLC Correction (Golden Ratio based)
def corrected_delta_mass(N_seg):
    """
    Compute Δm correction using φ/2-BLC formula.
    
    This is a mass-correction diagnostic, not bound energy calculation!
    φ = golden ratio, BLC = φ/2 ≈ 0.809017
    """
    φ = (Decimal(1) + Decimal(5).sqrt()) / 2
    BLC = φ / 2  # ~0.809017...
    return BLC * Decimal(N_seg)

# Optional: GR Gravitational Redshift
def z_gravitational(M_kg: Decimal|None, r_m: Decimal|None):
    """
    Compute gravitational redshift z_gr from mass and radius.
    
    Returns None if parameters unavailable or unphysical.
    """
    if M_kg is None or r_m is None or r_m <= 0:
        return None
    r_s = Decimal(2) * G * M_kg / (c**2)
    if r_m <= r_s:
        return None
    return Decimal(1) / (Decimal(1) - r_s/r_m).sqrt() - Decimal(1)

# Optional: SR Doppler Factor
def doppler_factor(beta: Decimal|None, beta_los: Decimal|None=None):
    """
    Compute Special Relativistic Doppler factor D.
    
    D = γ(1 + β_los) where γ = 1/√(1-β²)
    """
    if beta is None:
        return None
    if beta_los is None:
        beta_los = beta
    one = Decimal(1)
    gamma = one / (one - beta*beta).sqrt()
    return gamma * (one + beta_los)

# Test objects (all redshifts COMPUTED, not fixed values)
objects = [
    {
        "name": "S2 star (Sag A*)",
        "f_emit": Decimal("138394255537000"),
        "f_obs_raw": Decimal("134920458147000"),
        # Optional physics for decomposition:
        "M_kg": None,        # e.g. Decimal("4.297e6") * M_sun
        "r_emit_m": None,    # Pericenter in m
        "beta": None,        # v_tot/c
        "beta_los": None     # Line-of-sight component
    },
    {
        "name": "White dwarf (Sirius B)",
        "f_emit": Decimal("4.568e14"),
        "f_obs_raw": Decimal("4.567e14"),
        "M_kg": None, "r_emit_m": None, "beta": None, "beta_los": None
    },
    {
        "name": "Sun (solar line)",
        "f_emit": Decimal("4.759e14"),
        "f_obs_raw": Decimal("4.759e14"),
        "M_kg": None, "r_emit_m": None, "beta": None, "beta_los": None
    },
    {
        "name": "Pound-Rebka (1959)",
        "f_emit": Decimal("3.482e18"),
        "f_obs_raw": Decimal("3.482e18"),
        "M_kg": None, "r_emit_m": None, "beta": None, "beta_los": None
    },
    {
        "name": "Earth surface test",
        "f_emit": Decimal("4.570e14"),
        "f_obs_raw": Decimal("4.570e14"),
        "M_kg": None, "r_emit_m": None, "beta": None, "beta_los": None
    },
]

print("\n" + "="*80)
print(" SEGMENTED SPACETIME – REDSHIFT RATIO & SEGMENT DENSITY DIAGNOSTICS")
print(" WITH ΔM CORRECTION (φ/2-BLC computed)")
print("="*80)
print("\nNOTE: This script computes REDSHIFT and SEGMENT DENSITY diagnostics,")
print("      NOT bound energy! For true bound energy see: bound_energy.py")
print("="*80)

rows = []
for obj in objects:
    name = obj["name"]
    f_emit = obj["f_emit"]
    f_obs_raw = obj["f_obs_raw"]

    # Total quantities (always computable)
    ratio_total = f_emit / f_obs_raw
    z_total = ratio_total - Decimal(1)  # Redshift

    # Optional GR/SR decomposition
    z_gr = z_gravitational(obj.get("M_kg"), obj.get("r_emit_m"))
    D = doppler_factor(obj.get("beta"), obj.get("beta_los"))

    f_obs_corr = None
    if z_gr is not None:
        f_obs_corr = f_emit / (Decimal(1) + z_gr)

    # Segment density (raw, without N0 baseline)
    N_seg = z_total  # In this script: N_seg = f_emit/f_obs_raw - 1 ≈ z_total

    # Δm correction via φ/2-BLC
    delta_m = corrected_delta_mass(N_seg)

    print(f"\n--- {name} ---")
    print(f"f_emit           : {f_emit:.6E} Hz")
    print(f"f_obs_raw        : {f_obs_raw:.6E} Hz")
    print(f"ratio_total      : {ratio_total}")
    print(f"z_total (redshift): {z_total}")
    
    # Display with defaults instead of N/A
    z_gr_display = z_gr if z_gr is not None else Decimal(0)
    D_display = D if D is not None else Decimal(1)
    f_obs_corr_display = f_obs_corr if f_obs_corr is not None else f_obs_raw
    
    print(f"z_gr (from M,r)  : {z_gr_display:.6E} (0 = no GR correction available)")
    print(f"D (SR Doppler)   : {D_display} (1 = no Doppler shift)")
    print(f"f_obs_corr (GR)  : {f_obs_corr_display:.6E} Hz (no correction needed)")
    print(f"N_seg (raw)      : {N_seg}")
    print(f"Δm_corr (φ/2-BLC): {delta_m}")

    rows.append({
        "object": name,
        "f_emit_Hz": float(f_emit),
        "f_obs_raw_Hz": float(f_obs_raw),
        "ratio_total": float(ratio_total),
        "z_total_redshift": float(z_total),  # Renamed for clarity
        "z_gr": float(z_gr) if z_gr is not None else 0.0,  # 0.0 instead of None
        "D_SR": float(D) if D is not None else 1.0,  # 1.0 instead of None (no Doppler)
        "f_obs_corr_GR_Hz": float(f_obs_corr) if f_obs_corr is not None else float(f_obs_raw),  # f_obs_raw instead of None
        "N_seg_raw": float(N_seg),
        "delta_m_corr": float(delta_m)
    })

# Export CSV with updated filename
df = pd.DataFrame(rows)
csv_path = Path("redshift_ratio_with_deltaM.csv")
df.to_csv(csv_path, index=False)
print(f"\nCSV export completed: {csv_path.resolve()}")

# Plot (Δm correction values as example)
plt.figure(figsize=(10, 6))
plt.bar([r["object"] for r in rows], [r["delta_m_corr"] for r in rows])
plt.title("Δm Correction (φ/2-BLC) vs. Object (computed from redshift)")
plt.ylabel("Δm_corr (dimensionless)")
plt.xlabel("Object")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plot_path = Path("redshift_ratio_with_deltaM_plot.png")
plt.savefig(plot_path, dpi=200)
print(f"Plot saved as: {plot_path.resolve()}")
plt.close()  # Close instead of show() for non-interactive pipeline execution

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
print("\nReminder: This script computed REDSHIFT RATIOS and SEGMENT DENSITY,")
print("          NOT bound energy! The φ/2-BLC correction is a mass-correction")
print("          diagnostic tool, not a bound energy solver.")
print("="*80)
