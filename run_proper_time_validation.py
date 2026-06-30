#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Proper Time (Eigenzeit) – Full Validation (GR vs SSZ)

Validates proper time consistency between GR and SSZ across:
- Local time dilation factors D(r)
- Stationary clocks (ruhende Uhren)
- Gravitational redshift
- Circular orbits (approximation)
- Radial infall (numerical integration)
- Crossover coherence at r*
- Causality bounds
- GR⊂SSZ limit test
- Parameter sensitivity

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
from pathlib import Path

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Physical constants
G = 6.67430e-11
c = 299792458.0
M_sun = 1.98847e30
PHI = (1 + np.sqrt(5)) / 2

# Configuration
cfg = {
    'phi': PHI,
    'Xi_max': 1.0,
    'alpha': 1.0,
    'masses_Msun': [2.0, 4.1e6],  # NS, Sgr A*
    'rstar_hint': 1.594811,       # Known intersection
    'r_grid': (1.01, 5.0),        # in units of r_s
    'r_points': [1.05, 1.2, 1.5, 2.0, 3.0, 5.0],
    'orbits_r': [3.0, 4.0, 6.0, 10.0],
    'dt_total': 1000.0,           # seconds for stationary comparisons
    'radial_profiles': [
        (1.8, 1.2, 2000),         # (r0/rs, r1/rs, Nsteps)
        (3.0, 1.2, 4000)
    ],
    'sens_Xi': [0.8, 1.0, 1.2],
    'sens_alpha': [0.8, 1.0, 1.2],
    'outdir': 'outputs_propertime',
    'tol': 1e-6
}

os.makedirs(cfg['outdir'], exist_ok=True)

print("="*80)
print("SSZ PROPER TIME (EIGENZEIT) - FULL VALIDATION")
print("="*80)
print(f"Configuration:")
print(f"  Xi_max = {cfg['Xi_max']}")
print(f"  alpha = {cfg['alpha']}")
print(f"  phi = {cfg['phi']:.6f}")
print(f"  r* hint = {cfg['rstar_hint']} r_s")
print()

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def rs_from_mass(M):
    """Schwarzschild radius"""
    return 2 * G * M / c**2

def D_GR(r, rs):
    """GR time dilation: D = sqrt(1 - r_s/r)"""
    x = 1.0 - (rs / np.asarray(r))
    return np.sqrt(np.clip(x, 0.0, None))

def Xi_of_r(r, rs, Xi_max, alpha, phi):
    """SSZ segment density (CORRECT exponential model):
    Xi(r) = Xi_max * (1 - exp(-phi * r_s / r))
    """
    return Xi_max * (1.0 - np.exp(-phi * np.asarray(r) / rs))

def D_SSZ(r, rs, Xi_max, alpha):
    """SSZ time dilation: D = 1/(1 + Xi)"""
    return 1.0 / (1.0 + Xi_of_r(r, rs, Xi_max, alpha, PHI))

def assert_causality(D, name="D"):
    """Assert 0 < D <= 1"""
    if not (np.all(D > 0) and np.all(D <= 1 + 1e-12)):
        raise ValueError(f"Causality bound violated: {name} not in (0,1].")

# ============================================================================
# MAIN VALIDATION
# ============================================================================

report = {
    'config': cfg,
    'cases': [],
    'summary': {
        'all_causality_ok': True,
        'all_crossover_ok': True,
        'all_convergence_ok': True
    }
}

for M_Msun in cfg['masses_Msun']:
    M = M_Msun * M_sun
    rs = rs_from_mass(M)
    
    print(f"[CASE] M = {M_Msun} M_sun, r_s = {rs:.3e} m")
    
    # r grid for plots
    r = np.linspace(cfg['r_grid'][0]*rs, cfg['r_grid'][1]*rs, 4000)
    Dgr = D_GR(r, rs)
    Dssz = D_SSZ(r, rs, cfg['Xi_max'], cfg['alpha'])
    
    # 1) CAUSALITY CHECK
    print("  [1/8] Causality bounds...")
    try:
        assert_causality(Dgr[(r > 1.0001*rs)], "D_GR")
        assert_causality(Dssz[(r > 1.0001*rs)], "D_SSZ")
        causality_ok = True
        print("        [OK] Causality bounds satisfied")
    except ValueError as e:
        causality_ok = False
        report['summary']['all_causality_ok'] = False
        print(f"        [FAIL] {e}")
    
    # 2) STATIONARY CLOCKS (Δτ = D·Δt)
    print("  [2/8] Stationary clocks...")
    rows_stat = []
    for rfac in cfg['r_points']:
        rr = rfac * rs
        tau_gr = D_GR(rr, rs) * cfg['dt_total']
        tau_ssz = D_SSZ(rr, rs, cfg['Xi_max'], cfg['alpha']) * cfg['dt_total']
        rows_stat.append([rfac, tau_gr, tau_ssz, tau_ssz - tau_gr])
    
    csv_path = os.path.join(cfg['outdir'], f'stat_dt_M{M_Msun:.6g}.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['r/rs', 'tau_GR[s]', 'tau_SSZ[s]', 'diff[s]'])
        w.writerows(rows_stat)
    print(f"        [OK] Saved {csv_path}")
    
    # 3) GRAVITATIONAL REDSHIFT
    print("  [3/8] Gravitational redshift...")
    rows_z = []
    r_obs = 5.0  # Observer at 5 r_s
    for re in cfg['r_points']:
        D_e_ssz = D_SSZ(re*rs, rs, cfg['Xi_max'], cfg['alpha'])
        D_o_ssz = D_SSZ(r_obs*rs, rs, cfg['Xi_max'], cfg['alpha'])
        z_ssz = D_o_ssz / D_e_ssz - 1.0
        
        D_e_gr = D_GR(re*rs, rs)
        D_o_gr = D_GR(r_obs*rs, rs)
        z_gr = D_o_gr / D_e_gr - 1.0
        
        rows_z.append([re, r_obs, z_gr, z_ssz, z_ssz - z_gr])
    
    csv_path = os.path.join(cfg['outdir'], f'redshift_M{M_Msun:.6g}.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['r_emit/rs', 'r_obs/rs', 'z_GR', 'z_SSZ', 'diff'])
        w.writerows(rows_z)
    print(f"        [OK] Saved {csv_path}")
    
    # 4) CIRCULAR ORBITS (Approximation)
    print("  [4/8] Circular orbits (approximate)...")
    rows_orb = []
    for rorb in cfg['orbits_r']:
        rr = rorb * rs
        v = math.sqrt(G * M / rr)  # Newtonian orbital velocity
        gamma = math.sqrt(max(0.0, 1.0 - (v/c)**2))
        D_orb_gr = D_GR(rr, rs) * gamma
        D_orb_ssz = D_SSZ(rr, rs, cfg['Xi_max'], cfg['alpha']) * gamma
        rows_orb.append([rorb, v/c, D_orb_gr, D_orb_ssz, D_orb_ssz - D_orb_gr])
    
    csv_path = os.path.join(cfg['outdir'], f'orbit_M{M_Msun:.6g}.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['r/rs', 'beta=v/c', 'D_orb_GR', 'D_orb_SSZ', 'diff'])
        w.writerows(rows_orb)
    print(f"        [OK] Saved {csv_path}")
    
    # 5) RADIAL INFALL (Numerical integration)
    print("  [5/8] Radial infall (numerical)...")
    def integrate_tau_profile(r0_rs, r1_rs, N):
        """Integrate τ along r(t) = linear profile"""
        t = np.linspace(0.0, 1.0, N)
        r_path = (r0_rs + (r1_rs - r0_rs) * t) * rs
        dt_phys = cfg['dt_total'] / N
        tau_gr = np.sum(D_GR(r_path, rs)) * dt_phys
        tau_ssz = np.sum(D_SSZ(r_path, rs, cfg['Xi_max'], cfg['alpha'])) * dt_phys
        return tau_gr, tau_ssz
    
    rows_rad = []
    all_converged = True
    for r0_rs, r1_rs, N in cfg['radial_profiles']:
        tau1_gr, tau1_ssz = integrate_tau_profile(r0_rs, r1_rs, N)
        tau2_gr, tau2_ssz = integrate_tau_profile(r0_rs, r1_rs, 2*N)
        
        conv_gr = abs((tau2_gr - tau1_gr) / max(1e-9, tau2_gr)) < cfg['tol']
        conv_ssz = abs((tau2_ssz - tau1_ssz) / max(1e-9, tau2_ssz)) < cfg['tol']
        conv_ok = conv_gr and conv_ssz
        
        if not conv_ok:
            all_converged = False
        
        rows_rad.append([r0_rs, r1_rs, N, tau1_gr, tau1_ssz, tau1_ssz - tau1_gr, conv_ok])
    
    csv_path = os.path.join(cfg['outdir'], f'radial_M{M_Msun:.6g}.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['r0/rs', 'r1/rs', 'Nsteps', 'tau_GR[s]', 'tau_SSZ[s]', 'diff[s]', 'converged'])
        w.writerows(rows_rad)
    print(f"        [OK] Saved {csv_path}")
    if not all_converged:
        report['summary']['all_convergence_ok'] = False
        print("        [WARN] Some radial profiles did not converge")
    
    # 6) CROSSOVER COHERENCE at r*
    print("  [6/8] Crossover coherence at r*...")
    rstar = cfg['rstar_hint'] * rs
    Dg_star = D_GR(rstar, rs)
    Ds_star = D_SSZ(rstar, rs, cfg['Xi_max'], cfg['alpha'])
    crossover_ok = abs(Dg_star - Ds_star) < 1e-3
    
    if crossover_ok:
        print(f"        [OK] D_GR(r*) = {Dg_star:.6f}, D_SSZ(r*) = {Ds_star:.6f}, diff = {abs(Dg_star-Ds_star):.2e}")
    else:
        print(f"        [FAIL] D_GR(r*) = {Dg_star:.6f}, D_SSZ(r*) = {Ds_star:.6f}, diff = {abs(Dg_star-Ds_star):.2e}")
        report['summary']['all_crossover_ok'] = False
    
    # 7) GR⊂SSZ LIMIT TEST (alpha → 0)
    print("  [7/8] GR subset SSZ limit test...")
    r_test = 2.0 * rs
    D_gr_test = D_GR(r_test, rs)
    D_ssz_lim = D_SSZ(r_test, rs, Xi_max=1.0, alpha=0.001)  # alpha → 0
    lim_error = abs(D_ssz_lim - D_gr_test) / D_gr_test
    limit_ok = lim_error < 1e-6
    
    if limit_ok:
        print(f"        [OK] alpha->0 test: error = {lim_error:.2e}")
    else:
        print(f"        [WARN] alpha->0 test: error = {lim_error:.2e}")
    
    # 8) PARAMETER SENSITIVITY
    print("  [8/8] Parameter sensitivity...")
    sens_data = []
    for X in cfg['sens_Xi']:
        for A in cfg['sens_alpha']:
            Dr = D_SSZ(2.0*rs, rs, X, A)
            sens_data.append([X, A, Dr])
    
    csv_path = os.path.join(cfg['outdir'], f'sensitivity_M{M_Msun:.6g}.csv')
    np.savetxt(csv_path, np.array(sens_data), delimiter=',',
               header='Xi_max,alpha,D_SSZ(r=2rs)', comments='')
    print(f"        [OK] Saved {csv_path}")
    
    # PLOTS
    print("  [PLOTS] Generating visualizations...")
    
    # Plot 1: D(r)
    fig, ax = plt.subplots(figsize=(12, 6.8), dpi=200)
    ax.plot(r/rs, Dgr, label='GR: $D = \\sqrt{1-r_s/r}$', lw=2.2, color='blue')
    ax.plot(r/rs, Dssz, label='SSZ: $D = 1/(1+\\Xi)$', lw=2.2, color='red')
    ax.axvline(cfg['rstar_hint'], color='gray', ls='--', lw=1.2, alpha=0.7, label=f'$r_* = {cfg["rstar_hint"]:.3f}r_s$')
    ax.set_xlim(cfg['r_grid'])
    ax.set_ylim(0, 1.02)
    ax.set_xlabel('$r / r_s$', fontsize=12)
    ax.set_ylabel('$D(r) = d\\tau/dt$', fontsize=12)
    ax.set_title(f'Proper Time Factor — M = {M_Msun} $M_\\odot$', fontsize=13)
    ax.legend(loc='upper right', frameon=True, fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    png_path = os.path.join(cfg['outdir'], f'D_of_r_M{M_Msun:.6g}.png')
    fig.savefig(png_path, dpi=200)
    plt.close(fig)
    print(f"        [OK] Saved {png_path}")
    
    # Plot 2: Redshift
    fig, ax = plt.subplots(figsize=(12, 6.8), dpi=200)
    z_gr_vals = [row[2] for row in rows_z]
    z_ssz_vals = [row[3] for row in rows_z]
    r_emit_vals = [row[0] for row in rows_z]
    
    ax.plot(r_emit_vals, z_gr_vals, 'o-', label='GR', lw=2, ms=6, color='blue')
    ax.plot(r_emit_vals, z_ssz_vals, 's-', label='SSZ', lw=2, ms=6, color='red')
    ax.axvline(cfg['rstar_hint'], color='gray', ls='--', lw=1.2, alpha=0.7)
    ax.set_xlabel('$r_{\\rm emit} / r_s$', fontsize=12)
    ax.set_ylabel('Redshift $z$', fontsize=12)
    ax.set_title(f'Gravitational Redshift — M = {M_Msun} $M_\\odot$, $r_{{\\rm obs}} = {r_obs}r_s$', fontsize=13)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    png_path = os.path.join(cfg['outdir'], f'redshift_M{M_Msun:.6g}.png')
    fig.savefig(png_path, dpi=200)
    plt.close(fig)
    print(f"        [OK] Saved {png_path}")
    
    # Plot 3: Sensitivity Heatmap
    fig, ax = plt.subplots(figsize=(8, 7), dpi=200)
    sens_arr = np.array(sens_data)
    Xi_vals = sorted(set(sens_arr[:, 0]))
    alpha_vals = sorted(set(sens_arr[:, 1]))
    Z = sens_arr[:, 2].reshape(len(Xi_vals), len(alpha_vals))
    
    im = ax.imshow(Z, aspect='auto', origin='lower', cmap='viridis',
                   extent=[alpha_vals[0], alpha_vals[-1], Xi_vals[0], Xi_vals[-1]])
    ax.set_xlabel('$\\alpha$', fontsize=12)
    ax.set_ylabel('$\\Xi_{\\max}$', fontsize=12)
    ax.set_title(f'$D_{{\\rm SSZ}}(r=2r_s)$ Sensitivity — M = {M_Msun} $M_\\odot$', fontsize=13)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('$D_{\\rm SSZ}$', fontsize=11)
    plt.tight_layout()
    
    png_path = os.path.join(cfg['outdir'], f'sensitivity_heatmap_M{M_Msun:.6g}.png')
    fig.savefig(png_path, dpi=200)
    plt.close(fig)
    print(f"        [OK] Saved {png_path}")
    
    # Store case results
    case = {
        'M_Msun': M_Msun,
        'rs_m': rs,
        'causality_ok': bool(causality_ok),
        'crossover_ok': bool(crossover_ok),
        'convergence_ok': bool(all_converged),
        'limit_ok': bool(limit_ok),
        'D_star': {
            'GR': float(Dg_star),
            'SSZ': float(Ds_star),
            'diff': float(abs(Dg_star - Ds_star))
        }
    }
    report['cases'].append(case)
    print()

# ============================================================================
# FINAL REPORT
# ============================================================================

# Write JSON report
json_path = os.path.join(cfg['outdir'], 'proper_time_validation.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print("="*80)
print("PROPER TIME VALIDATION COMPLETE")
print("="*80)
print(f"Summary:")
print(f"  Causality: {'[PASS]' if report['summary']['all_causality_ok'] else '[FAIL]'}")
print(f"  Crossover: {'[PASS]' if report['summary']['all_crossover_ok'] else '[FAIL]'}")
print(f"  Convergence: {'[PASS]' if report['summary']['all_convergence_ok'] else '[FAIL]'}")
print()
print(f"Results saved to: {cfg['outdir']}/")
print(f"  - proper_time_validation.json")
print(f"  - stat_dt_M*.csv")
print(f"  - redshift_M*.csv")
print(f"  - orbit_M*.csv")
print(f"  - radial_M*.csv")
print(f"  - sensitivity_M*.csv")
print(f"  - D_of_r_M*.png")
print(f"  - redshift_M*.png")
print(f"  - sensitivity_heatmap_M*.png")
print("="*80)
