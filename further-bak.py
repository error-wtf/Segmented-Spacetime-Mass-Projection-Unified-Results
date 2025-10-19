#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
further.py – Erweiterte Segmentdichte, Kerr-Generalisierung und Unsicherheitsanalyse (mit Intervall-Check)
© 2025 Lino Casu & Carmen Wrede – All rights reserved.
"""

import math

# --- Physikalische Konstanten (CODATA 2022)
G = 6.67430e-11         # m^3 kg^-1 s^-2
c = 2.99792458e8        # m/s
phi = (1 + 5**0.5) / 2  # Golden Ratio ≈ 1.6180339887

# --- Kritische Segmentdichte (Normwert)
sigma_c = 1.0

# --- Objektauswahl (nur eine Zeile aktiv lassen!)
#M = 5.97219e24         # Erde (kg)
#M = 1.989e30           # Sonne (kg)
#M = 2.8e30             # Neutronenstern (≈1.4 M_sun)
M = 2e31                # Schwarzes Loch (~10 Sonnenmassen)
a = 0.7                 # Kerr-Parameter (|a| < 1)

# --- Segment- und Schwarzschildradien berechnen
def r_phi(M, phi=phi):
    return phi * G * M / c**2

def r_schw(M):
    return 2 * G * M / c**2

def r_phi_kerr(M, a, phi=phi):
    rplus = G * M / c**2 * (1 + (1 - a**2)**0.5)
    return phi * rplus

def sigma(r, r_phi_val, r_schw_val, sigma_c=sigma_c, eps=1e-15):
    if r <= r_schw_val or r >= r_phi_val:
        return float('nan')
    numerator = math.log((r_phi_val + eps) / (r + eps))
    denominator = math.log((r_phi_val + eps) / (r_schw_val + eps))
    return sigma_c * numerator / denominator

def rel_mass_error(dr_phi, r_phi_val, dG, G, dphi, phi, dc, c):
    relerr2 = (dr_phi/r_phi_val)**2 + (2*dc/c)**2 + (dG/G)**2 + (dphi/phi)**2
    return relerr2**0.5

# --------------------------------------------------------------------
if __name__ == '__main__':
    print("="*65)
    print(" SEGMENTED SPACETIME – Erweiterte Segmentdichte und Analyse")
    print("="*65)
    print(" Copyright (c) 2025 Carmen Wrede & Lino Casu – All rights reserved.\n")

    print("# 1. Kugelsymmetrische Segmentdichte σ(r) nach Spiralmodell")
    M_ = M
    r_phi_ = r_phi(M_)
    r_s_ = r_schw(M_)
    print(f"Beispiel: Masse (M = {M_:.3e} kg)")
    print(f"  Segmentradius r_phi     = {r_phi_:.6e} m")
    print(f"  Schwarzschildradius r_s = {r_s_:.6e} m\n")
    
    # Check, ob Segmentradius > Schwarzschildradius
    if r_phi_ <= r_s_:
        print("WARNUNG: Für diese Masse liegt der Segmentradius r_phi kleiner oder gleich dem Schwarzschildradius r_s.")
        print("         Es existiert kein physikalisch sinnvoller Bereich mit r_s < r < r_phi für σ(r)!")
        print("         → Wähle ein kompakteres Objekt (Neutronenstern, Schwarzes Loch).")
    else:
        print("Segmentdichte σ(r) für logarithmisch verteilte r (nur gültige Werte):")
        num_vals = 7  # Mehr Werte für bessere Übersicht
        r_vals = [r_s_ * (r_phi_/r_s_)**(i/(num_vals-1)) for i in range(num_vals)]
        print(f"{'Index':>3} | {'r [m]':>14} | {'σ(r)':>9}")
        print("-"*33)
        for idx, r in enumerate(r_vals):
            sig = sigma(r, r_phi_, r_s_)
            if math.isnan(sig):
                print(f"{idx:3d} | {r:14.6e} |   (außerhalb gültig)")
            else:
                print(f"{idx:3d} | {r:14.6e} | {sig:9.4f}")

    print("\n# 2. Axialsymmetrische Verallgemeinerung (Kerr, Rotation)")
    r_phi_rot = r_phi_kerr(M_, a)
    print(f"Für Kerr-Parameter a = {a:.2f}:")
    print(f"  r_phi_kerr = {r_phi_rot:.6e} m")
    for theta_deg in [0, 45, 90]:
        theta = math.radians(theta_deg)
        f_aniso = 1 + 0.2 * a**2 * math.cos(theta)**2
        r = r_s_ + 0.5 * (r_phi_rot - r_s_)
        sig = sigma(r, r_phi_rot, r_s_) * f_aniso
        print(f"  θ = {theta_deg:>2}°:  σ(r, θ) ≈ {sig:.4f}")

    print("\n# 3. Fehlerfortpflanzung der rekonstruierten Masse (Error Propagation)")
    dr_phi_val = 0.01 * r_phi_
    dG_val = 0.0001 * G
    dphi_val = 0.00001 * phi
    dc_val = 0.0
    rel_err = rel_mass_error(dr_phi_val, r_phi_, dG_val, G, dphi_val, phi, dc_val, c)
    print(f"  Relativer Fehler in Masse (für obige Unsicherheiten): {rel_err*100:.3f} %")
    print("  (Setze realistische Unsicherheiten für deine Messwerte ein!)")

    print("\n# 4. Interpretation und Vergleich:")
    print(" - σ(r) steigt nach innen logarithmisch an und erreicht am Schwarzschildradius r_s die Maximaldichte σ_c.")
    print(" - Für Kerr-Objekte hängt die Dichte von der Richtung ab (θ), z.B. ist sie am Äquator und Pol unterschiedlich.")
    print(" - Die Unsicherheiten in Messwerten und Konstanten propagieren direkt in die Masserekonstruktion.")
    print(" - Alternative Diskretisierungen (z.B. Loop Quantum Gravity) liefern andere Profile – nur hier ergibt sich φ/2 als invariantes Verhältnis.")
    print("\nFertig ✅")
