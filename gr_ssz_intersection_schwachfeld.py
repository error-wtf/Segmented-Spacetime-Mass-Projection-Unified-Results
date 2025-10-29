#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GR-SSZ Intersection - Schwachfeld Model

From ChatGPT prompt (the working model):
Xi(r) = min(Xi_max, alpha * r_s/(2r))
D_SSZ = 1 / (1 + Xi)

© 2025 Carmen Wrede & Lino Casu
"""
import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

PHI = (1 + np.sqrt(5)) / 2
G = 6.67430e-11
c = 299792458.0
M_sun = 1.98847e30

cfg = {
    "phi": PHI,
    "Xi_max": 0.802,
    "alpha": 1.0,
    "masses_Msun": [2.0, 4.1e6],
    "outdir": "outputs_intersection"
}

os.makedirs(cfg["outdir"], exist_ok=True)

print("="*80)
print("GR-SSZ INTERSECTION - SCHWACHFELD MODEL")
print("="*80)
print(f"Xi(r) = min(Xi_max, alpha * r_s/(2r))")
print(f"D_SSZ = 1 / (1 + Xi)")
print(f"Xi_max = {cfg['Xi_max']}, alpha = {cfg['alpha']}")
print()

def rs_from_mass(M):
    return 2*G*M/c**2

def D_GR(r, rs):
    x = 1.0 - (rs/np.asarray(r))
    x = np.clip(x, 0.0, None)
    return np.sqrt(x)

def Xi_schwachfeld(r, rs, Xi_max, alpha):
    """
    Schwachfeld model:
    Xi(r) = min(Xi_max, alpha * r_s / (2r))
    
    This gives Xi ~ GM/(rc^2) in weak field
    """
    Xi_uncut = alpha * rs / (2.0 * np.asarray(r))
    return np.minimum(Xi_uncut, Xi_max)

def D_SSZ(r, rs, Xi_max, alpha):
    Xi = Xi_schwachfeld(r, rs, Xi_max, alpha)
    return 1.0 / (1.0 + Xi)

def diff_D(r, rs, Xi_max, alpha):
    return D_GR(r, rs) - D_SSZ(r, rs, Xi_max, alpha)

report = {
    "config": cfg,
    "expected": {
        "r_star_over_rs": 1.386562,
        "D_star": 0.528007
    },
    "cases": []
}

for M_Msun in cfg["masses_Msun"]:
    M = M_Msun * M_sun
    rs = rs_from_mass(M)
    rmin = 1.01*rs
    rmax = 10.0*rs
    
    print(f"[CASE] M = {M_Msun} M_sun, r_s = {rs:.3e} m")
    
    f = lambda rr: diff_D(rr, rs, cfg["Xi_max"], cfg["alpha"])
    
    # Scan
    r_scan = np.linspace(rmin, rmax, 20000)
    vals = f(r_scan)
    s = np.sign(vals)
    idx = np.where(s[:-1]*s[1:] <= 0)[0]
    
    if len(idx) > 0:
        i = idx[0]
        r0, r1 = r_scan[i], r_scan[i+1]
        root = brentq(f, r0, r1, xtol=1e-10)
        
        Dgr_star = float(D_GR(root, rs))
        Dssz_star = float(D_SSZ(root, rs, cfg["Xi_max"], cfg["alpha"]))
        Xi_star = float(Xi_schwachfeld(root, rs, cfg["Xi_max"], cfg["alpha"]))
        
        print(f"  FOUND: r*/r_s = {root/rs:.6f}")
        print(f"         D* = {Dgr_star:.6f}")
        print(f"         Xi* = {Xi_star:.6f}")
        print(f"  Expected: r*/r_s = {report['expected']['r_star_over_rs']}")
        print(f"            D* = {report['expected']['D_star']}")
        
        dev_r = abs(root/rs - report["expected"]["r_star_over_rs"])
        dev_D = abs(Dgr_star - report["expected"]["D_star"])
        
        if dev_r < 0.01 and dev_D < 0.01:
            print(f"  [OK] MATCH!")
        else:
            print(f"  [WARN] Dev: |Dr| = {dev_r:.6f}, |DD| = {dev_D:.6f}")
        
        case = {
            "M_Msun": M_Msun,
            "r_star_over_rs": float(root/rs),
            "D_star": Dgr_star,
            "Xi_star": Xi_star,
            "deviation_r": dev_r,
            "deviation_D": dev_D
        }
    else:
        print(f"  [ERROR] No intersection found")
        case = {"M_Msun": M_Msun, "error": "no_intersection"}
    
    print()
    report["cases"].append(case)
    
    # Plot
    r_plot = np.linspace(1.0*rs, 5.0*rs, 4000)
    Dgr = D_GR(r_plot, rs)
    Dssz = D_SSZ(r_plot, rs, cfg["Xi_max"], cfg["alpha"])
    Xi_plot = Xi_schwachfeld(r_plot, rs, cfg["Xi_max"], cfg["alpha"])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=200)
    
    # D(r)
    ax1.plot(r_plot/rs, Dgr, label="GR", lw=2.2, color='blue')
    ax1.plot(r_plot/rs, Dssz, label="SSZ (Schwachfeld)", lw=2.2, color='red')
    if 'r_star_over_rs' in case:
        ax1.axvline(case['r_star_over_rs'], color="gray", ls="--", lw=1.2)
        ax1.plot([case['r_star_over_rs']], [case['D_star']], "o", color="green", ms=8)
    ax1.set_xlabel("$r / r_s$")
    ax1.set_ylabel("$D(r)$")
    ax1.set_title(f"Time Dilation - M = {M_Msun} $M_\\odot$")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Xi(r)
    ax2.plot(r_plot/rs, Xi_plot, lw=2.2, color='purple')
    ax2.axhline(cfg["Xi_max"], color="gray", ls="--", lw=1.0, label=f"Xi_max = {cfg['Xi_max']}")
    if 'r_star_over_rs' in case:
        ax2.axvline(case['r_star_over_rs'], color="green", ls="--", lw=1.2)
        ax2.plot([case['r_star_over_rs']], [case['Xi_star']], "o", color="green", ms=8)
    ax2.set_xlabel("$r / r_s$")
    ax2.set_ylabel("$\\Xi(r)$")
    ax2.set_title(f"Segment Density")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    png_path = os.path.join(cfg["outdir"], f"gr_ssz_schwachfeld_M{M_Msun:.6g}Msun.png")
    fig.savefig(png_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {png_path}")

# JSON
json_path = os.path.join(cfg["outdir"], "gr_ssz_schwachfeld_report.json")
with open(json_path, "w") as fj:
    json.dump(report, fj, indent=2)

print("="*80)
print("COMPLETE!")
print("="*80)
