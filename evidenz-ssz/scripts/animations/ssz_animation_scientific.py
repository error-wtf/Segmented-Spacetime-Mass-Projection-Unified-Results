#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ vs ΛCDM Animation - WISSENSCHAFTLICHE VERSION
Zeigt den fundamentalen Unterschied: Singularität vs. Segmentierte Struktur

© 2025 Carmen Wrede, Lino Casu
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, FancyBboxPatch
from pathlib import Path

# UTF-8 setup
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Physics constants
PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

print("="*70)
print("SSZ Animation - WISSENSCHAFTLICHE VERSION")
print("="*70)
print("\nKernbotschaft:")
print("  • Links: ΛCDM - Singularität als Problem")
print("  • Rechts: SSZ - Strukturierter Anfang")
print("  • Keine Explosion, sondern Entfaltung")
print("  • Resonanz-Limit statt Unendlichkeit")
print("\nOutput: D:\\ssz_scientific.gif\n")

# Animation parameters
duration_s = 30
fps = 30
total_frames = duration_s * fps

# Enhanced color palettes
colors_lcdm = {
    'particles': ['#ff0000', '#ff4400', '#ff8800', '#ffcc00'],  # Warnung: Rot
    'problem': '#ff0000',  # Problem-Marker
    'bg': '#1a0a0a',
    'text': '#ff6666'
}

colors_ssz = {
    'segments': ['#0088ff', '#00aaff', '#00ccff', '#00eeff'],
    'structure': '#00ffaa',
    'bg': '#0a0a1a',
    'text': '#00ffcc'
}

# Setup figure
fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor='black')
ax_left = fig.add_axes([0.00, 0.00, 0.48, 1.00])
ax_right = fig.add_axes([0.52, 0.00, 0.48, 1.00])

def ease_in_out_cubic(t):
    """Smooth easing"""
    return 3*t**2 - 2*t**3 if t < 0.5 else 1 - (-2*t + 2)**3 / 2

def render_lcdm_problem(ax, t_norm):
    """ΛCDM: Singularität als mathematisches Problem"""
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor(colors_lcdm['bg'])
    
    center_x, center_y = 0.5, 0.5
    expansion = ease_in_out_cubic(t_norm) ** 0.6
    
    # PROBLEM: Unendliche Dichte im Zentrum (blinkt)
    if t_norm < 0.5:
        # Singularität als "Problemzone"
        intensity = 1 - t_norm / 0.5
        
        # Warnung: Mathematisch instabil
        warning_alpha = 0.8 * (0.5 + 0.5 * np.sin(t_norm * 20 * PI))
        
        # Rotes Zentrum (Problem!)
        ax.scatter(center_x, center_y, c=colors_lcdm['problem'], 
                  s=3000 * intensity, alpha=warning_alpha, marker='*')
        
        # Warnungs-Ringe
        for ring in range(3):
            ring_phase = (t_norm * 3 - ring * 0.3) % 1.0
            if 0 < ring_phase < 0.8:
                ring_radius = ring_phase * 0.15
                ring_alpha = 0.6 * (1 - ring_phase / 0.8)
                circle = Circle((center_x, center_y), ring_radius, fill=False,
                              edgecolor=colors_lcdm['problem'], linewidth=3, 
                              alpha=ring_alpha, linestyle='--')
                ax.add_patch(circle)
        
        # Text: "Unendliche Dichte?"
        if t_norm < 0.3:
            ax.text(center_x, center_y - 0.15, '∞ ?', ha='center', va='top',
                   fontsize=60, color=colors_lcdm['problem'], 
                   alpha=warning_alpha, weight='bold')
    
    # Radiale Expansion (chaotisch)
    n_particles = 120
    for i in range(n_particles):
        angle = 2 * PI * i / n_particles + t_norm * 0.5
        
        # Chaotische Expansion
        noise = 0.1 * np.sin(i * 13.7 + t_norm * 10)
        radius = expansion * (0.45 + noise)
        
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        
        # Farbe: Rot → Gelb (abkühlend)
        color_idx = int((expansion + i / n_particles) * len(colors_lcdm['particles'])) % len(colors_lcdm['particles'])
        color = colors_lcdm['particles'][color_idx]
        
        size = 40 * (1 - expansion * 0.7)
        alpha = 0.7 - expansion * 0.3
        
        ax.scatter(x, y, c=color, s=max(10, size), alpha=alpha, 
                  edgecolors='white', linewidths=0.3)
    
    # Titel
    ax.text(0.5, 0.97, 'ΛCDM: "Big Bang"', ha='center', va='top',
           fontsize=32, fontweight='bold', color=colors_lcdm['text'],
           transform=ax.transAxes, alpha=0.9)
    
    # Kernproblem
    ax.text(0.5, 0.92, 'Singularität: ρ → ∞', ha='center', va='top',
           fontsize=20, color=colors_lcdm['text'], style='italic',
           transform=ax.transAxes, alpha=0.8)
    
    # Fußnote
    if t_norm > 0.6:
        ax.text(0.5, 0.05, 'Mathematisch instabil', ha='center', va='bottom',
               fontsize=16, color=colors_lcdm['problem'],
               transform=ax.transAxes, alpha=0.6)

def render_ssz_structure(ax, t_norm):
    """SSZ: Geordnete Entfaltung aus strukturiertem Anfang"""
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor(colors_ssz['bg'])
    
    center_x, center_y = 0.5, 0.5
    
    # KEIN zentraler Punkt - stattdessen: Segment-Layer
    unfold_factor = ease_in_out_cubic(t_norm)
    
    # Zentrale Segment-Schicht (KEIN Punkt!)
    if t_norm < 0.4:
        # Ursprungsschicht: Geordnete Hexagone
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
        
        # Text: "Endliche Dichte"
        if t_norm < 0.25:
            ax.text(center_x, center_y - 0.12, 'ρ_max', ha='center', va='top',
                   fontsize=40, color=colors_ssz['structure'], 
                   alpha=0.9, weight='bold')
    
    # Entfaltung der Segment-Ringe (φ-basiert)
    n_rings = 7
    for ring in range(n_rings):
        # φ-basierter Abstand
        ring_radius = 0.08 * PHI ** (ring * 0.4) * (1 + unfold_factor * 2)
        n_segments = 6 * max(ring, 1)
        
        # Sanfte Rotation
        rotation = unfold_factor * 0.3 * (1 if ring % 2 == 0 else -1)
        
        for i in range(n_segments):
            angle = 2 * PI * i / n_segments + rotation
            x = center_x + ring_radius * np.cos(angle)
            y = center_y + ring_radius * np.sin(angle)
            
            # Hexagon
            hex_radius = 0.04 * (1 + 0.2 * np.sin(unfold_factor * 2 * PI))
            hex_angles = np.linspace(0, 2*PI, 7) + angle
            hex_x = x + hex_radius * np.cos(hex_angles)
            hex_y = y + hex_radius * np.sin(hex_angles)
            
            # Farbe: Tiefes Blau → Helles Cyan
            color_idx = (ring + int(t_norm * 8)) % len(colors_ssz['segments'])
            color = colors_ssz['segments'][color_idx]
            
            # Pulsing alpha
            alpha = 0.4 + 0.15 * np.sin(t_norm * 2 * PI + ring)
            
            ax.fill(hex_x, hex_y, color=color, alpha=alpha,
                   edgecolor='white', linewidth=0.8)
    
    # φ-Spiral (Struktur-Marker)
    theta = np.linspace(0, 4 * PI, 400)
    r = 0.04 * PHI ** (theta / (2 * PI) - 1.2)
    
    spiral_rotation = unfold_factor * 2 * PI
    spiral_x = center_x + r * np.cos(theta + spiral_rotation)
    spiral_y = center_y + r * np.sin(theta + spiral_rotation)
    
    # Gradient entlang Spirale
    for j in range(len(spiral_x) - 1):
        alpha_grad = 0.3 + 0.5 * (j / len(spiral_x))
        ax.plot(spiral_x[j:j+2], spiral_y[j:j+2], 
               color=colors_ssz['structure'], linewidth=2.5, alpha=alpha_grad)
    
    # Titel
    ax.text(0.5, 0.97, 'SSZ: Segmentierte Raumzeit', ha='center', va='top',
           fontsize=32, fontweight='bold', color=colors_ssz['text'],
           transform=ax.transAxes, alpha=0.9)
    
    # Kernbotschaft
    ax.text(0.5, 0.92, 'Strukturierter Anfang', ha='center', va='top',
           fontsize=20, color=colors_ssz['text'], style='italic',
           transform=ax.transAxes, alpha=0.8)
    
    # Fußnote
    if t_norm > 0.6:
        ax.text(0.5, 0.05, 'Mathematisch stabil', ha='center', va='bottom',
               fontsize=16, color=colors_ssz['structure'],
               transform=ax.transAxes, alpha=0.6)

def update_frame(frame_num):
    """Update animation"""
    t_norm = frame_num / total_frames
    
    render_lcdm_problem(ax_left, t_norm)
    render_ssz_structure(ax_right, t_norm)
    
    # Progress
    if frame_num % 30 == 0:
        seconds = frame_num // 30
        print(f"  {seconds:2d}s / {duration_s}s ({100*t_norm:5.1f}%)")
    
    return ax_left, ax_right

# Create animation
print(f"Rendering {total_frames} frames @ {fps} fps...\n")

anim = FuncAnimation(
    fig,
    update_frame,
    frames=total_frames,
    interval=1000/fps,
    blit=False
)

# Save
output_file = Path("D:\\ssz_scientific.gif")
print("Saving scientific GIF...")

try:
    anim.save(str(output_file), writer='pillow', fps=fps, dpi=100)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    
    print("\n" + "="*70)
    print("✓ WISSENSCHAFTLICHE ANIMATION ERSTELLT!")
    print("="*70)
    print(f"\nDatei: {output_file}")
    print(f"Größe: {file_size:.1f} MB")
    print(f"Dauer: {duration_s} Sekunden @ {fps} fps")
    print(f"\nBotschaft:")
    print("  • ΛCDM: Singularität = Mathematisches Problem")
    print("  • SSZ: Strukturierter Anfang = Stabiler Zustand")
    print("  • Keine Explosion → Geordnete Entfaltung")
    print("  • ρ_max statt ρ → ∞")
    print("="*70)
    
except Exception as e:
    print(f"\n✗ Fehler: {e}")
    import traceback
    traceback.print_exc()

plt.close(fig)
