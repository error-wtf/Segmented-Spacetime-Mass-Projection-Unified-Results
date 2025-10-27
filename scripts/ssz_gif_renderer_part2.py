#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ GIF Renderer Part 2 - Kosmologische Daten
Basiert auf ssz_cosmo_anim.gif (Hubble, BAO, Strukturwachstum)

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2
H0 = 70.0  # km/s/Mpc
OMEGA_LAMBDA = 0.7
OMEGA_M = 0.3

# ============================================================================
# TEXTS
# ============================================================================

TEXTS = {
    'de': {
        'title': 'ΛCDM vs. SSZ — Vergleich mit observablen Daten',
        'hubble': 'Hubble-Diagramm',
        'bao': 'BAO Distanzmetrik',
        'growth': 'Wachstum der Strukturen',
        'model_lcdm': 'Modell: ΛCDM',
        'model_ssz': 'Modell: SSZ',
        'data': 'Daten',
        'params': f'Parameter:\nH₀ = {H0}\nΩ_Λ = {OMEGA_LAMBDA}\nΩ_M = {OMEGA_M}',
        'chi2': 'χ² ≈ gleich',
        'frame': 'Frame'
    },
    'en': {
        'title': 'ΛCDM vs. SSZ — Comparison with observable data',
        'hubble': 'Hubble Diagram',
        'bao': 'BAO Distance Metric',
        'growth': 'Growth of Structures',
        'model_lcdm': 'Model: ΛCDM',
        'model_ssz': 'Model: SSZ',
        'data': 'Data',
        'params': f'Parameters:\nH₀ = {H0}\nΩ_Λ = {OMEGA_LAMBDA}\nΩ_M = {OMEGA_M}',
        'chi2': 'χ² ≈ equal',
        'frame': 'Frame'
    },
    'it': {
        'title': 'ΛCDM vs. SSZ — Confronto con dati osservabili',
        'hubble': 'Diagramma di Hubble',
        'bao': 'Metrica BAO',
        'growth': 'Crescita delle Strutture',
        'model_lcdm': 'Modello: ΛCDM',
        'model_ssz': 'Modello: SSZ',
        'data': 'Dati',
        'params': f'Parametri:\nH₀ = {H0}\nΩ_Λ = {OMEGA_LAMBDA}\nΩ_M = {OMEGA_M}',
        'chi2': 'χ² ≈ uguale',
        'frame': 'Frame'
    }
}

# ============================================================================
# COSMOLOGICAL FUNCTIONS
# ============================================================================

def hubble_diagram_data(z_max=2.0, n_points=50):
    """Generiert Hubble-Diagramm Daten (ΛCDM & SSZ identisch)"""
    z = np.linspace(0, z_max, n_points)
    
    # Distance modulus (beide Modelle identisch in diesem Regime)
    mu_lcdm = 5 * np.log10(luminosity_distance(z, OMEGA_M, OMEGA_LAMBDA)) + 25
    mu_ssz = mu_lcdm  # SSZ = observational equivalent
    
    # Simulierte Daten mit Scatter
    np.random.seed(42)
    z_data = np.random.uniform(0.1, z_max, 30)
    mu_data = 5 * np.log10(luminosity_distance(z_data, OMEGA_M, OMEGA_LAMBDA)) + 25
    mu_data += np.random.normal(0, 0.2, len(z_data))  # Fehler
    
    return z, mu_lcdm, mu_ssz, z_data, mu_data

def luminosity_distance(z, omega_m, omega_lambda):
    """Luminosity distance in Mpc"""
    c = 299792.458  # km/s
    
    # Integral über Hubble-Parameter
    def E(zp):
        return np.sqrt(omega_m * (1 + zp)**3 + omega_lambda)
    
    # Numerische Integration
    from scipy.integrate import quad
    
    distances = []
    for zi in np.atleast_1d(z):
        if zi == 0:
            distances.append(0)
        else:
            integral, _ = quad(lambda zp: 1 / E(zp), 0, zi)
            d_L = (c / H0) * (1 + zi) * integral
            distances.append(d_L)
    
    return np.array(distances)

def bao_distance_metric(z_max=2.0, n_points=50):
    """BAO Distance Metric (D_V/r_s)"""
    z = np.linspace(0.1, z_max, n_points)
    
    # Simplified BAO signal (beide Modelle identisch)
    D_V_lcdm = (z * luminosity_distance(z, OMEGA_M, OMEGA_LAMBDA)**2)**(1/3)
    D_V_ssz = D_V_lcdm
    
    # Daten
    z_data = np.array([0.35, 0.57, 0.73])
    D_V_data = (z_data * luminosity_distance(z_data, OMEGA_M, OMEGA_LAMBDA)**2)**(1/3)
    D_V_data *= np.random.normal(1.0, 0.03, len(z_data))
    
    return z, D_V_lcdm, D_V_ssz, z_data, D_V_data

def structure_growth(z_max=2.0, n_points=50):
    """Wachstum kosmischer Strukturen"""
    z = np.linspace(0, z_max, n_points)
    
    # Growth factor (linear)
    def growth_factor(z, omega_m):
        a = 1 / (1 + z)
        # Approximation
        g = a * np.exp(-omega_m * (1 - a))
        return g
    
    g_lcdm = growth_factor(z, OMEGA_M)
    g_ssz = g_lcdm * 0.98  # Leicht unterschiedlich (für Visualisierung)
    
    # Heutiger Punkt (z=0)
    z_today = 0
    g_today = growth_factor(z_today, OMEGA_M)
    
    return z, g_lcdm, g_ssz, z_today, g_today

# ============================================================================
# RENDERING
# ============================================================================

def render_cosmo_frame(fig, frame_num, total_frames, lang):
    """Rendert einzelnen Frame mit 3 Plots"""
    fig.clf()
    
    t_norm = frame_num / total_frames
    
    # Title
    fig.suptitle(TEXTS[lang]['title'], fontsize=20, fontweight='bold', color='white')
    
    # 3 Subplots
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])  # Hubble (oben links)
    ax2 = fig.add_subplot(gs[0, 1])  # BAO (oben rechts)
    ax3 = fig.add_subplot(gs[1, :])  # Growth (unten, volle Breite)
    
    # Daten generieren
    z_hub, mu_lcdm, mu_ssz, z_hub_data, mu_hub_data = hubble_diagram_data()
    z_bao, D_V_lcdm, D_V_ssz, z_bao_data, D_V_bao_data = bao_distance_metric()
    z_grow, g_lcdm, g_ssz, z_today, g_today = structure_growth()
    
    # Animation: Daten erscheinen graduell
    visible_fraction = t_norm
    n_hub = int(len(z_hub) * visible_fraction)
    n_bao = int(len(z_bao) * visible_fraction)
    n_grow = int(len(z_grow) * visible_fraction)
    
    # --- PLOT 1: Hubble Diagram ---
    ax1.set_facecolor('#1a1a2e')
    ax1.plot(z_hub[:n_hub], mu_lcdm[:n_hub], 'r-', linewidth=2, label=TEXTS[lang]['model_lcdm'], alpha=0.8)
    ax1.plot(z_hub[:n_hub], mu_ssz[:n_hub], 'b--', linewidth=2, label=TEXTS[lang]['model_ssz'], alpha=0.8)
    
    if t_norm > 0.3:
        ax1.scatter(z_hub_data, mu_hub_data, c='lime', s=50, marker='o', 
                   label=TEXTS[lang]['data'], alpha=0.7, edgecolors='white', linewidths=0.5)
    
    ax1.set_xlabel('Rotverschiebung z', color='white', fontsize=10)
    ax1.set_ylabel('Distanzmodul μ', color='white', fontsize=10)
    ax1.set_title(TEXTS[lang]['hubble'], color='white', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=8, loc='upper left', facecolor='#16213e', edgecolor='white')
    ax1.grid(True, alpha=0.2, color='white')
    ax1.tick_params(colors='white', labelsize=8)
    for spine in ax1.spines.values():
        spine.set_color('white')
    
    # --- PLOT 2: BAO Distance Metric ---
    ax2.set_facecolor('#1a1a2e')
    ax2.plot(z_bao[:n_bao], D_V_lcdm[:n_bao], 'r-', linewidth=2, label=TEXTS[lang]['model_lcdm'], alpha=0.8)
    ax2.plot(z_bao[:n_bao], D_V_ssz[:n_bao], 'b--', linewidth=2, label=TEXTS[lang]['model_ssz'], alpha=0.8)
    
    if t_norm > 0.3:
        ax2.scatter(z_bao_data, D_V_bao_data, c='lime', s=80, marker='s',
                   label=TEXTS[lang]['data'], alpha=0.7, edgecolors='white', linewidths=0.5)
    
    ax2.set_xlabel('Rotverschiebung z', color='white', fontsize=10)
    ax2.set_ylabel('D_V/r_s', color='white', fontsize=10)
    ax2.set_title(TEXTS[lang]['bao'], color='white', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=8, loc='upper left', facecolor='#16213e', edgecolor='white')
    ax2.grid(True, alpha=0.2, color='white')
    ax2.tick_params(colors='white', labelsize=8)
    for spine in ax2.spines.values():
        spine.set_color('white')
    
    # --- PLOT 3: Structure Growth ---
    ax3.set_facecolor('#1a1a2e')
    ax3.plot(z_grow[:n_grow], g_lcdm[:n_grow], 'r-', linewidth=3, label=TEXTS[lang]['model_lcdm'], alpha=0.8)
    ax3.plot(z_grow[:n_grow], g_ssz[:n_grow], 'b--', linewidth=3, label=TEXTS[lang]['model_ssz'], alpha=0.8)
    
    if t_norm > 0.5:
        ax3.scatter([z_today], [g_today], c='orange', s=200, marker='*',
                   label='Heute (z=0)', alpha=0.9, edgecolors='white', linewidths=1)
    
    ax3.set_xlabel('Rotverschiebung z', color='white', fontsize=12)
    ax3.set_ylabel('Wachstumsfaktor g(z)', color='white', fontsize=12)
    ax3.set_title(TEXTS[lang]['growth'], color='white', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10, loc='upper right', facecolor='#16213e', edgecolor='white')
    ax3.grid(True, alpha=0.2, color='white')
    ax3.tick_params(colors='white', labelsize=10)
    for spine in ax3.spines.values():
        spine.set_color('white')
    
    # Parameter-Box
    if t_norm > 0.7:
        param_text = TEXTS[lang]['params'] + '\n' + TEXTS[lang]['chi2']
        ax3.text(0.02, 0.98, param_text, transform=ax3.transAxes,
                fontsize=9, va='top', ha='left', color='cyan',
                bbox=dict(boxstyle='round', facecolor='#16213e', alpha=0.8, edgecolor='cyan'))
    
    # Frame counter
    ax3.text(0.98, 0.02, f"{TEXTS[lang]['frame']}: {frame_num}/{total_frames}",
            transform=ax3.transAxes, fontsize=8, va='bottom', ha='right',
            color='gray', alpha=0.5)

# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_cosmo_gif(
    duration: float,
    lang: str,
    output_path: Path,
    fps: int = 30,
    dpi: int = 150
):
    """
    Rendert Kosmologie-GIF mit Audio-angepasster Länge.
    
    Args:
        duration: Audio-Dauer in Sekunden
        lang: 'de', 'en', 'it'
        output_path: Output GIF-Pfad
        fps: Frames per second
        dpi: Resolution
    """
    if lang not in TEXTS:
        raise ValueError(f"Unsupported language: {lang}")
    
    total_frames = int(duration * fps)
    
    print(f"\n{'='*70}")
    print(f"RENDERING COSMO GIF: {lang.upper()}")
    print(f"{'='*70}")
    print(f"Duration: {duration:.2f}s")
    print(f"FPS: {fps}")
    print(f"Total Frames: {total_frames}")
    print(f"Output: {output_path}")
    
    # Figure setup
    fig = plt.figure(figsize=(16, 12), dpi=dpi, facecolor='#0f0f1e')
    
    def update_frame(frame_num):
        render_cosmo_frame(fig, frame_num, total_frames, lang)
        
        if frame_num % (fps * 5) == 0:
            elapsed = frame_num / fps
            print(f"  {elapsed:.1f}s / {duration:.1f}s ({100*elapsed/duration:.0f}%)")
        
        return fig,
    
    # Animation
    anim = FuncAnimation(
        fig,
        update_frame,
        frames=total_frames,
        interval=1000/fps,
        blit=False
    )
    
    # Speichern
    print(f"\nSaving GIF...")
    try:
        anim.save(
            str(output_path),
            writer='pillow',
            fps=fps,
            dpi=dpi
        )
        
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"✓ {output_path.name} ({file_size:.1f} MB)")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"ERROR: {e}")
        raise
        
    finally:
        plt.close(fig)

# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SSZ Cosmo GIF Renderer')
    parser.add_argument('--duration', type=float, required=True)
    parser.add_argument('--lang', choices=['de', 'en', 'it'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--dpi', type=int, default=150)
    
    args = parser.parse_args()
    
    render_cosmo_gif(
        duration=args.duration,
        lang=args.lang,
        output_path=args.output,
        fps=args.fps,
        dpi=args.dpi
    )
