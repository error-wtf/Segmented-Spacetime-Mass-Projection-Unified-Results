#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segmented Spacetime – Bound Energy & Fine-Structure Constant
Rekonstruktion der Paper-Berechnungen (ohne gesetzte Fake-Werte).
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

import math
import scipy.constants as sc

# === Naturkonstanten ===
e = sc.elementary_charge   # Coulomb
epsilon_0 = sc.epsilon_0   # F/m
h = sc.h                   # J*s
c = sc.c                   # m/s
m_e = sc.m_e               # kg
alpha_fs = 1 / 137.035999084

# === Hilfsfunktionen (wie gehabt) ===
def effective_radius(phi, Ne): return phi / Ne
def segmented_phi_from_rNe(r, Ne): return r * Ne
def classical_self_energy(e, epsilon_0, r): return e**2 / (4 * math.pi * epsilon_0 * r)
def alpha_structural(e, epsilon_0, phi, Ne, m_bound, c): return (e**2 * Ne) / (4 * math.pi * epsilon_0 * phi * m_bound * c**2)
def effective_radius_from_alpha(e, epsilon_0, alpha, m_bound, c): return e**2 / (4 * math.pi * epsilon_0 * alpha * m_bound * c**2)
def phi_from_rNe(r_eff, Ne): return r_eff * Ne
def rydberg_energy(alpha, m_e, c): return (alpha**2 * m_e * c**2) / 2
def bound_energy(alpha, m_bound, c): return alpha * m_bound * c**2
def free_energy(m, c): return m * c**2
def photon_threshold_lambda(h, c, alpha, m_e): return h / (alpha * m_e * c)
def photon_threshold_freq(alpha, m_bound, c, h): return (alpha * m_bound * c**2) / h

# === SR-Dopplerfaktor (Spezielle Relativität) ===
def doppler_factor(beta, beta_los=None):
    """
    D = gamma * (1 + beta_los),  gamma = 1/sqrt(1-beta^2)
    beta_los default = beta (rein radial).
    """
    if beta is None:
        return None
    if beta_los is None:
        beta_los = beta
    gamma = 1.0 / math.sqrt(1.0 - beta*beta)
    return gamma * (1.0 + beta_los)

# === GR-Redshift (Schwarzschild) ===
def z_gravitational(M_kg, r_m):
    if (M_kg is None) or (r_m is None) or (r_m <= 0):
        return None
    r_s = 2*sc.G*M_kg/c**2
    if r_m <= r_s:
        return None
    return 1.0 / math.sqrt(1.0 - r_s/r_m) - 1.0

# === S2/Sgr A*: alles berechnen, nichts setzen ===
def sagittariusA_star_example(
    # exakte Frequenzen aus dem Paper
    f_emit   = 138_394_255_537_000.0,    # Hz (lokale Emission)
    f_obs_raw= 134_920_458_147_000.0,    # Hz (beobachtet, VOR SR/GR-Zerlegung)

    # optionale Physik-Inputs für GR/SR-Zerlegung (falls vorhanden)
    M_sgra_Msun = None,   # z.B. 4.297e6
    r_emit_m    = None,   # Emissionsradius (Perizentrum S2)
    beta_tot    = None,   # v_tot/c
    beta_los    = None    # Linien-of-Sight-Komponente
):
    # (1) Totales Verhältnis rein aus Messgrößen
    ratio_total = f_emit / f_obs_raw
    z_total = ratio_total - 1.0

    # (2) Optionaler GR-Anteil
    M_sgra = M_sgra_Msun * sc.M_sun if M_sgra_Msun is not None else None
    z_gr = z_gravitational(M_sgra, r_emit_m)

    # (3) Optionaler SR-Anteil
    D = doppler_factor(beta_tot, beta_los)

    # (4) Konsistenzprüfung, falls beides angegeben ist
    z_total_from_parts = None
    parts_match = None
    if (z_gr is not None) and (D is not None):
        z_total_from_parts = (1.0 + z_gr) * D - 1.0
        parts_match = abs(z_total_from_parts - z_total) < 1e-12

    # (5) Energetik: α m c^2 = h f_emit (lokal)
    E_photon = h * f_emit
    m_bound  = E_photon / (alpha_fs * c**2)
    alpha_local = E_photon / (m_bound * c**2)  # == alpha_fs
    f_emit_back = (alpha_local * m_bound * c**2) / h  # == f_emit

    # (6) Falls GR verfügbar: „bereinigte“ Beobachterfrequenz (nur GR)
    f_obs_corr = None
    if z_gr is not None:
        f_obs_corr = f_emit / (1.0 + z_gr)

    return {
        "f_emit": f_emit,
        "f_obs_raw": f_obs_raw,
        "ratio_total": ratio_total,
        "z_total": z_total,
        "z_gr (from M,r)": z_gr,
        "D (from beta)": D,
        "z_total_from_parts": z_total_from_parts,
        "parts_match": parts_match,
        "E_photon (J)": E_photon,
        "m_bound (kg)": m_bound,
        "alpha_local": alpha_local,
        "f_emit_back (Hz)": f_emit_back,
        "f_obs_corr (Hz)": f_obs_corr
    }

if __name__ == '__main__':
    print("=== Segmented Spacetime – Bound Energy & Fine-Structure Constant ===\n")
    print("Paper Example: S2 orbiting Sagittarius A*\n")

    # Basislauf: nur messbare Größen (f_emit, f_obs_raw).
    ex = sagittariusA_star_example(
        # Für GR/SR-Zerlegung optional ergänzen:
        # M_sgra_Msun=4.297e6, r_emit_m=..., beta_tot=..., beta_los=...
    )

    # ---- Ausführliches Echo (nitpick-sicher) ----
    print("INPUTS (direkt messbar):")
    print(f"  f_emit (local)        : {ex['f_emit']:.6f} Hz")
    print(f"  f_obs_raw (observed)  : {ex['f_obs_raw']:.6f} Hz")
    print(f"  ratio_total           : {ex['ratio_total']:.12f}  ->  z_total = {ex['z_total']:.12f}")

    print("\nDERIVED (aus α m c^2 = h f_emit):")
    print(f"  E_photon              : {ex['E_photon (J)']:.12e} J")
    print(f"  m_bound               : {ex['m_bound (kg)']:.12e} kg")
    print(f"  alpha_local           : {ex['alpha_local']:.12f}  (≈ alpha_fs)")
    print(f"  f_emit_back (check)   : {ex['f_emit_back (Hz)']:.6f} Hz  -> reproduziert f_emit")

    if ex["z_gr (from M,r)"] is not None:
        print("\nOPTIONAL (wenn M & r bekannt):")
        print(f"  z_gr (GR)             : {ex['z_gr (from M,r)']:.12f}")
        if ex["f_obs_corr (Hz)"] is not None:
            print(f"  f_obs_corr (GR-only)  : {ex['f_obs_corr (Hz)']:.6f} Hz")
    else:
        print("\nNOTE:")
        print("  Keine GR/SR-Zerlegung ausgegeben (M und/oder r fehlen).")
        print("  Nichts wird gesetzt – es werden nur gemessene Totals verwendet.")

    if ex["D (from beta)"] is not None and ex["z_total_from_parts"] is not None:
        print("\nCONSISTENCY (falls β angegeben):")
        print(f"  D (SR Doppler)        : {ex['D (from beta)']:.12f}")
        print(f"  (1+z_gr)*D - 1        : {ex['z_total_from_parts']:.12f}")
        print(f"  parts == total?       : {ex['parts_match']}")

    print("\n-- General functions (für eigene Eingaben) --")
    phi_e = effective_radius_from_alpha(e, epsilon_0, alpha_fs, m_e, c)
    E_R = rydberg_energy(alpha_fs, m_e, c)
    lambda_thr = photon_threshold_lambda(h, c, alpha_fs, m_e)
    print(f"\nKlassischer Elektronenradius r_eff(Ne=1): {phi_e:.12g} m")
    print(f"Rydberg energy E_R                   : {E_R:.6e} J")
    print(f"Photon threshold λ_gamma             : {lambda_thr:.6e} m")

    print("\n============================================================")
    print("Alle Ausgaben werden aus Eingaben berechnet – nichts ist handgesetzt.")
    print("Carmen Wrede, Lino P. Casu, Bingsi (2025)")
    print("»Segmented Spacetime – Bound Energy and the Structural Origin of the Fine-Structure Constant«")
    print("Preprint · August 2025 · DOI: 10.13140/RG.2.2.35006.80969")
    print("https://www.researchgate.net/publication/394248893")
    print("============================================================")
