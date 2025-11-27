#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Animation - Vereinfachte Version OHNE FFmpeg
Nutzt nur matplotlib + imageio für GIF-Export

© 2025 Carmen Wrede, Lino Casu
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path

# UTF-8 setup
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Physics constants
PHI = (1 + np.sqrt(5)) / 2

print("="*70)
print("SSZ Animation - Vereinfachte Render-Version")
print("="*70)
print("\nErstelle Animation ohne FFmpeg...")
print("Output: D:\\ssz_bigbang_vs_ssz_demo.gif\n")

# Setup figure
fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor='black')

# Left panel
ax_left = fig.add_axes([0.00, 0.00, 0.48, 1.00])
# Right panel
ax_right = fig.add_axes([0.52, 0.00, 0.48, 1.00])
# Divider
ax_div = fig.add_axes([0.48, 0.00, 0.04, 1.00])
ax_div.axis('off')

# Animation parameters
duration_s = 10  # 10 Sekunden
fps = 15  # Reduziert für schnelleres Rendern
total_frames = duration_s * fps

colors_lcdm = ['#ffcc00', '#ff6600', '#ff3300', '#441144']
colors_ssz = ['#00ccff', '#1a1f2b', '#f7b733', '#4ecdc4']

def render_bigbang(ax, t_norm):
    """ΛCDM: Radial explosion"""
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor('#1a0a2e')
    
    center_x, center_y = 0.5, 0.5
    expansion = t_norm ** 0.7
    
    # Particles
    n_particles = 100  # Reduziert
    for i in range(n_particles):
        angle = 2 * np.pi * i / n_particles + t_norm * 0.5
        radius = expansion * 0.4
        
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        
        color_idx = int((i / n_particles + t_norm) * len(colors_lcdm)) % len(colors_lcdm)
        size = 50 * (1 - expansion * 0.8)
        
        ax.scatter(x, y, c=colors_lcdm[color_idx], s=size, alpha=0.6)
    
    # Central glow
    if t_norm < 0.3:
        glow_size = 2000 * (1 - t_norm / 0.3)
        ax.scatter(center_x, center_y, c='#ffffff', s=glow_size, alpha=0.5 * (1 - t_norm / 0.3))

def render_ssz(ax, t_norm):
    """SSZ: Segmented spacetime"""
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor('#0a1f2e')
    
    center_x, center_y = 0.5, 0.5
    
    # Hexagonal grid
    n_rings = 4  # Reduziert
    hex_radius = 0.08
    
    for ring in range(n_rings):
        ring_radius = (ring + 1) * hex_radius * 1.5
        n_segments = 6 * max(ring, 1)
        
        for i in range(n_segments):
            angle = 2 * np.pi * i / n_segments + t_norm * 0.3
            x = center_x + ring_radius * np.cos(angle)
            y = center_y + ring_radius * np.sin(angle)
            
            hex_angles = np.linspace(0, 2*np.pi, 7) + angle
            hex_x = x + hex_radius * 0.5 * np.cos(hex_angles)
            hex_y = y + hex_radius * 0.5 * np.sin(hex_angles)
            
            color_idx = (ring + int(t_norm * 10)) % len(colors_ssz)
            alpha = 0.3 + 0.2 * np.sin(t_norm * 2 * np.pi + ring)
            
            ax.fill(hex_x, hex_y, color=colors_ssz[color_idx], alpha=alpha, 
                   edgecolor='#ffffff', linewidth=0.5)
    
    # φ-Spiral
    theta = np.linspace(0, 4 * np.pi, 200)  # Reduziert
    r = 0.05 * PHI ** (theta / (2 * np.pi) - 2)
    
    rotation = t_norm * 2 * np.pi
    spiral_x = center_x + r * np.cos(theta + rotation)
    spiral_y = center_y + r * np.sin(theta + rotation)
    
    ax.plot(spiral_x, spiral_y, color='#f7b733', linewidth=2, alpha=0.7)
    
    # Orbital particles
    n_particles = 50  # Reduziert
    for i in range(n_particles):
        orbit_angle = 2 * np.pi * i / n_particles + t_norm * 4 * np.pi
        orbit_radius = 0.15 * (1 + 0.3 * np.sin(t_norm * 2 * np.pi))
        
        px = center_x + orbit_radius * np.cos(orbit_angle)
        py = center_y + orbit_radius * np.sin(orbit_angle)
        
        ax.scatter(px, py, c='#f7b733', s=20, alpha=0.8)

def update_frame(frame_num):
    """Update animation"""
    t_norm = frame_num / total_frames
    
    render_bigbang(ax_left, t_norm)
    render_ssz(ax_right, t_norm)
    
    if frame_num % 15 == 0:
        print(f"  Frame {frame_num}/{total_frames} ({100*t_norm:.1f}%)")
    
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

# Save as GIF
output_file = Path("D:\\ssz_bigbang_vs_ssz_demo.gif")
print("Saving GIF...")

try:
    anim.save(str(output_file), writer='pillow', fps=fps, dpi=100)
    print(f"\n✓ Animation gespeichert: {output_file}")
    print(f"  Größe: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"  Dauer: {duration_s} Sekunden")
    print(f"  Frames: {total_frames}")
except Exception as e:
    print(f"\n✗ Fehler beim Speichern: {e}")
    print("\nInstalliere pillow:")
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pillow'])
    print("\nBitte erneut ausführen: python ssz_simple_render.py")

plt.close(fig)

print("\n" + "="*70)
print("Fertig!")
print("="*70)
