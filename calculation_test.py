#!/usr/bin/env python3
"""
segmented_mass_from_rphi.py  –  Derive gravitational mass *without* mass input
==========================================================================
This script demonstrates how the Segmented-Spacetime framework (φ/2-rule)
allows the reconstruction of an object's rest mass *solely* from its
measured segmented radius r_φ.

Mathematical background
-----------------------
Given
    r_s   = 2 G M / c²           (Schwarzschild radius)
    r_φ   = φ   G M / c²         (segmented radius)
we have the invariant ratio
    r_φ / r_s = φ / 2            (pure number, mass-free)
Re-arranging the second equation gives
    M = c² r_φ / (G φ)

Therefore – provided an experimental r_φ – you can compute the mass
without any circular dependency.

Usage
-----
1. Pure function call inside Python:
       >>> from segmented_mass_from_rphi import mass_from_rphi
       >>> mass_from_rphi(1.353e-57)   # example radius in metres

2. Command-line:
       $ python segmented_mass_from_rphi.py --rphi 1.353e-57

3. Validation round-trip (generates demo table)
       $ python segmented_mass_from_rphi.py --demo
   This takes a small built-in catalogue of objects, derives their r_φ
   *from* the known mass (to emulate a hypothetical measurement), then
   inverts r_φ back to the mass and prints the relative error.

Author: ChatGPT demo for the SST project – MIT License
"""

author = "ChatGPT"

import math
import sys
import argparse
from decimal import Decimal, getcontext
from typing import List, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────
G   = Decimal('6.67430e-11')      # m³ kg⁻¹ s⁻²
a_c = Decimal('299792458')        # m s⁻¹
phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)  # golden ratio ≈ 1.618…

# Set high precision for small radii such as electrons
getcontext().prec = 50

# ──────────────────────────────────────────────────────────────────────────────
# CORE FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def mass_from_rphi(r_phi: Decimal, *, phi_const: Decimal = phi) -> Decimal:
    """Return mass [kg] from segmented radius r_phi [m] using M = c² r_φ / (G φ)."""
    return (a_c ** 2) * r_phi / (G * phi_const)

def rphi_from_mass(mass: Decimal, *, phi_const: Decimal = phi) -> Decimal:
    """Return segmented radius r_φ [m] from mass [kg]."""
    return (G * mass / (a_c ** 2)) * phi_const

# Helper for pretty-printing
_si_prefix = {
    -24: 'y', -21: 'z', -18: 'a', -15: 'f', -12: 'p', -9: 'n', -6: 'µ', -3: 'm',
      0: '',  3: 'k',   6: 'M',   9: 'G',  12: 'T', 15: 'P', 18: 'E', 21: 'Z', 24: 'Y'
}

def human(val: Decimal, unit: str = '', width: int = 9) -> str:
    if val == 0:
        return f"0 {unit}"
    exp = int(math.floor(val.log10() / 3) * 3)
    exp = max(min(exp, 24), -24)
    scaled = val / (Decimal(10) ** exp)
    prefix = _si_prefix.get(exp, f"e{exp}")
    return f"{scaled:.{width}g} {prefix}{unit}"

# ──────────────────────────────────────────────────────────────────────────────
# DEMONSTRATION: ROUND-TRIP TESTS
# ──────────────────────────────────────────────────────────────────────────────
_catalogue: List[Tuple[str, str]] = [
    ("Elektron", "9.1093837015e-31"),
    ("Mond",      "7.342e22"),
    ("Erde",      "5.97219e24"),
    ("Sonne",     "1.98847e30"),
]

def run_demo() -> None:
    print("Round-trip validation using built-in catalogue:\n")
    header = ("Objekt", "M_in [kg]", "r_phi [m]", "M_out [kg]", "rel. Fehler")
    print("{:<10} {:>17} {:>14} {:>17} {:>12}".format(*header))
    print("-" * 78)
    for name, m_str in _catalogue:
        M_in  = Decimal(m_str)
        r_phi = rphi_from_mass(M_in)
        M_out = mass_from_rphi(r_phi)
        rel   = abs((M_out - M_in) / M_in)
        print(f"{name:<10} {human(M_in,'kg'):>17} {human(r_phi,'m'):>14} {human(M_out,'kg'):>17} {rel:.2e}")

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute mass from segmented radius r_phi.")
    parser.add_argument("--rphi", type=str, help="Measured r_phi in metres (float or Decimal).")
    parser.add_argument("--demo", action="store_true", help="Run round-trip validation table.")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        sys.exit()

    if args.rphi is None:
        parser.error("Either --rphi or --demo is required.")

    try:
        r_phi_val = Decimal(args.rphi)
    except Exception as e:
        parser.error(f"Could not parse r_phi: {e}")

    mass = mass_from_rphi(r_phi_val)
    print(f"Mass from r_phi = {r_phi_val} m → {mass} kg")
