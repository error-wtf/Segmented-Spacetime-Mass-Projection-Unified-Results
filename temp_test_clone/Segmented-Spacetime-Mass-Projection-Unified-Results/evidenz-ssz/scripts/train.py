#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einstein's Train - Complete Package
1. Statische Analyse mit 4 Diagrammen
2. Animierte Visualisierung mit GIF-Export

© 2025 Carmen Wrede
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Circle
from matplotlib.animation import FuncAnimation, PillowWriter
import os

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

print("="*80)
print("EINSTEINS ZUG-GEDANKENEXPERIMENT - COMPLETE EDITION")
print("="*80)
print("Teil 1: Statische Analyse (4 Diagramme)")
print("Teil 2: Licht-Weltlinien (Decken-Kollision)")
print("Teil 3: Animierte Visualisierung (GIF + PNG)")
print("="*80)

# ============================================================================
# TEIL 1: STATISCHE ANALYSE
# ============================================================================
print("\n[TEIL 1] Statische Analyse läuft...")

c = 299792458
L_train = 300
v = 0.6 * c
gamma = 1 / np.sqrt(1 - (v/c)**2)
L_contracted = L_train / gamma

x_blitz_vorne = L_contracted / 2
x_blitz_hinten = -L_contracted / 2
t_blitz_bahnsteig = 0

t_blitz_vorne_zug = gamma * (t_blitz_bahnsteig - v * x_blitz_vorne / c**2)
t_blitz_hinten_zug = gamma * (t_blitz_bahnsteig - v * x_blitz_hinten / c**2)
delta_t_zug = t_blitz_vorne_zug - t_blitz_hinten_zug

print(f"v = {v/c:.1f}c | γ = {gamma:.3f} | L₀ = {L_train} m | L' = {L_contracted:.1f} m")
print(f"Δt (Bahnsteig) = 0 | Δt (Zug) = {delta_t_zug*1e9:.2f} ns")

fig1, axes = plt.subplots(2, 2, figsize=(16, 10))
fig1.suptitle("Einstein's Train - Statische Analyse", fontsize=16, fontweight='bold')

# Plot 1: Bahnsteig t=0
ax1 = axes[0, 0]
ax1.set_xlim(-200, 200)
ax1.set_ylim(-2, 4)
ax1.set_xlabel("Position x [m]", fontsize=12)
ax1.set_title("Bahnsteig: t = 0 (Blitze gleichzeitig)", fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.axhline(0, color='brown', linewidth=3, label='Bahnsteig')
train_rect = Rectangle((-L_contracted/2, 0.5), L_contracted, 1, 
                       facecolor='blue', edgecolor='darkblue', linewidth=2, alpha=0.6)
ax1.add_patch(train_rect)
arrow = FancyArrow(0, 2, 60, 0, width=15, head_width=30, head_length=20, 
                   fc='red', ec='darkred')
ax1.add_patch(arrow)
ax1.plot(x_blitz_vorne, 1, 'y*', markersize=30, label='Blitz vorne')
ax1.plot(x_blitz_hinten, 1, 'y*', markersize=30, label='Blitz hinten')
ax1.plot(0, -1, 'go', markersize=15, label='Beobachter')
ax1.legend(loc='upper right', fontsize=10)

# Plot 2: Zug-Perspektive
ax2 = axes[0, 1]
ax2.set_xlim(-200, 200)
ax2.set_ylim(-2, 4)
ax2.set_xlabel("Position x' [m] (Zug)", fontsize=12)
ax2.set_title("Zug: Blitze NICHT gleichzeitig", fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
train_rect2 = Rectangle((-L_train/2, 0.5), L_train, 1, 
                        facecolor='blue', edgecolor='darkblue', linewidth=2, alpha=0.6)
ax2.add_patch(train_rect2)
ax2.plot(L_train/2, 1, 'y*', markersize=30, label=f"Vorne (t'={t_blitz_vorne_zug*1e9:.1f} ns)")
ax2.plot(-L_train/2, 1, 'orange', marker='*', markersize=30, 
         label=f"Hinten (t'={t_blitz_hinten_zug*1e9:.1f} ns)")
ax2.plot(0, 1.5, 'ro', markersize=15, label='Beobachter')
ax2.legend(loc='upper right', fontsize=10)

# Plot 3: Raumzeit Bahnsteig
ax3 = axes[1, 0]
ax3.set_xlim(-200, 200)
ax3.set_ylim(-0.5e-6, 1.5e-6)
ax3.set_xlabel("Position x [m]", fontsize=12)
ax3.set_ylabel("Zeit t [s]", fontsize=12)
ax3.set_title("Raumzeit-Diagramm (Bahnsteig)", fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)
t_range = np.linspace(-0.5e-6, 1.5e-6, 100)
x_front = x_blitz_vorne + v * t_range
x_back = x_blitz_hinten + v * t_range
ax3.plot(x_front, t_range, 'b-', linewidth=2, label='Zug vorne')
ax3.plot(x_back, t_range, 'b--', linewidth=2, label='Zug hinten')
ax3.plot(x_blitz_vorne, 0, 'y*', markersize=25, label='Blitz vorne')
ax3.plot(x_blitz_hinten, 0, 'y*', markersize=25, label='Blitz hinten')
ax3.axhline(0, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax3.legend(loc='upper left', fontsize=10)

# Plot 4: Raumzeit Zug
ax4 = axes[1, 1]
ax4.set_xlim(-200, 200)
ax4.set_ylim(-0.5e-6, 1.5e-6)
ax4.set_xlabel("Position x' [m] (Zug)", fontsize=12)
ax4.set_ylabel("Zeit t' [s]", fontsize=12)
ax4.set_title("Raumzeit-Diagramm (Zug)", fontsize=13, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.axvline(L_train/2, color='blue', linewidth=2, label='Zug vorne')
ax4.axvline(-L_train/2, color='blue', linewidth=2, linestyle='--', label='Zug hinten')
ax4.plot(L_train/2, t_blitz_vorne_zug, 'y*', markersize=25)
ax4.plot(-L_train/2, t_blitz_hinten_zug, 'orange', marker='*', markersize=25)
ax4.legend(loc='upper left', fontsize=10)

plt.tight_layout()
static_file = "d:\\einstein_train_static.png"
plt.savefig(static_file, dpi=300, bbox_inches='tight')
print(f"✓ Statische Analyse: {static_file}")
plt.show()

# ============================================================================
# TEIL 2: LICHT-WELTLINIEN (DECKEN-KOLLISION)
# ============================================================================
print("\n[TEIL 2] Licht-Weltlinien (Decken-Kollision)...")

# Ein Lichtstrahl steigt vom Boden zur Decke im Zug
# Zug-System: Strahl geht vertikal (x'=0, y'=c·t')
# Bahnsteig-System: Strahl geht diagonal (x=v·t, y=w'·t/γ)

H = 3.0  # Deckenhöhe [m]
w_prime = c  # Vertikale Lichtgeschwindigkeit im Zug-System

# Zeit bis Kollision im Zug-System
t_collision_train = H / w_prime

# Zeit bis Kollision im Bahnsteig-System (Zeitdilatation!)
t_collision_platform = gamma * t_collision_train

# Horizontale Verschiebung im Bahnsteig-System
x_collision_platform = v * t_collision_platform

print(f"Deckenhöhe H = {H:.1f} m")
print(f"Kollisionszeit (Zug): t' = {t_collision_train*1e9:.2f} ns")
print(f"Kollisionszeit (Bahnsteig): t = {t_collision_platform*1e9:.2f} ns (Faktor γ = {gamma:.3f})")
print(f"Horizontale Verschiebung: Δx = {x_collision_platform:.1f} m")

fig_worldlines, (ax_train, ax_platform) = plt.subplots(1, 2, figsize=(16, 7))
fig_worldlines.suptitle("Licht-Weltlinien: Vertikaler Lichtstrahl im Zug", 
                        fontsize=16, fontweight='bold')

# === Zug-System (x', y', t') ===
ax_train.set_xlim(-2, 2)
ax_train.set_ylim(0, H*1.5)
ax_train.set_xlabel("x' [m] (horizontal)", fontsize=12)
ax_train.set_ylabel("y' [m] (vertikal)", fontsize=12)
ax_train.set_title("Zug-System: Licht steigt VERTIKAL auf", fontsize=13, fontweight='bold')
ax_train.grid(True, alpha=0.3)
ax_train.set_aspect('equal')

# Zug (Rechteck)
train_rect_wl = Rectangle((-L_train/400, 0), L_train/200, H, 
                          facecolor='blue', edgecolor='darkblue', 
                          linewidth=2, alpha=0.3, label='Zug')
ax_train.add_patch(train_rect_wl)

# Lichtstrahl (vertikal)
t_range_train = np.linspace(0, t_collision_train, 50)
y_light_train = w_prime * t_range_train
ax_train.plot([0]*len(t_range_train), y_light_train, 'y-', linewidth=3, 
              label='Lichtstrahl (c)', zorder=5)
ax_train.plot(0, 0, 'go', markersize=12, label='Start (Boden)', zorder=6)
ax_train.plot(0, H, 'r*', markersize=20, label='Kollision (Decke)', zorder=6)

# Decke (horizontal im Zug-System)
ax_train.axhline(H, color='brown', linewidth=3, linestyle='--', alpha=0.7, label='Decke')

ax_train.legend(loc='upper right', fontsize=10)
ax_train.text(0, H*1.3, f"t' = {t_collision_train*1e9:.2f} ns\n(Strahl VERTIKAL)", 
              ha='center', fontsize=11, 
              bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

# === Bahnsteig-System (x, y, t) ===
ax_platform.set_xlim(-1, x_collision_platform*1.3)
ax_platform.set_ylim(0, H*1.5)
ax_platform.set_xlabel("x [m] (horizontal)", fontsize=12)
ax_platform.set_ylabel("y [m] (vertikal)", fontsize=12)
ax_platform.set_title("Bahnsteig-System: Licht geht DIAGONAL", fontsize=13, fontweight='bold')
ax_platform.grid(True, alpha=0.3)
ax_platform.set_aspect('equal')

# Zug bewegt sich → Decke bewegt sich
t_range_platform = np.linspace(0, t_collision_platform, 50)
x_train_platform = v * t_range_platform

# Lichtstrahl (diagonal)
# y = (w'/γ) · t, aber w' = c, also y = c/γ · t
y_light_platform = (w_prime / gamma) * t_range_platform
x_light_platform = v * t_range_platform  # Horizontal mit Zug mitbewegt

ax_platform.plot(x_light_platform, y_light_platform, 'y-', linewidth=3, 
                 label='Lichtstrahl (diagonal)', zorder=5)
ax_platform.plot(0, 0, 'go', markersize=12, label='Start', zorder=6)
ax_platform.plot(x_collision_platform, H, 'r*', markersize=20, 
                 label='Kollision', zorder=6)

# Decke bewegt sich horizontal
ax_platform.plot(x_train_platform, [H]*len(x_train_platform), 'brown', 
                 linewidth=3, linestyle='--', alpha=0.7, label='Decke (bewegt)')

# Anfangs- und Endposition des Zugs
train_start = Rectangle((-L_train/400, 0), L_train/200, H, 
                        facecolor='blue', edgecolor='blue', 
                        linewidth=1, alpha=0.2)
ax_platform.add_patch(train_start)
train_end = Rectangle((x_collision_platform - L_train/400, 0), L_train/200, H, 
                      facecolor='blue', edgecolor='darkblue', 
                      linewidth=2, alpha=0.5, label='Zug (Endposition)')
ax_platform.add_patch(train_end)

ax_platform.legend(loc='upper right', fontsize=10)
ax_platform.text(x_collision_platform/2, H*1.3, 
                 f"t = {t_collision_platform*1e9:.2f} ns\n(Faktor γ = {gamma:.3f})\nΔx = {x_collision_platform:.1f} m", 
                 ha='center', fontsize=11, 
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
worldlines_file = "d:\\einstein_train_worldlines.png"
plt.savefig(worldlines_file, dpi=300, bbox_inches='tight')
print(f"✓ Licht-Weltlinien: {worldlines_file}")
plt.show()

# ============================================================================
# TEIL 3: ANIMATION
# ============================================================================
print("\n[TEIL 3] Animation wird erstellt...")

# Normierte Einheiten für Animation
c_anim = 1.0
v_anim = 0.6 * c_anim
L_train_anim = 6.0
gamma_anim = 1 / np.sqrt(1 - v_anim**2/c_anim**2)
L_contracted_anim = L_train_anim / gamma_anim

fig2 = plt.figure(figsize=(16, 9), facecolor='#0a0a0a')
gs = fig2.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

PLATFORM_COLOR = '#8B4513'
TRAIN_COLOR = '#1E90FF'
LIGHT_COLOR = '#FFD700'
OBSERVER_COLOR = '#32CD32'

# Subplot 1: Bahnsteig
ax1 = fig2.add_subplot(gs[0, 0])
ax1.set_xlim(-12, 12)
ax1.set_ylim(-2, 6)
ax1.set_facecolor('#0f0f1e')
ax1.set_title('Bahnsteig-Beobachter (stationär)', fontsize=14, color='white', fontweight='bold')
ax1.set_xlabel('Position [m]', fontsize=11, color='white')
ax1.grid(True, alpha=0.2, color='white')
ax1.tick_params(colors='white')
for spine in ax1.spines.values():
    spine.set_color('white')

# Subplot 2: Zug
ax2 = fig2.add_subplot(gs[0, 1])
ax2.set_xlim(-12, 12)
ax2.set_ylim(-2, 6)
ax2.set_facecolor('#1e0f1e')
ax2.set_title('Zug-Beobachter (bewegt)', fontsize=14, color='white', fontweight='bold')
ax2.set_xlabel("Position [m]", fontsize=11, color='white')
ax2.grid(True, alpha=0.2, color='white')
ax2.tick_params(colors='white')
for spine in ax2.spines.values():
    spine.set_color('white')

# Subplot 3: Raumzeit
ax3 = fig2.add_subplot(gs[1, :])
ax3.set_xlim(-12, 12)
ax3.set_ylim(-2, 12)
ax3.set_facecolor('#0a0a1e')
ax3.set_title('Raumzeit-Diagramm (Zeit aufwärts)', fontsize=14, color='white', fontweight='bold')
ax3.set_xlabel('Position x [m]', fontsize=11, color='white')
ax3.set_ylabel('Zeit t', fontsize=11, color='white')
ax3.grid(True, alpha=0.2, color='white')
ax3.tick_params(colors='white')
for spine in ax3.spines.values():
    spine.set_color('white')

# Animation-Objekte
platform1, = ax1.plot([], [], color=PLATFORM_COLOR, linewidth=5)
train1 = Rectangle((0, 0), 1, 1, facecolor=TRAIN_COLOR, edgecolor='cyan', linewidth=2, alpha=0.7)
ax1.add_patch(train1)
observer1 = Circle((0, 0), 0.3, facecolor=OBSERVER_COLOR, edgecolor='lime', linewidth=2)
ax1.add_patch(observer1)
lightning_front1 = Circle((0, 0), 0, facecolor=LIGHT_COLOR, alpha=0)
ax1.add_patch(lightning_front1)
lightning_back1 = Circle((0, 0), 0, facecolor=LIGHT_COLOR, alpha=0)
ax1.add_patch(lightning_back1)
light_wave_front1 = Circle((0, 0), 0, fill=False, edgecolor=LIGHT_COLOR, linewidth=2, alpha=0)
ax1.add_patch(light_wave_front1)
light_wave_back1 = Circle((0, 0), 0, fill=False, edgecolor=LIGHT_COLOR, linewidth=2, alpha=0)
ax1.add_patch(light_wave_back1)
time_text1 = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, fontsize=12,
                      color='yellow', verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

platform2, = ax2.plot([], [], color=PLATFORM_COLOR, linewidth=5)
train2 = Rectangle((0, 0), 1, 1, facecolor=TRAIN_COLOR, edgecolor='cyan', linewidth=2, alpha=0.7)
ax2.add_patch(train2)
observer2 = Circle((0, 0), 0.3, facecolor='red', edgecolor='orange', linewidth=2)
ax2.add_patch(observer2)
lightning_front2 = Circle((0, 0), 0, facecolor=LIGHT_COLOR, alpha=0)
ax2.add_patch(lightning_front2)
lightning_back2 = Circle((0, 0), 0, facecolor='#FF8C00', alpha=0)
ax2.add_patch(lightning_back2)
light_wave_front2 = Circle((0, 0), 0, fill=False, edgecolor=LIGHT_COLOR, linewidth=2, alpha=0)
ax2.add_patch(light_wave_front2)
light_wave_back2 = Circle((0, 0), 0, fill=False, edgecolor='#FF8C00', linewidth=2, alpha=0)
ax2.add_patch(light_wave_back2)
time_text2 = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, fontsize=12,
                      color='yellow', verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

worldline_front, = ax3.plot([], [], 'c-', linewidth=2, alpha=0.8)
worldline_back, = ax3.plot([], [], 'c--', linewidth=2, alpha=0.8)
event_front = Circle((0, 0), 0.3, facecolor=LIGHT_COLOR, edgecolor='yellow', linewidth=2, alpha=0)
ax3.add_patch(event_front)
event_back = Circle((0, 0), 0.3, facecolor='#FF8C00', edgecolor='orange', linewidth=2, alpha=0)
ax3.add_patch(event_back)
current_time_line, = ax3.plot([], [], 'r--', linewidth=2, alpha=0.6)

t_lightning = 3.0
x_front_lightning = L_contracted_anim / 2
x_back_lightning = -L_contracted_anim / 2
t_front_train = gamma_anim * (t_lightning - v_anim * x_front_lightning / c_anim**2)
t_back_train = gamma_anim * (t_lightning - v_anim * x_back_lightning / c_anim**2)

def animate(frame):
    t = frame * 0.15
    x_train_center = -8 + v_anim * t
    
    # Bahnsteig-View
    platform1.set_data([-12, 12], [0, 0])
    train1.set_xy((x_train_center - L_contracted_anim/2, 0.5))
    train1.set_width(L_contracted_anim)
    train1.set_height(1.2)
    observer1.set_center((0, -1))
    
    if t >= t_lightning:
        dt = t - t_lightning
        r_light = c_anim * dt
        x_f = x_train_center + L_contracted_anim/2
        x_b = x_train_center - L_contracted_anim/2
        
        lightning_front1.set_center((x_f, 1.1))
        lightning_front1.set_radius(0.4)
        lightning_front1.set_alpha(max(0, 1 - dt*0.5))
        light_wave_front1.set_center((x_f, 1.1))
        light_wave_front1.set_radius(r_light)
        light_wave_front1.set_alpha(max(0, 0.8 - dt*0.3))
        
        lightning_back1.set_center((x_b, 1.1))
        lightning_back1.set_radius(0.4)
        lightning_back1.set_alpha(max(0, 1 - dt*0.5))
        light_wave_back1.set_center((x_b, 1.1))
        light_wave_back1.set_radius(r_light)
        light_wave_back1.set_alpha(max(0, 0.8 - dt*0.3))
    
    time_text1.set_text(f't = {t:.2f}')
    
    # Zug-View
    train2.set_xy((-L_train_anim/2, 0.5))
    train2.set_width(L_train_anim)
    train2.set_height(1.2)
    observer2.set_center((0, 1.1))
    x_platform = 8 - v_anim * t
    platform2.set_data([x_platform - 12, x_platform + 12], [0, 0])
    
    if t >= t_back_train:
        dt_b = t - t_back_train
        r_b = c_anim * dt_b
        lightning_back2.set_center((-L_train_anim/2, 1.1))
        lightning_back2.set_radius(0.4)
        lightning_back2.set_alpha(max(0, 1 - dt_b*0.5))
        light_wave_back2.set_center((-L_train_anim/2, 1.1))
        light_wave_back2.set_radius(r_b)
        light_wave_back2.set_alpha(max(0, 0.8 - dt_b*0.3))
    
    if t >= t_front_train:
        dt_f = t - t_front_train
        r_f = c_anim * dt_f
        lightning_front2.set_center((L_train_anim/2, 1.1))
        lightning_front2.set_radius(0.4)
        lightning_front2.set_alpha(max(0, 1 - dt_f*0.5))
        light_wave_front2.set_center((L_train_anim/2, 1.1))
        light_wave_front2.set_radius(r_f)
        light_wave_front2.set_alpha(max(0, 0.8 - dt_f*0.3))
    
    time_text2.set_text(f"t' = {t:.2f}")
    
    # Raumzeit
    t_range = np.linspace(0, t, max(2, int(t*10)))
    x_f_range = x_front_lightning + v_anim * (t_range - t_lightning)
    x_b_range = x_back_lightning + v_anim * (t_range - t_lightning)
    worldline_front.set_data(x_f_range, t_range)
    worldline_back.set_data(x_b_range, t_range)
    
    if t >= t_lightning:
        event_front.set_center((x_front_lightning, t_lightning))
        event_front.set_alpha(0.9)
        event_back.set_center((x_back_lightning, t_lightning))
        event_back.set_alpha(0.9)
    
    current_time_line.set_data([-12, 12], [t, t])
    
    return (platform1, train1, observer1, lightning_front1, lightning_back1,
            light_wave_front1, light_wave_back1, time_text1,
            platform2, train2, observer2, lightning_front2, lightning_back2,
            light_wave_front2, light_wave_back2, time_text2,
            worldline_front, worldline_back, event_front, event_back, current_time_line)

anim = FuncAnimation(fig2, animate, frames=120, interval=50, blit=True)

output_gif = "d:\\einstein_train_animation.gif"
writer = PillowWriter(fps=20)
anim.save(output_gif, writer=writer, dpi=100)
print(f"✓ Animation: {output_gif}")

# Schlüsselmoment
fig3, axes = plt.subplots(1, 2, figsize=(16, 6), facecolor='#0a0a0a')
for ax in axes:
    ax.set_facecolor('#0f0f1e')
    ax.grid(True, alpha=0.2, color='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

ax = axes[0]
ax.set_xlim(-8, 8)
ax.set_ylim(-2, 4)
ax.set_title('Bahnsteig: Blitze GLEICHZEITIG', fontsize=14, color='white', fontweight='bold')
ax.plot([-8, 8], [0, 0], color=PLATFORM_COLOR, linewidth=5)
train_r = Rectangle((-L_contracted_anim/2, 0.5), L_contracted_anim, 1.2, 
                   facecolor=TRAIN_COLOR, edgecolor='cyan', linewidth=2, alpha=0.7)
ax.add_patch(train_r)
ax.add_patch(Circle((L_contracted_anim/2, 1.1), 0.5, facecolor=LIGHT_COLOR, edgecolor='yellow', linewidth=3))
ax.add_patch(Circle((-L_contracted_anim/2, 1.1), 0.5, facecolor=LIGHT_COLOR, edgecolor='yellow', linewidth=3))
ax.add_patch(Circle((0, -1), 0.4, facecolor=OBSERVER_COLOR, edgecolor='lime', linewidth=2))

ax = axes[1]
ax.set_xlim(-8, 8)
ax.set_ylim(-2, 4)
ax.set_title('Zug: Blitze NICHT GLEICHZEITIG', fontsize=14, color='white', fontweight='bold')
train_r2 = Rectangle((-L_train_anim/2, 0.5), L_train_anim, 1.2, 
                    facecolor=TRAIN_COLOR, edgecolor='cyan', linewidth=2, alpha=0.7)
ax.add_patch(train_r2)
ax.add_patch(Circle((-L_train_anim/2, 1.1), 0.5, facecolor='#FF8C00', edgecolor='orange', linewidth=3))
ax.add_patch(Circle((L_train_anim/2, 1.1), 0.3, facecolor=LIGHT_COLOR, edgecolor='yellow', linewidth=2, alpha=0.5))
ax.add_patch(Circle((0, 1.1), 0.4, facecolor='red', edgecolor='orange', linewidth=2))

plt.tight_layout()
output_png = "d:\\einstein_train_diagram.png"
plt.savefig(output_png, dpi=300, facecolor='#0a0a0a')
print(f"✓ Diagramm: {output_png}")

print("\n" + "="*80)
print("✓✓✓ FERTIG! Alle Ausgaben erstellt:")
print("-" * 80)
print(f"  1. {static_file}")
print(f"  2. {worldlines_file}")
print(f"  3. {output_gif}")
print(f"  4. {output_png}")
print("="*80)
print("\nPHYSIKALISCHE ERKENNTNISSE:")
print("-" * 80)
print("• Gleichzeitigkeit ist relativ (Blitze)")
print("• Lichtgeschwindigkeit ist konstant in allen Systemen")
print("• Vertikales Licht im Zug → Diagonales Licht auf Bahnsteig")
print("• Zeitdilatation: t = γ·t' (bewegte Uhren gehen langsamer)")
print("• Längenkontraktion: L' = L₀/γ (bewegte Objekte sind kürzer)")
print("="*80)

plt.show()
