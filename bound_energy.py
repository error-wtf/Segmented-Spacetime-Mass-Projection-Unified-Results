#!/usr/bin/env python3
"""
Segmented Spacetime Modell: Berechnung der relevanten Größen

Copyright (c) 2025 Carmen Wrede & Lino Casu
"""

import numpy as np

# Physikalische Konstanten
g = 6.67430e-11        # Gravitationskonstante (m^3 kg^-1 s^-2)
c = 2.99792458e8       # Lichtgeschwindigkeit (m/s)
h = 6.62607015e-34     # Plancksches Wirkungsquantum (J s)
m_e = 9.10938356e-31   # Elektronenmasse (kg)
M_sun = 1.98847e30     # Sonnenmasse (kg)
au = 1.495978707e11    # Astronomische Einheit (m)

# Modellparameter als dict für einfache Anpassung
def get_model_params():
    return {
        'f_obs': 2.30e14,                 # Beobachtete Frequenz in Hz
        'N0': 1.000000028,                # Null-Level
        'M_smbh': 4.1e6 * M_sun,          # Masse des SMBH in kg
        'r_peri': 120 * au,               # Perizentrum-Abstand in m
        'v_peri': 7.65e6                  # Transversale Bahngeschwindigkeit in m/s
    }

# Berechnungsfunktionen
def compute_redshifts(params):
    """
    Berechnet Gravitation- und Doppler-Rotverschiebung.
    """
    z_gr = g * params['M_smbh'] / (params['r_peri'] * c**2)
    z_dopp = 0.5 * (params['v_peri'] / c)**2
    return z_gr, z_dopp, z_gr + z_dopp


def compute_segment_density(params, z_total):
    """
    Berechnet emittierte Frequenz und Segmentdichte.
    """
    f_emit = params['f_obs'] * (1 + z_total)
    N_seg = f_emit / params['f_obs'] - params['N0']
    return f_emit, N_seg


def compute_electron_mass_shift(f_emit):
    """
    Berechnet Massenverschiebung des Elektrons.
    """
    delta_m = h * f_emit / c**2
    return delta_m, delta_m / m_e


def main():
    params = get_model_params()

    # 1) Rotverschiebungen berechnen
    z_gr, z_dopp, z_total = compute_redshifts(params)
    # 2) Frequenz & Segmentdichte berechnen
    f_emit, N_seg = compute_segment_density(params, z_total)
    # 3) Elektronen-Massenverschiebung berechnen
    delta_m, ratio = compute_electron_mass_shift(f_emit)

    # Ausgaben aller Werte mit präziser Formatierung
    print("=== Segmented Spacetime Modell Ergebnisse ===")
    print("Copyright (c) 2025 Carmen Wrede & Lino Casu")
    print(f"Beobachtete Frequenz (f_obs)       = {params['f_obs']:.6e} Hz")
    print(f"Null-Level (N0)                    = {params['N0']:.9f}")
    print(f"Masse SMBH (M_smbh)                = {params['M_smbh']:.6e} kg")
    print(f"Perizentrum-Abstand (r_peri)       = {params['r_peri']:.6e} m")
    print(f"Transversale Geschwindigkeit        = {params['v_peri']:.6e} m/s")
    print()
    print(f"Gravitations-Rotverschiebung (z_gr) = {z_gr:.9e}")
    print(f"Doppler-Rotverschiebung (z_dopp)    = {z_dopp:.9e}")
    print(f"Gesamt-Rotverschiebung (z_total)    = {z_total:.9e}")
    print()
    print(f"Emittierte Frequenz (f_emit)        = {f_emit:.6e} Hz")
    print(f"Segmentdichte (N_seg)               = {N_seg:.9e}")
    print()
    print(f"Elektronenmassenänderung (Δm)       = {delta_m:.9e} kg")
    print(f"Verhältnis Δm/m_e                   = {ratio:.9e}")

if __name__ == "__main__":
    main()
