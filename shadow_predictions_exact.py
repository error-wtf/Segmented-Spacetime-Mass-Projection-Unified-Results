
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shadow_predictions_exact.py
Exact GR shadow diameters using analytic photon-sphere formulas.
Deterministic up to floating-point precision.

Formulas (Schwarzschild):
  r_s   = 2GM/c^2
  r_ph  = (3/2) r_s
  b_ph  = (3√3/2) r_s
  theta = b_ph / D   (radians),  diameter = 2 * theta

Distances:
  Provide in parsec. Defaults match our Sgr A* and M87* scripts.
"""

import math
import argparse

G   = 6.67430e-11
c   = 299_792_458.0
Msun= 1.98847e30
PC  = 3.085677581491367e16
PI  = math.pi

def shadow_diameter_microas(M_kg: float, D_pc: float) -> float:
    r_s  = 2.0 * G * M_kg / (c*c)
    b_ph = (3.0*math.sqrt(3.0)/2.0) * r_s
    D_m  = D_pc * PC
    theta_rad = b_ph / D_m
    microas = theta_rad * (180.0/PI) * 3.6e9  # µas (radius)
    return 2.0 * microas  # diameter

def main():
    ap = argparse.ArgumentParser(description="Exact GR shadow diameters (µas)")
    ap.add_argument("--sgrA_msun", type=float, default=4.297e6, help="Sgr A* mass in solar masses")
    ap.add_argument("--sgrA_dist_pc", type=float, default=8277.0, help="Sgr A* distance in parsec")
    ap.add_argument("--m87_msun", type=float, default=6.5e9, help="M87* mass in solar masses")
    ap.add_argument("--m87_dist_pc", type=float, default=1.68e7, help="M87* distance in parsec (≈16.8 Mpc)")
    args = ap.parse_args()

    d_sgr = shadow_diameter_microas(args.sgrA_msun*Msun, args.sgrA_dist_pc)
    d_m87 = shadow_diameter_microas(args.m87_msun*Msun, args.m87_dist_pc)

    print(f"Sgr A*: diameter = {d_sgr:.3f} µas  [M={args.sgrA_msun:.6g} Msun, D={args.sgrA_dist_pc:.6g} pc]")
    print(f"M87*:   diameter = {d_m87:.3f} µas  [M={args.m87_msun:.6g} Msun, D={args.m87_dist_pc:.6g} pc]")

if __name__ == "__main__":
    main()
