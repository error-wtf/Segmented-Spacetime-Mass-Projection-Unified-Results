#!/usr/bin/env python3
"""
High-Precision Bound Energy and Redshift Calculation
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

from decimal import Decimal, getcontext
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Decimal precision
getcontext().prec = 50

# Physical constants (SI units)
h = Decimal("6.62607015e-34")
c = Decimal("299792458")
m_e = Decimal("9.1093837015e-31")
alpha_fs = Decimal("1") / Decimal("137.035999084")
N0 = Decimal("1.000000028")

def compute_segment_density(f_emit, f_obs):
    return f_emit / f_obs - N0

def compute_photon_energy(f_emit):
    return h * f_emit

def compute_bound_mass(E_gamma):
    return m_e - (E_gamma / c**2)

def compute_local_alpha(f_obs):
    return (f_obs * h) / (m_e * c**2)

def compute_f_emit_from_alpha(alpha_local):
    return (alpha_local * m_e * c**2) / h

def compute_gravitational_redshift(f_emit, f_obs):
    return (f_emit - f_obs) / f_obs

# === Known, well-measured frequency pairs ===
sources = [
    {
        "label": "S2 star (Sag A*)",
        "f_emit": Decimal("1.384e14"),
        "f_obs":  Decimal("1.383e14")
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

print("="*70)
print(" SEGMENTED SPACETIME – CLEAN TEST SET (EXACT OBJECTS)")
print("="*70)

results = []
errors = []
labels = []

for i, src in enumerate(sources):
    f_emit = src["f_emit"]
    f_obs = src["f_obs"]
    label = src["label"]

    N_seg = compute_segment_density(f_emit, f_obs)
    E_gamma = compute_photon_energy(f_emit)
    m_bound = compute_bound_mass(E_gamma)
    alpha_local = compute_local_alpha(f_obs)
    f_emit_calc = compute_f_emit_from_alpha(alpha_local)
    z_gr = compute_gravitational_redshift(f_emit, f_obs)
    rel_error = abs(f_emit_calc - f_emit) / f_emit

    results.append({
        "label": label,
        "f_emit_Hz": f_emit,
        "f_obs_Hz": f_obs,
        "N_seg": N_seg,
        "E_gamma_J": E_gamma,
        "m_bound_kg": m_bound,
        "alpha_local": alpha_local,
        "z_gr": z_gr,
        "f_emit_back_calc_Hz": f_emit_calc,
        "rel_error": rel_error
    })

    labels.append(label)
    errors.append(float(rel_error))

    print(f"\n--- {label} ---")
    print(f"f_emit    : {f_emit:.3E} Hz")
    print(f"f_obs     : {f_obs:.3E} Hz")
    print(f"N_seg     : {N_seg}")
    print(f"z_gr      : {z_gr}")
    print(f"rel_error : {rel_error}")

# === CSV export ===
df = pd.DataFrame(results)
csv_path = Path("bound_energy_clean_objects.csv")
df.to_csv(csv_path, index=False)
print(f"\nCSV export completed: {csv_path.resolve()}")

# === Plotting ===
plt.figure()
plt.plot(range(1, len(errors)+1), errors, marker='o', label="Relative Error of $f_{emit}$")
plt.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
for i, txt in enumerate(labels):
    plt.annotate(txt, (i+1, errors[i]), fontsize=8, xytext=(3, 5), textcoords='offset points')
plt.xticks(range(1, len(labels)+1))
plt.xlabel("Source ID")
plt.ylabel("Relative Error")
plt.title("Fully Recalculated: Deviation of $f_{emit}$ from $f_{obs}$")
plt.legend()
plt.tight_layout()
plt.savefig("bound_energy_clean_plot.png")
plt.show()
