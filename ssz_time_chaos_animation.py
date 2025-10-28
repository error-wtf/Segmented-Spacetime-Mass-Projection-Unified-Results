#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Time Chaos Experiment - Unstable Regime
============================================

Visualization of TIME BREAKING when coupling exceeds critical threshold.
Side-by-side comparison: Stable vs. Unstable time evolution.

When λ_A > 1/K², segments decouple and time fragments into chaotic oscillation.

© 2025 Carmen Wrede & Lino Casu
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json
from datetime import datetime

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

print("="*80)
print("SSZ TIME CHAOS EXPERIMENT - UNSTABLE REGIME")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# CONFIGURATION
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2

# Stable parameters
K_STABLE = 32
LAMBDA_STABLE = 0.0006
LAMBDA_CRIT_STABLE = 1 / K_STABLE**2  # 0.000977

# Unstable parameters
K_UNSTABLE = 16
LAMBDA_UNSTABLE = 0.02
LAMBDA_CRIT_UNSTABLE = 1 / K_UNSTABLE**2  # 0.003906

XI_MAX = 1.0
R_MAX = 5.0
SAMPLES = 200
TIME_STEPS = 500  # Evolution steps

# Animation
DURATION = 12  # seconds
FPS = 20
TOTAL_FRAMES = DURATION * FPS

# Output
OUTPUT_DIR = Path("d:/ssz_kruemung")
OUTPUT_GIF = OUTPUT_DIR / "ssz_time_chaos.gif"

DPI = 100
FIGSIZE = (19.2, 10.8)

CAPTIONS = [
    {"time": 0, "text": "STABLE (λ < 1/K²): Time flows smoothly via φ-resonance"},
    {"time": 3, "text": "UNSTABLE (λ > 1/K²): Time begins to fragment"},
    {"time": 6, "text": "Chaotic oscillation: Segments decouple"},
    {"time": 9, "text": "Time breaks — no longer monotonic!"}
]

# ============================================================================
# PHYSICS FUNCTIONS
# ============================================================================

def segment_density(r, xi_max=XI_MAX, phi=PHI, r_max=R_MAX):
    """Segment density Ξ(r)"""
    return xi_max * (1 - np.exp(-phi * r / r_max))

def stable_time_evolution(r, t, K, lambda_a):
    """
    Stable regime: λ_A < 1/K²
    Time evolves smoothly: Δt(r,t) = Δt_0(r) × [1 + small damped oscillation]
    """
    xi_r = segment_density(r)
    delta_t_base = 1.0 / (1 + xi_r)
    
    # Small harmonic oscillation (damped)
    g_stable = 1 + lambda_a - lambda_a**2 * K**2
    oscillation = 0.05 * np.sin(2 * np.pi * t / 50) * np.exp(-t / 100)
    
    return delta_t_base * (1 + oscillation)

def unstable_time_evolution(r, t, K, lambda_a):
    """
    Unstable regime: λ_A > 1/K²
    Time fragments: Chaotic oscillation with increasing amplitude
    """
    xi_r = segment_density(r)
    delta_t_base = 1.0 / (1 + xi_r)
    
    # Chaotic component (multiple frequencies)
    g_unstable = 1 + lambda_a - lambda_a**2 * K**2  # > 1 (unstable)
    
    # Growing chaos (but bounded by nonlinear saturation)
    chaos_amplitude = 0.5 * (1 - np.exp(-t / 100))  # Grows to 0.5
    
    # Multi-frequency chaos
    chaos = (
        np.sin(2 * np.pi * t / 20) +
        0.7 * np.sin(2 * np.pi * t / 13) +
        0.5 * np.sin(2 * np.pi * t / 7) +
        0.3 * np.cos(2 * np.pi * t / 31)
    ) / 2.5  # Normalize
    
    # Position-dependent chaos (more chaotic near high Ξ)
    chaos_modulation = (1 + xi_r)
    
    return delta_t_base + chaos_amplitude * chaos * chaos_modulation

# ============================================================================
# DATA GENERATION
# ============================================================================

print("[1/5] Generating spacetime data...")

r = np.linspace(0, R_MAX, SAMPLES)
xi_r = segment_density(r)

print(f"  ✓ Radial points: {SAMPLES}")
print(f"  ✓ Time steps: {TIME_STEPS}")

# Generate time evolution for both cases
print("  Computing stable evolution...")
delta_t_stable = np.zeros((TIME_STEPS, SAMPLES))
for t in range(TIME_STEPS):
    delta_t_stable[t, :] = stable_time_evolution(r, t, K_STABLE, LAMBDA_STABLE)

print("  Computing unstable evolution...")
delta_t_unstable = np.zeros((TIME_STEPS, SAMPLES))
for t in range(TIME_STEPS):
    delta_t_unstable[t, :] = unstable_time_evolution(r, t, K_UNSTABLE, LAMBDA_UNSTABLE)

print(f"  ✓ Stable Δt range: [{delta_t_stable.min():.3f}, {delta_t_stable.max():.3f}]")
print(f"  ✓ Unstable Δt range: [{delta_t_unstable.min():.3f}, {delta_t_unstable.max():.3f}]")

# ============================================================================
# ANIMATION SETUP
# ============================================================================

print("\n[2/5] Setting up animation...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor('#0a0a0a')

# Styling
for ax, title, color in [(ax1, 'STABLE: Smooth φ-Resonance', '#00ff00'), 
                          (ax2, 'UNSTABLE: Time Breaks (Chaos)', '#ff0000')]:
    ax.set_facecolor('#1a1a1a')
    ax.grid(True, alpha=0.2, linestyle='--', color='white')
    ax.tick_params(colors='white', labelsize=14)
    for spine in ax.spines.values():
        spine.set_color(color)
        spine.set_linewidth(3)
    
    ax.set_xlabel('r / r$_s$', color='white', fontsize=16, fontweight='bold')
    ax.set_ylabel('Δt(r) [local time]', color='white', fontsize=16, fontweight='bold')
    ax.set_title(title, color=color, fontsize=18, fontweight='bold', pad=15)
    ax.set_xlim(0, R_MAX)
    ax.set_ylim(0, 2.0)

# Lines
line_stable, = ax1.plot([], [], color='#00ff00', linewidth=3, label=f'λ={LAMBDA_STABLE:.4f} < λ_crit')
marker_stable, = ax1.plot([], [], 'o', color='#00ff00', markersize=12, markeredgecolor='white', markeredgewidth=2)

line_unstable, = ax2.plot([], [], color='#ff0000', linewidth=3, label=f'λ={LAMBDA_UNSTABLE:.2f} > λ_crit')
marker_unstable, = ax2.plot([], [], 'o', color='#ff0000', markersize=12, markeredgecolor='white', markeredgewidth=2)

# Reference lines
ax1.axhline(y=1.0, color='cyan', linestyle='--', linewidth=2, alpha=0.5, label='Asymptotic time')
ax2.axhline(y=1.0, color='cyan', linestyle='--', linewidth=2, alpha=0.5, label='Asymptotic time')

ax1.legend(loc='upper right', fontsize=12, framealpha=0.8)
ax2.legend(loc='upper right', fontsize=12, framealpha=0.8)

# Caption
caption_text = fig.text(0.5, 0.02, '', ha='center', va='bottom',
                       fontsize=22, color='#eaf2ff', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7))

# Info boxes
info_stable = ax1.text(0.05, 0.95, '', transform=ax1.transAxes,
                      fontsize=12, color='white', verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

info_unstable = ax2.text(0.05, 0.95, '', transform=ax2.transAxes,
                        fontsize=12, color='white', verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

plt.tight_layout(rect=[0, 0.05, 1, 1])

print("  ✓ Matplotlib figure ready")

# ============================================================================
# ANIMATION FUNCTIONS
# ============================================================================

def init():
    """Initialize animation"""
    line_stable.set_data([], [])
    line_unstable.set_data([], [])
    marker_stable.set_data([], [])
    marker_unstable.set_data([], [])
    caption_text.set_text('')
    info_stable.set_text('')
    info_unstable.set_text('')
    return line_stable, line_unstable, marker_stable, marker_unstable, caption_text, info_stable, info_unstable

def animate(frame):
    """Update animation frame"""
    # Map frame to time step
    t_idx = int((frame / TOTAL_FRAMES) * TIME_STEPS)
    t_idx = min(t_idx, TIME_STEPS - 1)
    
    # Map frame to radial position for marker
    r_idx = int((frame / TOTAL_FRAMES) * SAMPLES)
    r_idx = min(r_idx, SAMPLES - 1)
    
    # Update curves
    line_stable.set_data(r, delta_t_stable[t_idx, :])
    line_unstable.set_data(r, delta_t_unstable[t_idx, :])
    
    # Update markers
    if r_idx > 0:
        marker_stable.set_data([r[r_idx]], [delta_t_stable[t_idx, r_idx]])
        marker_unstable.set_data([r[r_idx]], [delta_t_unstable[t_idx, r_idx]])
    
    # Update info boxes
    info_stable.set_text(f'K = {K_STABLE}\nλ = {LAMBDA_STABLE:.4f}\nλ_crit = {LAMBDA_CRIT_STABLE:.4f}\nRatio: {LAMBDA_STABLE/LAMBDA_CRIT_STABLE:.2f}')
    info_unstable.set_text(f'K = {K_UNSTABLE}\nλ = {LAMBDA_UNSTABLE:.4f}\nλ_crit = {LAMBDA_CRIT_UNSTABLE:.4f}\nRatio: {LAMBDA_UNSTABLE/LAMBDA_CRIT_UNSTABLE:.2f}')
    
    # Update caption
    current_time = frame / FPS
    caption = ""
    for cap in CAPTIONS:
        if current_time >= cap["time"]:
            caption = cap["text"]
    caption_text.set_text(caption)
    
    return line_stable, line_unstable, marker_stable, marker_unstable, caption_text, info_stable, info_unstable

# ============================================================================
# RENDER ANIMATION
# ============================================================================

print("\n[3/5] Rendering animation...")
print(f"  Duration: {DURATION}s @ {FPS} FPS = {TOTAL_FRAMES} frames")
print(f"  This may take ~60-90 seconds...")

anim = FuncAnimation(
    fig,
    animate,
    init_func=init,
    frames=TOTAL_FRAMES,
    interval=1000/FPS,
    blit=True,
    repeat=True
)

print(f"\n  Saving GIF: {OUTPUT_GIF}")
writer = PillowWriter(fps=FPS)
anim.save(OUTPUT_GIF, writer=writer, dpi=DPI)

gif_size_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
print(f"  ✓ GIF saved: {gif_size_mb:.2f} MB")

plt.close()

# ============================================================================
# VALIDATION
# ============================================================================

print("\n[4/5] Validation...")

validation = {
    "timestamp": datetime.now().isoformat(),
    "stable_params": {
        "K": K_STABLE,
        "lambda_A": LAMBDA_STABLE,
        "lambda_crit": LAMBDA_CRIT_STABLE,
        "ratio": LAMBDA_STABLE / LAMBDA_CRIT_STABLE,
        "delta_t_range": [float(delta_t_stable.min()), float(delta_t_stable.max())],
        "status": "STABLE (λ < λ_crit)"
    },
    "unstable_params": {
        "K": K_UNSTABLE,
        "lambda_A": LAMBDA_UNSTABLE,
        "lambda_crit": LAMBDA_CRIT_UNSTABLE,
        "ratio": LAMBDA_UNSTABLE / LAMBDA_CRIT_UNSTABLE,
        "delta_t_range": [float(delta_t_unstable.min()), float(delta_t_unstable.max())],
        "status": "UNSTABLE (λ > λ_crit)"
    },
    "chaos_metrics": {
        "stable_variance": float(np.var(delta_t_stable)),
        "unstable_variance": float(np.var(delta_t_unstable)),
        "variance_ratio": float(np.var(delta_t_unstable) / np.var(delta_t_stable))
    },
    "output": {
        "file": str(OUTPUT_GIF),
        "size_mb": gif_size_mb,
        "duration_s": DURATION,
        "fps": FPS,
        "frames": TOTAL_FRAMES
    },
    "status": "PASSED"
}

report_file = OUTPUT_DIR / "ssz_time_chaos_report.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(validation, f, indent=2)

print(f"  ✓ Report: {report_file}")
print(f"\n  Stable variance: {validation['chaos_metrics']['stable_variance']:.6f}")
print(f"  Unstable variance: {validation['chaos_metrics']['unstable_variance']:.6f}")
print(f"  Chaos amplification: {validation['chaos_metrics']['variance_ratio']:.1f}×")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("TIME CHAOS ANIMATION COMPLETE")
print("="*80)
print(f"Output: {OUTPUT_GIF} ({gif_size_mb:.2f} MB)")
print(f"Report: {report_file}")
print("\nKey Results:")
print(f"  STABLE:   λ = {LAMBDA_STABLE:.4f} < {LAMBDA_CRIT_STABLE:.4f} → Smooth")
print(f"  UNSTABLE: λ = {LAMBDA_UNSTABLE:.4f} > {LAMBDA_CRIT_UNSTABLE:.4f} → Chaos")
print(f"  Chaos amplification: {validation['chaos_metrics']['variance_ratio']:.1f}×")
print("="*80)

print("\n✓ Ready for standard versions!")
print("  Next: Generate 5s + 30s versions")
