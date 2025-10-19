#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segmented Spacetime – Schrittweise Massenrekonstruktion & Bound-Energy-Analyse
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

from decimal import Decimal as D, getcontext

# --- Präzision und Naturkonstanten ---
getcontext().prec = 50
G = D('6.67430e-11')            # Gravitationskonstante [m^3 kg^-1 s^-2]
c = D('2.99792458e8')           # Lichtgeschwindigkeit [m/s]
phi = (D(1) + D(5).sqrt()) / D(2)  # Goldener Schnitt (dimensionslos)
e = D('1.602176634e-19')        # Elementarladung [C]
epsilon_0 = D('8.854187817e-12')# Elektrische Feldkonstante [F/m]
h = D('6.62607015e-34')         # Planck-Konstante [J s]
m_e = D('9.10938356e-31')       # Elektronenmasse [kg]
alpha_fs = D('1')/D('137.035999084') # Feinstrukturkonstante CODATA
A, alpha_corr, B = D('98.01'), D('2.7177e4'), D('1.96')
TOL = D('1e-40')

print("="*80)
print("SEGMENTIERTE RAUMZEIT – Vollständig kommentierte Schritt-für-Schritt-Demo")
print("Dieses Skript zeigt ALLE Rechenschritte für:")
print("  (1) Die Massenrekonstruktion aus segmentiertem Radius nach φ/2-Theorie")
print("  (2) Die Berechnung der lokalen Feinstrukturkonstante α und gebundener Masse")
print("     aus einer gemessenen Frequenz, wie z.B. beim S2/Sgr A* Experiment")
print("\nJede Variable, Formel und Rechenbedeutung wird im Print erklärt!\n")
print("© 2025 Carmen Wrede & Lino Casu\n" + "="*80 + "\n")

# === TEIL 1: MASSENREKONSTRUKTION (mit φ/2 und exponentieller Korrektur) ===

def delta_percent(M):
    r_s = D(2)*G*M/c**2
    exp_term = (-alpha_corr * r_s).exp()
    delta = A * exp_term + B
    print(f"→ Schritt: Berechne Exponentialkorrektur Δ%(M):")
    print(f"   - Masse M = {M:.6e} kg")
    print(f"   - Schwarzschildradius r_s = 2GM/c² = {r_s:.6e} m")
    print(f"   - Exponentialterm = exp(-α·r_s) = exp(-{alpha_corr:.2e} * {r_s:.3e}) = {exp_term:.5e}")
    print(f"   - Δ%(M) = A·exp(-α·r_s) + B = {A:.2f} * {exp_term:.5e} + {B:.2f} = {delta:.5f} %\n")
    return delta

def r_phi_corr(M):
    r_s = D(2)*G*M/c**2
    delta = delta_percent(M)
    k = phi/D(2)
    r_phi = k * r_s * (D(1) + delta/D(100))
    print(f"→ Schritt: Segmentierter Radius nach φ/2:")
    print(f"   - φ/2 = {phi/2:.8f} (dimensionslos)")
    print(f"   - Korrigierter Radius: r_φ = (φ/2)·r_s·(1 + Δ%/100)")
    print(f"   -   = {k:.8f} * {r_s:.6e} * (1 + {delta:.5f}/100)")
    print(f"   -   = {r_phi:.6e} m\n")
    return r_phi

def mass_invert(r_obs, M_guess):
    print("→ Schritt: Newton-Inversion – Rekonstruktion der Masse aus segmentiertem Radius")
    print(f"   - Eingabe: gemessener segmentierter Radius r_φ = {r_obs:.6e} m")
    print(f"   - Startwert für Masse M_guess = {M_guess:.6e} kg")
    M = M_guess
    for i in range(200):
        r_s = D(2)*G*M/c**2
        delta = delta_percent(M)
        f = (G*phi*M/c**2)*(D(1)+delta/D(100)) - r_obs
        if abs(f) < TOL:
            print(f"   - Konvergenz erreicht nach {i+1} Schritten (|f| < TOL)\n")
            break
        h = M * D('1e-25')
        # Numerisches Differential
        f_plus = (G*phi*(M+h)/c**2)*(D(1)+delta_percent(M+h)/D(100)) - r_obs
        f_minus = (G*phi*(M-h)/c**2)*(D(1)+delta_percent(M-h)/D(100)) - r_obs
        df = (f_plus - f_minus)/(D('2')*h)
        step = -f/df
        if abs(step) > abs(M):
            step *= D('0.5')
        M += step
        print(f"     Iteration {i+1}: M = {M:.6e} kg, Schrittweite = {step:.2e}")
        if abs(step/M) < TOL:
            print("   - Schrittweite klein genug, Newton-Konvergenz\n")
            break
    print(f"→ Ergebnis: Rekonstruierte Masse M = {M:.6e} kg\n")
    return M

# --- Beispiel: Erde ---
print("==== 1. Beispiel: Masse der Erde aus segmentiertem Radius ====")
earth_true = D('5.97219e24')
print(f"Echte Masse der Erde (Referenz): {earth_true:.6e} kg")
print("Berechne den segmentierten Radius für diese Masse nach Theorie:\n")
r_phi_earth = r_phi_corr(earth_true)
print("Jetzt numerische Inversion: Ermittle aus diesem Radius wieder die Masse:\n")
earth_rec = mass_invert(r_phi_earth, earth_true)
rel_error = abs((earth_rec-earth_true)/earth_true)*100
print(f"Vergleich Referenz/Eigenwert: Relativer Fehler = {rel_error:.3e} %\n")
print("="*80 + "\n")

# === TEIL 2: FEINSTRUKTUR, ALPHA UND GEBUNDENE MASSE (S2/Sgr A*) ===

def alpha_local_from_freq(frequency):
    print(f"→ Schritt: Berechne lokale Feinstrukturkonstante aus gegebener Frequenz")
    print(f"   - Eingabe: Frequenz f = {frequency:.8e} Hz")
    numerator = frequency * h
    denominator = m_e * c**2
    result = numerator / denominator
    print(f"   - Formel: α_local = f·h / (m_e·c²)")
    print(f"   - Werte:  ({frequency:.3e} * {h:.3e}) / ({m_e:.3e} * {c:.3e}²)")
    print(f"           = {numerator:.4e} / {denominator:.4e}")
    print(f"           = {result:.8e}\n")
    return result

def m_bound_from_photon(frequency, alpha):
    print(f"→ Schritt: Gebundene Masse aus Photonenergie & gegebener Alpha")
    numerator = h * frequency
    denominator = alpha * c**2
    result = numerator / denominator
    print(f"   - Formel: m_bound = h·f / (α·c²)")
    print(f"   - Werte:  ({h:.3e} * {frequency:.3e}) / ({alpha:.3e} * {c:.3e}²)")
    print(f"           = {numerator:.4e} / {denominator:.4e}")
    print(f"           = {result:.4e} kg\n")
    return result

def photon_threshold_lambda(alpha):
    print(f"→ Schritt: Berechne Grenzwellenlänge eines Photons für gegebene Alpha")
    numerator = h
    denominator = alpha * m_e * c
    result = numerator / denominator
    print(f"   - Formel: λ_thr = h / (α·m_e·c)")
    print(f"   - Werte:  {h:.4e} / ({alpha:.4e} * {m_e:.4e} * {c:.4e})")
    print(f"           = {numerator:.4e} / {denominator:.4e}")
    print(f"           = {result:.4e} m\n")
    return result

# --- Beispiel: S2 bei Sagittarius A* ---
print("==== 2. Beispiel: Feinstruktur & gebundene Energie (S2/Sgr A*) ====")
f_obs  = D('134920458147000')
print(f"Gegebene beobachtete Frequenz (f_obs): {f_obs:.8e} Hz")
alpha_s2 = alpha_local_from_freq(f_obs)
print(f"Klassische Feinstrukturkonstante (CODATA): {alpha_fs:.8e}\n")
m_bound_s2 = m_bound_from_photon(f_obs, alpha=alpha_s2)
lambda_thr = photon_threshold_lambda(alpha=alpha_s2)

print("→ Schritt: Konsistenzcheck, ob Rückrechnung funktioniert:")
print("   - Formel: f_check = (α_local * m_bound * c²) / h")
f_check = (alpha_s2 * m_bound_s2 * c**2) / h
rel_err_f = abs(f_check - f_obs) / f_obs
print(f"   - Ergebnis: f_check = {f_check:.8e} Hz")
print(f"   - Erwartet: f_obs   = {f_obs:.8e} Hz")
print(f"   - Relativer Fehler: {rel_err_f:.2e}")
if rel_err_f < 1e-10:
    print("   → Konsistenztest bestanden: Die Rückrechnung stimmt exakt.\n")
else:
    print("   → Achtung: Rückrechnung weicht ab – Überprüfe Eingabewerte!\n")

print("="*80)
print("Alle Berechnungsschritte und Erklärungen basieren auf:")
print("Carmen Wrede & Lino Casu (2025):")
print("Segmented Spacetime – Bound Energy and the Structural Origin of the Fine-Structure Constant")
print("DOI: 10.13140/RG.2.2.35006.80969")
print("https://www.researchgate.net/publication/394248893")
print("="*80)
