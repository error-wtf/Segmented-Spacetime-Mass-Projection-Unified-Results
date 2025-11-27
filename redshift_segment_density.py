#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
redshift_segment_density.py – Segmented Spacetime vs. Classical GR Redshift

Dieses Skript macht NICHTS mit Bound Energy,
sondern:

- nimmt eine Emissionsfrequenz f_emit und eine beobachtete Frequenz f_obs
- berechnet:
    * Segmentdichte N_seg = f_emit / f_obs - N0
    * klassischen GR-Redshift z_gr = (f_emit - f_obs) / f_obs
    * Photonenergie E_gamma = h * f_emit
    * lokales Energieverhältnis
          epsilon_local = E_gamma(f_obs) / (m_e c^2)
      (reine Skalenrelation, keine Feinstrukturkonstante!)

- vergleicht N_seg und z_gr
- exportiert alles in eine CSV-Datei.
"""

import os
import sys

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

from scipy.constants import h, m_e, c
import pandas as pd
from pathlib import Path
import pprint
import os
import sys

# === FUNCTIONS ===


def compute_segment_density(f_emit: float, f_obs: float,
                            N0: float = 1.000000028) -> float:
    """Segmentdichte im SSZ-Modell, hier einfach als Offset relativ zu N0."""
    return f_emit / f_obs - N0


def compute_photon_energy(f_emit: float) -> float:
    """Photonenergie zur Emissionsfrequenz."""
    return h * f_emit


def compute_gravitational_redshift(f_emit: float, f_obs: float) -> float:
    """Klassischer GR-Redshift (kleine z): (f_emit - f_obs) / f_obs."""
    return (f_emit - f_obs) / f_obs


def compute_local_energy_ratio(f_obs: float,
                               m_e_: float = m_e,
                               c_: float = c,
                               h_: float = h) -> float:
    """
    Lokales Energieverhältnis epsilon_local:

        epsilon_local = E_gamma(f_obs) / (m_e c^2)

    Das ist nur ein dimensionsloses Energieskalen-Verhältnis und
    KEINE lokale Feinstrukturkonstante.
    """
    E_gamma_obs = h_ * f_obs
    return E_gamma_obs / (m_e_ * c_**2)


# === MAIN ===

if __name__ == '__main__':
    print("=" * 72)
    print(" SEGMENTED SPACETIME – REDSHIFT & SEGMENT DENSITY CHECK")
    print("=" * 72)
    print(" Copyright (c) 2025 Carmen Wrede & Lino Casu – All rights reserved.\n")

    # Beispiel: S2/Sgr A* Linie
    f_emit = 138_392_455_537_000   # [Hz]
    f_obs  = 134_920_458_147_000   # [Hz]
    N0     = 1.000000028

    # Berechnungen
    N_seg   = compute_segment_density(f_emit, f_obs, N0)
    E_gamma = compute_photon_energy(f_emit)
    z_gr    = compute_gravitational_redshift(f_emit, f_obs)
    epsilon_local = compute_local_energy_ratio(f_obs)

    # Feinstrukturkonstante nur als Referenz (wird hier NICHT benutzt)
    alpha_fs = 1.0 / 137.035999084  # CODATA 2018

    result = {
        "Emission frequency f_emit [Hz]": f_emit,
        "Observed frequency f_obs [Hz]": f_obs,
        "Base segmentation density N0": N0,
        "Segment density N_seg": N_seg,
        "Photon energy E_gamma [J]": E_gamma,
        "Fine-structure constant alpha_fs (CODATA)": alpha_fs,
        "Classical gravitational redshift z_gr": z_gr,
        "Local energy ratio epsilon_local": epsilon_local,
    }

    print("Computed parameters (all values calculated, not just printed):")
    pprint.pprint(result, sort_dicts=False)

    print("\nComparison: Segmented model vs. classical gravitational redshift:")
    print(f"  Segment density (N_seg)   : {N_seg:.9f}")
    print(f"  GR redshift (z_gr)        : {z_gr:.9f}")
    if abs(N_seg - z_gr) < 1e-6:
        print("  → Both models yield nearly identical results for these values.")
    else:
        print("  → The values differ – see model assumptions.")

    print("\nInterpretation note:")
    print("  epsilon_local = E_gamma(f_obs) / (m_e c^2) ist nur ein")
    print("  Energieskalen-Verhältnis und KEINE lokale Feinstrukturkonstante.")
    print("  Es hat hier rein diagnostischen Charakter (Größenordnung der Linie).")

    # === CSV EXPORT ===
    csv_data = {
        "f_emit_Hz": [f_emit],
        "f_obs_Hz": [f_obs],
        "N0": [N0],
        "N_seg": [N_seg],
        "E_gamma_J": [E_gamma],
        "alpha_fs": [alpha_fs],
        "z_gr": [z_gr],
        "epsilon_local": [epsilon_local],
    }
    df = pd.DataFrame(csv_data)
    csv_path = Path("redshift_segment_density_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nResults have also been exported as CSV: {csv_path.resolve()}")
