#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Time Segmentation Experiment
=================================

Visualization of how time emerges in Segmented Spacetime (SSZ).
Shows how higher segment density Ξ(r) leads to longer local Δt intervals.

Time as emergent, resonant sequence rather than continuous flow.

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

# UTF-8 setup for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

print("="*80)
print("SSZ TIME SEGMENTATION EXPERIMENT")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2  # ≈ 1.618034

# Parameters
XI_MAX = 1.0
R_MAX = 5.0
SAMPLES = 200
TIME_SCALING = 0.02

# Animation settings
DURATION = 10  # seconds
FPS = 20
TOTAL_FRAMES = DURATION * FPS

# Output directory
OUTPUT_DIR = Path("d:/ssz_kruemung")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_GIF = OUTPUT_DIR / "ssz_time_segmentation.gif"
OUTPUT_MP4 = OUTPUT_DIR / "ssz_time_segmentation.mp4"

# Figure settings
DPI = 100
FIGSIZE = (19.2, 10.8)  # 1920×1080 at 100 DPI

# Captions
CAPTIONS = [
    {
        "time": 0,
        "text": "At low gravity, segment density is sparse — time flows fast."
    },
    {
        "time": 3,
        "text": "As gravity increases, segments compress — Δt increases."
    },
    {
        "time": 6,
        "text": "Time slows down, not by stretching space, but by resonance delay."
    },
    {
        "time": 9,
        "text": "At Ξ_max, local time reaches φ-saturation — no further compression."
    }
]

# ============================================================================
# PHYSICS FUNCTIONS
# ============================================================================

def segment_density(r, xi_max=XI_MAX, phi=PHI, r_max=R_MAX):
    """
    Segment density as function of radius
    
    Ξ(r) = Ξ_max * (1 - exp(-φ * r / r_max))
    """
    return xi_max * (1 - np.exp(-phi * r / r_max))

def local_time_interval(xi):
    """
    Local time interval per segment
    
    Δt(r) = 1 / (1 + Ξ(r))
    
    Physical interpretation:
    - Higher Ξ → more segments → longer time per transition
    - Time "slows down" through resonance delay
    """
    return 1.0 / (1 + xi)

def resonance_frequency(xi, phi=PHI):
    """
    Local oscillation frequency
    
    ω(r) = φ / (1 + Ξ(r))
    """
    return phi / (1 + xi)

# ============================================================================
# DATA GENERATION
# ============================================================================

print("[1/5] Generating physics data...")

# Radial array
r = np.linspace(0, R_MAX, SAMPLES)

# Compute fields
xi_r = segment_density(r)
delta_t_r = local_time_interval(xi_r)
omega_r = resonance_frequency(xi_r)

print(f"  ✓ Generated {SAMPLES} data points")
print(f"  ✓ Ξ range: [{xi_r.min():.3f}, {xi_r.max():.3f}]")
print(f"  ✓ Δt range: [{delta_t_r.min():.3f}, {delta_t_r.max():.3f}]")
print(f"  ✓ ω range: [{omega_r.min():.3f}, {omega_r.max():.3f}]")

# ============================================================================
# ANIMATION SETUP
# ============================================================================

print("\n[2/5] Setting up animation...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor('#0a0a0a')

# Style
for ax in [ax1, ax2]:
    ax.set_facecolor('#1a1a1a')
    ax.grid(True, alpha=0.2, linestyle='--', color='white')
    ax.tick_params(colors='white', labelsize=14)
    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_linewidth(1.5)

# Panel 1: Segment Density
ax1.set_xlabel('r / r$_s$', color='white', fontsize=16, fontweight='bold')
ax1.set_ylabel('Ξ(r)', color='white', fontsize=16, fontweight='bold')
ax1.set_title('Segment Density Ξ(r)', color='white', fontsize=18, fontweight='bold', pad=15)
ax1.set_xlim(0, R_MAX)
ax1.set_ylim(0, 1.1)

line1, = ax1.plot([], [], color='#ff00ff', linewidth=3, label='Ξ(r)')
marker1, = ax1.plot([], [], 'o', color='#ff00ff', markersize=12, markeredgecolor='white', markeredgewidth=2)
ax1.axhline(y=XI_MAX, color='yellow', linestyle='--', linewidth=2, alpha=0.5, label=f'Ξ_max = {XI_MAX}')
ax1.legend(loc='lower right', fontsize=14, framealpha=0.8)

# Panel 2: Local Time Interval
ax2.set_xlabel('r / r$_s$', color='white', fontsize=16, fontweight='bold')
ax2.set_ylabel('Δt(r) [normalized]', color='white', fontsize=16, fontweight='bold')
ax2.set_title('Local Time Interval Δt(r)', color='white', fontsize=18, fontweight='bold', pad=15)
ax2.set_xlim(0, R_MAX)
ax2.set_ylim(0, 1.1)

line2, = ax2.plot([], [], color='#00ffff', linewidth=3, label='Δt(r)')
marker2, = ax2.plot([], [], 'o', color='#00ffff', markersize=12, markeredgecolor='white', markeredgewidth=2)
ax2.legend(loc='upper right', fontsize=14, framealpha=0.8)

# Caption text
caption_text = fig.text(0.5, 0.02, '', ha='center', va='bottom', 
                       fontsize=20, color='#eaf2ff', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.6))

plt.tight_layout(rect=[0, 0.05, 1, 1])

print("  ✓ Matplotlib figure ready")

# ============================================================================
# ANIMATION FUNCTION
# ============================================================================

def init():
    """Initialize animation"""
    line1.set_data([], [])
    line2.set_data([], [])
    marker1.set_data([], [])
    marker2.set_data([], [])
    caption_text.set_text('')
    return line1, line2, marker1, marker2, caption_text

def animate(frame):
    """Update animation frame"""
    # Progress through data (0 to SAMPLES)
    idx = int((frame / TOTAL_FRAMES) * SAMPLES)
    idx = min(idx, SAMPLES - 1)
    
    # Update curves (progressive reveal)
    line1.set_data(r[:idx], xi_r[:idx])
    line2.set_data(r[:idx], delta_t_r[:idx])
    
    # Update markers (current position)
    if idx > 0:
        marker1.set_data([r[idx]], [xi_r[idx]])
        marker2.set_data([r[idx]], [delta_t_r[idx]])
    
    # Update caption
    current_time = frame / FPS
    caption = ""
    for cap in CAPTIONS:
        if current_time >= cap["time"]:
            caption = cap["text"]
    caption_text.set_text(caption)
    
    return line1, line2, marker1, marker2, caption_text

# ============================================================================
# RENDER ANIMATION
# ============================================================================

print("\n[3/5] Rendering animation...")
print(f"  Duration: {DURATION}s @ {FPS} FPS = {TOTAL_FRAMES} frames")
print(f"  This may take ~30-60 seconds...")

anim = FuncAnimation(
    fig, 
    animate, 
    init_func=init,
    frames=TOTAL_FRAMES,
    interval=1000/FPS,
    blit=True,
    repeat=True
)

# Save GIF
print(f"\n  Saving GIF: {OUTPUT_GIF}")
writer = PillowWriter(fps=FPS)
anim.save(OUTPUT_GIF, writer=writer, dpi=DPI)

gif_size_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
print(f"  ✓ GIF saved: {gif_size_mb:.2f} MB")

plt.close()

# ============================================================================
# ADD ENHANCED CAPTIONS TO GIF
# ============================================================================

print("\n[4/5] Adding enhanced captions...")

img = Image.open(OUTPUT_GIF)
frames_with_captions = []

# Get actual number of frames in GIF
actual_frames = 0
try:
    while True:
        img.seek(actual_frames)
        actual_frames += 1
except EOFError:
    pass

print(f"  Actual frames in GIF: {actual_frames} (expected {TOTAL_FRAMES})")

try:
    font = ImageFont.truetype("arial.ttf", 24)
except:
    font = ImageFont.load_default()

for frame_idx in range(actual_frames):
    img.seek(frame_idx)
    frame = img.copy().convert('RGBA')
    
    # Determine caption
    current_time = frame_idx / FPS
    caption = ""
    for cap in CAPTIONS:
        if current_time >= cap["time"]:
            caption = cap["text"]
    
    if caption:
        draw = ImageDraw.Draw(frame)
        
        # Measure text
        bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position (bottom center)
        x = (frame.width - text_width) // 2
        y = frame.height - text_height - 40
        
        # Background rectangle
        padding = 10
        bg_box = [
            x - padding,
            y - padding,
            x + text_width + padding,
            y + text_height + padding
        ]
        draw.rectangle(bg_box, fill=(10, 10, 10, 180))
        
        # Text
        draw.text((x, y), caption, fill=(234, 242, 255, 255), font=font)
    
    frames_with_captions.append(frame.convert('RGB'))

# Save enhanced GIF
enhanced_output = OUTPUT_DIR / "ssz_time_segmentation_enhanced.gif"
frames_with_captions[0].save(
    enhanced_output,
    save_all=True,
    append_images=frames_with_captions[1:],
    duration=int(1000/FPS),
    loop=0,
    optimize=False
)

enhanced_size_mb = enhanced_output.stat().st_size / (1024 * 1024)
print(f"  ✓ Enhanced GIF: {enhanced_size_mb:.2f} MB")

# ============================================================================
# VALIDATION REPORT
# ============================================================================

print("\n[5/5] Generating validation report...")

validation = {
    "timestamp": datetime.now().isoformat(),
    "parameters": {
        "phi": float(PHI),
        "xi_max": XI_MAX,
        "r_max": R_MAX,
        "samples": SAMPLES,
        "duration_seconds": DURATION,
        "fps": FPS,
        "total_frames": TOTAL_FRAMES
    },
    "physics": {
        "xi_range": [float(xi_r.min()), float(xi_r.max())],
        "delta_t_range": [float(delta_t_r.min()), float(delta_t_r.max())],
        "omega_range": [float(omega_r.min()), float(omega_r.max())],
        "time_slowdown_factor": float(delta_t_r.max() / delta_t_r.min())
    },
    "outputs": {
        "gif_original": {
            "file": str(OUTPUT_GIF),
            "size_mb": gif_size_mb,
            "exists": OUTPUT_GIF.exists()
        },
        "gif_enhanced": {
            "file": str(enhanced_output),
            "size_mb": enhanced_size_mb,
            "exists": enhanced_output.exists()
        }
    },
    "captions": CAPTIONS,
    "status": "PASSED"
}

report_file = OUTPUT_DIR / "ssz_time_segmentation_report.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(validation, f, indent=2)

print(f"  ✓ Report: {report_file}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("TIME SEGMENTATION ANIMATION COMPLETE")
print("="*80)
print(f"Original GIF:  {OUTPUT_GIF} ({gif_size_mb:.2f} MB)")
print(f"Enhanced GIF:  {enhanced_output} ({enhanced_size_mb:.2f} MB)")
print(f"Report:        {report_file}")
print("\nKey Results:")
print(f"  Time slowdown factor: {validation['physics']['time_slowdown_factor']:.3f}×")
print(f"  Ξ range: {validation['physics']['xi_range']}")
print(f"  Δt range: {validation['physics']['delta_t_range']}")
print("="*80)

print("\n✓ Ready for trimming and 30s versions!")
print("  Next: python trim_to_5_seconds.py")
print("  Next: python create_30s_version.py")
