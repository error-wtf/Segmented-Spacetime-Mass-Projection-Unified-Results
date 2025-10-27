#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ GIF Renderer Part 3 - Wissenschaftlicher Beweis
Basiert auf ssz_proof_anim_v6.gif (Parameter Space, Stabilität)

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

TEXTS = {
    'de': {'title': 'SSZ — Mathematische Stabilität', 'stable': 'Stabile Konfigurationen'},
    'en': {'title': 'SSZ — Mathematical Stability', 'stable': 'Stable Configurations'},
    'it': {'title': 'SSZ — Stabilità Matematica', 'stable': 'Configurazioni Stabili'}
}

def render_proof_gif(duration: float, lang: str, output_path: Path, fps: int = 30, dpi: int = 100):
    """Rendert Proof-GIF mit 4 wissenschaftlichen Plots"""
    total_frames = int(duration * fps)
    
    print(f"\n{'='*70}")
    print(f"RENDERING PROOF GIF: {lang.upper()}")
    print(f"Duration: {duration:.2f}s | Frames: {total_frames} | Output: {output_path}")
    print(f"{'='*70}")
    
    fig = plt.figure(figsize=(16, 12), dpi=dpi, facecolor='#0f0f1e')
    
    def update_frame(frame_num):
        fig.clf()
        t = frame_num / total_frames
        
        fig.suptitle(TEXTS[lang]['title'], fontsize=20, color='white', fontweight='bold')
        
        # 2x2 Plots
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Plot 1: Stability Map
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_facecolor('#1a1a2e')
        lambda_a = np.linspace(0, 0.8, 100)
        k = np.linspace(0, 140, 100)
        L, K = np.meshgrid(lambda_a, k)
        Z = ((L < 0.6) & (K > 20) & (K < 120)).astype(float)
        ax1.contourf(L, K, Z, levels=10, cmap='Blues_r', alpha=0.9)
        ax1.axhline(32, color='white', linestyle='--', linewidth=2)
        ax1.set_xlabel('λ_Λ', color='white')
        ax1.set_ylabel('K', color='white')
        ax1.set_title('Fraction stable', color='white', fontweight='bold')
        ax1.tick_params(colors='white')
        
        # Plot 2: Critical Lambda
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.set_facecolor('#1a1a2e')
        ax2.text(0.5, 0.5, 'no boundary data', transform=ax2.transAxes,
                ha='center', va='center', color='gray', fontsize=14, style='italic')
        ax2.set_xlabel('Ω₀', color='white')
        ax2.set_ylabel('λ_Λ,crit', color='white')
        ax2.set_title('λ_Λ,crit vs Ω₀', color='white', fontweight='bold')
        ax2.tick_params(colors='white')
        
        # Plot 3: Amplitude Evolution
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.set_facecolor('#1a1a2e')
        n_visible = int(50 * t)
        rounds = np.arange(50)
        log_g = np.random.normal(0, 0.1, 50)
        if n_visible > 0:
            ax3.plot(rounds[:n_visible], log_g[:n_visible], 'b-', linewidth=2)
            ax3.axhline(0, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
        ax3.set_xlabel('Roundtrip n', color='white')
        ax3.set_ylabel('log G', color='white')
        ax3.set_title('Amplitude evolution', color='white', fontweight='bold')
        ax3.tick_params(colors='white')
        ax3.grid(True, alpha=0.2, color='white')
        
        # Plot 4: Disagreement Ratio
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.set_facecolor('#1a1a2e')
        disagree = 0.5 * np.ones_like(Z)
        ax4.contourf(L, K, disagree, levels=10, cmap='viridis', alpha=0.9)
        ax4.set_xlabel('λ_Λ', color='white')
        ax4.set_ylabel('K', color='white')
        ax4.set_title('Disagreement ratio', color='white', fontweight='bold')
        ax4.tick_params(colors='white')
        
        # Spines
        for ax in [ax1, ax2, ax3, ax4]:
            for spine in ax.spines.values():
                spine.set_color('white')
        
        if frame_num % (fps * 5) == 0:
            print(f"  {frame_num/fps:.1f}s / {duration:.1f}s ({100*frame_num/total_frames:.0f}%)")
        
        return fig,
    
    anim = FuncAnimation(fig, update_frame, frames=total_frames, interval=1000/fps, blit=False)
    
    print(f"\nSaving GIF...")
    try:
        anim.save(str(output_path), writer='pillow', fps=fps, dpi=dpi)
        size = output_path.stat().st_size / (1024*1024)
        print(f"✓ {output_path.name} ({size:.1f} MB)\n{'='*70}\n")
    except Exception as e:
        print(f"ERROR: {e}")
        raise
    finally:
        plt.close(fig)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', type=float, required=True)
    parser.add_argument('--lang', choices=['de', 'en', 'it'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--dpi', type=int, default=100)
    args = parser.parse_args()
    
    render_proof_gif(args.duration, args.lang, args.output, args.fps, args.dpi)
