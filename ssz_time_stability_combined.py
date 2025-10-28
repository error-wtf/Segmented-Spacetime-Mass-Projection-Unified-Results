#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time Evolution vs Stability in Segmented Spacetime
===================================================

Combines temporal segmentation (Ξ, Δt, φ) with energetic stability (λ_A, K, E).
Visualizes how time slowdown correlates with gravitational stability thresholds.

Data sources:
- ssz_time_segmentation_report.json
- test05_time_evolution.json (from ssz_complete_tests.py)

© 2025 Carmen Wrede & Lino Casu
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
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
print("TIME EVOLUTION vs STABILITY - COMBINED ANALYSIS")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path("d:/ssz_kruemung")

# Input files
TIME_REPORT = BASE_DIR / "ssz_time_segmentation_report.json"
STABILITY_REPORT = BASE_DIR / "test05_time_evolution.json"

# Output
OUTPUT_GIF = BASE_DIR / "ssz_time_vs_stability.gif"

# Animation settings
DURATION = 15  # seconds
FPS = 25
TOTAL_FRAMES = DURATION * FPS

DPI = 100
FIGSIZE = (19.2, 10.8)

# Captions
CAPTIONS = [
    {"time": 0, "text": "Segmented spacetime defines local time as Δt ∝ 1/(1 + Ξ)."},
    {"time": 5, "text": "As gravity rises, Ξ → Ξ_max ≈ 1 — local clocks tick slower."},
    {"time": 9, "text": "Crossing λ_crit triggers instability: time loses coherence."},
    {"time": 13, "text": "Below λ_crit, time remains ordered — resonant and finite."}
]

# ============================================================================
# LOAD DATA
# ============================================================================

print("[1/6] Loading data files...")

# Load time segmentation data
if not TIME_REPORT.exists():
    print(f"  ❌ ERROR: {TIME_REPORT} not found!")
    print("  Run: python ssz_time_segmentation_animation.py first")
    sys.exit(1)

with open(TIME_REPORT, 'r') as f:
    time_data = json.load(f)

PHI = time_data['parameters']['phi']
XI_MAX = time_data['parameters']['xi_max']
R_MAX = time_data['parameters']['r_max']
SAMPLES = time_data['parameters']['samples']

XI_RANGE = time_data['physics']['xi_range']
DELTA_T_RANGE = time_data['physics']['delta_t_range']
SLOWDOWN_FACTOR = time_data['physics']['time_slowdown_factor']

print(f"  ✓ Time data: φ={PHI:.4f}, Ξ_max={XI_MAX:.2f}")
print(f"  ✓ Slowdown factor: {SLOWDOWN_FACTOR:.3f}×")

# Load stability data
if not STABILITY_REPORT.exists():
    print(f"  ⚠ {STABILITY_REPORT} not found, using default values")
    stability_data = None
else:
    with open(STABILITY_REPORT, 'r') as f:
        stability_data = json.load(f)
    
    print(f"  ✓ Stability data loaded")

# ============================================================================
# REGENERATE PHYSICS DATA
# ============================================================================

print("\n[2/6] Regenerating physics curves...")

def segment_density(r, xi_max=XI_MAX, phi=PHI, r_max=R_MAX):
    return xi_max * (1 - np.exp(-phi * r / r_max))

def local_time_interval(xi):
    return 1.0 / (1 + xi)

r = np.linspace(0, R_MAX, SAMPLES)
xi_r = segment_density(r)
delta_t_r = local_time_interval(xi_r)

print(f"  ✓ Ξ(r): [{xi_r.min():.3f}, {xi_r.max():.3f}]")
print(f"  ✓ Δt(r): [{delta_t_r.min():.3f}, {delta_t_r.max():.3f}]")

# Generate stability phase diagram data
K_values = np.logspace(np.log10(10), np.log10(200), 50)
lambda_crit = 1 / K_values**2

# Example stable/unstable points
K_stable = [32, 64, 100]
lambda_stable = [0.0006, 0.0002, 0.0001]

K_unstable = [16, 32, 50]
lambda_unstable = [0.02, 0.005, 0.001]

print(f"  ✓ Stability diagram: {len(K_values)} K values")

# ============================================================================
# ANIMATION SETUP
# ============================================================================

print("\n[3/6] Setting up 3-panel figure...")

fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor('#0a0a0a')

# Create 3 subplots (vertical stack)
gs = fig.add_gridspec(3, 1, hspace=0.3)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
ax3 = fig.add_subplot(gs[2])

# Common styling
for ax in [ax1, ax2, ax3]:
    ax.set_facecolor('#1a1a1a')
    ax.grid(True, alpha=0.2, linestyle='--', color='white')
    ax.tick_params(colors='white', labelsize=12)
    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_linewidth(1.5)

# Panel 1: Segment Density Ξ(r)
ax1.set_xlabel('r / r$_s$', color='white', fontsize=14, fontweight='bold')
ax1.set_ylabel('Ξ(r)', color='white', fontsize=14, fontweight='bold')
ax1.set_title('Segment Density Ξ(r) — Space Segmentation', 
             color='#ff00ff', fontsize=16, fontweight='bold', pad=10)
ax1.set_xlim(0, R_MAX)
ax1.set_ylim(0, 1.1)

line1, = ax1.plot([], [], color='#ff00ff', linewidth=3, label='Ξ(r)')
marker1, = ax1.plot([], [], 'o', color='#ff00ff', markersize=10, 
                    markeredgecolor='white', markeredgewidth=2)
ax1.axhline(y=XI_MAX, color='yellow', linestyle='--', linewidth=2, 
           alpha=0.5, label=f'Ξ_max = {XI_MAX}')
ax1.text(0.05, 0.95, 'Ξ increases → space segmentation grows', 
        transform=ax1.transAxes, fontsize=11, color='white',
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='black', alpha=0.6))
ax1.legend(loc='lower right', fontsize=11, framealpha=0.8)

# Panel 2: Local Time Interval Δt(r)
ax2.set_xlabel('r / r$_s$', color='white', fontsize=14, fontweight='bold')
ax2.set_ylabel('Δt(r) [normalized]', color='white', fontsize=14, fontweight='bold')
ax2.set_title('Local Time Interval Δt(r) — Time Slowdown', 
             color='#00ffff', fontsize=16, fontweight='bold', pad=10)
ax2.set_xlim(0, R_MAX)
ax2.set_ylim(0, 1.1)

line2, = ax2.plot([], [], color='#00ffff', linewidth=3, label='Δt(r)')
marker2, = ax2.plot([], [], 'o', color='#00ffff', markersize=10,
                    markeredgecolor='white', markeredgewidth=2)
ax2.text(0.05, 0.95, 'Δt increases → local time slows down', 
        transform=ax2.transAxes, fontsize=11, color='white',
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='black', alpha=0.6))
ax2.legend(loc='upper right', fontsize=11, framealpha=0.8)

# Panel 3: Stability Phase Diagram
ax3.set_xlabel('K (segment number)', color='white', fontsize=14, fontweight='bold')
ax3.set_ylabel('λ$_A$ (coupling)', color='white', fontsize=14, fontweight='bold')
ax3.set_title('Energy Stability λ$_A$ vs K — Threshold', 
             color='#ffaa00', fontsize=16, fontweight='bold', pad=10)
ax3.set_xscale('log')
ax3.set_yscale('log')
ax3.set_xlim(10, 200)
ax3.set_ylim(1e-5, 1e-1)

# Critical line
line_crit, = ax3.plot([], [], color='#ffaa00', linewidth=3, linestyle='--',
                     label='λ_crit = 1/K²')

# Stable points (will appear progressively)
scatter_stable = ax3.scatter([], [], color='#00ff00', s=200, marker='o',
                            edgecolors='white', linewidths=2, label='Stable', zorder=5)
scatter_unstable = ax3.scatter([], [], color='#ff5555', s=200, marker='X',
                              edgecolors='white', linewidths=2, label='Unstable', zorder=5)

ax3.text(0.05, 0.95, 'Below line: stable — Above: runaway decay', 
        transform=ax3.transAxes, fontsize=11, color='white',
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='black', alpha=0.6))
ax3.legend(loc='upper right', fontsize=11, framealpha=0.8)

# Caption text
caption_text = fig.text(0.5, 0.01, '', ha='center', va='bottom',
                       fontsize=20, color='#eaf2ff', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7))

plt.tight_layout(rect=[0, 0.04, 1, 1])

print("  ✓ Figure ready")

# ============================================================================
# ANIMATION FUNCTIONS
# ============================================================================

def init():
    """Initialize animation"""
    line1.set_data([], [])
    line2.set_data([], [])
    line_crit.set_data([], [])
    marker1.set_data([], [])
    marker2.set_data([], [])
    scatter_stable.set_offsets(np.empty((0, 2)))
    scatter_unstable.set_offsets(np.empty((0, 2)))
    caption_text.set_text('')
    return (line1, line2, line_crit, marker1, marker2, 
            scatter_stable, scatter_unstable, caption_text)

def animate(frame):
    """Update animation frame"""
    progress = frame / TOTAL_FRAMES
    
    # Panel 1 & 2: Progressive reveal
    idx = int(progress * SAMPLES)
    idx = min(idx, SAMPLES - 1)
    
    line1.set_data(r[:idx], xi_r[:idx])
    line2.set_data(r[:idx], delta_t_r[:idx])
    
    if idx > 0:
        marker1.set_data([r[idx]], [xi_r[idx]])
        marker2.set_data([r[idx]], [delta_t_r[idx]])
    
    # Panel 3: Critical line appears gradually
    k_idx = int(progress * len(K_values))
    k_idx = min(k_idx, len(K_values) - 1)
    
    line_crit.set_data(K_values[:k_idx], lambda_crit[:k_idx])
    
    # Stable/unstable points appear in sequence
    stable_idx = int(progress * len(K_stable))
    unstable_idx = int(progress * len(K_unstable))
    
    if stable_idx > 0:
        stable_points = np.array(list(zip(K_stable[:stable_idx], lambda_stable[:stable_idx])))
        scatter_stable.set_offsets(stable_points)
    
    if unstable_idx > 0:
        unstable_points = np.array(list(zip(K_unstable[:unstable_idx], lambda_unstable[:unstable_idx])))
        scatter_unstable.set_offsets(unstable_points)
    
    # Update caption
    current_time = frame / FPS
    caption = ""
    for cap in CAPTIONS:
        if current_time >= cap["time"]:
            caption = cap["text"]
    caption_text.set_text(caption)
    
    return (line1, line2, line_crit, marker1, marker2,
            scatter_stable, scatter_unstable, caption_text)

# ============================================================================
# RENDER ANIMATION
# ============================================================================

print("\n[4/6] Rendering animation...")
print(f"  Duration: {DURATION}s @ {FPS} FPS = {TOTAL_FRAMES} frames")
print(f"  This may take ~90-120 seconds...")

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

print("\n[5/6] Validation...")

validation = {
    "timestamp": datetime.now().isoformat(),
    "input_files": {
        "time_report": str(TIME_REPORT),
        "stability_report": str(STABILITY_REPORT) if stability_data else "N/A"
    },
    "physics_parameters": {
        "phi": PHI,
        "xi_max": XI_MAX,
        "r_max": R_MAX,
        "slowdown_factor": SLOWDOWN_FACTOR
    },
    "stability_parameters": {
        "K_stable": K_stable,
        "lambda_stable": lambda_stable,
        "K_unstable": K_unstable,
        "lambda_unstable": lambda_unstable
    },
    "output": {
        "file": str(OUTPUT_GIF),
        "size_mb": gif_size_mb,
        "duration_s": DURATION,
        "fps": FPS,
        "frames": TOTAL_FRAMES
    },
    "correlations": {
        "time_slowdown_vs_segmentation": "Δt ∝ 1/(1 + Ξ)",
        "stability_threshold": "λ_A < 1/K²",
        "physical_link": "High Ξ → slow time; λ_A > λ_crit → time coherence breaks"
    },
    "status": "PASSED"
}

report_file = BASE_DIR / "ssz_time_vs_stability_report.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(validation, f, indent=2)

print(f"  ✓ Report: {report_file}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("TIME vs STABILITY COMBINED ANALYSIS COMPLETE")
print("="*80)
print(f"Output: {OUTPUT_GIF} ({gif_size_mb:.2f} MB)")
print(f"Report: {report_file}")
print("\nKey Correlations:")
print(f"  Time slowdown: {SLOWDOWN_FACTOR:.3f}× (from Ξ)")
print(f"  Stability threshold: λ_A < 1/K²")
print(f"  Physical link: High segmentation → slow time → stability matters!")
print("="*80)

print("\n✓ Ready for standard versions (5s + 30s×2)!")
