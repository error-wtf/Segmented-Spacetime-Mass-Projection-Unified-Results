#!/usr/bin/env python3
"""
redshift_segment_density_plot.py

High-precision check für:

- Frequenzverhältnis ratio = f_emit / f_obs
- Gesamten Redshift z_total = ratio - 1
- Segmentdichte N_seg = f_emit / f_obs - N0
- Photonenergie E_gamma
- (optional) lokales Energieverhältnis epsilon_local = E_gamma(f_obs)/(m_e c^2)

Plot: z_total pro Objekt.

© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

# Set non-interactive backend for pipeline execution
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

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

# Optional: Baseline N0 (Dokuzweck) – gerechnet wird immer mit dem Rohverhältnis
N0 = Decimal("1.000000028")


def compute_ratio(f_emit, f_obs):
    return f_emit / f_obs


def compute_z_total(f_emit, f_obs):
    return f_emit / f_obs - Decimal(1)


def compute_segment_density(f_emit, f_obs, N0_):
    return f_emit / f_obs - N0_


def compute_photon_energy(f_emit):
    return h * f_emit


def compute_local_energy_ratio_from_obs(f_obs):
    """
    epsilon_local = E_gamma(f_obs) / (m_e c^2)
    Nur Energieskalen-Verhältnis, kein „local alpha".
    """
    E_gamma_obs = h * f_obs
    return E_gamma_obs / (m_e * c**2)


# === Testobjekte (z.T. fiktive, z.T. Literatur-nah) ===
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
        "f_emit": Decimal("3.0e18"),
        "f_obs":  Decimal("3.0e18")
    },
    {
        "label": "Earth surface lab test",
        "f_emit": Decimal("1.0e14"),
        "f_obs":  Decimal("1.0e14")
    },
]

rows = []
labels = []
z_values = []

for src in sources:
    label = src["label"]
    f_emit = src["f_emit"]
    f_obs = src["f_obs"]

    ratio = compute_ratio(f_emit, f_obs)
    z_total = compute_z_total(f_emit, f_obs)
    N_seg = compute_segment_density(f_emit, f_obs, N0)
    E_gamma = compute_photon_energy(f_emit)
    epsilon_local = compute_local_energy_ratio_from_obs(f_obs)

    print(f"\n=== {label} ===")
    print(f"f_emit     : {f_emit}")
    print(f"f_obs      : {f_obs}")
    print(f"ratio      : {ratio}  (f_emit / f_obs)")
    print(f"z_total    : {z_total} (f_emit / f_obs - 1)")
    print(f"N_seg      : {N_seg} (relativ zu N0={N0})")
    print(f"E_gamma    : {E_gamma} J")
    print(f"epsilon_local = E_gamma(f_obs)/(m_e c^2) : {epsilon_local}")

    rows.append({
        "object": label,
        "f_emit_Hz": f_emit,
        "f_obs_Hz": f_obs,
        "ratio": ratio,
        "z_total": z_total,
        "N_seg_minus_N0": N_seg,
        "E_gamma_J": E_gamma,
        "epsilon_local": epsilon_local,
    })
    labels.append(label)
    z_values.append(float(z_total))

# CSV-Export
df = pd.DataFrame(rows)
csv_path = Path("redshift_segment_density_clean_objects.csv")
df.to_csv(csv_path, index=False)
print(f"\nCSV export completed: {csv_path.resolve()}")

# Plot: z_total pro Objekt
plt.figure()
plt.plot(range(1, len(z_values) + 1),
         z_values,
         marker='o',
         label="z_total = f_emit/f_obs - 1")
plt.axhline(y=0.0, color='gray', linestyle='--', linewidth=0.8)

for i, txt in enumerate(labels):
    plt.annotate(txt,
                 (i + 1, z_values[i]),
                 fontsize=8,
                 xytext=(3, 5),
                 textcoords='offset points')

plt.xticks(range(1, len(labels) + 1))
plt.xlabel("Source ID")
plt.ylabel("Redshift z_total")
plt.title("Redshift vs. Objekt (SSZ-Segmentdichte ≈ z_total)")
plt.legend()
plt.tight_layout()
plt.savefig("redshift_segment_density_clean_plot.png", dpi=200)
plt.close()  # Close instead of show() for non-interactive pipeline execution
print("Plot saved and closed (non-interactive mode)")
