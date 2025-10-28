#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create All Versions of Time vs Stability Animation
===================================================

Standard versions: 5s + 30s×2

© 2025 Carmen Wrede & Lino Casu
"""
import os
import sys
from pathlib import Path
from PIL import Image
import json
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

print("="*80)
print("SSZ TIME vs STABILITY - ALL VERSIONS GENERATOR")
print("="*80)

BASE_DIR = Path("d:/ssz_kruemung")
INPUT_GIF = BASE_DIR / "ssz_time_vs_stability.gif"

OUTPUT_5S = BASE_DIR / "ssz_time_vs_stability_5s.gif"
OUTPUT_30S_REPEAT = BASE_DIR / "ssz_time_vs_stability_30s_repeat.gif"
OUTPUT_30S_SLOW = BASE_DIR / "ssz_time_vs_stability_30s_slow.gif"

FPS = 25  # Original FPS
SLOW_FPS = 8  # Slow FPS (25/3 ≈ 8)

# Load frames
img = Image.open(INPUT_GIF)
actual_frames = 0
try:
    while True:
        img.seek(actual_frames)
        actual_frames += 1
except EOFError:
    pass

print(f"Source: {actual_frames} frames @ {FPS} FPS\n")

# 1. 5s version
print("[1/3] Creating 5-second preview...")
target_5s = min(int(5 * FPS), actual_frames)  # 125 frames
frames_5s = []
for i in range(target_5s):
    img.seek(i)
    frames_5s.append(img.copy())

frames_5s[0].save(OUTPUT_5S, save_all=True, append_images=frames_5s[1:],
                  duration=int(1000/FPS), loop=0, optimize=False)
size_5s = OUTPUT_5S.stat().st_size / (1024 * 1024)
print(f"  ✓ {OUTPUT_5S.name} ({size_5s:.2f} MB)")

# 2. 30s repeat
print("\n[2/3] Creating 30-second repeat (2× loop)...")
frames_all = []
for i in range(actual_frames):
    img.seek(i)
    frames_all.append(img.copy())

frames_repeat = frames_all * 2  # 2× for ~30s
frames_repeat[0].save(OUTPUT_30S_REPEAT, save_all=True, append_images=frames_repeat[1:],
                     duration=int(1000/FPS), loop=0, optimize=False)
size_30s_repeat = OUTPUT_30S_REPEAT.stat().st_size / (1024 * 1024)
duration_repeat = len(frames_repeat) / FPS
print(f"  ✓ {OUTPUT_30S_REPEAT.name} ({size_30s_repeat:.2f} MB, {duration_repeat:.1f}s)")

# 3. 30s slow
print("\n[3/3] Creating 30-second slow motion...")
frames_all[0].save(OUTPUT_30S_SLOW, save_all=True, append_images=frames_all[1:],
                  duration=int(1000/SLOW_FPS), loop=0, optimize=False)
size_30s_slow = OUTPUT_30S_SLOW.stat().st_size / (1024 * 1024)
duration_slow = len(frames_all) / SLOW_FPS
print(f"  ✓ {OUTPUT_30S_SLOW.name} ({size_30s_slow:.2f} MB, {duration_slow:.1f}s)")

# Summary
print("\n" + "="*80)
print("ALL COMBINED VERSIONS COMPLETE")
print("="*80)
print(f"1. Original (15s):  {INPUT_GIF.name} (1.77 MB)")
print(f"2. Preview (5s):    {OUTPUT_5S.name} ({size_5s:.2f} MB)")
print(f"3. Repeat (30s):    {OUTPUT_30S_REPEAT.name} ({size_30s_repeat:.2f} MB)")
print(f"4. Slow (47s):      {OUTPUT_30S_SLOW.name} ({size_30s_slow:.2f} MB)")
print("="*80)

summary = {
    "timestamp": datetime.now().isoformat(),
    "animation": "ssz_time_vs_stability",
    "versions": {
        "original": {"file": str(INPUT_GIF.name), "duration_s": 15, "size_mb": 1.77},
        "preview_5s": {"file": str(OUTPUT_5S.name), "duration_s": 5, "size_mb": round(size_5s, 2)},
        "repeat_30s": {"file": str(OUTPUT_30S_REPEAT.name), "duration_s": round(duration_repeat, 1), "size_mb": round(size_30s_repeat, 2)},
        "slow_30s": {"file": str(OUTPUT_30S_SLOW.name), "duration_s": round(duration_slow, 1), "size_mb": round(size_30s_slow, 2)}
    },
    "status": "COMPLETE"
}

summary_file = BASE_DIR / "time_vs_stability_versions_summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

print(f"\n✓ Summary: {summary_file}")
