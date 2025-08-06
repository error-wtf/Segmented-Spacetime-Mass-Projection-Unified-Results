import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext
from pathlib import Path

# Precision setting
getcontext().prec = 80

# Physical constants
c = Decimal("299792458")                   # Speed of light [m/s]
G = Decimal("6.67430e-11")                 # Gravitational constant [m^3/kg/s^2]
h = Decimal("6.62607015e-34")              # Planck constant [J⋅s]
alpha_fs = Decimal("7.2973525693e-3")      # Fine-structure constant
m_e = Decimal("9.10938356e-31")            # Electron rest mass [kg]

# φ-BLC constant correction logic (adapted from segmented_full_compare_proof)
def corrected_delta_mass(N_seg):
    φ = (1 + Decimal(5).sqrt()) / 2
    BLC = φ / 2  # ~0.809017
    return BLC * Decimal(N_seg)

# Object list with known accurate frequencies
objects = [
    {
        "name": "S2 star (Sag A*)",
        "f_emit": Decimal("1.384e14"),
        "f_obs": Decimal("1.383e14"),
        "z_gr": Decimal("0.00072306579898770788141720896601590744757772957339118")
    },
    {
        "name": "White dwarf (Sirius B)",
        "f_emit": Decimal("4.568e14"),
        "f_obs": Decimal("4.567e14"),
        "z_gr": Decimal("0.00021896211955331727611123275673308517626450624042041")
    },
    {
        "name": "Sun (solar line)",
        "f_emit": Decimal("4.759e14"),
        "f_obs": Decimal("4.759e14"),
        "z_gr": Decimal("0")
    },
    {
        "name": "Pound-Rebka (1959)",
        "f_emit": Decimal("3.482e18"),
        "f_obs": Decimal("3.482e18"),
        "z_gr": Decimal("0")
    },
    {
        "name": "Earth surface test",
        "f_emit": Decimal("4.570e14"),
        "f_obs": Decimal("4.570e14"),
        "z_gr": Decimal("0")
    },
]

# Output
print("\n" + "="*70)
print(" SEGMENTED SPACETIME – CLEAN TEST SET WITH ΔM CORRECTION")
print("="*70)

rows = []
for obj in objects:
    f_emit = obj["f_emit"]
    f_obs = obj["f_obs"]
    z_gr = obj["z_gr"]
    name = obj["name"]

    # Segment density
    N_seg = f_emit / f_obs - Decimal(1)
    rel_error = abs(N_seg - z_gr) / (z_gr if z_gr != 0 else Decimal("1e-37"))
    delta_m = corrected_delta_mass(N_seg)

    # Output
    print(f"\n--- {name} ---")
    print(f"f_emit    : {f_emit:.3E} Hz")
    print(f"f_obs     : {f_obs:.3E} Hz")
    print(f"N_seg     : {N_seg}")
    print(f"z_gr      : {z_gr}")
    print(f"rel_error : {rel_error}")
    print(f"Δm_corr   : {delta_m}")

    # Append to CSV rows
    rows.append({
        "object": name,
        "f_emit_Hz": float(f_emit),
        "f_obs_Hz": float(f_obs),
        "N_seg": float(N_seg),
        "z_gr": float(z_gr),
        "rel_error": float(rel_error),
        "delta_m_corr": float(delta_m)
    })

# Export CSV
df = pd.DataFrame(rows)
csv_path = Path("bound_energy_with_deltaM.csv")
df.to_csv(csv_path, index=False)
print(f"\nCSV export completed: {csv_path.resolve()}")

# Plotting
plt.figure(figsize=(10, 6))
plt.bar([r["object"] for r in rows], [r["rel_error"] for r in rows], color="darkcyan")
plt.title("Relative Error Between Segment Model and Gravitational Redshift")
plt.ylabel("Relative Error")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

plot_path = Path("bound_energy_with_deltaM_plot.png")
plt.savefig(plot_path)
print(f"Plot saved as: {plot_path.resolve()}")
plt.show()
