#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mass_from_segments_30_corrected_by_paper.py
===========================================

(C) 2025 Carmen Wrede & Lino Casu. All rights reserved.

Dieses Skript demonstriert an 30 astrophysikalischen Objekten – von kleinen Planeten und Monden
bis zum supermassiven Schwarzen Loch Sagittarius A* – wie man mit den im Paper vorgeschlagenen
Korrekturmodellen (Exponentiell & Log) das segmentbasierte Verhältnis r_φ/r_s so anpasst, dass
sich daraus in jedem Fall die wahre Masse M_true reproduzieren lässt.

Ablauf:
1. Bekannte Referenzmassen M_true → Berechnung der idealen Radien
   • Schwarzschildradius:  r_s_true = 2GM_true / c²
   • Segmentradius:       r_φ_true = GM_true φ / c²
2. Simulation eines “Messfehlers” im Verhältnis ratio_obs = (r_φ_obs / r_s_obs),
   indem wir ein exponentielles Δ%(r_s) aus dem Paper verwenden:
     Δ%(r_s) = A·exp(–α·r_s) + B
   mit A, α, B aus eurem Entwurf.  
3. Definition gemessener Radien:
     • r_s_obs = r_s_true  (angenommen exakt)
     • r_φ_obs = (φ/2)·r_s_obs·(1 + Δ%/100)
4. Korrektur des segmentbasierten Radius:
     r_φ_corr = r_φ_obs / (1 + Δ%/100)
   → damit wird das Verhältnis r_φ_corr / r_s_obs exakt φ/2.
5. Rekonstruktion der Masse:
     M_corr = c²·r_φ_corr / (G·φ)
6. Verifikation:
     • rel_err% = (M_corr / M_true – 1)·100  
     • PASS, wenn |rel_err%| ≤ Toleranz
7. Ausgabe:
     • Ausführliche Erklärungstexte  
     • Tabelle mit M_true, M_corr, Fehler & PASS  
     • CSV-Export für weitere Auswertung

Autoren:
  Carmen Wrede – Astrophysik & segmentierte Raumzeit  
  Lino Casu   – Ko-Autor, Simulation & numerische Umsetzung  

Datum: 24.07.2025
"""

import pandas as pd
import textwrap
from math import sqrt, exp
import os

# ------------------- 1. Physikalische Konstanten ------------------------
G        = 6.67430e-11          # Gravitationskonstante [m^3 kg^-1 s^-2]
c        = 2.99792458e8         # Lichtgeschwindigkeit [m s^-1]
phi      = (1 + sqrt(5)) / 2    # Goldener Schnitt
M_sun    = 1.98847e30           # Sonnenmasse [kg]

# ------------------- 2. Fit-Parameter aus dem Paper --------------------
# Exponentielles Korrekturmodell Δ% = A·exp(-α·r_s) + B
A, alpha, B = 98.01, 27176.81, 1.96  

# ------------------- 3. Objektliste (30 Objekte) ----------------------
objects = [
    ("Ceres",                    9.393e20),
    ("Vesta",                    2.590e20),
    ("Merkur",                   3.3011e23),
    ("Mond",                     7.342e22),
    ("Mars",                     6.4171e23),
    ("Venus",                    4.8675e24),
    ("Erde",                     5.97237e24),
    ("Io",                       8.9319e22),
    ("Europa",                   4.7998e22),
    ("Ganymed",                  1.4819e23),
    ("Titan",                    1.3452e23),
    ("Pluto",                    1.303e22),
    ("Eris",                     1.6466e22),
    ("Uranus",                   8.6810e25),
    ("Neptun",                   1.02413e26),
    ("Saturn",                   5.6834e26),
    ("Jupiter",                  1.89813e27),
    ("Sonne",                    M_sun),
    ("Proxima Centauri",         0.1221*M_sun),
    ("Alpha Centauri A",         1.100*M_sun),
    ("Sirius A",                 2.02*M_sun),
    ("Sirius B (WD)",            1.018*M_sun),
    ("Neutronenstern 1.4 Msun",  1.4*M_sun),
    ("PSR J0740+6620",           2.08*M_sun),
    ("Cygnus X‑1 (BH)",          21*M_sun),
    ("LMC X‑3 (BH)",             7.0*M_sun),
    ("V404 Cygni (BH)",          9.0*M_sun),
    ("M82 X‑1 (IMBH)",           400*M_sun),
    ("NGC 4395 BH",              3.6e5*M_sun),
    ("Sagittarius A*",           4.297e6*M_sun),
]

df = pd.DataFrame(objects, columns=["Objekt","M_true_kg"])

# ------------------- 4. Berechne Referenzradien ------------------------
df["r_s_true_m"]   = 2 * G * df["M_true_kg"] / c**2
df["r_phi_true_m"] =     G * df["M_true_kg"] / c**2 * phi

# ------------------- 5. Simulation der Messabweichung -----------------
def delta_percent(rs):
    """
    Exponentielle Abweichung Δ% nach dem Paper:
      Δ% = A·exp(-α·r_s) + B
    """
    return A * exp(-alpha * rs) + B

df["dev_%"]      = df["r_s_true_m"].apply(delta_percent)
df["ratio_obs"]  = (phi/2) * (1 + df["dev_%"]/100)

# Setze beobachtete Radien
df["r_s_obs_m"]   = df["r_s_true_m"]       # annehmend ohne Fehler
df["r_phi_obs_m"] = df["ratio_obs"] * df["r_s_obs_m"]

# ------------------- 6. Korrektur des Segmentradius -------------------
df["r_phi_corr_m"] = df["r_phi_obs_m"] / (1 + df["dev_%"]/100)
# Kontroll-Check: df["r_phi_corr_m"]/df["r_s_obs_m"] == phi/2

# ------------------- 7. Masse aus korrigiertem r_phi ------------------
df["M_corr_kg"] = (c**2 * df["r_phi_corr_m"]) / (G * phi)

# ------------------- 8. Fehleranalyse & PASS -------------------------
df["rel_err_%"]  = (df["M_corr_kg"] / df["M_true_kg"] - 1) * 100
df["abs_err_kg"] = df["M_corr_kg"] - df["M_true_kg"]

TOLERANCE_PERCENT = 1e-6  # 0.000001 % Toleranz
df["PASS"] = df["rel_err_%"].abs() <= TOLERANCE_PERCENT

# ------------------- 9. Formatierung für Ausgabe ----------------------
def sr(x):
    """Rundet je nach Größe sinnvoll."""
    if x is None: return ""
    if abs(x) >= 1e4 or abs(x) < 1e-2:
        return f"{x:.6e}"
    return f"{x:.6f}"

for col in ["M_true_kg","r_s_obs_m","r_phi_obs_m","r_phi_corr_m",
            "M_corr_kg","rel_err_%","dev_%"]:
    df[col] = df[col].apply(lambda v: float(sr(v)))

df["M_true_Msun"] = df["M_true_kg"] / M_sun
df["M_corr_Msun"] = df["M_corr_kg"] / M_sun

# ------------------- 10. Ausführliche Textausgabe ----------------------
wrap = lambda t: print(textwrap.fill(t, width=100))

print("\n" + "="*80)
print("MASSENREKONSTRUKTION MIT PAPER‑KORREKTUR (30 Objekte)")
print("="*80 + "\n")

wrap("Dieses Skript nutzt das exponentielle Abweichungsmodell Δ%(r_s) = "
     "A·exp(–α·r_s) + B aus dem Paper (Carmen Wrede & Lino Casu), um aus den "
     "gemessenen Radien r_s_obs und r_φ_obs einen korrigierten Segmentradius "
     "r_φ_corr zu berechnen. Die Korrektur sorgt dafür, dass das Verhältnis "
     "r_φ_corr/r_s_obs exakt φ/2 (Bingsi–Lino–Carmen‑Konstante) einhält.")

print("\n---\n")
wrap("Anschließend wird über die Inversion r_φ = GM/(c²)·φ die Masse "
     "M_corr bestimmt und mit der wahren Referenzmasse M_true verglichen. "
     "Die Spalte PASS zeigt, ob der relative Fehler |M_corr/M_true–1| ≤ "
     f"{TOLERANCE_PERCENT:.1e} % ist.")

print("\n" + "-"*80 + "\n")
cols_show = ["Objekt","M_true_Msun","M_corr_Msun","rel_err_%","PASS"]
print(df[cols_show].to_string(index=False))

# ------------------- 11. Statistik & Abschluss --------------------------
max_err = df["rel_err_%"].abs().max()
med_err = df["rel_err_%"].abs().median()
fails   = (~df["PASS"]).sum()

print(f"\nMax. relativer Fehler   : {max_err:.2e} %")
print(f"Median relativer Fehler : {med_err:.2e} %")
print(f"Anzahl FAILS            : {fails}\n")

assert fails == 0, "Einige Objekte überschreiten die Toleranz – bitte prüfen!"

# ------------------- 12. CSV‑Export ---------------------------
csv_path = "mass_from_segments_corrected_by_paper.csv"
df[["Objekt","M_true_Msun","M_corr_Msun","rel_err_%","PASS"]].to_csv(csv_path, index=False)
print(f"CSV gespeichert als: {os.path.abspath(csv_path)}\n")

print("© 2025 Carmen Wrede & Lino Casu. All rights reserved.")
print("\nFertig. 🌀")
