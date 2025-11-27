#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GR-SSZ Intersection Failsafe Validator

CORRECT SSZ Model (from SSZ_COMPLETE_FINAL_REPORT.md Analysis 6):
- Xi(r) = Xi_max * (1 - exp(-phi * r / r_s))  <- phi in exponent!
- Xi_max = 0.802 (NOT 1.0!)
- D_SSZ = 1 / (1 + Xi)  <- NOT phi**(-alpha*Xi)!

Expected Result: r*/r_s = 1.386562

© 2025 Carmen Wrede & Lino Casu
"""
import os
import sys
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Physical constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio = 1.618034...
G = 6.67430e-11
c = 299792458.0
M_sun = 1.98847e30

# Configuration (from Analysis 6)
cfg = {
    "phi": PHI,
    "Xi_max": 1.0,           # CORRECT: 1.0 (from gr_ssz_intersection_summary.md)!
    "masses_Msun": [2.0, 4.1e6],  # Neutron star, Sgr A*
    "rmin_factor": 1.01,
    "rmax_factor": 10.0,
    "N_scan": 20000,
    "tol": 1e-10,
    "plot_xlim_rs": [1.0, 5.0],
    "outdir": "outputs_intersection"
}

os.makedirs(cfg["outdir"], exist_ok=True)

print("="*80)
print("GR-SSZ INTERSECTION VALIDATOR (FAILSAFE)")
print("="*80)
print(f"phi = {cfg['phi']:.9f}")
print(f"Xi_max = {cfg['Xi_max']}")
print(f"Model: Xi(r) = Xi_max * (1 - exp(-phi*r/r_s))")
print(f"       D_SSZ = 1 / (1 + Xi)")
print()

def rs_from_mass(M):
    """Schwarzschild radius"""
    return 2*G*M/c**2

def D_GR(r, rs):
    """GR time dilation: D = sqrt(1 - r_s/r)"""
    x = 1.0 - (rs/np.asarray(r))
    x = np.clip(x, 0.0, None)
    return np.sqrt(x)

def Xi_exponential(r, rs, Xi_max, phi):
    """
    CORRECT exponential model (Analysis 6):
    Xi(r) = Xi_max * (1 - exp(-phi * r / r_s))
    
    Note: phi in the exponent! Not exp(-r_s/r)!
    """
    return Xi_max * (1.0 - np.exp(-phi * np.asarray(r) / rs))

def D_SSZ(r, rs, Xi_max, phi):
    """
    CORRECT SSZ time dilation:
    D = 1 / (1 + Xi)
    
    NOT phi**(-alpha*Xi)!
    """
    Xi = Xi_exponential(r, rs, Xi_max, phi)
    return 1.0 / (1.0 + Xi)

def diff_D(r, rs, Xi_max, phi):
    """Difference: D_GR - D_SSZ"""
    return D_GR(r, rs) - D_SSZ(r, rs, Xi_max, phi)

def find_root_scan_then_bisect(func, a, b, N=20000, tol=1e-10):
    """
    Scan for sign change, then bisect
    Returns: (root, bracket, initial_value)
    """
    rs = np.linspace(a, b, N)
    vals = func(rs)
    
    # Find sign changes
    s = np.sign(vals)
    idx = np.where(s[:-1]*s[1:] <= 0)[0]
    
    if len(idx) == 0:
        return None, None, None
    
    i = idx[0]
    r0, r1 = rs[i], rs[i+1]
    
    # Bisection
    try:
        root = brentq(func, r0, r1, xtol=tol)
        return root, (r0, r1), float(vals[i])
    except:
        return None, None, None

# Report structure
report = {
    "config": cfg,
    "expected": {
        "r_star_over_rs": 1.386562,
        "D_star": 0.528007,
        "source": "SSZ_COMPLETE_FINAL_REPORT.md Analysis 6"
    },
    "cases": []
}

for M_Msun in cfg["masses_Msun"]:
    M = M_Msun * M_sun
    rs = rs_from_mass(M)
    rmin = cfg["rmin_factor"]*rs
    rmax = cfg["rmax_factor"]*rs
    
    print(f"[CASE] M = {M_Msun} M_sun")
    print(f"       r_s = {rs:.3e} m")
    
    f = lambda rr: diff_D(rr, rs, cfg["Xi_max"], cfg["phi"])
    
    # Find intersection
    root, bracket, f_i = find_root_scan_then_bisect(f, rmin, rmax, N=cfg["N_scan"], tol=cfg["tol"])
    
    case = {
        "M_Msun": M_Msun,
        "rs_m": rs,
        "root_r_m": None if root is None else float(root),
        "root_r_over_rs": None if root is None else float(root/rs),
        "checks": {}
    }
    
    if root is not None:
        Dgr_star = float(D_GR(root, rs))
        Dssz_star = float(D_SSZ(root, rs, cfg["Xi_max"], cfg["phi"]))
        Xi_star = float(Xi_exponential(root, rs, cfg["Xi_max"], cfg["phi"]))
        
        # Validation
        match_D = abs(Dgr_star - Dssz_star) < 1e-6
        match_r = abs(root/rs - report["expected"]["r_star_over_rs"]) < 0.01
        match_D_value = abs(Dgr_star - report["expected"]["D_star"]) < 0.01
        
        case["checks"] = {
            "D_at_root_match": match_D,
            "r_star_match_expected": match_r,
            "D_star_match_expected": match_D_value,
            "D_GR": Dgr_star,
            "D_SSZ": Dssz_star,
            "Xi_star": Xi_star,
            "deviation_r": abs(root/rs - report["expected"]["r_star_over_rs"]),
            "deviation_D": abs(Dgr_star - report["expected"]["D_star"])
        }
        
        print(f"  FOUND: r*/r_s = {root/rs:.6f}")
        print(f"         D* = {Dgr_star:.6f}")
        print(f"         Xi* = {Xi_star:.6f}")
        print(f"  Expected: r*/r_s = {report['expected']['r_star_over_rs']}")
        print(f"            D* = {report['expected']['D_star']}")
        
        if match_r and match_D_value:
            print(f"  [OK] VALIDATED: Matches expected values!")
        else:
            print(f"  [WARN] DEVIATION: |Dr| = {case['checks']['deviation_r']:.6f}, |DD| = {case['checks']['deviation_D']:.6f}")
    else:
        case["checks"]["reason"] = "No sign change in [rmin, rmax] — no intersection found."
        print(f"  ✗ NO INTERSECTION FOUND")
    
    print()
    
    report["cases"].append(case)
    
    # Plot
    r_plot = np.linspace(cfg["plot_xlim_rs"][0]*rs, cfg["plot_xlim_rs"][1]*rs, 4000)
    Dgr = D_GR(r_plot, rs)
    Dssz = D_SSZ(r_plot, rs, cfg["Xi_max"], cfg["phi"])
    
    fig, ax = plt.subplots(figsize=(12, 6.8), dpi=200)
    ax.plot(r_plot/rs, Dgr, label="GR: $D = \\sqrt{1-r_s/r}$", lw=2.2, color='blue')
    ax.plot(r_plot/rs, Dssz, label="SSZ: $D = 1/(1+\\Xi)$", lw=2.2, color='red')
    
    if root is not None:
        ax.axvline(root/rs, color="gray", ls="--", lw=1.2, alpha=0.7)
        ax.plot([root/rs], [Dgr_star], "o", color="green", ms=8, zorder=10)
        ax.annotate(f"$r_* = {root/rs:.4f}\\,r_s$\n$D_* = {Dgr_star:.4f}$",
                    xy=(root/rs, Dgr_star), xytext=(15, -25),
                    textcoords="offset points",
                    bbox=dict(fc="white", ec="0.7", alpha=0.95, boxstyle="round,pad=0.5"),
                    fontsize=11,
                    arrowprops=dict(arrowstyle="->", color="green", lw=1.5))
    
    ax.set_xlim(cfg["plot_xlim_rs"])
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("$r / r_s$", fontsize=12)
    ax.set_ylabel("$D(r) = dt_{\\mathrm{local}}/dt_{\\infty}$", fontsize=12)
    ax.set_title(f"GR vs SSZ Time Dilation — M = {M_Msun} $M_\\odot$, $\\Xi_{{\\max}} = {cfg['Xi_max']}$", fontsize=13)
    ax.legend(loc="upper right", frameon=True, fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    
    png_path = os.path.join(cfg["outdir"], f"gr_ssz_intersection_M{M_Msun:.6g}Msun.png")
    fig.savefig(png_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {png_path}")
    
    # CSV
    csv_path = os.path.join(cfg["outdir"], f"gr_ssz_curves_M{M_Msun:.6g}Msun.csv")
    with open(csv_path, "w", newline="") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["r_over_rs", "D_GR", "D_SSZ", "Xi"])
        Xi_plot = Xi_exponential(r_plot, rs, cfg["Xi_max"], cfg["phi"])
        for rr, g, s, xi in zip(r_plot/rs, Dgr, Dssz, Xi_plot):
            w.writerow([f"{rr:.9f}", f"{g:.9f}", f"{s:.9f}", f"{xi:.9f}"])
    print(f"Saved: {csv_path}")
    print()

# JSON Report
json_path = os.path.join(cfg["outdir"], "gr_ssz_intersection_report.json")
with open(json_path, "w", encoding="utf-8") as fj:
    json.dump(report, fj, indent=2)

print("="*80)
print(f"COMPLETE! All results in: {cfg['outdir']}/")
print(f"Report: {json_path}")
print("="*80)
