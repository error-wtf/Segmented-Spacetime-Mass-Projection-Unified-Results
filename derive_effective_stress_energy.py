
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
derive_effective_stress_energy.py

Compute the Einstein tensor G_{μν} and an *effective* stress-energy tensor
T_{μν} = (c^4 / 8πG) G_{μν} for the segmented-spacetime (SSZ) metric

    ds² = -A(r) c² dt² + B(r) dr² + r²(dθ² + sin²θ dφ²),
    A(U)=1 - 2U + 2U² + ε₃ U³,   B(r)=1/A(r),   U=GM/(rc²).

This does **not** provide a fundamental gravitational/matter action.
It reverse-engineers the stress-energy that would *source* the given metric.
Use it to inspect ρ, p_r, p_t, and ∇_μ T^{μ}{}_{ν}.

Usage examples:
    python derive_effective_stress_energy.py --M 1.98847e30 --eps3 -4.8 --r-mults 1.1,1.5,2,5,10
    python derive_effective_stress_energy.py --M 8.544456e36 --eps3 -4.8 --r-mults 1.2,2,3,5 --latex out_latex.txt

Author: ChatGPT (assistant) for user request
"""
import argparse
import math
from math import sin, cos
import sympy as sp

# ----------------------------------
# Symbols and metric specification
# ----------------------------------
t, r, th, ph = sp.symbols('t r theta phi', real=True)
Gc, cc, M, eps3 = sp.symbols('G c M eps3', positive=True, real=True)

U = Gc*M/(r*cc**2)
A = 1 - 2*U + 2*U**2 + eps3*U**3
B = sp.simplify(1/A)

coords = (t, r, th, ph)
g = sp.diag(-A*cc**2, B, r**2, r**2*sp.sin(th)**2)  # metric
g_inv = sp.simplify(g.inv())

def christoffel_symbols(metric, inv_metric, coordinates):
    n = len(coordinates)
    Gamma = [[ [sp.S(0)]*n for _ in range(n)] for __ in range(n)]
    # precompute derivatives
    dg = [[sp.diff(metric[i,j], coordinates[k]) for k in range(n)] for i in range(n) for j in range(n)]
    def dg_ijk(i,j,k): return dg[i*len(coordinates)+j][k]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                s = sp.S(0)
                for d in range(n):
                    s += inv_metric[a,d]*(dg_ijk(d,c,b) + dg_ijk(d,b,c) - dg_ijk(b,c,d))
                Gamma[a][b][c] = sp.simplify(sp.Rational(1,2)*s)
    return Gamma

def riemann_tensor(Gamma, coordinates):
    n = len(coordinates)
    R = [[[[sp.S(0)]*n for _ in range(n)] for __ in range(n)] for ___ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(n):
                    term = sp.diff(Gamma[a][b][d], coordinates[c]) - sp.diff(Gamma[a][b][c], coordinates[d])
                    s = sp.S(0)
                    for e in range(n):
                        s += Gamma[a][c][e]*Gamma[e][b][d] - Gamma[a][d][e]*Gamma[e][b][c]
                    R[a][b][c][d] = sp.simplify(term + s)
    return R

def ricci_tensor(Riemann):
    n = len(Riemann)
    Ric = [[sp.S(0) for _ in range(n)] for __ in range(n)]
    for a in range(n):
        for b in range(n):
            s = sp.S(0)
            for c in range(n):
                s += Riemann[c][a][c][b]
            Ric[a][b] = sp.simplify(s)
    return Ric

def scalar_curvature(Ric, inv_metric):
    n = len(Ric)
    Rsc = sp.S(0)
    for a in range(n):
        for b in range(n):
            Rsc += inv_metric[a,b]*Ric[a][b]
    return sp.simplify(Rsc)

def einstein_tensor(metric, inv_metric, coordinates):
    Gamma = christoffel_symbols(metric, inv_metric, coordinates)
    Riem = riemann_tensor(Gamma, coordinates)
    Ric = ricci_tensor(Riem)
    Rsc = scalar_curvature(Ric, inv_metric)
    n = len(coordinates)
    Gmn = [[sp.simplify(Ric[i][j] - sp.Rational(1,2)*metric[i,j]*Rsc) for j in range(n)] for i in range(n)]
    return Gmn, Gamma, Rsc

# Compute tensors
Gmn, Gamma, Rsc = einstein_tensor(g, g_inv, coords)

# Effective stress-energy: T_{μν} = (c^4 / 8πG) G_{μν}
pref = cc**4/(8*sp.pi*Gc)
Tmn = [[sp.simplify(pref*Gmn[i][j]) for j in range(4)] for i in range(4)]

# Extract fluid interpretation for static spherical: diag(-ρ c², p_r, p_t, p_t)
rho = sp.simplify(-Tmn[0][0]/(cc**2))           # energy density
p_r = sp.simplify(Tmn[1][1])                    # radial pressure
p_t = sp.simplify(Tmn[2][2])                    # tangential pressure

# Mixed tensor and covariant divergence ∇_μ T^{μ}{}_ν
T_updown = [[sp.S(0) for _ in range(4)] for __ in range(4)]
for mu in range(4):
    for nu in range(4):
        s = sp.S(0)
        for alpha in range(4):
            s += g_inv[mu,alpha]*Tmn[alpha][nu]
        T_updown[mu][nu] = sp.simplify(s)

def covariant_divergence_T(T_updown, Gamma, coordinates):
    # (∇_μ T^{μ}{}_ν) = ∂_μ T^{μ}{}_ν + Γ^{μ}_{μα} T^{α}{}_ν - Γ^{α}_{μν} T^{μ}{}_α
    n = len(coordinates)
    div = [sp.S(0) for _ in range(n)]
    for nu in range(n):
        term = sp.S(0)
        for mu in range(n):
            term += sp.diff(T_updown[mu][nu], coordinates[mu])
            # Γ^{μ}_{μα} T^{α}{}_ν
            s1 = sp.S(0)
            for alpha in range(n):
                s1 += Gamma[mu][mu][alpha]*T_updown[alpha][nu]
            # - Γ^{α}_{μν} T^{μ}{}_α
            s2 = sp.S(0)
            for alpha in range(n):
                s2 -= Gamma[alpha][mu][nu]*T_updown[mu][alpha]
            term += s1 + s2
        div[nu] = sp.simplify(term)
    return div

divT = covariant_divergence_T(T_updown, Gamma, coords)

def main():
    ap = argparse.ArgumentParser(description="Effective stress-energy for SSZ metric (no fundamental action).")
    ap.add_argument("--M", type=float, required=True, help="Mass [kg]")
    ap.add_argument("--eps3", type=float, default=-4.8, help="epsilon_3 in A(U)")
    ap.add_argument("--G", type=float, default=6.67430e-11, help="Newton G")
    ap.add_argument("--c", type=float, default=299792458.0, help="speed of light")
    ap.add_argument("--r-mults", type=str, default="1.2,2,3,5,10", help="comma list of r/r_s to evaluate")
    ap.add_argument("--latex", type=str, default="", help="optional path to dump latex for rho, p_r, p_t")
    args = ap.parse_args()

    subs = {Gc: args.G, cc: args.c, M: args.M, eps3: args.eps3}
    rs = 2*args.G*args.M/(args.c**2)  # Schwarzschild radius

    print("="*90)
    print("SSZ Effective Stress-Energy (reverse engineered)")
    print("="*90)
    print(f"M = {args.M:.6e} kg | eps3 = {args.eps3} | r_s = {rs:.6e} m\n")

    # Symbolic summaries
    print("[Symbolic] rho(r), p_r(r), p_t(r) (compact forms):")
    print("rho(r) =", sp.simplify(rho.subs({Gc:sp.Symbol('G'), cc:sp.Symbol('c')})))
    print("p_r(r) =", sp.simplify(p_r.subs({Gc:sp.Symbol('G'), cc:sp.Symbol('c')})))
    print("p_t(r) =", sp.simplify(p_t.subs({Gc:sp.Symbol('G'), cc:sp.Symbol('c')})))
    print()

    if args.latex:
        with open(args.latex, "w", encoding="utf-8") as f:
            f.write(sp.latex(sp.simplify(rho)) + "\n")
            f.write(sp.latex(sp.simplify(p_r)) + "\n")
            f.write(sp.latex(sp.simplify(p_t)) + "\n")
        print(f"[OK] LaTeX dumped to: {args.latex}\n")

    rmults = [float(x.strip()) for x in args.r_mults.split(",") if x.strip()]
    print("r/rs        rho [J/m^3]             p_r [Pa]                 p_t [Pa]          |∇·T| components")
    print("-"*90)
    for mval in rmults:
        rval = mval*rs
        numsubs = subs | {r: rval, th: math.pi/2, ph: 0.0, t: 0.0}
        rho_v = float(sp.N(rho.subs(numsubs)))
        pr_v  = float(sp.N(p_r.subs(numsubs)))
        pt_v  = float(sp.N(p_t.subs(numsubs)))
        # Check divergence numerically
        div_vals = [float(sp.N(d.subs(numsubs))) for d in divT]
        norm_div = math.sqrt(sum(abs(x)**2 for x in div_vals))
        print(f"{mval:5.2f}  {rho_v: .6e}   {pr_v: .6e}   {pt_v: .6e}   ||∇·T||={norm_div: .3e}")

    print("\nNote: This script reconstructs an *effective* T_{μν} for the chosen metric. "
          "It does not specify a fundamental action nor field equations for matter.\n")

if __name__ == "__main__":
    main()
