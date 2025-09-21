#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lagrangian-based geodesic tests for the segmented-spacetime metric:
  ds^2 = -A(r)c^2 dt^2 + A(r)^{-1} dr^2 + r^2 dΩ^2
with A(U) = 1 - 2U + 2U^2 + eps3 * U^3, U = GM/(r c^2).

Checks:
- Photon sphere r_ph from r*A'(r) - 2*A(r) = 0  (null circular)
- Timelike circular orbits: Ω^2, E(r), L(r)
- ISCO from d/dr L^2(r) = 0
- Compare against GR baselines (eps3=0): r_ph=1.5 r_s, r_isco=3 r_s

No external deps: uses Decimal + simple Newton/bisection + central differences.

Usage examples:
  python lagrangian_tests.py --object sun
  python lagrangian_tests.py --mass 8.544456e36 --label "SgrA*" --eps3 -4.8
"""
from decimal import Decimal, getcontext
import argparse, math

# High precision like the rest of the pipeline
getcontext().prec = 80

D = Decimal
G = D('6.67430e-11')
c = D('299792458')
MSUN = D('1.98847e30')

PRESETS = {
    "sun": {"mass": MSUN, "label": "Sun"},
    "sgrA": {"mass": D('8.544456e36'), "label": "Sgr A*"},
}

def A_of_r(r, M, eps3):
    """A(r) for U = GM/(r c^2) with A(U)=1-2U+2U^2+eps3 U^3."""
    U = G*M/(r*c*c)
    return (D(1) - 2*U + 2*U*U + eps3*(U*U*U))

def dA_dr(r, M, eps3):
    """dA/dr via chain rule: dA/dU * dU/dr with U=GM/(r c^2)."""
    U = G*M/(r*c*c)
    dA_dU = (-2 + 4*U + 3*eps3*(U*U))
    dU_dr = -U/r  # since U ~ 1/r
    return dA_dU * dU_dr

def photon_sphere_r(M, eps3):
    """
    Solve f(r) = r*A'(r) - 2*A(r) = 0 using safeguarded Newton.
    Start near 1.5 r_s; r_s=2GM/c^2.
    """
    rs = 2*G*M/(c*c)
    r = D('1.5')*rs  # good initial guess
    for _ in range(80):
        A  = A_of_r(r, M, eps3)
        Ap = dA_dr(r, M, eps3)
        f  = r*Ap - 2*A
        # df/dr = Ap + r*A'' - 2*A'
        # Avoid deriving A'': use secant on f
        h = r * D('1e-20')
        if h == 0: h = rs*D('1e-20')
        rp = r + h
        A2  = A_of_r(rp, M, eps3)
        Ap2 = dA_dr(rp, M, eps3)
        f2  = rp*Ap2 - 2*A2
        df  = (f2 - f)/h
        if df == 0: break
        step = f/df
        r_new = r - step
        # guard: stay > rs
        if r_new <= rs*(1+D('1e-9')):
            r_new = (r + rs*(1+D('1e-9')))/2
        # convergence
        if abs(step) <= D('1e-30')*max(D(1), r):
            return r_new
        r = r_new
    return r  # return best effort

def L2_of_r(r, M, eps3):
    """
    L^2(r) for timelike circular orbits:
      L^2 = r^3 A'(r) / ( 2A(r) - r A'(r) )
    """
    A  = A_of_r(r, M, eps3)
    Ap = dA_dr(r, M, eps3)
    denom = (2*A - r*Ap)
    if denom <= 0:
        return D('NaN')
    return (r**3) * Ap / denom

def dL2_dr_central(r, M, eps3):
    """High-precision central difference for d/dr L^2."""
    h = r * D('1e-7')
    if h == 0:
        h = D('1e-7')
    r1 = r - h
    r2 = r + h
    return (L2_of_r(r2, M, eps3) - L2_of_r(r1, M, eps3)) / (2*h)

def isco_r(M, eps3):
    """
    Solve d/dr L^2(r) = 0 using bracketed secant around ~3 r_s.
    """
    rs = 2*G*M/(c*c)
    # bracket around 3 r_s
    a = D('2.2')*rs
    b = D('4.5')*rs
    fa = dL2_dr_central(a, M, eps3)
    fb = dL2_dr_central(b, M, eps3)
    # If not bracketed, widen once
    if fa*fb > 0:
        a = D('2.0')*rs; fa = dL2_dr_central(a, M, eps3)
        b = D('6.0')*rs; fb = dL2_dr_central(b, M, eps3)
    # Secant with damping
    r = b
    for _ in range(120):
        fa = dL2_dr_central(a, M, eps3)
        fb = dL2_dr_central(b, M, eps3)
        if (fb - fa) == 0:
            break
        r_new = b - fb*(b - a)/(fb - fa)
        # keep inside [a,b]
        if not (min(a,b) < r_new < max(a,b)):
            r_new = (a + b)/2
        fr = dL2_dr_central(r_new, M, eps3)
        # update bracket
        if fa*fr <= 0:
            b = r_new
        else:
            a = r_new
        # convergence
        if abs(fr) <= D('1e-30'):
            return r_new
    return (a + b)/2

def omega_sq(r, M, eps3):
    """Ω^2 = A'(r) c^2 / (2 r)"""
    return dA_dr(r, M, eps3) * (c*c) / (2*r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--object", choices=list(PRESETS.keys()))
    ap.add_argument("--mass", type=str, help="Mass in kg (overrides --object)")
    ap.add_argument("--label", type=str, default=None)
    ap.add_argument("--eps3", type=str, default="-4.8", help="ε3 parameter; GR is 0")
    args = ap.parse_args()

    if args.object:
        M = PRESETS[args.object]["mass"]
        label = PRESETS[args.object]["label"]
    else:
        if not args.mass:
            ap.error("Provide --object or --mass")
        M = D(args.mass)
        label = args.label or "Custom"

    eps3 = D(args.eps3)
    rs = 2*G*M/(c*c)

    print("="*78)
    print(f"LAGRANGIAN TESTS — {label} | M = {M:.6E} kg | eps3 = {eps3}")
    print("="*78)
    print(f"Schwarzschild radius r_s : {rs:.6E} m")

    # Photon sphere
    rph = photon_sphere_r(M, eps3)
    rph_gr = D('1.5')*rs
    print(f"Photon sphere r_ph       : {rph:.6E} m")
    print(f"GR baseline (eps3=0)     : {rph_gr:.6E} m")
    print(f"Δrel vs GR               : {((rph-rph_gr)/rph_gr):.6E}")

    # ISCO
    risco = isco_r(M, eps3)
    risco_gr = D('3')*rs
    print(f"ISCO radius r_isco       : {risco:.6E} m")
    print(f"GR baseline (eps3=0)     : {risco_gr:.6E} m")
    print(f"Δrel vs GR               : {((risco-risco_gr)/risco_gr):.6E}")

    # Example frequency at r=10 r_s (weak-field sanity)
    r10 = D('10')*rs
    Om2 = omega_sq(r10, M, eps3)
    print(f"Ω^2 at 10 r_s            : {Om2:.6E} s^-2")

    print("\nSummary:")
    print(" - r_ph from d/dr(A/r^2)=0 (null circular)")
    print(" - r_isco from d/dr L^2=0 (marginally stable timelike circular)")
    print(" - GR baselines: r_ph=1.5 r_s, r_isco=3 r_s")
    print(" - Finite, small deviations indicate the strong-field SSZ signature.")
    print("="*78)

if __name__ == "__main__":
    main()

