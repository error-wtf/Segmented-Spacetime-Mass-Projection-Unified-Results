#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Black Hole Animation - Segmented Spacetime Framework
Visualisiert Raumzeit um ein Schwarzes Loch mit φ-basierter Geometrie

Mathematik aus: perfect_paired_test.py
Framework: Segmented Spacetime (Casu & Wrede)

© 2025 Carmen Wrede
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, FancyArrowPatch
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D
import os

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# ============================================================================
# Physikalische Konstanten (aus perfect_paired_test.py)
# ============================================================================
C = 299792458  # Lichtgeschwindigkeit [m/s]
G = 6.67430e-11  # Gravitationskonstante [m²/kg·s²]
PHI = (1 + 5**0.5) / 2  # Goldener Schnitt φ ≈ 1.618 (FUNDAMENTAL!)
M_SUN = 1.98847e30  # Sonnenmasse [kg]

# Schwarzes Loch Parameter - SAGITTARIUS A* (Galaktisches Zentrum)
M_BH = 4.154e6 * M_SUN  # Sagittarius A*: 4.154 Millionen Sonnenmassen
r_s = 2 * G * M_BH / (C**2)  # Schwarzschild-Radius [m]

print("="*80)
print("SAGITTARIUS A* - SEGMENTED SPACETIME ANIMATION")
print("="*80)
print(f"Galaktisches Zentrum (Supermassives Schwarzes Loch)")
print(f"Masse: M = {M_BH/M_SUN:.3e} M_sun = 4.154 Millionen Sonnenmassen")
print(f"Schwarzschild-Radius: r_s = {r_s:.2f} m = {r_s/1e6:.2f} Millionen km")
print(f"Photonen-Sphaere: r_ph = 1.5 r_s = {1.5*r_s/1e6:.2f} Millionen km")
print(f"Phi-Grenze: r_phi = {PHI:.3f} r_s = {PHI*r_s/1e6:.2f} Millionen km")
print(f"ISCO: r_isco = 3 r_s = {3*r_s/1e6:.2f} Millionen km")
print(f"Entfernung zur Erde: ~26,000 Lichtjahre")
print("="*80)

# ============================================================================
# Segmented Spacetime Funktionen
# ============================================================================

def gravitational_redshift(r, M=M_BH):
    """
    Gravitational Redshift in Segmented Spacetime
    z_grav = 1/√(1 - r_s/r) - 1
    """
    r_s = 2 * G * M / (C**2)
    x = r / r_s
    if x > 1.0:
        return 1.0 / np.sqrt(1 - 1.0/x) - 1.0
    else:
        return np.nan  # Inside horizon

def phi_correction(r, M=M_BH):
    """
    φ-basierte Masse-Korrektur (aus perfect_paired_test.py)
    ΔM(%) = A·exp(-α·r_s) + B
    """
    r_s_local = 2 * G * M / (C**2)
    # Kalibrierte Parameter aus φ-Geometrie
    A = 98.01
    ALPHA = 2.7177e4
    B = 1.96
    deltaM_pct = (A * np.exp(-ALPHA * r_s_local) + B)
    return 1.0 + deltaM_pct / 100.0

def time_dilation(r, M=M_BH):
    """
    Zeitdilatation: τ = 1/√(1 - r_s/r)
    """
    r_s = 2 * G * M / (C**2)
    x = r / r_s
    if x > 1.0:
        return 1.0 / np.sqrt(1 - 1.0/x)
    else:
        return np.inf

def segment_density(r, M=M_BH):
    """
    Segment-Dichte N(r) ~ φ·(r_s/r)²
    Basiert auf φ-Spirale Geometrie
    """
    r_s = 2 * G * M / (C**2)
    if r > 0:
        return PHI * (r_s / r)**2
    else:
        return np.inf

def orbital_velocity(r, M=M_BH):
    """
    Keplersche Orbitalgeschwindigkeit
    v_orb = √(GM/r)
    """
    if r > 0:
        return np.sqrt(G * M / r)
    else:
        return 0

def escape_velocity(r, M=M_BH):
    """
    Fluchtgeschwindigkeit
    v_esc = √(2GM/r)
    """
    if r > 0:
        return np.sqrt(2 * G * M / r)
    else:
        return 0

# ============================================================================
# Visualisierung Setup
# ============================================================================

# Normierte Koordinaten (r_s = 1)
r_s_norm = 1.0
r_photon = 1.5 * r_s_norm  # Photonen-Sphäre
r_isco = 3.0 * r_s_norm  # ISCO (Innermost Stable Circular Orbit)
r_phi = PHI * r_s_norm  # φ-Grenze ≈ 1.618 r_s

# Raster für Raumzeit-Gitter
theta = np.linspace(0, 2*np.pi, 100)
r_grid = np.linspace(1.0, 8.0, 50)  # Von Horizont bis 8 r_s

# ============================================================================
# Figur Setup (2 Zeilen, 3 Spalten - Werte-Panel rechts über 2 Zeilen)
# ============================================================================
fig = plt.figure(figsize=(24, 12), facecolor='#000')
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.4, left=0.05, right=0.98, top=0.95, bottom=0.05,
                     width_ratios=[1, 1, 1.2])

# Farbschema
BH_COLOR = '#000'
HORIZON_COLOR = '#FF0000'
PHOTON_COLOR = '#FFD700'
ISCO_COLOR = '#00FF00'
PHI_COLOR = '#FF00FF'
GRID_COLOR = '#00FFFF'

# ============================================================================
# Plot 1: Schwarzschild-Geometrie (2D Draufsicht)
# ============================================================================
ax1 = fig.add_subplot(gs[0, 0], facecolor='#000')
ax1.set_xlim(-8, 8)
ax1.set_ylim(-8, 8)
ax1.set_aspect('equal')
ax1.set_title('Schwarzschild-Geometrie (Draufsicht)', fontsize=13, color='white', fontweight='bold')
ax1.set_xlabel('x / r_s', fontsize=11, color='white')
ax1.set_ylabel('y / r_s', fontsize=11, color='white')
ax1.tick_params(colors='white')
for spine in ax1.spines.values():
    spine.set_color('white')

# Schwarzes Loch (Event Horizon)
horizon = Circle((0, 0), r_s_norm, facecolor=BH_COLOR, edgecolor=HORIZON_COLOR, 
                linewidth=3, label='Event Horizon (r_s)', zorder=10)
ax1.add_patch(horizon)

# Photonen-Sphäre
photon_sphere = Circle((0, 0), r_photon, fill=False, edgecolor=PHOTON_COLOR, 
                       linewidth=2, linestyle='--', label='Photonen-Sphäre (1.5 r_s)', zorder=5)
ax1.add_patch(photon_sphere)

# ISCO
isco_circle = Circle((0, 0), r_isco, fill=False, edgecolor=ISCO_COLOR, 
                     linewidth=2, linestyle='--', label='ISCO (3 r_s)', zorder=5)
ax1.add_patch(isco_circle)

# φ-Grenze (FUNDAMENTAL!)
phi_circle = Circle((0, 0), r_phi, fill=False, edgecolor=PHI_COLOR, 
                    linewidth=2, linestyle=':', label=f'φ-Grenze ({PHI:.3f} r_s)', zorder=5)
ax1.add_patch(phi_circle)

# Raumzeit-Gitter (wird animiert)
grid_lines = []
for r in [2, 3, 4, 5, 6, 7]:
    circle, = ax1.plot([], [], color=GRID_COLOR, linewidth=0.5, alpha=0.3)
    grid_lines.append(circle)

# Test-Partikel (wird animiert)
particle, = ax1.plot([], [], 'wo', markersize=8, label='Test-Partikel', zorder=15)

ax1.legend(loc='upper right', fontsize=9, facecolor='black', edgecolor='white', labelcolor='white')
ax1.grid(True, alpha=0.1, color='white')

# ============================================================================
# Plot 2: Zeit-Dilatation & Redshift
# ============================================================================
ax2 = fig.add_subplot(gs[0, 1], facecolor='#0a0a1e')
ax2.set_xlim(1, 8)
ax2.set_ylim(0, 10)
ax2.set_title('Zeitdilatation & Gravitational Redshift', fontsize=13, color='white', fontweight='bold')
ax2.set_xlabel('r / r_s', fontsize=11, color='white')
ax2.set_ylabel('Faktor', fontsize=11, color='white')
ax2.tick_params(colors='white')
for spine in ax2.spines.values():
    spine.set_color('white')

r_plot = np.linspace(1.01, 8, 200)
tau_plot = [time_dilation(r*r_s, M_BH) for r in r_plot]
z_plot = [gravitational_redshift(r*r_s, M_BH) for r in r_plot]

ax2.plot(r_plot, tau_plot, color='#00FF00', linewidth=2, label='τ (Zeitdilatation)', zorder=5)
ax2.plot(r_plot, [1+z for z in z_plot], color='#FFD700', linewidth=2, label='1+z_grav', zorder=5)

# φ-Grenze markieren
ax2.axvline(r_phi, color=PHI_COLOR, linewidth=2, linestyle=':', alpha=0.7, label=f'φ-Grenze')
ax2.axvline(r_photon, color=PHOTON_COLOR, linewidth=1, linestyle='--', alpha=0.5)
ax2.axvline(r_isco, color=ISCO_COLOR, linewidth=1, linestyle='--', alpha=0.5)

# Animierter Marker
current_pos_marker, = ax2.plot([], [], 'ro', markersize=10, zorder=20)

ax2.legend(loc='upper right', fontsize=9, facecolor='black', edgecolor='white', labelcolor='white')
ax2.grid(True, alpha=0.2, color='white')

# ============================================================================
# Plot 3: Mathematische Werte (Live) - RECHTS über beide Zeilen
# ============================================================================
ax_values = fig.add_subplot(gs[:, 2], facecolor='#0a0a1e')
ax_values.set_xlim(0, 1)
ax_values.set_ylim(0, 1)
ax_values.axis('off')
ax_values.set_title('Mathematische Werte (Live) - Sagittarius A*', fontsize=14, color='white', fontweight='bold', pad=20)

# Linke Spalte
values_text_left = ax_values.text(0.05, 0.95, '', fontsize=11, color='white', 
                                  verticalalignment='top', family='monospace',
                                  bbox=dict(boxstyle='round', facecolor='#1a1a2e', 
                                          edgecolor='#00FFFF', alpha=0.8, linewidth=2))

# Rechte Spalte
values_text_right = ax_values.text(0.52, 0.95, '', fontsize=11, color='white', 
                                   verticalalignment='top', family='monospace',
                                   bbox=dict(boxstyle='round', facecolor='#1a1a2e', 
                                           edgecolor='#FF00FF', alpha=0.8, linewidth=2))

# ============================================================================
# Plot 4: Segment-Dichte (φ-basiert)
# ============================================================================
ax3 = fig.add_subplot(gs[1, 0], facecolor='#0a0a1e')
ax3.set_xlim(1, 8)
ax3.set_ylim(0, 5)
ax3.set_title('Segment-Dichte N(r) ~ φ·(r_s/r)²', fontsize=13, color='white', fontweight='bold')
ax3.set_xlabel('r / r_s', fontsize=11, color='white')
ax3.set_ylabel('N(r) / N(r_s)', fontsize=11, color='white')
ax3.tick_params(colors='white')
for spine in ax3.spines.values():
    spine.set_color('white')

N_plot = [segment_density(r*r_s, M_BH) / segment_density(r_s, M_BH) for r in r_plot]
ax3.plot(r_plot, N_plot, color='#FF00FF', linewidth=2, label='N(r) (φ-Spirale)', zorder=5)

# φ-Potenzen markieren
ax3.axvline(r_phi, color=PHI_COLOR, linewidth=2, linestyle=':', alpha=0.7, label=f'φ¹ = {PHI:.3f}')
ax3.axvline(PHI**2, color=PHI_COLOR, linewidth=1, linestyle=':', alpha=0.5, label=f'φ² = {PHI**2:.3f}')

# Animierter Marker
segment_marker, = ax3.plot([], [], 'ro', markersize=10, zorder=20)

ax3.legend(loc='upper right', fontsize=9, facecolor='black', edgecolor='white', labelcolor='white')
ax3.grid(True, alpha=0.2, color='white')

# ============================================================================
# Plot 5: Geschwindigkeiten
# ============================================================================
ax4 = fig.add_subplot(gs[1, 1], facecolor='#0a0a1e')
ax4.set_xlim(1, 8)
ax4.set_ylim(0, 1)
ax4.set_title('Orbital- & Fluchtgeschwindigkeit', fontsize=13, color='white', fontweight='bold')
ax4.set_xlabel('r / r_s', fontsize=11, color='white')
ax4.set_ylabel('v / c', fontsize=11, color='white')
ax4.tick_params(colors='white')
for spine in ax4.spines.values():
    spine.set_color('white')

v_orb_plot = [orbital_velocity(r*r_s, M_BH) / C for r in r_plot]
v_esc_plot = [escape_velocity(r*r_s, M_BH) / C for r in r_plot]

ax4.plot(r_plot, v_orb_plot, color='#00FF00', linewidth=2, label='v_orb (Kepler)', zorder=5)
ax4.plot(r_plot, v_esc_plot, color='#FF0000', linewidth=2, label='v_esc (Flucht)', zorder=5)
ax4.axhline(1.0, color='white', linewidth=1, linestyle='--', alpha=0.5, label='c')

# ISCO markieren
ax4.axvline(r_isco, color=ISCO_COLOR, linewidth=2, linestyle='--', alpha=0.7, label='ISCO')

# Animierter Marker
velocity_marker, = ax4.plot([], [], 'ro', markersize=10, zorder=20)

ax4.legend(loc='upper right', fontsize=9, facecolor='black', edgecolor='white', labelcolor='white')
ax4.grid(True, alpha=0.2, color='white')

# Info ist jetzt im Werte-Panel integriert

# ============================================================================
# Animation-Funktion
# ============================================================================

def animate(frame):
    """
    Animiert ein Test-Partikel das um das Schwarze Loch kreist
    """
    t = frame * 0.05  # Zeitschritt
    
    # Partikel-Orbit (elliptisch, r variiert zwischen 2 und 6 r_s)
    r_min = 2.5
    r_max = 6.0
    r_current = r_min + (r_max - r_min) * (0.5 + 0.5 * np.sin(t))
    
    # Winkel (schneller näher am Schwarzen Loch)
    omega = 2.0 / r_current**1.5  # Kepler's 3rd law approximation
    theta_current = omega * t * 10
    
    # Kartesische Koordinaten
    x = r_current * np.cos(theta_current)
    y = r_current * np.sin(theta_current)
    
    # Update Partikel-Position
    particle.set_data([x], [y])
    
    # Update Gitter (visualisiert Raumzeit-Krümmung)
    for i, line in enumerate(grid_lines):
        r_line = 2 + i
        # Gitter "pulsiert" näher am Schwarzen Loch
        pulse_factor = 1.0 + 0.1 * np.sin(t * 3 - r_line)
        x_circle = r_line * pulse_factor * np.cos(theta)
        y_circle = r_line * pulse_factor * np.sin(theta)
        line.set_data(x_circle, y_circle)
    
    # Update Marker in anderen Plots
    current_pos_marker.set_data([r_current], [time_dilation(r_current*r_s, M_BH)])
    segment_marker.set_data([r_current], [segment_density(r_current*r_s, M_BH) / segment_density(r_s, M_BH)])
    velocity_marker.set_data([r_current], [orbital_velocity(r_current*r_s, M_BH) / C])
    
    # Update mathematische Werte (Live) - ZWEISPALTIG
    r_actual = r_current * r_s  # Tatsächlicher Radius [m]
    z_grav = gravitational_redshift(r_actual, M_BH)
    tau = time_dilation(r_actual, M_BH)
    N_rel = segment_density(r_actual, M_BH) / segment_density(r_s, M_BH)
    v_orb = orbital_velocity(r_actual, M_BH)
    v_esc = escape_velocity(r_actual, M_BH)
    phi_corr = phi_correction(r_actual, M_BH)
    
    # LINKE SPALTE: Sgr A* Info, Position, Zeitdilatation, Redshift
    values_left = (
        f"SAGITTARIUS A*\n"
        f"{'='*30}\n"
        f"Supermassives Schwarzes Loch\n"
        f"Galaktisches Zentrum\n\n"
        f"M = {M_BH/M_SUN:.2e} M_sun\n"
        f"  = 4.154 Millionen Sonnen\n"
        f"r_s = {r_s/1e9:.1f} Mio km\n"
        f"Entfernung: 26,000 Lj\n"
        f"{'='*30}\n\n"
        f"POSITION (Partikel):\n"
        f"{'='*30}\n"
        f"r = {r_current:.3f} r_s\n"
        f"  = {r_actual/1e9:.2f} Millionen km\n"
        f"  = {r_actual/(C*60):.2f} Lichtminuten\n\n"
        f"ZEITDILATATION:\n"
        f"{'='*30}\n"
        f"tau (τ) = {tau:.4f}\n"
        f"Zeit läuft {1/tau:.4f}× langsamer\n"
        f"als im Unendlichen\n\n"
        f"Für 1 Jahr hier vergehen\n"
        f"  {tau:.3f} Jahre unendlich\n\n"
        f"GRAVITATIONAL REDSHIFT:\n"
        f"{'='*30}\n"
        f"z_grav = {z_grav:.6f}\n"
        f"1 + z  = {1+z_grav:.6f}\n\n"
        f"Photon verliert:\n"
        f"  {z_grav/(1+z_grav)*100:.2f}% Energie\n"
    )
    
    # RECHTE SPALTE: Segment-Dichte, Geschwindigkeiten, φ-Korrektur
    values_right = (
        f"SEGMENT-DICHTE:\n"
        f"{'='*30}\n"
        f"N(r) / N(r_s) = {N_rel:.4f}\n\n"
        f"Segmente pro Volumen:\n"
        f"  {N_rel:.3f}× dichter als bei r_s\n\n"
        f"GESCHWINDIGKEITEN:\n"
        f"{'='*30}\n"
        f"v_orbital = {v_orb/C:.5f} c\n"
        f"          = {v_orb/1000:.1f} km/s\n"
        f"          = {v_orb/1000/299792.458:.4f} c\n\n"
        f"v_escape  = {v_esc/C:.5f} c\n"
        f"          = {v_esc/1000:.1f} km/s\n"
        f"          = {v_esc/1000/299792.458:.4f} c\n\n"
        f"PHI (φ) KORREKTUR:\n"
        f"{'='*30}\n"
        f"φ = {PHI:.8f}\n"
        f"  (Goldener Schnitt)\n\n"
        f"Korrekturfaktor = {phi_corr:.6f}\n"
        f"Delta M (ΔM)    = {(phi_corr-1)*100:.4f}%\n\n"
        f"φ-Grenze bei:\n"
        f"  r_φ = {PHI:.3f} × r_s\n"
        f"      = {PHI*r_s/1e9:.2f} Mio km\n"
    )
    
    values_text_left.set_text(values_left)
    values_text_right.set_text(values_right)
    
    return [particle] + grid_lines + [current_pos_marker, segment_marker, velocity_marker, 
            values_text_left, values_text_right]

# ============================================================================
# Animation erstellen
# ============================================================================
print("\nErstelle Animation...")
anim = FuncAnimation(fig, animate, frames=200, interval=50, blit=True)

# Als GIF speichern
output_gif = "d:\\blackhole_segmented_spacetime.gif"
writer = PillowWriter(fps=20)
anim.save(output_gif, writer=writer, dpi=120)
print(f"Animation gespeichert: {output_gif}")

# Als PNG speichern (Schlüsselbild)
fig.savefig("d:\\blackhole_segmented_spacetime.png", dpi=300, facecolor='#000', bbox_inches='tight')
print(f"Statisches Bild gespeichert: d:\\blackhole_segmented_spacetime.png")

print("\n" + "="*80)
print("PHYSIKALISCHE INTERPRETATION:")
print("-" * 80)
print(f"- Phi-Grenze bei r = {PHI:.3f} r_s ist fundamental (Goldener Schnitt!)")
print(f"- Photonen-Sphaere bei r = 1.5 r_s (instabile Licht-Orbits)")
print(f"- ISCO bei r = 3 r_s (innermost stable circular orbit)")
print(f"- Segment-Dichte N(r) ~ Phi*(r_s/r)^2 aus Phi-Spirale")
print(f"- Zeitdilatation tau -> unendlich am Event Horizon")
print("="*80)

plt.show()
