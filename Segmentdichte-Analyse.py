#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
further-final.py – Segmentdichte-Analyse: Physikmodus + Demomodus + Erklärung
© 2025 Lino Casu & Carmen Wrede – All rights reserved.
"""

import math

# Optional: matplotlib für Plot
try:
    import matplotlib.pyplot as plt
    has_plot = True
except ImportError:
    has_plot = False

# --- Konstanten (CODATA 2022)
G = 6.67430e-11
c = 2.99792458e8
phi = (1 + 5**0.5) / 2
sigma_c = 1.0

# === 1. MODUSWAHL ==========================
DEMO_MODE = True  # True = Demo (beliebiges Intervall), False = Physik (Massenwahl)

# === 2. INTERVALL-SETUP ====================

if DEMO_MODE:
    # --- Demo: Modellintervall (z.B. für Paper-Plot) ---
    r_s_ = 1.0
    r_phi_ = 2.0
    print("### DEMO-MODUS: Künstliches Intervall für Segmentdichte ###\n")
    print(f"  r_s    = {r_s_:.6e} m")
    print(f"  r_phi  = {r_phi_:.6e} m\n")
    explain_physics = False
else:
    # --- Physik: Wähle astronomische Masse (Erde, Sonne, NS, BH) ---
    #M = 5.97219e24         # Erde
    #M = 1.989e30           # Sonne
    #M = 2.8e30             # Neutronenstern (~1.4 Sonnenmassen)
    M = 2e31                # Schwarzes Loch (~10 Sonnenmassen)
    a = 0.7                 # Kerr
    def r_phi(M, phi=phi):
        return phi * G * M / c**2
    def r_schw(M):
        return 2 * G * M / c**2
    r_phi_ = r_phi(M)
    r_s_ = r_schw(M)
    print("### PHYSIK-MODUS: Segmentdichte für reale Masse ###\n")
    print(f"Beispiel: Masse (M = {M:.3e} kg)")
    print(f"  Segmentradius r_phi     = {r_phi_:.6e} m")
    print(f"  Schwarzschildradius r_s = {r_s_:.6e} m\n")
    explain_physics = True

# === 3. SEGMENTDICHTE-BERECHNUNG ===========
def sigma(r, r_phi_val, r_schw_val, sigma_c=sigma_c, eps=1e-15):
    if r <= r_schw_val or r >= r_phi_val:
        return float('nan')
    numerator = math.log((r_phi_val + eps) / (r + eps))
    denominator = math.log((r_phi_val + eps) / (r_schw_val + eps))
    return sigma_c * numerator / denominator

# === 4. TABELLENAUSGABE ====================

num_vals = 80
r_vals = [r_s_ * (r_phi_/r_s_)**(i/(num_vals-1)) for i in range(num_vals)]
sigmas = [sigma(r, r_phi_, r_s_) for r in r_vals]

print("Segmentdichte σ(r) im Intervall (nur gültige Werte):")
print(f"{'Idx':>3} | {'r [m]':>14} | {'σ(r)':>9}")
print("-"*33)
valid_count = 0
for idx, (r, sig) in enumerate(zip(r_vals, sigmas)):
    if math.isnan(sig):
        print(f"{idx:3d} | {r:14.6e} |   (außerhalb gültig)")
    else:
        print(f"{idx:3d} | {r:14.6e} | {sig:9.4f}")
        valid_count += 1

# === 5. PLOT ===============================
if has_plot and valid_count > 0:
    print("\nPlot wird angezeigt...")
    import numpy as np
    r_plot = np.array([r for r, sig in zip(r_vals, sigmas) if not math.isnan(sig)])
    sigma_plot = np.array([sig for sig in sigmas if not math.isnan(sig)])
    plt.figure(figsize=(7,4))
    plt.plot(r_plot, sigma_plot, label=r"$\sigma(r)$", linewidth=2)
    plt.xlabel(r"$r$")
    plt.ylabel(r"$\sigma(r)$")
    plt.title(r"Segmentdichte $\sigma(r)$ zwischen $r_s$ und $r_\varphi$")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
elif valid_count == 0:
    print("\n--- Kein gültiges Intervall für σ(r): Für diese Masse ist r_phi <= r_s ---")
else:
    print("\nHinweis: Für grafische Ausgabe installiere matplotlib (pip install matplotlib)")

# === 6. PHYSIK-INTERPRETATION ==============
print("\n" + "="*50 + "\n")

if not explain_physics:
    # Für Paper oder README (DEMO-Modus)
    print(
"""Segmentdichte σ(r) – Modell-Erklärung (Kopiervorlage):

Die Segmentdichte σ(r) im Intervall zwischen Schwarzschildradius r_s und Segmentradius r_φ ist im spiraligen Modell exakt logarithmisch fallend.
- Am Schwarzschildrand (r = r_s) erreicht σ(r) stets den Wert 1 (kritische Dichte).
- Zum Segmentradius (r = r_φ) sinkt σ(r) kontinuierlich bis auf 0 ab.
Dieses universelle Profil ist eine direkte Folge der spiraligen Diskretisierung segmentierter Raumzeit und ermöglicht einen topologischen Zugang zu Massen- und Gravitationsstrukturen jenseits der klassischen Relativitätstheorie.
Der charakteristische Verlauf kann für beliebige Intervalle (z. B. r_s=1 m, r_φ=2 m) analytisch und numerisch dargestellt werden.
""")
else:
    # Für reale Masse (Physik-Modus)
    if r_phi_ <= r_s_:
        print(
"""WARNUNG: Für diese Masse liegt der Segmentradius r_φ kleiner oder gleich dem Schwarzschildradius r_s.
Es existiert kein physikalisch sinnvoller Bereich mit r_s < r < r_φ für σ(r)!
→ Segmentdichte ist nur für extrem kompakte Objekte relevant (Neutronensterne, Schwarze Löcher mit hoher Rotation).""")
    else:
        print(
f"""Physikalische Interpretation (Kopiervorlage):

Für M = {M:.3e} kg ergibt sich nach dem Modell ein Intervall {r_s_:.3e} m < r < {r_phi_:.3e} m,
in dem die Segmentdichte σ(r) zwischen 1 (maximal, am Schwarzschildrand) und 0 (am Segmentradius) abfällt.
Dies illustriert, wie im segmentierten Raum Zeit und Dichte unmittelbar verknüpft sind – ein möglicher Mechanismus zur Singularitätsvermeidung.
""")
print("="*50)
print("\nFertig ✅")
