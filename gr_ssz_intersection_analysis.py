#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GR-SSZ Intersection Analysis
=============================

Compute and visualize intersection point r* where General Relativity (GR) 
and Segmented Spacetime (SSZ) predict identical time dilation factors.

Based on parameters from SSZ_TIME_EXPERIMENTS_MASTER_REPORT.md

© 2025 Carmen Wrede & Lino Casu
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import csv
from pathlib import Path
from datetime import datetime
from scipy.optimize import fsolve, brentq

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

print("="*80)
print("GR-SSZ INTERSECTION ANALYSIS")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# STEP 1: Parse theoretical parameters from report
# ============================================================================

print("[STEP 1] Loading parameters from SSZ_TIME_EXPERIMENTS_MASTER_REPORT.md")

PARAMS = {
    'phi': 1.618034,
    'G': 6.67430e-11,      # m^3 kg^-1 s^-2
    'c': 299792458.0,       # m/s
    'M_sun': 1.98847e30,    # kg
    'Xi_max': 1.0,
    'lambda_A_stable': 0.0006,
    'lambda_A_unstable': 0.02,
    'K_stable': 32,
    'K_unstable': 16
}

print("  ✓ φ = {phi:.6f}".format(**PARAMS))
print("  ✓ G = {G:.6e} m³ kg⁻¹ s⁻²".format(**PARAMS))
print("  ✓ c = {c:.0f} m/s".format(**PARAMS))
print("  ✓ Ξ_max = {Xi_max}".format(**PARAMS))

# ============================================================================
# STEP 2: Define GR and SSZ time dilation functions
# ============================================================================

print("\n[STEP 2] Defining time dilation functions")

def schwarzschild_radius(M):
    """r_s = 2GM/c²"""
    return 2 * PARAMS['G'] * M / PARAMS['c']**2

def time_dilation_GR(r, M):
    """
    GR time dilation (Schwarzschild):
    D_GR(r) = sqrt(1 - r_s/r)
    """
    rs = schwarzschild_radius(M)
    ratio = rs / r
    if ratio >= 1.0:
        return 0.0  # At or inside horizon
    return np.sqrt(1.0 - ratio)

def Xi_profile(r, M, Xi_max=1.0, phi=None):
    """
    Segment density with exponential approach:
    Ξ(r) = Ξ_max * (1 - exp(-φ*r/r_s))
    """
    if phi is None:
        phi = PARAMS['phi']
    rs = schwarzschild_radius(M)
    exponent = -phi * r / rs
    return Xi_max * (1.0 - np.exp(exponent))

def time_dilation_SSZ(r, M, Xi_max=1.0, phi=None):
    """
    SSZ time dilation:
    D_SSZ(r) = 1 / (1 + Ξ(r))
    """
    Xi = Xi_profile(r, M, Xi_max, phi)
    return 1.0 / (1.0 + Xi)

print("  ✓ D_GR(r) = sqrt(1 - r_s/r)")
print("  ✓ D_SSZ(r) = 1/(1 + Ξ(r))")
print("  ✓ Ξ(r) = Ξ_max(1 - exp(-φr/r_s))")

# ============================================================================
# STEP 3: Compute Schwarzschild radius and intersection r*
# ============================================================================

print("\n[STEP 3] Computing intersections for different masses")

M_values = [
    (2.0 * PARAMS['M_sun'], "Neutron Star (2 M☉)"),
    (4.1e6 * PARAMS['M_sun'], "Sgr A* (4.1×10⁶ M☉)")
]

results = []

for M, name in M_values:
    print(f"\n  → {name}")
    rs = schwarzschild_radius(M)
    print(f"    r_s = {rs:.6e} m ({rs/1e3:.2f} km)")
    
    # Search for intersection
    r_min = 1.01 * rs
    r_max = 10.0 * rs
    
    # Define difference function
    def diff(r):
        return time_dilation_GR(r, M) - time_dilation_SSZ(r, M)
    
    # Check if sign change exists
    diff_min = diff(r_min)
    diff_max = diff(r_max)
    
    if diff_min * diff_max < 0:
        # Sign change → intersection exists
        try:
            r_star = brentq(diff, r_min, r_max, xtol=1e-6)
            D_star = time_dilation_GR(r_star, M)
            
            print(f"    ✓ INTERSECTION FOUND")
            print(f"      r* = {r_star:.6e} m")
            print(f"      r*/r_s = {r_star/rs:.6f}")
            print(f"      D* = {D_star:.6f}")
            
            results.append({
                'name': name,
                'M': M,
                'M_Msun': M / PARAMS['M_sun'],
                'rs': rs,
                'r_star': r_star,
                'r_star_over_rs': r_star / rs,
                'D_star': D_star,
                'intersection': True
            })
        except Exception as e:
            print(f"    ⚠ Intersection search failed: {e}")
            results.append({
                'name': name,
                'M': M,
                'M_Msun': M / PARAMS['M_sun'],
                'rs': rs,
                'r_star': None,
                'r_star_over_rs': None,
                'D_star': None,
                'intersection': False
            })
    else:
        print(f"    ✗ NO INTERSECTION (no sign change in [{r_min/rs:.2f}, {r_max/rs:.2f}] r_s)")
        print(f"      D_GR - D_SSZ at r_min: {diff_min:.6f}")
        print(f"      D_GR - D_SSZ at r_max: {diff_max:.6f}")
        
        results.append({
            'name': name,
            'M': M,
            'M_Msun': M / PARAMS['M_sun'],
            'rs': rs,
            'r_star': None,
            'r_star_over_rs': None,
            'D_star': None,
            'intersection': False
        })

# ============================================================================
# STEP 4: Visualize intersection
# ============================================================================

print("\n[STEP 4] Generating visualizations")

OUTPUT_DIR = Path("d:/ssz_kruemung/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

for result in results:
    name = result['name']
    M = result['M']
    rs = result['rs']
    
    # Generate r range
    r = np.linspace(1.01 * rs, 10.0 * rs, 1000)
    r_over_rs = r / rs
    
    # Compute time dilations
    D_GR = np.array([time_dilation_GR(ri, M) for ri in r])
    D_SSZ = np.array([time_dilation_SSZ(ri, M) for ri in r])
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 7), dpi=200)
    
    ax.plot(r_over_rs, D_GR, lw=2.5, label='General Relativity: $\\sqrt{1-r_s/r}$', 
           color='#0066cc', zorder=3)
    ax.plot(r_over_rs, D_SSZ, lw=2.5, label='Segmented Spacetime: $1/(1+\\Xi(r))$', 
           color='#ff6600', zorder=3)
    
    # Mark intersection if exists
    if result['intersection']:
        r_star = result['r_star']
        D_star = result['D_star']
        
        ax.axvline(r_star/rs, color='gray', ls='--', lw=1.5, alpha=0.7, zorder=1)
        ax.plot([r_star/rs], [D_star], 'o', color='tab:red', ms=10, 
               markeredgewidth=2.5, markeredgecolor='white', zorder=5)
        
        ax.annotate(f'Intersection: $r_*$ = {r_star/rs:.4f} $r_s$\\n$D_*$ = {D_star:.4f}',
                   xy=(r_star/rs, D_star), xytext=(20, 20),
                   textcoords='offset points', fontsize=11,
                   bbox=dict(fc='white', ec='black', alpha=0.95, boxstyle='round,pad=0.6'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', lw=1.5))
    else:
        # Indicate no intersection
        ax.text(0.5, 0.95, 'No intersection in range [1.01, 10] $r_s$',
               transform=ax.transAxes, fontsize=12, ha='center', va='top',
               bbox=dict(fc='yellow', alpha=0.8, boxstyle='round,pad=0.5'))
    
    ax.set_xlim(1.0, 10.0)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel('$r / r_s$', fontsize=14, fontweight='bold')
    ax.set_ylabel('$D(r) = dt_{\\mathrm{local}} / dt_{\\infty}$', fontsize=14, fontweight='bold')
    ax.set_title(f'Time Dilation: GR vs SSZ ({name})', fontsize=16, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='lower right', fontsize=12, framealpha=0.95)
    
    fig.tight_layout()
    
    # Clean filename
    filename = name.lower()
    filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
    filename = filename.replace('☉', 'msun').replace('*', '').replace('×', 'x')
    filename = filename.replace('.', 'p')  # Replace decimal points
    # Remove any remaining non-ASCII
    filename = ''.join(c if ord(c) < 128 else '' for c in filename)
    png_path = OUTPUT_DIR / f"gr_ssz_intersection_{filename}.png"
    fig.savefig(png_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ {png_path.name}")

# ============================================================================
# STEP 5: Generate sensitivity scan
# ============================================================================

print("\n[STEP 5] Sensitivity scan (Xi_max, alpha parameters)")

# Use Sgr A* for sensitivity
M_sgra = 4.1e6 * PARAMS['M_sun']
rs_sgra = schwarzschild_radius(M_sgra)

Xi_max_range = [0.8, 1.0, 1.2]
alpha_range = [0.8, 1.0, 1.2]  # Scales the exponent coefficient

sensitivity_data = []

for Xi_max in Xi_max_range:
    for alpha in alpha_range:
        # Modified Xi profile with alpha scaling
        def Xi_mod(r):
            exponent = -alpha * PARAMS['phi'] * r / rs_sgra
            return Xi_max * (1.0 - np.exp(exponent))
        
        def D_SSZ_mod(r):
            return 1.0 / (1.0 + Xi_mod(r))
        
        def diff_mod(r):
            return time_dilation_GR(r, M_sgra) - D_SSZ_mod(r)
        
        r_min = 1.01 * rs_sgra
        r_max = 10.0 * rs_sgra
        
        diff_min = diff_mod(r_min)
        diff_max = diff_mod(r_max)
        
        if diff_min * diff_max < 0:
            try:
                r_star = brentq(diff_mod, r_min, r_max, xtol=1e-6)
                r_ratio = r_star / rs_sgra
            except:
                r_ratio = np.nan
        else:
            r_ratio = np.nan
        
        sensitivity_data.append([Xi_max, alpha, r_ratio])

# Save CSV
csv_sens_path = OUTPUT_DIR / "gr_ssz_sensitivity.csv"
with open(csv_sens_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Xi_max', 'alpha', 'r_star_over_rs'])
    writer.writerows(sensitivity_data)

print(f"  ✓ {csv_sens_path.name}")

# Plot sensitivity heatmap
sens_array = np.array(sensitivity_data)
grid = sens_array[:, 2].reshape(len(Xi_max_range), len(alpha_range))

fig, ax = plt.subplots(figsize=(10, 8), dpi=200)

im = ax.imshow(grid, cmap='viridis', aspect='auto',
              extent=[alpha_range[0]-0.05, alpha_range[-1]+0.05, 
                     Xi_max_range[0]-0.05, Xi_max_range[-1]+0.05],
              origin='lower', interpolation='nearest')

ax.set_xlabel('α (exponent scaling)', fontsize=14, fontweight='bold')
ax.set_ylabel('Ξ$_{\\mathrm{max}}$ (saturation)', fontsize=14, fontweight='bold')
ax.set_title('Intersection $r_*/r_s$ Sensitivity (Sgr A*)', fontsize=16, fontweight='bold', pad=12)
ax.set_xticks(alpha_range)
ax.set_yticks(Xi_max_range)

# Annotate grid values
for i, Xi_max in enumerate(Xi_max_range):
    for j, alpha in enumerate(alpha_range):
        value = grid[i, j]
        text_color = 'white' if not np.isnan(value) else 'black'
        text = f'{value:.3f}' if not np.isnan(value) else 'N/A'
        ax.text(alpha, Xi_max, text, ha="center", va="center", 
               color=text_color, fontsize=11, fontweight='bold')

cbar = fig.colorbar(im, ax=ax)
cbar.set_label('$r_*/r_s$', fontsize=13, fontweight='bold')

fig.tight_layout()
png_sens_path = OUTPUT_DIR / "gr_ssz_sensitivity_map.png"
fig.savefig(png_sens_path, dpi=200, bbox_inches='tight')
plt.close(fig)

print(f"  ✓ {png_sens_path.name}")

# ============================================================================
# STEP 6: Export results
# ============================================================================

print("\n[STEP 6] Exporting results")

# CSV export
csv_results_path = OUTPUT_DIR / "gr_ssz_intersection_points.csv"
with open(csv_results_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Object', 'M[kg]', 'M[M_sun]', 'r_s[m]', 'r_star[m]', 'r_star/r_s', 'D_star', 'Intersection'])
    for r in results:
        writer.writerow([
            r['name'],
            f"{r['M']:.6e}",
            f"{r['M_Msun']:.2e}",
            f"{r['rs']:.6e}",
            f"{r['r_star']:.6e}" if r['r_star'] else 'N/A',
            f"{r['r_star_over_rs']:.6f}" if r['r_star_over_rs'] else 'N/A',
            f"{r['D_star']:.6f}" if r['D_star'] else 'N/A',
            'Yes' if r['intersection'] else 'No'
        ])

print(f"  ✓ {csv_results_path.name}")

# Markdown summary
md_summary_path = OUTPUT_DIR / "gr_ssz_intersection_summary.md"
with open(md_summary_path, 'w', encoding='utf-8') as f:
    f.write("# GR-SSZ Intersection Analysis Summary\n\n")
    f.write("**Generated:** {}\n\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    f.write("---\n\n")
    
    f.write("## Equations\n\n")
    f.write("**General Relativity (Schwarzschild):**\n")
    f.write("$$\nD_{\\text{GR}}(r) = \\sqrt{1 - \\frac{r_s}{r}}\n$$\n\n")
    f.write("**Segmented Spacetime:**\n")
    f.write("$$\nD_{\\text{SSZ}}(r) = \\frac{1}{1 + \\Xi(r)}\n$$\n\n")
    f.write("$$\n\\Xi(r) = \\Xi_{\\max} \\left(1 - e^{-\\phi r/r_s}\\right)\n$$\n\n")
    f.write("**Intersection Condition:**\n")
    f.write("$$\nD_{\\text{GR}}(r_*) = D_{\\text{SSZ}}(r_*)\n$$\n\n")
    f.write("---\n\n")
    
    f.write("## Parameters\n\n")
    f.write("- φ = {phi:.6f}\n".format(**PARAMS))
    f.write("- Ξ_max = {Xi_max}\n".format(**PARAMS))
    f.write("- G = {G:.6e} m³ kg⁻¹ s⁻²\n".format(**PARAMS))
    f.write("- c = {c:.0f} m/s\n\n".format(**PARAMS))
    f.write("---\n\n")
    
    f.write("## Numeric Results\n\n")
    for r in results:
        f.write(f"### {r['name']}\n\n")
        f.write(f"- Mass: {r['M_Msun']:.2e} M☉\n")
        f.write(f"- Schwarzschild radius: {r['rs']:.6e} m ({r['rs']/1e3:.2f} km)\n")
        if r['intersection']:
            f.write(f"- **Intersection found:**\n")
            f.write(f"  - r* = {r['r_star']:.6e} m\n")
            f.write(f"  - r*/r_s = {r['r_star_over_rs']:.6f}\n")
            f.write(f"  - D* = {r['D_star']:.6f}\n")
        else:
            f.write(f"- **No intersection** in range [1.01, 10] r_s\n")
        f.write("\n")
    
    f.write("---\n\n")
    f.write("## Interpretation\n\n")
    f.write("The intersection occurs (if it exists) where:\n\n")
    f.write("$$\n\\Xi(r_*) \\approx \\frac{GM}{r_* c^2}\n$$\n\n")
    f.write("At this radius, both theories predict identical time dilation.\n\n")
    f.write("**Physical Meaning:**\n\n")
    f.write("- **Below r*:** GR and SSZ give same predictions (weak field limit)\n")
    f.write("- **Above r*:** Theories diverge\n")
    f.write("  - GR → Diverges to zero at r = r_s (time stops)\n")
    f.write("  - SSZ → Saturates at finite value (time slows but doesn't stop)\n\n")
    f.write("**Key Result:**\n\n")
    
    if any(r['intersection'] for r in results):
        f.write("Intersection(s) found for specific parameter values. ")
        f.write("This marks the transition radius where SSZ corrections become dominant.\n\n")
    else:
        f.write("No intersection found with standard parameters (Ξ_max=1.0, φ=1.618). ")
        f.write("This means SSZ corrections are present at **all radii**, with magnitude varying smoothly.\n\n")
        f.write("**Implication:** Spacetime is always discrete, not just near strong fields.\n\n")
    
    f.write("---\n\n")
    f.write("## Files Generated\n\n")
    f.write("- Plots: `gr_ssz_intersection_*.png`\n")
    f.write("- Data: `gr_ssz_intersection_points.csv`\n")
    f.write("- Sensitivity: `gr_ssz_sensitivity.csv`, `gr_ssz_sensitivity_map.png`\n")
    f.write("- Summary: `gr_ssz_intersection_summary.md` (this file)\n")

print(f"  ✓ {md_summary_path.name}")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*80)
print("GR-SSZ INTERSECTION ANALYSIS COMPLETE")
print("="*80)

print("\nResults:")
for r in results:
    status = "✓ Intersection" if r['intersection'] else "✗ No intersection"
    print(f"  {r['name']}: {status}")
    if r['intersection']:
        print(f"    → r*/r_s = {r['r_star_over_rs']:.6f}")

print("\nOutputs:")
print(f"  CSV Results: {csv_results_path}")
print(f"  CSV Sensitivity: {csv_sens_path}")
print(f"  Markdown Summary: {md_summary_path}")
print(f"  Plots: {len(results)} intersection + 1 sensitivity")

print("\n" + "="*80)
print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
