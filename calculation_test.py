#!/usr/bin/env python3
"""
segmented_mass_from_rphi.py  –  Extended Roundtrip Validation with Real Calculations
====================================================================================
This script demonstrates and validates the segmented-spacetime principle by:
  1. Computing the Schwarzschild radius r_s from a known mass.
  2. Computing the segmented radius r_phi from that mass.
  3. Inverting r_phi back to mass and comparing to the original.
  4. Reporting relative errors.

Usage:
  • Demo mode (round-trip validation):
      python segmented_mass_from_rphi.py --demo

  • Single calculation:
      python segmented_mass_from_rphi.py --rphi <segmented_radius_in_meters>

Author: Carmen Wrede & Lino Casu – 2025
License: MIT
"""

from decimal import Decimal, getcontext
import math
import sys
import argparse
from typing import List, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

# Set high precision for tiny and huge values
getcontext().prec = 50

# Physical constants
G   = Decimal('6.67430e-11')       # gravitational constant [m^3 kg^-1 s^-2]
c   = Decimal('299792458')         # speed of light [m/s]
phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)  # golden ratio ≈ 1.618…

# Demo catalogue of known masses
_catalogue: List[Tuple[str, str]] = [
    ("Electron", "9.10938356e-31"),
    ("Moon",     "7.342e22"),
    ("Earth",    "5.97219e24"),
    ("Sun",      "1.98847e30"),
]

# SI prefix mapping for human-readable output
_si_prefix = {
    -24: 'y', -21: 'z', -18: 'a', -15: 'f', -12: 'p', -9: 'n',
     -6: 'µ', -3: 'm',   0: '',    3: 'k',   6: 'M',  9: 'G',
     12: 'T', 15: 'P',   18: 'E', 21: 'Z', 24: 'Y'
}

# ──────────────────────────────────────────────────────────────────────────────
# CORE FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def schwartzschild_radius(mass: Decimal) -> Decimal:
    """Return Schwarzschild radius [m] for a given mass."""
    return (Decimal(2) * G * mass) / (Decimal(c) ** 2)

def rphi_from_mass(mass: Decimal) -> Decimal:
    """Return segmented radius r_phi [m] from mass [kg]."""
    return (G * mass / (Decimal(c) ** 2)) * phi

def mass_from_rphi(r_phi: Decimal) -> Decimal:
    """Return mass [kg] from segmented radius r_phi [m]."""
    return (Decimal(c) ** 2) * r_phi / (G * phi)

def human(val: Decimal, unit: str = '', width: int = 9) -> str:
    """Format a Decimal with SI-prefix for readability."""
    if val == 0:
        return f"0 {unit}"
    exp = int(math.floor(val.log10() / 3) * 3)
    exp = max(min(exp, 24), -24)
    scaled = val / (Decimal(10) ** exp)
    prefix = _si_prefix.get(exp, f"e{exp}")
    return f"{scaled:.{width}g} {prefix}{unit}"

# ──────────────────────────────────────────────────────────────────────────────
# DEMO MODE
# ──────────────────────────────────────────────────────────────────────────────

def run_demo() -> None:
    print("Enhanced Round-trip Validation with Real Calculations:\n")
    header = ("Object", "M_in [kg]", "r_s [m]", "r_phi [m]", "M_out [kg]", "Rel Error")
    print("{:<10} {:>17} {:>15} {:>15} {:>17} {:>12}".format(*header))
    print("-" * 95)
    for name, m_str in _catalogue:
        M_in  = Decimal(m_str)
        r_s   = schwartzschild_radius(M_in)
        r_phi = rphi_from_mass(M_in)
        M_out = mass_from_rphi(r_phi)
        rel   = abs((M_out - M_in) / M_in)
        print(f"{name:<10}"
              f" {human(M_in,'kg'):>17}"
              f" {human(r_s,'m'):>15}"
              f" {human(r_phi,'m'):>15}"
              f" {human(M_out,'kg'):>17}"
              f" {rel:.2e}")

# ──────────────────────────────────────────────────────────────────────────────
# MAIN ENTRYPOINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compute/restmass inversion with segmented-spacetime principle."
    )
    parser.add_argument(
        "--rphi",
        type=str,
        help="Segmented radius r_phi in metres (as decimal string)."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run enhanced round-trip validation demo."
    )
    args = parser.parse_args()

    if args.demo:
        run_demo()
        sys.exit(0)

    if args.rphi:
        try:
            r_phi_val = Decimal(args.rphi)
        except Exception as e:
            parser.error(f"Invalid r_phi: {e}")
        m = mass_from_rphi(r_phi_val)
        print(f"Computed mass from segmented radius {r_phi_val} m → {m} kg")
        sys.exit(0)

    parser.error("Please specify --rphi <value> or --demo to run calculations.")
    
if __name__ == "__main__":
    print("© Carmen Wrede & Lino Casu")
    main()
