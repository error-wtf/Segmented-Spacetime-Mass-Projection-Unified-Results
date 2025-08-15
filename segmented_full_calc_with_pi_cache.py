
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segmented Spacetime — Δ(M) Mass Validation with Chudnovsky-π Cache
==================================================================
This prototype computes π via the Chudnovsky series (configurable terms
and precision), caches high-precision constants, and then runs the
segmented Δ(M)-inversion (mass reconstruction) with improved initial
guessing and iteration instrumentation.

© 2025 Carmen Wrede & Lino Casu · Prototype integration by Akira
License: MIT
"""

from __future__ import annotations
import sys, argparse, math, time
from decimal import Decimal as D, getcontext
from typing import Tuple, Dict

# ──────────────────────────────────────────────────────────────────────────────
# Chudnovsky π (Decimal, simple iterative form)
# ──────────────────────────────────────────────────────────────────────────────
def chudnovsky_pi(n_terms: int, prec: int) -> D:
    """
    Compute π using the Chudnovsky series with Decimal arithmetic.
    n_terms: number of series terms (≈ digits/14)
    prec   : Decimal precision (digits)
    """
    getcontext().prec = prec
    # C = 426880 * sqrt(10005)
    sqrt10005 = getcontext().sqrt(D(10005))
    C = D(426880) * sqrt10005

    # Iterate terms: M_k, L_k, X_k (classic update, simple form)
    S = D(0)
    M = D(1)                   # ratio of factorials (6k)!/( (3k)!(k!)^3 )
    L = D(13591409)
    X = D(1)
    SIGN = 1
    # Constant: 640320^3
    C3 = D(640320) ** 3

    for k in range(n_terms):
        term = (M * L) / X
        if SIGN < 0:
            term = -term
        S += term

        # Next k
        # Update M by multiplying with rational factor to avoid factorials
        k1 = k + 1
        num = D( (6*k1 - 5) * (6*k1 - 4) * (6*k1 - 3) * (6*k1 - 2) * (6*k1 - 1) * (6*k1) )
        den = D( (3*k1 - 2) * (3*k1 - 1) * (3*k1) * (k1 * k1 * k1) )
        M = M * (num / den)

        L += D(545140134)
        X *= C3
        SIGN = -SIGN

    pi = C / S
    return +pi  # apply context rounding

# ──────────────────────────────────────────────────────────────────────────────
# Δ(M) model (as in segmented_full_calc_proof.py), with iteration stats
# ──────────────────────────────────────────────────────────────────────────────
def make_constants(prec: int, chud_terms: int) -> Dict[str, D]:
    getcontext().prec = prec
    # Physical constants
    G     = D('6.67430e-11')
    c     = D('2.99792458e8')
    phi   = (D(1)+D(5).sqrt())/D(2)

    # π via Chudnovsky (for cache/reporting; Δ(M) here does not use π directly)
    t0 = time.time()
    pi_chud = chudnovsky_pi(chud_terms, prec)
    t1 = time.time()

    return {
        "G": G, "c": c, "phi": phi, "pi": pi_chud,
        "pi_ms": D(str((t1 - t0) * 1000.0)).quantize(D('1.000')),
        "C_rs": D(2) * G / (c**2),       # helper for r_s = C_rs * M
        "C_seg": (G * phi) / (c**2),     # helper for r_seg_base = C_seg * M
    }

# Δ(M) raw and normalized (same structure as your full script)
def delta_raw(M: D, G: D, c: D, A: D, alpha: D, B: D) -> D:
    rs = (D(2)*G*M)/(c**2)
    return A * (-(alpha*rs)).exp() + B

def build_log_norm_bounds(M_list) -> Tuple[D, D]:
    logs = [D(str(math.log10(m))) for m in M_list]
    return min(logs), max(logs)

def delta_percent(M: D, G: D, c: D, A: D, alpha: D, B: D, Lmin: D, Lmax: D) -> D:
    ΔL = Lmax - Lmin
    if ΔL == 0:
        return delta_raw(M, G, c, A, alpha, B)
    norm = (D(str(math.log10(M))) - Lmin) / ΔL
    return delta_raw(M, G, c, A, alpha, B) * norm

def f_eq(M: D, r_obs: D, const: Dict[str, D], A: D, alpha: D, B: D, Lmin: D, Lmax: D) -> D:
    G = const["G"]; c = const["c"]; phi = const["phi"]
    Δpct = delta_percent(M, G, c, A, alpha, B, Lmin, Lmax)
    return (G*phi*M/c**2) * (D(1) + Δpct/D(100)) - r_obs

def df_dM_numeric(M: D, r_obs: D, const: Dict[str, D], A: D, alpha: D, B: D, Lmin: D, Lmax: D) -> D:
    h = M*D('1e-25') if M != 0 else D('1e-25')
    return (f_eq(M+h, r_obs, const, A, alpha, B, Lmin, Lmax) -
            f_eq(M-h, r_obs, const, A, alpha, B, Lmin, Lmax)) / (D(2)*h)

def invert_mass(r_obs: D, M0: D, const: Dict[str, D], A: D, alpha: D, B: D, Lmin: D, Lmax: D,
                tol: D = D('1e-120'), max_iter: int = 200) -> Tuple[D, int]:
    """
    Newton with a refined initial guess: one fixed-point step using Δ(M0).
    Returns (M_rec, iterations).
    """
    G = const["G"]; c = const["c"]; phi = const["phi"]

    # Refinement of the initial guess (cheap fixed-point step)
    Δ0 = delta_percent(M0, G, c, A, alpha, B, Lmin, Lmax)
    denom = (G*phi/c**2) * (D(1) + Δ0/D(100))
    if denom != 0:
        M = r_obs / denom
    else:
        M = M0

    it = 0
    for it in range(1, max_iter+1):
        y = f_eq(M, r_obs, const, A, alpha, B, Lmin, Lmax)
        if abs(y) < tol:
            break
        dy = df_dM_numeric(M, r_obs, const, A, alpha, B, Lmin, Lmax)
        step = -y / dy if dy != 0 else -y
        # backtracking to avoid overshoot
        while abs(step) > abs(M) and step != 0:
            step *= D('0.5')
        M += step
        if M != 0 and abs(step/M) < tol:
            break
    return M, it

# ──────────────────────────────────────────────────────────────────────────────
# Demo dataset (as in your base lists)
# ──────────────────────────────────────────────────────────────────────────────
BASE = {
    'Elektron':        D('9.10938356e-31'),
    'Mond':            D('7.342e22'),
    'Erde':            D('5.97219e24'),
    'Sonne':           D('1.98847e30'),
    'Sagittarius A*':  D('4.297e6')*D('1.98847e30'),
}

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Segmented Δ(M) mass validation with Chudnovsky π cache")
    ap.add_argument("--prec", type=int, default=200, help="Decimal precision (digits)")
    ap.add_argument("--chud-terms", type=int, default=20, help="Chudnovsky terms (≈digits/14)")
    ap.add_argument("--A", type=str, default="98.01", help="Δ(M) A parameter (percent)")
    ap.add_argument("--alpha", type=str, default="2.7177e4", help="Δ(M) alpha parameter [1/m]")
    ap.add_argument("--B", type=str, default="1.96", help="Δ(M) B parameter (percent)")
    args = ap.parse_args()

    getcontext().prec = args.prec
    A = D(args.A); alpha = D(args.alpha); B = D(args.B)

    const = make_constants(args.prec, args.chud_terms)
    G = const["G"]; c = const["c"]; phi = const["phi"]
    pi_chud = const["pi"]

    # Build log-normalization bounds
    Ms = list(BASE.values())
    Lmin, Lmax = build_log_norm_bounds(Ms)

    # Header
    print("\n=============================================================")
    print(" SEGMENTED SPACETIME – Δ(M) + CHUDNOVSKY-π CACHE")
    print("=============================================================")
    print(f"Decimal precision  : {args.prec}")
    print(f"Chudnovsky terms   : {args.chud_terms}  (~ {args.chud_terms*14} digits rough)")
    print(f"π (Chudnovsky)     : {pi_chud}")
    print(f"π compute time     : {const['pi_ms']} ms")
    print(f"φ (sqrt formula)   : {phi}")
    print(f"C_rs (2G/c^2)      : {const['C_rs']}")
    print(f"C_seg (Gφ/c^2)     : {const['C_seg']}")
    print(f"Δ(M) params        : A={A}%, α={alpha} [1/m], B={B}%")
    print("-------------------------------------------------------------")
    print(f"{'Objekt':<20} {'M_true(kg)':>15} {'M_rec(kg)':>15} {'Δ%(true)':>10} {'iters':>5} {'RelErr%':>12}")
    print("-"*80)

    # Loop
    total_iters = 0
    for name, M_true in BASE.items():
        # Construct the "observed" segmented radius using the model itself
        r_s = D(2)*G*M_true/c**2
        Δpct_true = delta_percent(M_true, G, c, A, alpha, B, Lmin, Lmax)
        r_obs = (phi/D(2)) * r_s * (D(1) + Δpct_true/D(100))

        # Initial guess without Δ(M)
        M0 = (c**2) * r_obs / (G * phi)

        # Invert
        M_rec, iters = invert_mass(r_obs, M0, const, A, alpha, B, Lmin, Lmax)
        rel_err = abs((M_rec - M_true)/M_true) * D(100)
        total_iters += iters
        print(f"{name:<20} {M_true:15.6e} {M_rec:15.6e} {float(Δpct_true):10.3f} {iters:5d} {float(rel_err):12.3e}")

    print("-"*80)
    print(f"Avg Newton iterations: {total_iters/len(BASE):.2f}")
    print("Done. ✅")

if __name__ == "__main__":
    main()
