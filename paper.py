#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segmented Spacetime – Bound Energy & Fine Structure Constant
Rekonstruktion aller Paper-Berechnungen (2025)
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

import math
import scipy.constants as sc

# === Naturkonstanten ===
e = sc.elementary_charge  # Coulomb
epsilon_0 = sc.epsilon_0  # F/m
h = sc.h                  # J*s
c = sc.c                  # m/s
m_e = sc.m_e              # kg
alpha_fs = 1 / 137.035999084

# === 1. Effektiver Radius r, Segmentlänge phi, Segmentanzahl Ne ===
def effective_radius(phi, Ne):
    """r = phi / Ne"""
    return phi / Ne

def segmented_phi_from_rNe(r, Ne):
    """phi = r * Ne"""
    return r * Ne

# === 2. Klassische elektromagnetische Selbstenergie ===
def classical_self_energy(e, epsilon_0, r):
    """E_el = e^2 / (4 * pi * epsilon_0 * r)"""
    return e**2 / (4 * math.pi * epsilon_0 * r)

# === 3. Verhältnis Selbstenergie zu Ruheenergie ===
def alpha_structural(e, epsilon_0, phi, Ne, m_bound, c):
    """alpha = (e^2 * Ne) / (4 * pi * epsilon_0 * phi * m_bound * c^2)"""
    return (e**2 * Ne) / (4 * math.pi * epsilon_0 * phi * m_bound * c**2)

# === 4. Effektiver Radius bei fester alpha ===
def effective_radius_from_alpha(e, epsilon_0, alpha, m_bound, c):
    """r_eff = e^2 / (4 * pi * epsilon_0 * alpha * m_bound * c^2)"""
    return e**2 / (4 * math.pi * epsilon_0 * alpha * m_bound * c**2)

# === 5. Segmentlänge phi aus r_eff, Ne ===
def phi_from_rNe(r_eff, Ne):
    """phi = r_eff * Ne"""
    return r_eff * Ne

# === 6. Photon: minimal N = 4 (4-Segment-Basis), Elektron: N_e = 1 (unsegmentiert) ===

# === 7. Bound vs Free Energy ===
def rydberg_energy(alpha, m_e, c):
    """E_R = (alpha^2 * m_e * c^2) / 2"""
    return (alpha**2 * m_e * c**2) / 2

def bound_energy(alpha, m_bound, c):
    """E_bound = alpha * m_bound * c^2"""
    return alpha * m_bound * c**2

def free_energy(m, c):
    """E_free = m * c^2"""
    return m * c**2

# === 8. Segmentabhängige Kopplung: Wellenlänge/Grenzfrequenz für Photonen ===
def photon_threshold_lambda(h, c, alpha, m_e):
    """lambda_gamma = h / (alpha * m_e * c)"""
    return h / (alpha * m_e * c)

def photon_threshold_freq(alpha, m_bound, c, h):
    """f = (alpha * m_bound * c^2) / h"""
    return (alpha * m_bound * c**2) / h

# === 9. Beispiel: S2 bei Sgr A* ===
def sagittariusA_star_example():
    f_emit = 138_394_255_537_000  # Hz (lokale Emissionsfrequenz S2)
    f_obs  = 134_920_458_147_000  # Hz (auf Erde, Doppler-korrigiert)
    N0 = 1.0000000028             # Basis-Segmentierung
    alpha_fs = 1 / 137.035999084

    # Frequenzverhältnis
    ratio = f_emit / f_obs
    N_S2 = ratio - N0

    # Photonenergie
    E_photon = h * f_emit

    # α * m_bound * c^2 = E_photon ⇒ m_bound = E_photon / (alpha_fs * c^2)
    m_bound = E_photon / (alpha_fs * c**2)

    # Lokale α aus gemessener Energie
    alpha_local = E_photon / (m_bound * c**2)

    # Check: f' = alpha_local * m_bound * c^2 / h == f_obs
    f_check = (alpha_local * m_bound * c**2) / h

    return {
        "f_emit": f_emit,
        "f_obs": f_obs,
        "N0": N0,
        "N_S2": N_S2,
        "E_photon (J)": E_photon,
        "alpha_fs": alpha_fs,
        "m_bound (kg)": m_bound,
        "alpha_local": alpha_local,
        "f_check": f_check,
        "check_match": abs(f_check - f_obs) < 1,
    }

if __name__ == '__main__':
    print("=== Segmented Spacetime – Bound Energy & Fine-Structure Constant ===\n")
    # Paper-Beispielrechnung S2/Sgr A*
    example = sagittariusA_star_example()
    print("Paper Example: S2 orbiting Sagittarius A*")
    for k, v in example.items():
        print(f"{k:20}: {v:.12g}" if isinstance(v, float) else f"{k:20}: {v}")

    print("\n-- General Functions (ready for custom input) --")
    # Beliebige Werte einsetzbar!
    # (siehe Funktionsdefinitionen oben)

    # Demo für klassischen Elektronenradius bei Ne=1
    phi_e = effective_radius_from_alpha(e, epsilon_0, alpha_fs, m_e, c)
    print(f"\nKlassischer Elektronenradius (r_eff, Ne=1, alpha=alpha_fs): {phi_e:.12g} m")

    # Demo: Rydberg energy
    E_R = rydberg_energy(alpha_fs, m_e, c)
    print(f"Rydberg energy (E_R): {E_R:.6e} J")

    # Demo: photon wavelength threshold
    lambda_thr = photon_threshold_lambda(h, c, alpha_fs, m_e)
    print(f"Photon threshold wavelength (lambda_gamma): {lambda_thr:.6e} m")

    # -- Erweiterbar für beliebige Szenarien/Gravitationsfeld --
print("\n============================================================")
print("Alle Berechnungen und Konzepte stammen aus:")
print("Carmen Wrede, Lino P. Casu, Bingsi (2025):")
print("»Segmented Spacetime – Bound Energy and the Structural Origin of the Fine-Structure Constant«")
print("Preprint · August 2025 · DOI: 10.13140/RG.2.2.35006.80969")
print("https://www.researchgate.net/publication/394248893")
print("============================================================")
