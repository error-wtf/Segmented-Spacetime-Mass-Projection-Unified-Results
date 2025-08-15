
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chudnovsky‑π + Segmented‑Spacetime Δ(M) — Unified Pipeline
==========================================================
- Computes π via Chudnovsky (Decimal; configurable precision/terms)
- Caches constants (π, φ, 2G/c², Gφ/c²)
- Uses analytic derivative for Δ(M) Newton‑Inversion (faster than numeric diff)
- Validates masses (electron + Solar System + Sgr A*) with tiny rel. error

© 2025 Carmen Wrede & Lino Casu · Bridge prototype by Akira
License: MIT
"""

from __future__ import annotations
import argparse, math, time
from decimal import Decimal as D, getcontext
from typing import Dict, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Chudnovsky π (iterative Decimal version; simple and sufficiently fast for 1e3–1e4 dps)
# For ultra‑high precision, consider binary‑splitting with pure integers.
# ──────────────────────────────────────────────────────────────────────────────
def chudnovsky_pi(n_terms: int, prec: int) -> D:
    getcontext().prec = prec
    # C = 426880 * sqrt(10005)
    sqrt10005 = getcontext().sqrt(D(10005))
    C = D(426880) * sqrt10005

    S = D(0)
    M = D(1)                   # ratio of factorials (6k)!/( (3k)!(k!)^3 ), updated iteratively
    L = D(13591409)
    X = D(1)
    SIGN = 1
    C3 = D(640320) ** 3

    for k in range(n_terms):
        term = (M * L) / X
        S += term if SIGN > 0 else -term

        # Update to k+1 without factorials:
        k1 = k + 1
        num = D( (6*k1 - 5) * (6*k1 - 4) * (6*k1 - 3) * (6*k1 - 2) * (6*k1 - 1) * (6*k1) )
        den = D( (3*k1 - 2) * (3*k1 - 1) * (3*k1) * (k1 * k1 * k1) )
        M = M * (num / den)

        L += D(545140134)
        X *= C3
        SIGN = -SIGN

    pi = C / S
    return +pi  # context rounding

# ──────────────────────────────────────────────────────────────────────────────
# Δ(M) model with analytic derivative
# ──────────────────────────────────────────────────────────────────────────────
def make_constants(prec: int, chud_terms: int) -> Dict[str, D]:
    getcontext().prec = prec
    G   = D('6.67430e-11')
    c   = D('2.99792458e8')
    phi = (D(1)+D(5).sqrt())/D(2)

    t0 = time.time()
    pi_chud = chudnovsky_pi(chud_terms, prec)
    t1 = time.time()

    K_rs  = D(2) * G / (c*c)      # r_s = K_rs * M
    K_seg = (G * phi) / (c*c)     # segment base radius factor

    return {
        "G": G, "c": c, "phi": phi, "pi": pi_chud,
        "pi_ms": D(str((t1 - t0) * 1000.0)).quantize(D('1.000')),
        "K_rs": K_rs, "K_seg": K_seg,
        "LN10": D(str(math.log(10.0)))  # Decimal ln(10) via float bridge (adequate)
    }

def build_log_bounds(M_list) -> Tuple[D, D]:
    logs = [D(str(math.log10(m))) for m in M_list]
    return min(logs), max(logs)

def delta_components(M: D, A: D, alpha: D, B: D, K_rs: D, Lmin: D, Lmax: D, LN10: D):
    """Return (delta_percent, raw_delta, norm, exp_term) for reuse."""
    rs = K_rs * M
    exp_term = (-alpha * rs).exp()             # e^{-α r_s}
    raw_delta = A * exp_term + B               # A e^{-α r_s} + B
    ΔL = (Lmax - Lmin)
    norm = (D(str(math.log10(M))) - Lmin) / ΔL if ΔL != 0 else D(1)
    delta_pct = raw_delta * norm               # Δ%
    return delta_pct, raw_delta, norm, exp_term

def delta_prime(M: D, A: D, alpha: D, B: D, K_rs: D, Lmin: D, Lmax: D, LN10: D) -> D:
    """
    Analytic derivative d/dM [Δ%(M)] with
      Δ%(M) = (A e^{-α K_rs M} + B) * ((log10 M - Lmin)/(Lmax - Lmin))
    """
    ΔL = (Lmax - Lmin)
    if ΔL == 0:
        # Only raw term changes with M
        exp_term = (-alpha * K_rs * M).exp()
        return A * exp_term * (-alpha * K_rs)

    # Pieces
    exp_term = (-alpha * K_rs * M).exp()
    raw_delta = A * exp_term + B
    norm = (D(str(math.log10(M))) - Lmin) / ΔL

    # d/dM raw_delta = A e^{-α K_rs M} * (-α K_rs)
    d_raw = A * exp_term * (-alpha * K_rs)

    # d/dM norm = (1 / (M ln 10)) / ΔL
    d_norm = (D(1) / (M * LN10)) / ΔL

    return d_raw * norm + raw_delta * d_norm

def f_eq(M: D, r_obs: D, const: Dict[str, D], A: D, alpha: D, B: D, Lmin: D, Lmax: D) -> D:
    K_seg = const["K_seg"]; K_rs = const["K_rs"]; LN10 = const["LN10"]
    delta_pct, _, _, _ = delta_components(M, A, alpha, B, K_rs, Lmin, Lmax, LN10)
    return K_seg * M * (D(1) + delta_pct/D(100)) - r_obs

def fprime_eq(M: D, const: Dict[str, D], A: D, alpha: D, B: D, Lmin: D, Lmax: D) -> D:
    K_seg = const["K_seg"]; K_rs = const["K_rs"]; LN10 = const["LN10"]
    delta_pct = delta_components(M, A, alpha, B, K_rs, Lmin, Lmax, LN10)[0]
    d_delta   = delta_prime(M, A, alpha, B, K_rs, Lmin, Lmax, LN10)
    return K_seg * (D(1) + delta_pct/D(100)) + K_seg * M * (d_delta/D(100))

def invert_mass(r_obs: D, M0: D, const: Dict[str, D], A: D, alpha: D, B: D, Lmin: D, Lmax: D,
                tol: D, max_iter: int = 100) -> Tuple[D, int]:
    M = M0
    it = 0
    for it in range(1, max_iter+1):
        y  = f_eq(M, r_obs, const, A, alpha, B, Lmin, Lmax)
        if abs(y) < tol:
            break
        dy = fprime_eq(M, const, A, alpha, B, Lmin, Lmax)
        step = -y / dy if dy != 0 else -y
        # gentle damping
        if M != 0 and abs(step/M) > D('0.5'):
            step = step * D('0.5')
        M = M + step
        if M != 0 and abs(step/M) < tol:
            break
    return M, it

# ──────────────────────────────────────────────────────────────────────────────
# Demo dataset
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
    ap = argparse.ArgumentParser(description="Chudnovsky‑π + Segmented‑Spacetime Δ(M) unified validation")
    ap.add_argument("--prec", type=int, default=200, help="Decimal precision (digits)")
    ap.add_argument("--chud-terms", type=int, default=16, help="Chudnovsky terms (≈ 14 digits/term)")
    ap.add_argument("--A", type=str, default="98.01", help="Δ(M) parameter A (percent)")
    ap.add_argument("--alpha", type=str, default="2.7177e4", help="Δ(M) parameter alpha [1/m]")
    ap.add_argument("--B", type=str, default="1.96", help="Δ(M) parameter B (percent)")
    ap.add_argument("--tol", type=str, default="1e-120", help="Newton tolerance (relative)")
    args = ap.parse_args()

    getcontext().prec = args.prec
    A = D(args.A); alpha = D(args.alpha); B = D(args.B); tol = D(args.tol)

    const = make_constants(args.prec, args.chud_terms)
    Ms = list(BASE.values())
    Lmin, Lmax = build_log_bounds(Ms)

    print("\n=============================================================")
    print(" CHUDNOVSKY‑π + SEGMENTED‑SPACETIME  Δ(M)  —  VALIDATION")
    print("=============================================================")
    print(f"Decimal precision  : {args.prec}")
    print(f"Chudnovsky terms   : {args.chud_terms}  (~ {args.chud_terms*14} digits)")
    print(f"π (Chudnovsky)     : {const['pi']}")
    print(f"π compute time     : {const['pi_ms']} ms")
    print(f"φ (sqrt formula)   : {const['phi']}")
    print(f"K_rs = 2G/c²       : {const['K_rs']}")
    print(f"K_seg= Gφ/c²       : {const['K_seg']}")
    print(f"Δ(M) params        : A={A}%, α={alpha} [1/m], B={B}%, tol={tol}")
    print("-------------------------------------------------------------")
    print(f"{'Objekt':<20} {'M_true(kg)':>15} {'M_rec(kg)':>15} {'Δ%(true)':>10} {'iters':>5} {'RelErr%':>12}")
    print("-"*85)

    total_iters = 0
    for name, M_true in BASE.items():
        # Build r_obs from the forward model (ground truth path)
        K_rs  = const['K_rs']
        K_seg = const['K_seg']
        LN10  = const['LN10']

        rs = K_rs * M_true
        # Δ%(true)
        delta_pct_true, _, _, _ = delta_components(M_true, A, alpha, B, K_rs, Lmin, Lmax, LN10)
        r_obs = (K_seg * M_true) * (D(1) + delta_pct_true/D(100))

        # Initial guess: ignore Δ(M)
        M0 = r_obs / K_seg

        M_rec, iters = invert_mass(r_obs, M0, const, A, alpha, B, Lmin, Lmax, tol)
        rel_err = abs((M_rec - M_true)/M_true) * D(100)
        total_iters += iters

        print(f"{name:<20} {M_true:15.6e} {M_rec:15.6e} {float(delta_pct_true):10.3f} {iters:5d} {float(rel_err):12.3e}")

    print("-"*85)
    print(f"Avg Newton iterations: {total_iters/len(BASE):.2f}")
    print("Done. ✅")

if __name__ == "__main__":
    main()
