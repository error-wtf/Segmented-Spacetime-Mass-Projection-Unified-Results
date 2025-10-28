#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create All Standard Versions of Time Segmentation Animation
============================================================

Automatically generates:
1. Original (10s) - Already created
2. 5s Preview
3. 30s Repeat (3× loop)
4. 30s Slow Motion

© 2025 Carmen Wrede & Lino Casu
"""
import os
import sys
from pathlib import Path
from PIL import Image
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
print("SSZ TIME SEGMENTATION - ALL VERSIONS GENERATOR")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

BASE_DIR = Path("d:/ssz_kruemung")
INPUT_GIF = BASE_DIR / "ssz_time_segmentation_enhanced.gif"

# Output files
OUTPUT_5S = BASE_DIR / "ssz_time_segmentation_5s.gif"
OUTPUT_30S_REPEAT = BASE_DIR / "ssz_time_segmentation_30s_repeat.gif"
OUTPUT_30S_SLOW = BASE_DIR / "ssz_time_segmentation_30s_slow.gif"

FPS = 20
SLOW_FPS = 6

# ============================================================================
# 1. CREATE 5S VERSION
# ============================================================================

print("[1/3] Creating 5-second preview...")

if not INPUT_GIF.exists():
    print(f"  ❌ ERROR: {INPUT_GIF} not found!")
    sys.exit(1)

img = Image.open(INPUT_GIF)
actual_frames = 0
try:
    while True:
        img.seek(actual_frames)
        actual_frames += 1
except EOFError:
    pass

print(f"  Source: {actual_frames} frames")

# Extract first 5 seconds (100 frames at 20 FPS)
target_5s_frames = min(100, actual_frames)

frames_5s = []
for i in range(target_5s_frames):
    img.seek(i)
    frames_5s.append(img.copy())

print(f"  Extracting first {target_5s_frames} frames...")

frames_5s[0].save(
    OUTPUT_5S,
    save_all=True,
    append_images=frames_5s[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=False
)

size_5s = OUTPUT_5S.stat().st_size / (1024 * 1024)
print(f"  ✓ Saved: {OUTPUT_5S.name} ({size_5s:.2f} MB)")

# ============================================================================
# 2. CREATE 30S REPEAT VERSION (3× LOOP)
# ============================================================================

print("\n[2/3] Creating 30-second repeat version (3× loop)...")

frames_all = []
for i in range(actual_frames):
    img.seek(i)
    frames_all.append(img.copy())

print(f"  Loaded {len(frames_all)} frames")

# Repeat 3 times
frames_repeat = frames_all * 3
print(f"  Repeating 3× = {len(frames_repeat)} frames")

frames_repeat[0].save(
    OUTPUT_30S_REPEAT,
    save_all=True,
    append_images=frames_repeat[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=False
)

size_30s_repeat = OUTPUT_30S_REPEAT.stat().st_size / (1024 * 1024)
print(f"  ✓ Saved: {OUTPUT_30S_REPEAT.name} ({size_30s_repeat:.2f} MB)")

# ============================================================================
# 3. CREATE 30S SLOW MOTION VERSION
# ============================================================================

print("\n[3/3] Creating 30-second slow motion version...")

# Same frames, but at 6 FPS instead of 20 FPS
slow_duration_ms = int(1000 / SLOW_FPS)

frames_all[0].save(
    OUTPUT_30S_SLOW,
    save_all=True,
    append_images=frames_all[1:],
    duration=slow_duration_ms,
    loop=0,
    optimize=False
)

size_30s_slow = OUTPUT_30S_SLOW.stat().st_size / (1024 * 1024)
actual_duration_slow = len(frames_all) / SLOW_FPS

print(f"  ✓ Saved: {OUTPUT_30S_SLOW.name} ({size_30s_slow:.2f} MB)")
print(f"  Duration: {actual_duration_slow:.1f}s @ {SLOW_FPS} FPS")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ALL TIME SEGMENTATION VERSIONS COMPLETE")
print("="*80)
print(f"1. Original (10s):   {INPUT_GIF.name} (11.10 MB)")
print(f"2. Preview (5s):     {OUTPUT_5S.name} ({size_5s:.2f} MB)")
print(f"3. Repeat (30s):     {OUTPUT_30S_REPEAT.name} ({size_30s_repeat:.2f} MB)")
print(f"4. Slow Motion (30s): {OUTPUT_30S_SLOW.name} ({size_30s_slow:.2f} MB)")
print("="*80)

# Save summary
summary = {
    "timestamp": datetime.now().isoformat(),
    "base_animation": "ssz_time_segmentation",
    "versions": {
        "original": {
            "file": str(INPUT_GIF.name),
            "duration_s": actual_frames / FPS,
            "frames": actual_frames,
            "fps": FPS,
            "size_mb": 11.10
        },
        "preview_5s": {
            "file": str(OUTPUT_5S.name),
            "duration_s": target_5s_frames / FPS,
            "frames": target_5s_frames,
            "fps": FPS,
            "size_mb": round(size_5s, 2)
        },
        "repeat_30s": {
            "file": str(OUTPUT_30S_REPEAT.name),
            "duration_s": len(frames_repeat) / FPS,
            "frames": len(frames_repeat),
            "fps": FPS,
            "size_mb": round(size_30s_repeat, 2)
        },
        "slow_30s": {
            "file": str(OUTPUT_30S_SLOW.name),
            "duration_s": round(actual_duration_slow, 1),
            "frames": len(frames_all),
            "fps": SLOW_FPS,
            "size_mb": round(size_30s_slow, 2)
        }
    },
    "status": "COMPLETE"
}

summary_file = BASE_DIR / "time_segmentation_versions_summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

print(f"\n✓ Summary: {summary_file}")
