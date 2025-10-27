#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ GIF Renderer Part 1 - Vereinfachte Intro-Visualisierung
Basiert auf create_all_language_versions.py, Audio-Längen-angepasst

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
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

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PI = np.pi

# ============================================================================
# TEXTS
# ============================================================================

TEXTS = {
    'de': {
        'lcdm_title': 'ΛCDM Big Bang',
        'lcdm_subtitle': 'Singularität: ρ → ∞',
        'lcdm_problem': 'Mathematisch instabil',
        'ssz_title': 'SSZ: Segmentierte Raumzeit',
        'ssz_subtitle': 'Strukturierter Anfang',
        'ssz_stable': 'Mathematisch stabil',
        'infinity': '∞ ?',
        'rho_max': 'ρ_max'
    },
    'en': {
        'lcdm_title': 'ΛCDM Big Bang',
        'lcdm_subtitle': 'Singularity: ρ → ∞',
        'lcdm_problem': 'Mathematically unstable',
        'ssz_title': 'SSZ: Segmented Spacetime',
        'ssz_subtitle': 'Structured Beginning',
        'ssz_stable': 'Mathematically stable',
        'infinity': '∞ ?',
        'rho_max': 'ρ_max'
    },
    'it': {
        'lcdm_title': 'ΛCDM Big Bang',
        'lcdm_subtitle': 'Singolarità: ρ → ∞',
        'lcdm_problem': 'Matematicamente instabile',
        'ssz_title': 'SSZ: Spaziotempo Segmentato',
        'ssz_subtitle': 'Inizio Strutturato',
        'ssz_stable': 'Matematicamente stabile',
        'infinity': '∞ ?',
        'rho_max': 'ρ_max'
    }
}

# ============================================================================
# COLOR SCHEMES
# ============================================================================

colors_lcdm = {
    'particles': ['#ff0000', '#ff4400', '#ff8800', '#ffcc00'],
    'problem': '#ff0000',
    'bg': '#1a0a0a',
    'text': '#ff6666'
}

colors_ssz = {
    'segments': ['#0088ff', '#00aaff', '#00ccff', '#00eeff'],
    'structure': '#00ffaa',
    'bg': '#0a0a1a',
    'text': '#00ffcc'
}

# ============================================================================
# EASING FUNCTION
# ============================================================================

def ease_in_out_cubic(t):
    """Smooth easing function"""
    return 3*t**2 - 2*t**3 if t < 0.5 else 1 - (-2*t + 2)**3 / 2

# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def render_lcdm_problem(ax, t_norm, lang):
    """ΛCDM mit Singularitäts-Problem"""
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor(colors_lcdm['bg'])
    
    center_x, center_y = 0.5, 0.5
    expansion = ease_in_out_cubic(t_norm) ** 0.6
    
    # Singularität (blinkend)
    if t_norm < 0.5:
        intensity = 1 - t_norm / 0.5
        warning_alpha = 0.8 * (0.5 + 0.5 * np.sin(t_norm * 20 * PI))
        
        ax.scatter(center_x, center_y, c=colors_lcdm['problem'], 
                  s=3000 * intensity, alpha=warning_alpha, marker='*')
        
        # Warnringe
        for ring in range(3):
            ring_phase = (t_norm * 3 - ring * 0.3) % 1.0
            if 0 < ring_phase < 0.8:
                ring_radius = ring_phase * 0.15
                ring_alpha = 0.6 * (1 - ring_phase / 0.8)
                circle = Circle((center_x, center_y), ring_radius, fill=False,
                              edgecolor=colors_lcdm['problem'], linewidth=3, 
                              alpha=ring_alpha, linestyle='--')
                ax.add_patch(circle)
        
        if t_norm < 0.3:
            ax.text(center_x, center_y - 0.15, TEXTS[lang]['infinity'], 
                   ha='center', va='top', fontsize=60, 
                   color=colors_lcdm['problem'], alpha=warning_alpha, weight='bold')
    
    # Partikel
    n_particles = 120
    for i in range(n_particles):
        angle = 2 * PI * i / n_particles + t_norm * 0.5
        noise = 0.1 * np.sin(i * 13.7 + t_norm * 10)
        radius = expansion * (0.45 + noise)
        
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        
        color_idx = int((expansion + i / n_particles) * len(colors_lcdm['particles'])) % len(colors_lcdm['particles'])
        color = colors_lcdm['particles'][color_idx]
        size = 40 * (1 - expansion * 0.7)
        
        ax.scatter(x, y, c=color, s=max(10, size), alpha=0.7 - expansion * 0.3, 
                  edgecolors='white', linewidths=0.3)
    
    # Text
    ax.text(0.5, 0.97, TEXTS[lang]['lcdm_title'], ha='center', va='top',
           fontsize=32, fontweight='bold', color=colors_lcdm['text'],
           transform=ax.transAxes, alpha=0.9)
    ax.text(0.5, 0.92, TEXTS[lang]['lcdm_subtitle'], ha='center', va='top',
           fontsize=20, color=colors_lcdm['text'], style='italic',
           transform=ax.transAxes, alpha=0.8)
    if t_norm > 0.6:
        ax.text(0.5, 0.05, TEXTS[lang]['lcdm_problem'], ha='center', va='bottom',
               fontsize=16, color=colors_lcdm['problem'],
               transform=ax.transAxes, alpha=0.6)

def render_ssz_structure(ax, t_norm, lang):
    """SSZ mit Segment-Struktur"""
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor(colors_ssz['bg'])
    
    center_x, center_y = 0.5, 0.5
    unfold_factor = ease_in_out_cubic(t_norm)
    
    # Ursprungsschicht
    if t_norm < 0.4:
        core_size = 0.08 * (1 - unfold_factor)
        for i in range(6):
            angle = i * PI / 3 + t_norm * 0.2
            cx = center_x + core_size * np.cos(angle)
            cy = center_y + core_size * np.sin(angle)
            
            hex_angles = np.linspace(0, 2*PI, 7) + angle
            hex_x = cx + core_size * 0.3 * np.cos(hex_angles)
            hex_y = cy + core_size * 0.3 * np.sin(hex_angles)
            
            ax.fill(hex_x, hex_y, color=colors_ssz['structure'], 
                   alpha=0.8, edgecolor='white', linewidth=1.5)
        
        if t_norm < 0.25:
            ax.text(center_x, center_y - 0.12, TEXTS[lang]['rho_max'], 
                   ha='center', va='top', fontsize=40, 
                   color=colors_ssz['structure'], alpha=0.9, weight='bold')
    
    # Hexagon-Ringe
    n_rings = 7
    for ring in range(n_rings):
        ring_radius = 0.08 * PHI ** (ring * 0.4) * (1 + unfold_factor * 2)
        n_segments = 6 * max(ring, 1)
        rotation = unfold_factor * 0.3 * (1 if ring % 2 == 0 else -1)
        
        for i in range(n_segments):
            angle = 2 * PI * i / n_segments + rotation
            x = center_x + ring_radius * np.cos(angle)
            y = center_y + ring_radius * np.sin(angle)
            
            hex_radius = 0.04 * (1 + 0.2 * np.sin(unfold_factor * 2 * PI))
            hex_angles = np.linspace(0, 2*PI, 7) + angle
            hex_x = x + hex_radius * np.cos(hex_angles)
            hex_y = y + hex_radius * np.sin(hex_angles)
            
            color_idx = (ring + int(t_norm * 8)) % len(colors_ssz['segments'])
            alpha = 0.4 + 0.15 * np.sin(t_norm * 2 * PI + ring)
            
            ax.fill(hex_x, hex_y, color=colors_ssz['segments'][color_idx], 
                   alpha=alpha, edgecolor='white', linewidth=0.8)
    
    # φ-Spiral
    theta = np.linspace(0, 4 * PI, 400)
    r = 0.04 * PHI ** (theta / (2 * PI) - 1.2)
    spiral_rotation = unfold_factor * 2 * PI
    spiral_x = center_x + r * np.cos(theta + spiral_rotation)
    spiral_y = center_y + r * np.sin(theta + spiral_rotation)
    
    for j in range(len(spiral_x) - 1):
        alpha_grad = 0.3 + 0.5 * (j / len(spiral_x))
        ax.plot(spiral_x[j:j+2], spiral_y[j:j+2], 
               color=colors_ssz['structure'], linewidth=2.5, alpha=alpha_grad)
    
    # Text
    ax.text(0.5, 0.97, TEXTS[lang]['ssz_title'], ha='center', va='top',
           fontsize=32, fontweight='bold', color=colors_ssz['text'],
           transform=ax.transAxes, alpha=0.9)
    ax.text(0.5, 0.92, TEXTS[lang]['ssz_subtitle'], ha='center', va='top',
           fontsize=20, color=colors_ssz['text'], style='italic',
           transform=ax.transAxes, alpha=0.8)
    if t_norm > 0.6:
        ax.text(0.5, 0.05, TEXTS[lang]['ssz_stable'], ha='center', va='bottom',
               fontsize=16, color=colors_ssz['structure'],
               transform=ax.transAxes, alpha=0.6)

# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_intro_gif(
    duration: float,
    lang: str,
    output_path: Path,
    fps: int = 30,
    dpi: int = 100
):
    """
    Rendert Intro-GIF mit Audio-angepasster Länge.
    
    Args:
        duration: Audio-Dauer in Sekunden
        lang: 'de', 'en', 'it'
        output_path: Output GIF-Pfad
        fps: Frames per second
        dpi: Resolution (100 = 1920x1080)
    """
    if lang not in TEXTS:
        raise ValueError(f"Unsupported language: {lang}")
    
    total_frames = int(duration * fps)
    
    print(f"\n{'='*70}")
    print(f"RENDERING INTRO GIF: {lang.upper()}")
    print(f"{'='*70}")
    print(f"Duration: {duration:.2f}s")
    print(f"FPS: {fps}")
    print(f"Total Frames: {total_frames}")
    print(f"Output: {output_path}")
    
    # Figure setup (1920x1080 at 100dpi)
    fig = plt.figure(figsize=(19.2, 10.8), dpi=dpi, facecolor='black')
    ax_left = fig.add_axes([0.00, 0.00, 0.48, 1.00])
    ax_right = fig.add_axes([0.52, 0.00, 0.48, 1.00])
    
    def update_frame(frame_num):
        t_norm = frame_num / total_frames
        render_lcdm_problem(ax_left, t_norm, lang)
        render_ssz_structure(ax_right, t_norm, lang)
        
        if frame_num % (fps * 5) == 0:  # Alle 5 Sekunden
            elapsed = frame_num / fps
            print(f"  {elapsed:.1f}s / {duration:.1f}s ({100*elapsed/duration:.0f}%)")
        
        return ax_left, ax_right
    
    # Animation erstellen
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
    
    parser = argparse.ArgumentParser(description='SSZ Intro GIF Renderer')
    parser.add_argument('--duration', type=float, required=True, help='Audio duration in seconds')
    parser.add_argument('--lang', choices=['de', 'en', 'it'], required=True, help='Language')
    parser.add_argument('--output', type=Path, required=True, help='Output GIF path')
    parser.add_argument('--fps', type=int, default=30, help='FPS (default: 30)')
    parser.add_argument('--dpi', type=int, default=100, help='DPI (default: 100)')
    
    args = parser.parse_args()
    
    render_intro_gif(
        duration=args.duration,
        lang=args.lang,
        output_path=args.output,
        fps=args.fps,
        dpi=args.dpi
    )
