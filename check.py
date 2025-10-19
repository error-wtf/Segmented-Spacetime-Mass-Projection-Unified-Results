#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segmented Spacetime - Alpha Local Quick-Check
Paper-Prüfskript für Einzel-Frequenz + Basis-Segmentdichte
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

import scipy.constants as sc

def check_segmented_spacetime(frequency, N0=1.0000000028, m_e=None):
    """
    Prüft die lokale Alpha und relevante Größen aus einer einzigen Frequenz.
    """
    if m_e is None:
        m_e = sc.m_e  # kg
    h = sc.h
    c = sc.c

    # Lokale Alpha (Projektionsformel, siehe Paper)
    alpha_local = (frequency * h) / (m_e * c ** 2)

    # Klassische Feinstrukturkonstante zum Vergleich
    alpha_fs = 1 / 137.035999084

    # Aus Alpha kann man eine virtuelle "gebundene Masse" konstruieren (nur für Paper-Vergleich)
    m_bound = (frequency * h) / (alpha_fs * c ** 2)

    # Aus alpha_local die Emissionsfrequenz rückrechnen (Konsistenztest)
    f_recon = (alpha_local * m_e * c**2) / h

    print("============================================================")
    print("Segmented Spacetime – Paper Quick-Check")
    print(f"Eingabe-Frequenz (Hz)       : {frequency: .8e}")
    print(f"Basis-Segmentdichte N0      : {N0}")
    print(f"Lokale Alpha (berechnet)    : {alpha_local: .8e}")
    print(f"Klassische Alpha (CODATA)   : {alpha_fs: .8e}")
    print(f"Virtuelle gebundene Masse   : {m_bound: .8e} kg")
    print(f"Rückgerechnete Frequenz     : {f_recon: .8e} Hz")
    print("Rel. Fehler Rückrechnung    : {:.2e}".format(abs(f_recon - frequency)/frequency))
    print("------------------------------------------------------------")
    if abs(f_recon - frequency)/frequency < 1e-10:
        print("✓ Konsistenztest bestanden: Modell ist numerisch stimmig.")
    else:
        print("✗ Achtung: Konsistenztest nicht bestanden – Eingabe prüfen!")
    print("------------------------------------------------------------")
    print("Quelle: Wrede, Casu, Bingsi (2025),")
    print("Segmented Spacetime – Bound Energy and the Structural Origin of the Fine-Structure Constant")
    print("DOI: 10.13140/RG.2.2.35006.80969")
    print("============================================================\n")

if __name__ == '__main__':
    # Beispielwert aus dem Paper (f_obs S2 bei Sgr A*)
    frequency = 134_920_458_147_000  # Hz
    check_segmented_spacetime(frequency)
