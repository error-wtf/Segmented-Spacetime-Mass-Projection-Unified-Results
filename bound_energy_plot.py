#!/usr/bin/env python3
"""
bound_energy.py – Segmented Spacetime vs. Classical Gravitational Redshift
© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

from scipy.constants import h, m_e, c
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# === FUNCTIONS ===

def compute_segment_density(f_emit: float, f_obs: float, N0: float = 1.000000028) -> float:
    return f_emit / f_obs - N0

def compute_photon_energy(f_emit: float) -> float:
    return h * f_emit

def compute_bound_mass(E_gamma: float, m_e_: float = m_e, c_: float = c) -> float:
    return m_e_ - E_gamma / c_**2

def compute_gravitational_redshift(f_emit: float, f_obs: float) -> float:
    return (f_emit - f_obs) / f_obs

def compute_local_alpha(f_obs: float, m_e_: float = m_e, c_: float = c, h_: float = h) -> float:
    return (f_obs * h_) / (m_e_ * c_**2)

def compute_f_emit_from_alpha(alpha_local: float, m_e_: float = m_e, c_: float = c, h_: float = h) -> float:
    return (alpha_local * m_e_ * c_**2) / h_

# === CONSTANT ===
alpha_fs = 1 / 137.035999084  # CODATA 2018
N0 = 1.000000028

# === BATCH FREQUENCY PAIRS ===
frequency_pairs = [
    (138_392_455_537_000, 134_920_458_147_000),  # Pair 1
    (2.301525e14, 2.300000e14),                  # Pair 2
    (1.38394e14, 1.35000e14),                    # Pair 3
]

results = []

print("="*70)
print(" SEGMENTED SPACETIME – MULTI-PAIR PROCESSING AND EXPORT")
print("="*70)

for idx, (f_emit, f_obs) in enumerate(frequency_pairs):
    N_seg = compute_segment_density(f_emit, f_obs, N0)
    E_gamma = compute_photon_energy(f_emit)
    m_bound = compute_bound_mass(E_gamma)
    alpha_local = compute_local_alpha(f_obs)
    f_emit_check = compute_f_emit_from_alpha(alpha_local)
    z_gr = compute_gravitational_redshift(f_emit, f_obs)
    rel_error_f_emit = abs(f_emit_check - f_emit) / f_emit

    row = {
        "id": idx + 1,
        "f_emit_Hz": f_emit,
        "f_obs_Hz": f_obs,
        "N0": N0,
        "N_seg": N_seg,
        "E_gamma_J": E_gamma,
        "m_bound_kg": m_bound,
        "alpha_local": alpha_local,
        "alpha_fs": alpha_fs,
        "z_gr": z_gr,
        "f_emit_check_Hz": f_emit_check,
        "rel_error_f_emit": rel_error_f_emit
    }
    results.append(row)

    print(f"\n--- Frequency Pair {idx+1} ---")
    print(f"f_emit       : {f_emit:.3e} Hz")
    print(f"f_obs        : {f_obs:.3e} Hz")
    print(f"N_seg        : {N_seg:.9f}")
    print(f"z_gr         : {z_gr:.9f}")
    print(f"rel_error    : {rel_error_f_emit:.2e}")

# === CSV EXPORT ===
df_all = pd.DataFrame(results)
csv_batch_path = Path("bound_energy_batch_results.csv")
df_all.to_csv(csv_batch_path, index=False)
print(f"\nAll results exported to CSV: {csv_batch_path.resolve()}")

# === PLOT ===
plt.figure(figsize=(8, 5))
plt.plot(df_all["id"], df_all["rel_error_f_emit"], marker='o', label="Relative Error of f_emit")
plt.axhline(0, color='gray', linestyle='--')
plt.xlabel("Frequency Pair ID")
plt.ylabel("Relative Error")
plt.title("Deviation between Measured and Back-Calculated f_emit")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("bound_energy_plot.png")
print("Plot saved as bound_energy_plot.png")
plt.show()
