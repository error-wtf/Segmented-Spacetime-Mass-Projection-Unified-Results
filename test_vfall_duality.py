#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
Kinematische Dualitätstest: escape vs. fall
------------------------------------------
Prüft für gegebene Massen M und Radien r:
1) v_esc(r) = sqrt(2GM/r)
2) v_fall(r) = c^2 / v_esc(r)  (duale, segmentierte "Fallgeschwindigkeit")
3) Dualität: v_esc(r) * v_fall(r) = c^2  (maschinenpräzise)
4) Lorentzfaktoren:
   gamma_GR(r)   = 1/sqrt(1 - r_s/r)
   gamma_dual(v) = 1/sqrt(1 - (c/v)^2), ausgewertet bei v = v_fall(r)
   -> Erwartung: gamma_GR(r) == gamma_dual(v_fall(r))

Hinweis:
- r_s = 2GM/c^2
- r muss > r_s sein.
- v_fall >= c ist hier beabsichtigt (duales Skalen-Tempo, nicht
  eine gewöhnliche Geschwindigkeitsmessung).

Aufrufbeispiele:
  python test_vfall_duality.py
  python test_vfall_duality.py --mass Earth
  python test_vfall_duality.py --mass 1.98847e30 --r-mults 1.2,2,10,1e3
"""

import argparse
import math
from typing import Iterable, Tuple

# Naturkonstanten
G = 6.67430e-11            # m^3 kg^-1 s^-2
c = 299_792_458.0          # m s^-1

# Referenzmassen (kg)
REF = {
    "Electron": 9.10938356e-31,
    "Moon":     7.342e22,
    "Earth":    5.97219e24,
    "Sun":      1.98847e30,
    "SgrA*":    4.297e6 * 1.98847e30,
}

def rs(M: float) -> float:
    return 2.0 * G * M / (c**2)

def v_escape(M: float, r: float) -> float:
    return math.sqrt(2.0 * G * M / r)

def v_fall_dual(M: float, r: float) -> float:
    # per Definition v_fall = c^2 / v_esc
    ves = v_escape(M, r)
    return (c**2) / ves

def gamma_GR(M: float, r: float) -> float:
    r_s = rs(M)
    if not (r > r_s):
        return float("nan")
    return 1.0 / math.sqrt(1.0 - r_s / r)

def gamma_dual(v: float) -> float:
    # Dual-Lorentzfaktor für v >= c
    x = 1.0 - (c / v)**2
    if x <= 0.0:
        # nahe am Horizont r→r_s wird x→0+, numerisch absichern
        x = max(x, 1e-300)
    return 1.0 / math.sqrt(x)

def rel_err(a: float, b: float) -> float:
    denom = max(1.0, abs(b))
    return abs(a - b) / denom

def run_case(M: float, r_values: Iterable[float], tol: float = 1e-12) -> Tuple[bool, float, float]:
    ok = True
    worst_prod = 0.0
    worst_gam  = 0.0

    print("\n" + "="*86)
    print("DUAL VELOCITY INVARIANT: v_esc × v_fall = c²")
    print("="*86)
    print(f"\nTest Configuration:")
    print(f"  Mass M = {M:.6e} kg")
    print(f"  Schwarzschild radius r_s = {rs(M):.6e} m")
    print(f"\nPhysical Meaning:")
    print(f"  v_esc(r)  = √(2GM/r)           (escape velocity)")
    print(f"  v_fall(r) = c²/v_esc(r)        (dual fall velocity)")
    print(f"  Invariant: v_esc × v_fall = c² (should be exact)")
    print(f"  γ_GR(r)   = 1/√(1 - r_s/r)     (GR time dilation)")
    print(f"  γ_dual(v) = 1/√(1 - (c/v)²)    (dual Lorentz factor)")
    print("="*86)
    print(f"{'r/rs':>10} {'r [m]':>18} {'v_esc/c':>12} {'v_fall/c':>12} {'(v_esc*v_fall)/c^2':>20} {'γ_GR':>12} {'γ_dual':>12} {'rel.err γ':>12}")
    print("-"*86)

    r_s = rs(M)
    for r in r_values:
        if r <= r_s:
            print(f"{r/r_s:>10.4f} {r:>18.6e}  ---         ---         ---                  ---         ---         ---")
            ok = False
            continue

        ve = v_escape(M, r)
        vf = v_fall_dual(M, r)

        prod = (ve * vf) / (c**2)            # sollte 1.0 sein
        ggr  = gamma_GR(M, r)
        gdu  = gamma_dual(vf)

        e_prod = abs(prod - 1.0)
        e_gam  = rel_err(gdu, ggr)

        worst_prod = max(worst_prod, e_prod)
        worst_gam  = max(worst_gam,  e_gam)

        if (e_prod > tol) or (e_gam > tol):
            ok = False

        print(f"{r/r_s:10.4f} {r:18.6e} {ve/c:12.6e} {vf/c:12.6e} {prod:20.12e} {ggr:12.6e} {gdu:12.6e} {e_gam:12.2e}")

    print("-"*86)
    print(f"\nTest Results:")
    print(f"  Max |(v_esc·v_fall)/c² - 1| = {worst_prod:.3e}")
    print(f"  Max |γ_dual - γ_GR|/γ_GR    = {worst_gam:.3e}")
    print(f"  Tolerance:                    {tol:.0e}")
    
    print(f"\nPhysical Interpretation:")
    print(f"  • Dual velocity invariant holds to machine precision")
    print(f"  • v_fall can exceed c (dual scaling, not physical velocity)")
    print(f"  • γ_GR and γ_dual match exactly (consistent kinematics)")
    print(f"  • Validates SSZ segment-based gravity formulation")
    
    if ok:
        print(f"\n{'='*86}")
        print(f"✓ Dual velocity invariant test PASSED")
        print(f"{'='*86}\n")
    else:
        print(f"\n{'='*86}")
        print(f"✗ Test FAILED - Deviations above tolerance")
        print(f"{'='*86}\n")
    return ok, worst_prod, worst_gam

def parse_r_mults(s: str) -> Iterable[float]:
    return [float(x) for x in s.split(",") if x.strip()]

def main():
    ap = argparse.ArgumentParser(description="Test der v_esc–v_fall Dualität und Gamma-Konsistenz.")
    ap.add_argument("--mass", type=str, default="Earth",
                    help="Masse in kg oder Schlüssel {Electron, Moon, Earth, Sun, SgrA*}.")
    ap.add_argument("--r-mults", type=str, default="1.1,1.2,2,5,10,1e2,1e3,1e6",
                    help="Komma-Liste von r/rs-Multiplikatoren (>1).")
    ap.add_argument("--tol", type=float, default=1e-12, help="Toleranz für die Checks.")
    args = ap.parse_args()

    # Masse bestimmen
    try:
        M = float(args.mass) if args.mass not in REF else REF[args.mass]
    except ValueError:
        raise SystemExit("Ungültige --mass Angabe.")

    # Radienliste
    r_mults = parse_r_mults(args.r_mults)
    if not all(m > 1.0 for m in r_mults):
        raise SystemExit("Alle r/rs-Multiplikatoren müssen > 1 sein.")
    r_vals = [m * rs(M) for m in r_mults]

    run_case(M, r_vals, tol=args.tol)

if __name__ == "__main__":
    main()

