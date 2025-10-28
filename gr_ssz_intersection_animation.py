#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time Dilation Intersection – GR meets SSZ
==========================================

Visualize the intersection point where GR and SSZ predict identical time dilation.
Generate animation and Fliki-compatible audio scripts.

Based on: gr_ssz_intersection_summary.md

© 2025 Carmen Wrede & Lino Casu
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

print("="*80)
print("GR-SSZ INTERSECTION ANIMATION")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# PARAMETERS (from gr_ssz_intersection_summary.md)
# ============================================================================

PARAMS = {
    'r_star_ratio': 1.386562,  # r*/r_s
    'D_star': 0.528007,         # Time dilation at intersection
    'phi': 1.618034,
    'Xi_max': 1.0,
    'G': 6.67430e-11,
    'c': 299792458.0,
    'M_sun': 1.98847e30
}

print("[STEP 1] Parameters loaded")
print(f"  r*/r_s = {PARAMS['r_star_ratio']:.6f}")
print(f"  D* = {PARAMS['D_star']:.6f}")
print(f"  φ = {PARAMS['phi']:.6f}")

# ============================================================================
# TIME DILATION FUNCTIONS
# ============================================================================

def time_dilation_GR(r_over_rs):
    """D_GR(r) = sqrt(1 - r_s/r) = sqrt(1 - 1/(r/r_s))"""
    ratio = 1.0 / r_over_rs
    if ratio >= 1.0:
        return 0.0
    return np.sqrt(1.0 - ratio)

def time_dilation_SSZ(r_over_rs, phi=None, Xi_max=1.0):
    """D_SSZ(r) = 1/(1 + Ξ) where Ξ = Ξ_max(1 - exp(-φ·r/r_s))"""
    if phi is None:
        phi = PARAMS['phi']
    exponent = -phi * r_over_rs
    Xi = Xi_max * (1.0 - np.exp(exponent))
    return 1.0 / (1.0 + Xi)

print("\n[STEP 2] Time dilation functions defined")
print("  D_GR(r) = sqrt(1 - r_s/r)")
print("  D_SSZ(r) = 1/(1 + Ξ(r))")

# ============================================================================
# GENERATE STATIC PLOT
# ============================================================================

print("\n[STEP 3] Generating static plot...")

OUTPUT_DIR = Path("d:/ssz_kruemung/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

r_range = np.linspace(1.01, 5.0, 1000)
D_GR_vals = np.array([time_dilation_GR(r) for r in r_range])
D_SSZ_vals = np.array([time_dilation_SSZ(r) for r in r_range])

fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#1a1a1a')

# Plot curves
ax.plot(r_range, D_GR_vals, lw=3.5, label='General Relativity', 
       color='#00bfff', zorder=3)
ax.plot(r_range, D_SSZ_vals, lw=3.5, label='Segmented Spacetime', 
       color='#ffb347', zorder=3)

# Mark intersection
r_star = PARAMS['r_star_ratio']
D_star = PARAMS['D_star']

ax.axvline(r_star, color='#888888', ls='--', lw=2, alpha=0.7, zorder=1)
ax.plot([r_star], [D_star], 'o', color='#ff4444', ms=12, 
       markeredgewidth=3, markeredgecolor='white', zorder=5)

# Annotation
ax.annotate(f'Intersection\n$r_* = {r_star:.3f}\\,r_s$\n$D_* = {D_star:.3f}$',
           xy=(r_star, D_star), xytext=(r_star + 0.5, D_star - 0.15),
           fontsize=13, color='white', weight='bold',
           bbox=dict(fc='#222222', ec='#ff4444', alpha=0.9, boxstyle='round,pad=0.8'),
           arrowprops=dict(arrowstyle='->', color='#ff4444', lw=2))

# Styling
ax.set_xlim(1.0, 5.0)
ax.set_ylim(0, 1.05)
ax.set_xlabel('$r / r_s$', fontsize=16, color='white', fontweight='bold')
ax.set_ylabel('$D(r) = dt_{\\mathrm{local}} / dt_{\\infty}$', 
             fontsize=16, color='white', fontweight='bold')
ax.set_title('Time Dilation: General Relativity meets Segmented Spacetime',
            fontsize=18, color='white', fontweight='bold', pad=20)

ax.tick_params(colors='white', labelsize=12)
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.spines['top'].set_color('#1a1a1a')
ax.spines['right'].set_color('#1a1a1a')

ax.grid(True, alpha=0.2, linestyle='--', color='white')
leg = ax.legend(loc='lower right', fontsize=14, framealpha=0.95, 
               facecolor='#222222', edgecolor='white')
for text in leg.get_texts():
    text.set_color('white')

fig.tight_layout()

plot_path = OUTPUT_DIR / "gr_ssz_time_dilation_plot.png"
fig.savefig(plot_path, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
plt.close(fig)

print(f"  ✓ {plot_path.name}")

# ============================================================================
# GENERATE ANIMATION (GIF)
# ============================================================================

print("\n[STEP 4] Generating animation (8 seconds @ 25 FPS)...")

FPS = 25
DURATION = 8
NUM_FRAMES = FPS * DURATION

frames = []

for frame_idx in range(NUM_FRAMES):
    # Progress: 0 to 1
    progress = frame_idx / (NUM_FRAMES - 1)
    
    # Animate curve revelation
    reveal_point = int(progress * len(r_range))
    
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#1a1a1a')
    
    # Plot revealed portions
    if reveal_point > 0:
        ax.plot(r_range[:reveal_point], D_GR_vals[:reveal_point], 
               lw=3.5, color='#00bfff', zorder=3)
        ax.plot(r_range[:reveal_point], D_SSZ_vals[:reveal_point], 
               lw=3.5, color='#ffb347', zorder=3)
    
    # Show intersection when reached
    if progress > 0.3:  # Show after 30% of animation
        ax.axvline(r_star, color='#888888', ls='--', lw=2, alpha=0.7, zorder=1)
        
    if progress > 0.35:
        ax.plot([r_star], [D_star], 'o', color='#ff4444', ms=12, 
               markeredgewidth=3, markeredgecolor='white', zorder=5)
    
    # Labels and styling
    ax.set_xlim(1.0, 5.0)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel('$r / r_s$', fontsize=16, color='white', fontweight='bold')
    ax.set_ylabel('$D(r)$', fontsize=16, color='white', fontweight='bold')
    ax.set_title('Time Dilation: GR meets SSZ', fontsize=18, color='white', 
                fontweight='bold', pad=20)
    
    ax.tick_params(colors='white', labelsize=12)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_color('#1a1a1a')
    ax.spines['right'].set_color('#1a1a1a')
    ax.grid(True, alpha=0.2, linestyle='--', color='white')
    
    # Legend (fade in)
    if progress > 0.5:
        alpha = min((progress - 0.5) * 2, 1.0)
        leg = ax.legend(['General Relativity', 'Segmented Spacetime'], 
                       loc='lower right', fontsize=14, framealpha=0.95*alpha,
                       facecolor='#222222', edgecolor='white')
        for text in leg.get_texts():
            text.set_color('white')
    
    fig.tight_layout()
    
    # Convert to image
    fig.canvas.draw()
    
    # Use buffer_rgba() for newer matplotlib
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    w, h = fig.canvas.get_width_height()
    buf = buf.reshape((h, w, 4))  # RGBA
    
    # Convert RGBA to RGB
    buf_rgb = buf[:, :, :3]
    
    frames.append(Image.fromarray(buf_rgb))
    plt.close(fig)
    
    if (frame_idx + 1) % 50 == 0:
        print(f"  Progress: {frame_idx+1}/{NUM_FRAMES} frames")

# Save GIF
gif_path = OUTPUT_DIR / "gr_ssz_intersection.gif"
frames[0].save(gif_path, save_all=True, append_images=frames[1:],
              duration=int(1000/FPS), loop=0, optimize=False)

size_mb = gif_path.stat().st_size / (1024 * 1024)
print(f"  ✓ {gif_path.name} ({size_mb:.2f} MB)")

# ============================================================================
# GENERATE FLIKI AUDIO SCRIPTS
# ============================================================================

print("\n[STEP 5] Generating Fliki-compatible audio scripts...")

AUDIO_DIR = OUTPUT_DIR / "gr_ssz_audio_tracks"
AUDIO_DIR.mkdir(exist_ok=True)

# English script
script_en = """[0:00] This visualization shows the intersection point
where General Relativity and Segmented Spacetime
predict the same time dilation.

[0:08] At one point three eight six Schwarzschild radii,
both theories agree.

[0:14] The time dilation factor is zero point five two eight.

[0:20] Beyond this radius, General Relativity predicts infinite slowdown,
collapsing into a singularity.

[0:28] But Segmented Spacetime saturates.
Time slows, but never stops.

[0:34] This confirms that both models share the same low-field limit,
but SSZ remains physically defined at high curvature.

[0:42] The intersection marks the transition
from continuous to segmented spacetime.

[0:48] Time does not disappear — it becomes granular.
"""

script_de = """[0:00] Diese Visualisierung zeigt den Schnittpunkt,
an dem Allgemeine Relativitätstheorie und Segmentierte Raumzeit
dieselbe Zeitdilatation vorhersagen.

[0:10] Bei eins Komma drei acht sechs Schwarzschildradien
stimmen beide Theorien überein.

[0:16] Der Zeitdilatationsfaktor beträgt null Komma fünf zwei acht.

[0:22] Jenseits dieses Radius sagt die Relativitätstheorie
eine unendliche Verlangsamung voraus und kollabiert in eine Singularität.

[0:32] Aber die Segmentierte Raumzeit sättigt sich.
Die Zeit verlangsamt sich, aber sie hört nie auf.

[0:40] Dies bestätigt, dass beide Modelle im schwachen Feld übereinstimmen,
aber SSZ im starken Krümmungsfeld physikalisch definiert bleibt.

[0:50] Der Schnittpunkt markiert den Übergang
von kontinuierlicher zu segmentierter Raumzeit.

[0:56] Die Zeit verschwindet nicht — sie wird granular.
"""

script_it = """[0:00] Questa visualizzazione mostra il punto d'intersezione
dove la Relatività Generale e lo Spaziotempo Segmentato
prevedono la stessa dilatazione del tempo.

[0:10] A uno virgola tre otto sei raggi di Schwarzschild,
entrambe le teorie concordano.

[0:16] Il fattore di dilatazione temporale è zero virgola cinque due otto.

[0:22] Oltre questo raggio, la Relatività Generale prevede
un rallentamento infinito, collassando in una singolarità.

[0:32] Ma lo Spaziotempo Segmentato si satura.
Il tempo rallenta, ma non finisce mai.

[0:40] Questo conferma che entrambi i modelli condividono
lo stesso limite di campo debole,
ma SSZ rimane fisicamente definito in alta curvatura.

[0:50] L'intersezione segna la transizione
da spaziotempo continuo a segmentato.

[0:56] Il tempo non scompare — diventa granulare.
"""

# Save scripts
scripts = {
    'en_matthew.txt': script_en,
    'de_anna.txt': script_de,
    'it_giorgio.txt': script_it
}

for filename, content in scripts.items():
    script_path = AUDIO_DIR / filename
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ {filename}")

# ============================================================================
# GENERATE FLIKI INSTRUCTIONS
# ============================================================================

instructions_path = AUDIO_DIR / "FLIKI_INSTRUCTIONS.md"
with open(instructions_path, 'w', encoding='utf-8') as f:
    f.write("""# Fliki Audio Production Instructions

## Files Generated

1. `en_matthew.txt` - English narration (Voice: Matthew)
2. `de_anna.txt` - German narration (Voice: Anna)  
3. `it_giorgio.txt` - Italian narration (Voice: Giorgio)

## Fliki Workflow

### Step 1: Create New Project
- Go to Fliki.ai
- Create new project: "GR-SSZ Intersection"
- Format: Video (1920×1080)
- Duration: Auto (from script)

### Step 2: Import Script
- Copy text from `en_matthew.txt` (or DE/IT)
- Paste into Fliki script editor
- Fliki will auto-detect timestamps `[0:00]`

### Step 3: Select Voice
- **English:** Matthew (Male, Professional, Clear)
- **German:** Anna (Female, Warm, Academic)
- **Italian:** Giorgio (Male, Energetic, Narrator)

### Step 4: Add Video
- Upload: `gr_ssz_intersection.gif` (background)
- OR use: `gr_ssz_time_dilation_plot.png` (static)
- Alignment: Full screen, centered

### Step 5: Sync Timing
- Fliki auto-syncs with timestamps
- Verify each segment aligns with visuals
- Adjust pauses if needed (Fliki editor)

### Step 6: Export
- Format: MP4 (1920×1080)
- Quality: High (10 Mbps)
- Audio: 192 kbps stereo
- Output: `gr_ssz_intersection_final_[lang].mp4`

## Timing Breakdown

| Timestamp | Content | Visual |
|-----------|---------|--------|
| 0:00-0:08 | Introduction | Curves appearing |
| 0:08-0:14 | Intersection value | Red dot highlight |
| 0:14-0:20 | Time dilation factor | Full curves visible |
| 0:20-0:28 | GR divergence | GR curve → 0 |
| 0:28-0:34 | SSZ saturation | SSZ curve stable |
| 0:34-0:42 | Theoretical meaning | Legend fade-in |
| 0:42-0:48 | Transition point | Intersection marker |
| 0:48-1:00 | Granular time | Final frame hold |

## Production Notes

**Voice Settings:**
- Speed: 0.95× (slightly slower, clearer)
- Pitch: 0 (neutral)
- Emphasis: Auto (Fliki AI)

**Background Music:**
- Optional: Ambient/Scientific (low volume 15%)
- Recommendation: None (let narration carry)

**Transitions:**
- Between segments: Crossfade 0.3s
- At timestamps: Hard cut (for precision)

## Multi-Language Strategy

**Primary:** English (Matthew)  
**Secondary:** German (Anna) for European audience  
**Tertiary:** Italian (Giorgio) for Italian physics community  

Upload all three versions to:
- YouTube (EN primary, DE/IT subtitles)
- Vimeo (separate EN/DE/IT)
- ResearchGate (EN with multilingual abstract)

## Expected Output

**File Size:** ~20-40 MB per video (1 minute @ 1080p)  
**Total:** 3 videos × ~30 MB = ~90 MB  
**Duration:** ~60 seconds each (narration + pauses)

---

**Generated:** {}
**Source Animation:** gr_ssz_intersection.gif  
**Source Plot:** gr_ssz_time_dilation_plot.png  
**Scripts:** en_matthew.txt, de_anna.txt, it_giorgio.txt

**Ready for Fliki production!**
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

print(f"  ✓ FLIKI_INSTRUCTIONS.md")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("GR-SSZ INTERSECTION ANIMATION COMPLETE")
print("="*80)

print(f"""
Outputs:
  1. Static Plot:  {plot_path.name}
  2. Animation:    {gif_path.name} ({size_mb:.2f} MB, {DURATION}s @ {FPS} FPS)
  3. Audio Scripts:
     - en_matthew.txt (English)
     - de_anna.txt (German)
     - it_giorgio.txt (Italian)
  4. Instructions: FLIKI_INSTRUCTIONS.md

Next Steps:
  1. Upload gif/plot to Fliki.ai
  2. Import script (auto-detects timestamps)
  3. Select voice (Matthew/Anna/Giorgio)
  4. Export as MP4 (1920×1080)
  5. Publish!

Key Result:
  Intersection at r*/r_s = {PARAMS['r_star_ratio']:.6f}
  where D_GR = D_SSZ = {PARAMS['D_star']:.3f}
  
  → Transition from continuous (GR) to segmented (SSZ) spacetime
  → Time slows but never stops (SSZ saturation)
  → Universal, mass-independent ratio!
""")

print("="*80)
print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
