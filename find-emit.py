#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emissionsfrequenz-Rekonstruktion in segmentierter Raumzeit
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

from decimal import Decimal as D, getcontext

# Hohe Präzision für astrophysikalische Rechnungen
getcontext().prec = 40

# Physikalische Konstanten (CODATA)
alpha_0 = D('1')/D('137.035999084')    # Referenz-Feinstrukturkonstante (z.B. Erde/Labor)
h = D('6.62607015e-34')                # Plancksches Wirkungsquantum [J s]
c = D('2.99792458e8')                  # Lichtgeschwindigkeit [m/s]
m_e = D('9.10938356e-31')              # Elektronenmasse [kg]

print("="*75)
print("EMISSIONSFREQUENZ-BERECHNUNG AUS BEOBACHTUNGSFREQUENZ")
print("Schritt-für-Schritt-Skript nach segmentierter Raumzeit- und α-Modell")
print("© 2025 Carmen Wrede & Lino Casu\n" + "="*75 + "\n")

# ----------------------
# Eingabewerte
# ----------------------
f_obs = D('134920458147000')   # Beispiel: Beobachtungsfrequenz S2/Sgr A* [Hz]
print(f"Gegebene Beobachtungsfrequenz (f_obs): {f_obs:.8e} Hz\n")

# OPTION 1: Segmentierungsverhältnis N' bekannt (z.B. aus Modell, Fit oder Theorie)
N_prime = D('1.02574')  # Annahme aus Paper (z.B. aus Daten oder Theorie, N' > 1)
print(f"Annahme: Segmentierungsverhältnis N' (z.B. aus Modell): {N_prime}\n")

# Rechenschritt 1: Emissionsfrequenz direkt aus N' und f_obs
f_emit_from_N = N_prime * f_obs
print("Schritt 1: Berechne Emissionsfrequenz, wenn N' bekannt ist")
print(f"  Formel:   f_emit = N' * f_obs")
print(f"  Rechnung: f_emit = {N_prime} * {f_obs:.8e} Hz = {f_emit_from_N:.8e} Hz\n")

# OPTION 2: α_local bekannt (z.B. aus Modell oder unabhängiger Messung)
alpha_local = D('6.802e-3')  # Annahme aus Paper-Analyse (lokale Alpha am Emissionsort)
print(f"Annahme: Lokale Feinstrukturkonstante am Emissionsort (α_local): {alpha_local:.8e}")

# Rechenschritt 2: Berechne Segmentierungsverhältnis aus α_0 und α_local
N_prime_from_alpha = alpha_0 / alpha_local
print("\nSchritt 2: Bestimme N' aus α_0 / α_local")
print(f"  Formel:   N' = α_0 / α_local")
print(f"  Rechnung: N' = {alpha_0:.8e} / {alpha_local:.8e} = {N_prime_from_alpha:.8f}")

# Emissionsfrequenz berechnen
f_emit_from_alpha = N_prime_from_alpha * f_obs
print(f"  → Daraus folgt: f_emit = N' * f_obs = {N_prime_from_alpha:.8f} * {f_obs:.8e} Hz")
print(f"                  = {f_emit_from_alpha:.8e} Hz\n")

# KURZZUSAMMENFASSUNG/FAZIT:
print("-"*75)
print("FAZIT:")
print("Du kannst die Emissionsfrequenz f_emit NICHT nur aus f_obs berechnen.")
print("Du brauchst immer zusätzlich entweder:")
print("  - das Segmentierungsverhältnis N' am Emissionsort (z.B. aus Modell/Theorie) ODER")
print("  - die lokale Feinstrukturkonstante α_local am Emissionsort (aus Messung/Modell)")
print("\nDas Skript zeigt beide Rechenwege mit typischen Paper-Parametern.")
print("-"*75)

print("Referenz: Wrede, Casu (2025) — Segmented Spacetime, Bound Energy and the Structural Origin of α")
print("DOI: 10.13140/RG.2.2.35006.80969\n")
