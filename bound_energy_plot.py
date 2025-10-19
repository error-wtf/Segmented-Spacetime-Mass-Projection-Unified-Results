#!/usr/bin/env python3
"""
High-Precision Bound Energy and Redshift Calculation (berechnet, nicht gesetzt)
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

from decimal import Decimal, getcontext
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Decimal-Präzision
getcontext().prec = 50

# Konstanten (SI)
h = Decimal("6.62607015e-34")
c = Decimal("299792458")
m_e = Decimal("9.1093837015e-31")
alpha_fs = Decimal(1) / Decimal("137.035999084")

# Optional: Baseline N0 (Dokuzweck) – gerechnet wird immer mit dem Rohverhältnis
N0 = Decimal("1.000000028")

def compute_ratio(f_emit, f_obs):
    return f_emit / f_obs

def compute_z_total(f_emit, f_obs):
    return f_emit / f_obs - Decimal(1)

def compute_segment_density(f_emit, f_obs, N0):
    return f_emit / f_obs - N0

def compute_photon_energy(f_emit):
    return h * f_emit

def compute_bound_mass(E_gamma):
    return m_e - (E_gamma / (c**2))

def compute_local_alpha_from_obs(f_obs):
    return (f_obs * h) / (m_e * c**2)

def compute_f_emit_from_alpha(alpha_local):
    return (alpha_local * m_e * c**2) / h

# === Exakte Paare (S2 jetzt korrekt) ===
sources = [
    {
        "label": "S2 star (Sag A*)",
        "f_emit": Decimal("138394255537000"),
        "f_obs":  Decimal("134920458147000")
    },
    {
        "label": "White dwarf (Sirius B)",
        "f_emit": Decimal("4.568e14"),
        "f_obs":  Decimal("4.567e14")
    },
    {
        "label": "Sun (solar line)",
        "f_emit": Decimal("4.759e14"),
        "f_obs":  Decimal("4.759e14")
    },
    {
        "label": "Pound-Rebka (1959)",
        "f_emit": Decimal("3.482e18"),
        "f_obs":  Decimal("3.482e18")
    },
    {
        "label": "Earth surface lab test",
        "f_emit": Decimal("4.570e14"),
        "f_obs":  Decimal("4.570e14")
    }
]

print("="*74)
print(" SEGMENTED SPACETIME – CLEAN TEST SET (ALL VALUES COMPUTED)")
print("="*74)

rows = []
errors = []
labels = []

for src in sources:
    f_emit = src["f_emit"]
    f_obs  = src["f_obs"]
    label  = src["label"]

    ratio   = compute_ratio(f_emit, f_obs)
    z_total = compute_z_total(f_emit, f_obs)
    N_seg   = compute_segment_density(f_emit, f_obs, N0)
    E_gamma = compute_photon_energy(f_emit)
    m_bound = compute_bound_mass(E_gamma)
    alpha_local = compute_local_alpha_from_obs(f_obs)
    f_emit_calc = compute_f_emit_from_alpha(alpha_local)
    rel_error   = abs(f_emit_calc - f_emit) / f_emit

    print(f"\n--- {label} ---")
    print(f"f_emit      : {f_emit:.6E} Hz")
    print(f"f_obs       : {f_obs:.6E} Hz")
    print(f"ratio       : {ratio}")
    print(f"z_total     : {z_total}")
    print(f"N_seg(N0)   : {N_seg}  (Dokuwert; Rohrechnung nutzt ratio/z_total)")
    print(f"E_photon    : {E_gamma:.6E} J")
    print(f"m_bound     : {m_bound:.6E} kg")
    print(f"alpha_local : {alpha_local}")
    print(f"f_emit_back : {f_emit_calc:.6E} Hz")
    print(f"rel_error   : {rel_error}")

    rows.append({
        "label": label,
        "f_emit_Hz": f_emit,
        "f_obs_Hz": f_obs,
        "ratio": ratio,
        "z_total": z_total,
        "N_seg_minus_N0": N_seg,
        "E_gamma_J": E_gamma,
        "m_bound_kg": m_bound,
        "alpha_local": alpha_local,
        "f_emit_back_Hz": f_emit_calc,
        "rel_error": rel_error
    })
    labels.append(label)
    errors.append(float(rel_error))

# CSV-Export
df = pd.DataFrame(rows)
csv_path = Path("bound_energy_clean_objects.csv")
df.to_csv(csv_path, index=False)
print(f"\nCSV export completed: {csv_path.resolve()}")

# Plot
plt.figure()
plt.plot(range(1, len(errors)+1), errors, marker='o', label="Relativer Fehler von f_emit (Backcalc)")
plt.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
for i, txt in enumerate(labels):
    plt.annotate(txt, (i+1, errors[i]), fontsize=8, xytext=(3, 5), textcoords='offset points')
plt.xticks(range(1, len(labels)+1))
plt.xlabel("Source ID")
plt.ylabel("Relative Error")
plt.title("Back-Calculation Check: f_emit aus alpha_local (aus f_obs)")
plt.legend()
plt.tight_layout()
plt.savefig("bound_energy_clean_plot.png", dpi=200)
plt.show()
