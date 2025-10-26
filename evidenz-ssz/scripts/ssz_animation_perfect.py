#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ vs ΛCDM Animation - Perfekte Version
Hochwertige Visualisierung mit allen Details

© 2025 Carmen Wrede, Lino Casu
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
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
print("SSZ Animation - PERFEKTE VERSION")
print("="*70)
print("\nHochwertige Visualisierung mit:")
print("  • 30 fps (smooth playback)")
print("  • 25 Sekunden Dauer")
print("  • Erweiterte Partikel-Systeme")
print("  • Professionelle Farbpalette")
print("  • Physikalisch korrekte Darstellung")
print("  • Titel und Beschriftungen")
print("\nOutput: D:\\ssz_perfect_demo.gif\n")

# Animation parameters
duration_s = 25
fps = 30
total_frames = duration_s * fps

# Enhanced color palettes
colors_lcdm = {
    'particles': ['#ffcc00', '#ff8800', '#ff4400', '#cc0044', '#880088'],
    'glow': '#ffffff',
    'bg': '#0a0a1e',
    'label': '#ffaa00'
}

colors_ssz = {
    'segments': ['#00ccff', '#00aadd', '#0088bb', '#006699', '#004477'],
    'spiral': '#f7b733',
    'particles': '#4ecdc4',
    'bg': '#0a1a2e',
    'label': '#00ccff'
}

# Setup figure
fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor='black')

# Left panel
ax_left = fig.add_axes([0.00, 0.00, 0.48, 1.00])
# Right panel  
ax_right = fig.add_axes([0.52, 0.00, 0.48, 1.00])

# Divider with gradient
ax_div = fig.add_axes([0.48, 0.00, 0.04, 1.00])
ax_div.axis('off')

def ease_in_out_cubic(t):
    """Smooth easing function"""
    return 3*t**2 - 2*t**3 if t < 0.5 else 1 - (-2*t + 2)**3 / 2

def render_bigbang(ax, t_norm):
    """ΛCDM: Enhanced radial explosion with singularity"""
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor(colors_lcdm['bg'])
    
    center_x, center_y = 0.5, 0.5
    
    # Smooth expansion
    expansion = ease_in_out_cubic(t_norm) ** 0.6
    
    # Multi-layer particle system
    n_layers = 5
    particles_per_layer = 40
    
    for layer in range(n_layers):
        layer_expansion = expansion * (1 + layer * 0.15)
        layer_alpha = 0.8 - layer * 0.15
        
        for i in range(particles_per_layer):
            angle = 2 * PI * i / particles_per_layer + layer * 0.3 + t_norm * 0.3
            radius = layer_expansion * 0.42
            
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            
            # Color cycling
            color_idx = int((i / particles_per_layer + t_norm + layer * 0.2) * len(colors_lcdm['particles'])) % len(colors_lcdm['particles'])
            color = colors_lcdm['particles'][color_idx]
            
            # Size decreases with expansion
            size = 60 * (1 - expansion * 0.7) * (1 - layer * 0.1)
            
            ax.scatter(x, y, c=color, s=max(10, size), alpha=layer_alpha, edgecolors='white', linewidths=0.5)
    
    # Central singularity glow
    if t_norm < 0.4:
        intensity = 1 - t_norm / 0.4
        glow_size = 3000 * intensity
        ax.scatter(center_x, center_y, c=colors_lcdm['glow'], s=glow_size, alpha=0.6 * intensity)
        
        # Inner bright core
        core_size = 800 * intensity
        ax.scatter(center_x, center_y, c=colors_lcdm['glow'], s=core_size, alpha=0.9 * intensity)
    
    # Expanding shockwave rings
    n_rings = 3
    for ring in range(n_rings):
        ring_phase = (t_norm - ring * 0.15) % 1.0
        if ring_phase > 0 and ring_phase < 0.8:
            ring_radius = ring_phase * 0.45
            ring_alpha = 0.5 * (1 - ring_phase / 0.8)
            circle = Circle((center_x, center_y), ring_radius, fill=False, 
                          edgecolor=colors_lcdm['particles'][ring % len(colors_lcdm['particles'])],
                          linewidth=2, alpha=ring_alpha)
            ax.add_patch(circle)
    
    # Title
    ax.text(0.5, 0.95, 'ΛCDM Big Bang', ha='center', va='top',
           fontsize=28, fontweight='bold', color=colors_lcdm['label'],
           transform=ax.transAxes, alpha=0.9)
    
    # Subtitle
    ax.text(0.5, 0.90, 'Singularität → Expansion', ha='center', va='top',
           fontsize=16, color=colors_lcdm['label'], style='italic',
           transform=ax.transAxes, alpha=0.7)

def render_ssz(ax, t_norm):
    """SSZ: Enhanced segmented spacetime with φ-structure"""
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor(colors_ssz['bg'])
    
    center_x, center_y = 0.5, 0.5
    
    # Hexagonal segment grid with φ-based scaling
    n_rings = 6
    hex_radius = 0.06
    
    for ring in range(n_rings):
        # φ-based ring spacing
        ring_radius = hex_radius * PHI ** (ring * 0.5) * 1.2
        n_segments = 6 * max(ring, 1)
        
        for i in range(n_segments):
            angle = 2 * PI * i / n_segments + t_norm * 0.25 * (1 if ring % 2 == 0 else -1)
            x = center_x + ring_radius * np.cos(angle)
            y = center_y + ring_radius * np.sin(angle)
            
            # Hexagon vertices
            hex_angles = np.linspace(0, 2*PI, 7) + angle + t_norm * 0.1
            hex_x = x + hex_radius * 0.4 * np.cos(hex_angles)
            hex_y = y + hex_radius * 0.4 * np.sin(hex_angles)
            
            # Dynamic color based on position and time
            color_idx = (ring + int(t_norm * 10) + i // 3) % len(colors_ssz['segments'])
            color = colors_ssz['segments'][color_idx]
            
            # Pulsing alpha
            alpha = 0.35 + 0.15 * np.sin(t_norm * 2 * PI + ring + i * 0.1)
            
            ax.fill(hex_x, hex_y, color=color, alpha=alpha, 
                   edgecolor='white', linewidth=0.8)
    
    # Multi-layer φ-Spiral
    n_spirals = 3
    for spiral_idx in range(n_spirals):
        theta = np.linspace(0, 4 * PI, 300)
        
        # φ-based logarithmic spiral
        r = 0.04 * PHI ** (theta / (2 * PI) - 1.5 + spiral_idx * 0.3)
        
        # Rotation with different speeds
        rotation = t_norm * 2 * PI * (1 + spiral_idx * 0.5)
        spiral_x = center_x + r * np.cos(theta + rotation)
        spiral_y = center_y + r * np.sin(theta + rotation)
        
        # Gradient color along spiral
        alpha_gradient = np.linspace(0.3, 0.9, len(spiral_x))
        
        for j in range(len(spiral_x) - 1):
            ax.plot(spiral_x[j:j+2], spiral_y[j:j+2], 
                   color=colors_ssz['spiral'], linewidth=2.5, 
                   alpha=alpha_gradient[j] * (0.8 - spiral_idx * 0.2))
    
    # Orbital particle system (resonance)
    n_orbits = 4
    particles_per_orbit = 20
    
    for orbit in range(n_orbits):
        orbit_radius = 0.12 + orbit * 0.06
        orbit_speed = (orbit + 1) * 2
        
        for i in range(particles_per_orbit):
            # φ-based phase distribution
            phase = 2 * PI * i / particles_per_orbit
            orbit_angle = phase + t_norm * orbit_speed * PI
            
            # Pulsing radius (breathing)
            radius_pulse = 1 + 0.15 * np.sin(t_norm * 3 * PI + orbit)
            
            px = center_x + orbit_radius * radius_pulse * np.cos(orbit_angle)
            py = center_y + orbit_radius * radius_pulse * np.sin(orbit_angle)
            
            # Particle size based on orbit
            size = 25 - orbit * 3
            alpha = 0.9 - orbit * 0.15
            
            ax.scatter(px, py, c=colors_ssz['particles'], s=size, 
                      alpha=alpha, edgecolors='white', linewidths=0.8)
    
    # Central φ-symbol
    ax.text(center_x, center_y, 'φ', ha='center', va='center',
           fontsize=40, fontweight='bold', color=colors_ssz['spiral'],
           alpha=0.3 + 0.2 * np.sin(t_norm * 2 * PI))
    
    # Title
    ax.text(0.5, 0.95, 'Segmentierte Raumzeit (SSZ)', ha='center', va='top',
           fontsize=28, fontweight='bold', color=colors_ssz['label'],
           transform=ax.transAxes, alpha=0.9)
    
    # Subtitle
    ax.text(0.5, 0.90, 'Geordnete Entfaltung via φ', ha='center', va='top',
           fontsize=16, color=colors_ssz['label'], style='italic',
           transform=ax.transAxes, alpha=0.7)

def update_frame(frame_num):
    """Update animation with smooth transitions"""
    t_norm = frame_num / total_frames
    
    render_bigbang(ax_left, t_norm)
    render_ssz(ax_right, t_norm)
    
    # Divider gradient effect
    ax_div.clear()
    ax_div.axis('off')
    gradient = np.linspace(0, 1, 256).reshape(1, 256)
    ax_div.imshow(gradient, extent=[0, 1, 0, 1], aspect='auto', 
                 cmap='gray', alpha=0.4)
    
    # Progress indicator (every 30 frames = 1 second)
    if frame_num % 30 == 0:
        seconds = frame_num // 30
        print(f"  {seconds:2d}s / {duration_s}s ({100*t_norm:5.1f}%)")
    
    return ax_left, ax_right, ax_div

# Create animation
print(f"Rendering {total_frames} frames @ {fps} fps...\n")

anim = FuncAnimation(
    fig,
    update_frame,
    frames=total_frames,
    interval=1000/fps,
    blit=False
)

# Save with high quality
output_file = Path("D:\\ssz_perfect_demo.gif")
print("Saving high-quality GIF...")
print("(Dies kann 2-3 Minuten dauern...)\n")

try:
    anim.save(str(output_file), writer='pillow', fps=fps, dpi=100)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    
    print("\n" + "="*70)
    print("✓ PERFEKTE ANIMATION ERSTELLT!")
    print("="*70)
    print(f"\nDatei: {output_file}")
    print(f"Größe: {file_size:.1f} MB")
    print(f"Dauer: {duration_s} Sekunden @ {fps} fps")
    print(f"Frames: {total_frames}")
    print(f"Auflösung: 1920×1080")
    print("\nFeatures:")
    print("  ✓ Smooth 30 fps Playback")
    print("  ✓ Multi-Layer Partikel-Systeme")
    print("  ✓ φ-basierte Spiralen (golden ratio)")
    print("  ✓ Dynamische Farb-Gradienten")
    print("  ✓ Pulsing & Breathing Effekte")
    print("  ✓ Professionelle Beschriftungen")
    print("  ✓ Physikalisch korrekte Darstellung")
    print("="*70)
    
except Exception as e:
    print(f"\n✗ Fehler: {e}")
    import traceback
    traceback.print_exc()

plt.close(fig)
