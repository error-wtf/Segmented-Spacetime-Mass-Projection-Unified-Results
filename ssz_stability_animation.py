#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Black Hole Stability - Animated GIF Generator

Creates animated visualization of Black Hole Bomb evolution.

© 2025 Carmen Wrede & Lino Casu
"""
import os, sys, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

PHI = (1 + np.sqrt(5)) / 2

def energy_step(E, lam, K):
    return E * (1 + lam - lam**2 * K**2)

def run_sim(K, lam, steps, saturate=True):
    E = np.zeros(steps)
    E[0] = 1.0
    E_max = 1.0 * (1 - np.exp(-PHI * K))
    for t in range(steps-1):
        E[t+1] = energy_step(E[t], lam, K)
        if saturate:
            E[t+1] = min(E[t+1], E_max)
    return E, E_max

def create_animation(outdir="./results"):
    """Create side-by-side animated comparison"""
    print("="*80)
    print("CREATING ANIMATION: Stable vs. Unstable")
    print("="*80)
    
    n_steps = 500
    n_frames = 100
    
    # Simulations
    E_s, E_max_s = run_sim(32, 0.0006, n_steps, True)
    E_u, _ = run_sim(16, 0.02, n_steps, False)
    
    # Figure setup
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#0a0a1e')
    
    def init():
        for ax in (ax1, ax2):
            ax.set_facecolor('#0a0a1e')
            ax.tick_params(colors='white')
            for s in ax.spines.values():
                s.set_color('white')
        return []
    
    def animate(frame):
        step = int((frame / n_frames) * n_steps)
        
        ax1.clear()
        ax2.clear()
        
        time = np.arange(step)
        
        # Left: Stable
        ax1.set_facecolor('#0a0a1e')
        ax1.plot(time, E_s[:step], '#00FF00', lw=2.5)
        ax1.axhline(E_max_s, color='#FFD700', ls=':', lw=1.5, label='φ² Sättigung')
        ax1.fill_between(time, 0, E_s[:step], color='#00FF00', alpha=0.2)
        ax1.set_xlabel('Zeit (Schritte)', color='white', fontsize=11)
        ax1.set_ylabel('E / E₀', color='white', fontsize=11)
        ax1.set_title(f'STABIL (K=32, λ=0.0006)\nSchritt {step}/{n_steps}', 
                      color='#00FF00', fontweight='bold', fontsize=12)
        ax1.set_xlim(0, n_steps)
        ax1.set_ylim(0, E_max_s * 1.5)
        ax1.grid(True, alpha=0.3, color='white')
        ax1.legend(fontsize=10, facecolor='black', edgecolor='white', labelcolor='white')
        ax1.tick_params(colors='white')
        for s in ax1.spines.values():
            s.set_color('white')
        
        # Right: Unstable
        ax2.set_facecolor('#0a0a1e')
        ax2.semilogy(time, E_u[:step], '#FF6B6B', lw=2.5)
        ax2.fill_between(time, 1, E_u[:step], color='#FF6B6B', alpha=0.2)
        ax2.axhline(10, color='#FFD700', ls='--', lw=1, alpha=0.5, label='10× Verstärkung')
        ax2.set_xlabel('Zeit (Schritte)', color='white', fontsize=11)
        ax2.set_ylabel('log(E / E₀)', color='white', fontsize=11)
        ax2.set_title(f'INSTABIL (K=16, λ=0.02)\nSchritt {step}/{n_steps}', 
                      color='#FF6B6B', fontweight='bold', fontsize=12)
        ax2.set_xlim(0, n_steps)
        ax2.set_ylim(1, max(100, E_u[step] * 1.5))
        ax2.grid(True, alpha=0.3, color='white', which='both')
        ax2.legend(fontsize=10, facecolor='black', edgecolor='white', labelcolor='white')
        ax2.tick_params(colors='white')
        for s in ax2.spines.values():
            s.set_color('white')
        
        # Add current values
        ax1.text(0.02, 0.98, f'E = {E_s[step]:.3f}', transform=ax1.transAxes,
                 color='white', fontsize=12, va='top', fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
        
        ax2.text(0.02, 0.98, f'E = {E_u[step]:.2e}', transform=ax2.transAxes,
                 color='white', fontsize=12, va='top', fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
        
        return []
    
    print("Rendering animation...")
    anim = FuncAnimation(fig, animate, init_func=init, frames=n_frames, 
                        interval=50, blit=True)
    
    out = Path(outdir) / "ssz_bomb_evolution.gif"
    out.parent.mkdir(parents=True, exist_ok=True)
    writer = PillowWriter(fps=20)
    anim.save(out, writer=writer, dpi=120)
    plt.close()
    
    print(f"✓ Saved: {out}")
    print(f"  Frames: {n_frames}, FPS: 20, Duration: {n_frames/20:.1f}s")
    print("="*80)

if __name__ == "__main__":
    outdir = "H:/WINDSURF/Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00/results"
    create_animation(outdir)
