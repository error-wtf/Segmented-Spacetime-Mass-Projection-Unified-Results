#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Black Hole Stability - Three Core Visualizations

Reproduziert die drei Schlüsselabbildungen:
1. Segmentation & Krümmungsgrenze (Ξ(r), R_proxy(r))
2. Stabilitätskarte (K, λ_A)
3. Energie-Zeitreihen (Bomb-Szenario)

© 2025 Carmen Wrede & Lino Casu
"""
import os, sys, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio

def Xi(r, Xi_max=0.99, eps=0.001):
    """Segmentdichte: Ξ(r) = Ξ_max(1 - exp(-φ(r+ε)))"""
    return Xi_max * (1 - np.exp(-PHI * (r + eps)))

def R_proxy(r):
    """Krümmungs-Proxy: R(r) = 1 / (1 + Ξ(r))"""
    return 1.0 / (1 + Xi(r))

def energy_step(E, lam, K):
    """E_{t+1} = E_t(1 + λ - λ²K²)"""
    return E * (1 + lam - lam**2 * K**2)

def run_simulation(K, lam, steps=1000, saturate=True):
    """Bomb-Simulation"""
    E = np.zeros(steps)
    E[0] = 1.0
    E_max = 1.0 * (1 - np.exp(-PHI * K))
    for t in range(steps-1):
        E[t+1] = energy_step(E[t], lam, K)
        if saturate:
            E[t+1] = min(E[t+1], E_max)
    return E, E_max

# Figure 1: Ξ(r) and R_proxy(r)
def fig1(outdir="./results"):
    r = np.linspace(0.001, 5, 500)
    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(16,6))
    fig.patch.set_facecolor('#0a0a1e')
    
    for ax in (ax1,ax2):
        ax.set_facecolor('#0a0a1e')
        ax.tick_params(colors='white')
        for s in ax.spines.values(): s.set_color('white')
    
    ax1.plot(r, Xi(r), '#FF00FF', lw=2.5, label='Ξ(r)')
    ax1.axhline(0.99, color='#FFD700', ls='--', lw=1.5, label='Ξ_max')
    ax1.set_xlabel('r/r_s', color='white')
    ax1.set_ylabel('Ξ(r)', color='white')
    ax1.set_title('Segmentdichte', fontweight='bold', color='white')
    ax1.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax1.grid(True, alpha=0.3, color='white')
    
    ax2.plot(r, R_proxy(r), '#00FFFF', lw=2.5, label='R_proxy(r)')
    ax2.text(0.5,0.95,'Endlich bei r→0!\nKeine Singularität', transform=ax2.transAxes,
             color='#00FF00', fontweight='bold', va='top', fontsize=11,
             bbox=dict(boxstyle='round',facecolor='black',alpha=0.8,edgecolor='#00FF00'))
    ax2.set_xlabel('r/r_s', color='white')
    ax2.set_ylabel('R_proxy/R_0', color='white')
    ax2.set_title('Krümmungsindikator', fontweight='bold', color='white')
    ax2.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax2.grid(True, alpha=0.3, color='white')
    
    plt.tight_layout()
    out = Path(outdir)/"ssz_formal_fig_Xi_Rproxy.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300, facecolor='#0a0a1e', bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {out}")

# Figure 2: Stability Map
def fig2(outdir="./results"):
    K = np.logspace(0.7,2.5,100)
    lam = np.logspace(-5,-1,100)
    Kg, lamg = np.meshgrid(K, lam)
    stable = (lamg < 1/Kg**2).astype(float)
    
    fig, ax = plt.subplots(figsize=(12,9))
    fig.patch.set_facecolor('#0a0a1e')
    ax.set_facecolor('#0a0a1e')
    
    ax.contourf(Kg, lamg, stable, levels=[0,0.5,1], colors=['#FF6B6B','#00FF00'], alpha=0.6)
    ax.loglog(K, 1/K**2, 'w-', lw=3, label='λ_crit=1/K²')
    ax.loglog(K, 1/K**2, color='#FFD700', lw=2, ls='--')
    
    examples = [(32,0.0006,'Stabil','#00FF00'), (16,0.02,'Instabil','#FF0000')]
    for Kx,lx,lab,col in examples:
        ax.plot(Kx,lx,'o',ms=12,color=col,mec='white',mew=2,label=lab)
        ax.text(Kx*1.2,lx,f'K={Kx}, λ={lx:.4f}', color='white', fontsize=9,
                bbox=dict(boxstyle='round',facecolor='black',alpha=0.7))
    
    ax.set_xlabel('K', color='white', fontsize=12)
    ax.set_ylabel('λ_A', color='white', fontsize=12)
    ax.set_title('SSZ Stability Map: λ_A < 1/K²', fontweight='bold', color='white', fontsize=14)
    ax.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.grid(True, alpha=0.3, color='white', which='both', ls=':')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_color('white')
    
    plt.tight_layout()
    out = Path(outdir)/"ssz_formal_fig_stability_map.png"
    plt.savefig(out, dpi=300, facecolor='#0a0a1e', bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {out}")

# Figure 3: Energy Time Series
def fig3(outdir="./results"):
    E_stable, E_max_s = run_simulation(32, 0.0006, 1000, True)
    E_unstable, _ = run_simulation(16, 0.02, 1000, False)
    
    fig, (ax1,ax2) = plt.subplots(2,1,figsize=(14,10))
    fig.patch.set_facecolor('#0a0a1e')
    
    time = np.arange(1000)
    
    for ax in (ax1,ax2):
        ax.set_facecolor('#0a0a1e')
        ax.tick_params(colors='white')
        for s in ax.spines.values(): s.set_color('white')
    
    ax1.plot(time, E_stable, '#00FF00', lw=2, label='Stabil: K=32, λ=0.0006')
    ax1.plot(time, E_unstable, '#FF6B6B', lw=2, ls='--', label='Instabil: K=16, λ=0.02')
    ax1.axhline(E_max_s, color='#FFD700', ls=':', lw=1.5, label='φ-Sättigung')
    ax1.set_xlabel('Zeit', color='white')
    ax1.set_ylabel('E/E₀', color='white')
    ax1.set_title('Black-Hole-Bomb: Stabil vs. Instabil (Linear)', fontweight='bold', color='white')
    ax1.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax1.grid(True, alpha=0.3, color='white')
    ax1.set_ylim(0, min(20, E_unstable[500]))
    
    ax2.semilogy(time, E_stable, '#00FF00', lw=2, label='Stabil')
    ax2.semilogy(time, E_unstable, '#FF6B6B', lw=2, ls='--', label='Instabil')
    ax2.set_xlabel('Zeit', color='white')
    ax2.set_ylabel('log(E/E₀)', color='white')
    ax2.set_title('Black-Hole-Bomb: Stabil vs. Instabil (Log)', fontweight='bold', color='white')
    ax2.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax2.grid(True, alpha=0.3, color='white', which='both')
    
    stats = f"STABLE:\n λ_crit={1/32**2:.6f}\n E_final/E₀={E_stable[-1]:.2f}\n\n"
    stats += f"UNSTABLE:\n λ_crit={1/16**2:.6f}\n E_final/E₀={E_unstable[-1]:.1e}"
    ax2.text(0.98,0.98,stats,transform=ax2.transAxes,color='white',va='top',ha='right',
             family='monospace',fontsize=10,
             bbox=dict(boxstyle='round',facecolor='black',alpha=0.8,edgecolor='white'))
    
    plt.tight_layout()
    out = Path(outdir)/"ssz_formal_fig_energy_series.png"
    plt.savefig(out, dpi=300, facecolor='#0a0a1e', bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {out}")
    print(f"  Dämpfung: {E_unstable[-1]/E_stable[-1]:.1e}×")

if __name__ == "__main__":
    print("="*80)
    print("SSZ BLACK HOLE STABILITY - THREE CORE FIGURES")
    print("="*80)
    outdir = "H:/WINDSURF/Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00/results"
    fig1(outdir)
    fig2(outdir)
    fig3(outdir)
    print("\n" + "="*80)
    print("COMPLETE! All figures saved.")
    print("="*80)
