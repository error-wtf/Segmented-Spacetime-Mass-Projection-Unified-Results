#!/usr/bin/env python3
"""
Clean Test Set WITH ΔM correction (φ/2-BLC) – berechnet, nicht gesetzt.
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

from decimal import Decimal, getcontext
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Präzision
getcontext().prec = 80

# Konstanten
c = Decimal("299792458")
G = Decimal("6.67430e-11")
h = Decimal("6.62607015e-34")

# φ/2-BLC-Korrektur (wie gehabt)
def corrected_delta_mass(N_seg):
    φ = (Decimal(1) + Decimal(5).sqrt()) / 2
    BLC = φ / 2  # ~0.809017...
    return BLC * Decimal(N_seg)

# Optional: GR-Redshift (wenn Masse & Radius vorliegen)
def z_gravitational(M_kg: Decimal|None, r_m: Decimal|None):
    if M_kg is None or r_m is None or r_m <= 0:
        return None
    r_s = Decimal(2) * G * M_kg / (c**2)
    if r_m <= r_s:
        return None
    return Decimal(1) / (Decimal(1) - r_s/r_m).sqrt() - Decimal(1)

# Optional: SR-Doppler (wenn beta/beta_los vorliegt)
def doppler_factor(beta: Decimal|None, beta_los: Decimal|None=None):
    if beta is None:
        return None
    if beta_los is None:
        beta_los = beta
    one = Decimal(1)
    gamma = one / (one - beta*beta).sqrt()
    return gamma * (one + beta_los)

# Objekte (S2 jetzt exakt). Alle z werden BERECHNET – keine Festwerte.
objects = [
    {
        "name": "S2 star (Sag A*)",
        "f_emit": Decimal("138394255537000"),
        "f_obs_raw": Decimal("134920458147000"),
        # Optional verfügbare Physik für Zerlegung:
        "M_kg": None,        # z.B. Decimal("4.297e6") * M_sun
        "r_emit_m": None,    # Perizentrum in m
        "beta": None,        # v_tot/c
        "beta_los": None     # Linien-of-Sight Komponente
    },
    {
        "name": "White dwarf (Sirius B)",
        "f_emit": Decimal("4.568e14"),
        "f_obs_raw": Decimal("4.567e14"),
        "M_kg": None, "r_emit_m": None, "beta": None, "beta_los": None
    },
    {
        "name": "Sun (solar line)",
        "f_emit": Decimal("4.759e14"),
        "f_obs_raw": Decimal("4.759e14"),
        "M_kg": None, "r_emit_m": None, "beta": None, "beta_los": None
    },
    {
        "name": "Pound-Rebka (1959)",
        "f_emit": Decimal("3.482e18"),
        "f_obs_raw": Decimal("3.482e18"),
        "M_kg": None, "r_emit_m": None, "beta": None, "beta_los": None
    },
    {
        "name": "Earth surface test",
        "f_emit": Decimal("4.570e14"),
        "f_obs_raw": Decimal("4.570e14"),
        "M_kg": None, "r_emit_m": None, "beta": None, "beta_los": None
    },
]

print("\n" + "="*74)
print(" SEGMENTED SPACETIME – CLEAN TEST SET WITH ΔM CORRECTION (computed)")
print("="*74)

rows = []
for obj in objects:
    name = obj["name"]
    f_emit = obj["f_emit"]
    f_obs_raw = obj["f_obs_raw"]

    # Totale Größen (immer berechenbar)
    ratio_total = f_emit / f_obs_raw
    z_total = ratio_total - Decimal(1)

    # optional GR/SR-Zerlegung
    z_gr = z_gravitational(obj.get("M_kg"), obj.get("r_emit_m"))
    D = doppler_factor(obj.get("beta"), obj.get("beta_los"))

    f_obs_corr = None
    if z_gr is not None:
        f_obs_corr = f_emit / (Decimal(1) + z_gr)

    # Segmentdichte (Roh, ohne N0)
    N_seg = z_total  # in diesem Script: N_seg = f_emit/f_obs_raw - 1

    # Δm-Korrektur nach φ/2-BLC
    delta_m = corrected_delta_mass(N_seg)

    print(f"\n--- {name} ---")
    print(f"f_emit           : {f_emit:.6E} Hz")
    print(f"f_obs_raw        : {f_obs_raw:.6E} Hz")
    print(f"ratio_total      : {ratio_total}")
    print(f"z_total          : {z_total}")
    if z_gr is not None:
        print(f"z_gr (from M,r)  : {z_gr}")
    else:
        print("z_gr (from M,r)  : N/A")
    if D is not None:
        print(f"D (SR Doppler)   : {D}")
    else:
        print("D (SR Doppler)   : N/A")
    if f_obs_corr is not None:
        print(f"f_obs_corr (GR)  : {f_obs_corr:.6E} Hz")
    else:
        print("f_obs_corr (GR)  : N/A")

    print(f"N_seg (raw)      : {N_seg}")
    print(f"Δm_corr (φ/2-BLC): {delta_m}")

    rows.append({
        "object": name,
        "f_emit_Hz": float(f_emit),
        "f_obs_raw_Hz": float(f_obs_raw),
        "ratio_total": float(ratio_total),
        "z_total": float(z_total),
        "z_gr": float(z_gr) if z_gr is not None else None,
        "D_SR": float(D) if D is not None else None,
        "f_obs_corr_GR_Hz": float(f_obs_corr) if f_obs_corr is not None else None,
        "N_seg_raw": float(N_seg),
        "delta_m_corr": float(delta_m)
    })

# Export CSV
df = pd.DataFrame(rows)
csv_path = Path("bound_energy_with_deltaM.csv")
df.to_csv(csv_path, index=False)
print(f"\nCSV export completed: {csv_path.resolve()}")

# Plot (nur die Δm-Korrekturgrößen als Beispiel)
plt.figure(figsize=(10, 6))
plt.bar([r["object"] for r in rows], [r["delta_m_corr"] for r in rows])
plt.title("Δm-Korrektur (φ/2-BLC) vs. Objekt (aus N_seg berechnet)")
plt.ylabel("Δm_corr (dimensionslos)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plot_path = Path("bound_energy_with_deltaM_plot.png")
plt.savefig(plot_path, dpi=200)
print(f"Plot saved as: {plot_path.resolve()}")
plt.show()
