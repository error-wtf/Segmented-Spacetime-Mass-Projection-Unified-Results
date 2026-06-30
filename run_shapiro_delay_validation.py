#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shapiro Delay Proxy – GR vs SSZ (weak-field vs path integral)

Tests gravitational time delay for light passing near a massive object.
GR: Classical weak-field Shapiro formula (log term)
SSZ: Path integral over effective refractive index n(r) = 1/D(r)

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import json
import csv
import math
import numpy as np
import matplotlib.pyplot as plt

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Physical constants
G = 6.67430e-11
c = 299792458.0
M_sun = 1.98847e30
PHI = (1 + np.sqrt(5)) / 2

# Configuration
cfg = {
    'masses_Msun': [2.0, 4.1e6],  # Neutron star, Sgr A*
    'rmin_factor': 1.05,
    'rmax_factor': 200.0,
    'impact_params_rs': [1.2, 1.5, 2.0, 3.0, 5.0, 10.0],
    'N_path': 200000,
    'Xi_max': 1.0,
    'alpha': 1.0,
    'phi': PHI,
    'outdir': 'outputs_shapiro_proxy'
}

os.makedirs(cfg['outdir'], exist_ok=True)

print("="*80)
print("SHAPIRO DELAY PROXY - GR VS SSZ")
print("="*80)
print(f"Configuration:")
print(f"  Xi_max = {cfg['Xi_max']}")
print(f"  alpha = {cfg['alpha']}")
print(f"  phi = {cfg['phi']:.6f}")
print(f"  N_path = {cfg['N_path']} (path integration points)")
print()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def rs_from_mass(M):
    """Schwarzschild radius"""
    return 2 * G * M / c**2

def D_GR(r, rs):
    """GR time dilation: D = sqrt(1 - r_s/r)"""
    x = 1.0 - (rs / np.asarray(r))
    x = np.clip(x, 0.0, None)
    return np.sqrt(x)

def Xi_of_r(r, rs, Xi_max, alpha, phi):
    """SSZ segment density (exponential model):
    Xi(r) = Xi_max * (1 - exp(-phi * r_s / r))
    """
    return Xi_max * (1.0 - np.exp(-phi * np.asarray(r) / rs))

def D_SSZ(r, rs, Xi_max, alpha):
    """SSZ time dilation: D = 1/(1 + Xi)"""
    return 1.0 / (1.0 + Xi_of_r(r, rs, Xi_max, alpha, PHI))

def shapiro_GR(M, rE, rR, b):
    """GR Shapiro delay (weak-field approximation):
    Delta_t = (2GM/c^3) * ln(4*r_E*r_R / b^2)
    
    rE, rR: distances of emitter/receiver from mass center
    b: impact parameter
    """
    if b <= 0:
        return np.nan
    return (2 * G * M / c**3) * math.log((4.0 * rE * rR) / (b * b))

def shapiro_SSZ_proxy(M, rs, b, Xmax, N, Xi_max, alpha):
    """SSZ Shapiro delay via path integral:
    
    Integrate along straight path with impact parameter b.
    Coordinate x from -Xmax to +Xmax, r(x) = sqrt(x^2 + b^2).
    
    Time delay = integral of (n(r)-1)/c * dx
    where n(r) = 1/D(r) is effective refractive index
    """
    x = np.linspace(-Xmax, Xmax, N)
    r = np.sqrt(x*x + b*b)
    D = D_SSZ(r, rs, Xi_max, alpha)
    n_eff = 1.0 / np.clip(D, 1e-15, None)
    
    # Extra time = integral of (n-1)/c dx
    extra = np.trapz(n_eff - 1.0, x) / c
    return extra

# ============================================================================
# MAIN VALIDATION
# ============================================================================

report = {
    'config': cfg,
    'cases': []
}

for M_Msun in cfg['masses_Msun']:
    M = M_Msun * M_sun
    rs = rs_from_mass(M)
    rE = cfg['rmax_factor'] * rs
    rR = cfg['rmax_factor'] * rs
    
    print(f"[CASE] M = {M_Msun} M_sun, r_s = {rs:.3e} m")
    
    rows = []
    for b_rs in cfg['impact_params_rs']:
        b = b_rs * rs
        
        # Safety: b > rmin
        if b <= cfg['rmin_factor'] * rs:
            print(f"  [SKIP] b/r_s = {b_rs} (too close to horizon)")
            continue
        
        # Symmetric path: -Xmax to +Xmax
        # Xmax chosen so r ~ sqrt(x^2 + b^2) reaches rmax
        Xmax = math.sqrt(max((cfg['rmax_factor']*rs)**2 - b*b, (50*rs)**2))
        
        dGR = shapiro_GR(M, rE, rR, b)
        dSSZ = shapiro_SSZ_proxy(M, rs, b, Xmax, cfg['N_path'], 
                                  cfg['Xi_max'], cfg['alpha'])
        
        rows.append([b_rs, dGR, dSSZ, dSSZ - dGR])
        
        print(f"  b/r_s = {b_rs:5.1f}: Delta_t_GR = {dGR:.6e} s, "
              f"Delta_t_SSZ = {dSSZ:.6e} s, diff = {(dSSZ-dGR):.6e} s")
    
    # Save CSV
    csv_path = os.path.join(cfg['outdir'], f'shapiro_proxy_M{M_Msun:.6g}.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['b/rs', 'Delta_t_GR[s]', 'Delta_t_SSZ_proxy[s]', 'diff[s]'])
        w.writerows(rows)
    print(f"  [OK] Saved {csv_path}")
    
    # Plot
    if rows:
        data = np.array(rows)
        fig, ax = plt.subplots(figsize=(11, 6.5), dpi=200)
        ax.plot(data[:, 0], data[:, 1], 'o-', label='GR (weak-field log)', 
                lw=2.2, ms=6, color='blue')
        ax.plot(data[:, 0], data[:, 2], 's-', label='SSZ (path integral proxy)', 
                lw=2.2, ms=6, color='red')
        ax.set_xlabel('Impact parameter $b / r_s$', fontsize=12)
        ax.set_ylabel('Shapiro delay $\\Delta t$ [s]', fontsize=12)
        ax.set_title(f'Shapiro Delay Proxy — M = {M_Msun} $M_\\odot$', fontsize=13)
        ax.legend(loc='upper right', frameon=True, fontsize=11)
        ax.grid(alpha=0.15)
        plt.tight_layout()
        
        png_path = os.path.join(cfg['outdir'], f'shapiro_proxy_M{M_Msun:.6g}.png')
        fig.savefig(png_path, dpi=200)
        plt.close(fig)
        print(f"  [OK] Saved {png_path}")
        
        # Calculate metrics
        max_abs_diff = max(abs(row[3]) for row in rows)
        max_GR = max(abs(row[1]) for row in rows)
        rel_agreement = 1.0 - (max_abs_diff / max_GR) if max_GR > 0 else None
        
        print(f"  [METRICS] Max abs diff = {max_abs_diff:.6e} s")
        print(f"            Relative agreement = {rel_agreement:.6f}")
        
        report['cases'].append({
            'M_Msun': M_Msun,
            'rs_m': rs,
            'max_abs_diff_s': max_abs_diff,
            'relative_agreement': rel_agreement,
            'num_points': len(rows)
        })
    
    print()

# Write JSON report
json_path = os.path.join(cfg['outdir'], 'shapiro_proxy_report.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print("="*80)
print("SHAPIRO DELAY VALIDATION COMPLETE")
print("="*80)
print(f"Results saved to: {cfg['outdir']}/")
print(f"  - shapiro_proxy_report.json")
print(f"  - shapiro_proxy_M*.csv")
print(f"  - shapiro_proxy_M*.png")
print("="*80)
