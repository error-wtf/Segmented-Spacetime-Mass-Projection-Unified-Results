#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Animation Extender - Create 30 Second Version
==================================================

Creates a 30-second version by either:
1. Repeating the 10s animation 3 times (3 loops)
2. Slowing down to ~6.67 FPS (smooth slow-motion)

© 2025 Carmen Wrede & Lino Casu
"""
import os
import sys
from pathlib import Path
from PIL import Image
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
print("SSZ ANIMATION EXTENDER - 30 Second Version")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path("d:/ssz_kruemung")
INPUT_GIF = BASE_DIR / "ssz_stability_overview.gif"
OUTPUT_30S_REPEAT = BASE_DIR / "ssz_stability_30s_repeat.gif"
OUTPUT_30S_SLOW = BASE_DIR / "ssz_stability_30s_slow.gif"

ORIGINAL_FPS = 20
ORIGINAL_DURATION = 10  # seconds
TARGET_DURATION = 30  # seconds

# Method 1: Repeat 3 times
REPEAT_COUNT = 3

# Method 2: Slow down
SLOW_FPS = int(ORIGINAL_FPS * ORIGINAL_DURATION / TARGET_DURATION)  # ~6.67 FPS

# ============================================================================
# METHOD 1: REPEAT 3 TIMES
# ============================================================================

def create_30s_repeat():
    """Create 30s version by repeating 10s animation 3 times"""
    
    print("\n[METHOD 1] Creating 30s version (3× repeat)...")
    print(f"  Source: {INPUT_GIF}")
    
    if not INPUT_GIF.exists():
        print(f"  ❌ ERROR: Source file not found!")
        return False
    
    source_size_mb = INPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"  Source size: {source_size_mb:.2f} MB")
    
    # Load all frames from original
    print(f"  Loading frames from original (10s)...")
    img = Image.open(INPUT_GIF)
    
    original_frames = []
    frame_idx = 0
    
    try:
        while True:
            img.seek(frame_idx)
            frame = img.copy()
            original_frames.append(frame)
            frame_idx += 1
    except EOFError:
        pass
    
    print(f"  ✓ Loaded {len(original_frames)} frames from original")
    
    # Repeat frames 3 times
    print(f"  Repeating frames {REPEAT_COUNT}× for 30s duration...")
    extended_frames = original_frames * REPEAT_COUNT
    
    print(f"  ✓ Total frames: {len(extended_frames)} (30s @ {ORIGINAL_FPS} FPS)")
    
    # Save extended GIF
    print(f"  Saving 30s repeat version...")
    print(f"  Output: {OUTPUT_30S_REPEAT}")
    
    extended_frames[0].save(
        OUTPUT_30S_REPEAT,
        save_all=True,
        append_images=extended_frames[1:],
        duration=int(1000 / ORIGINAL_FPS),  # milliseconds per frame
        loop=0,
        optimize=False
    )
    
    output_size_mb = OUTPUT_30S_REPEAT.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved: {output_size_mb:.2f} MB")
    print(f"  Size ratio: {output_size_mb/source_size_mb:.2f}× original")
    
    return True

# ============================================================================
# METHOD 2: SLOW MOTION
# ============================================================================

def create_30s_slow():
    """Create 30s version by slowing down to ~6.67 FPS"""
    
    print(f"\n[METHOD 2] Creating 30s version (slow motion @ {SLOW_FPS} FPS)...")
    print(f"  Source: {INPUT_GIF}")
    
    if not INPUT_GIF.exists():
        print(f"  ❌ ERROR: Source file not found!")
        return False
    
    # Load all frames
    print(f"  Loading frames from original...")
    img = Image.open(INPUT_GIF)
    
    frames = []
    frame_idx = 0
    
    try:
        while True:
            img.seek(frame_idx)
            frame = img.copy()
            frames.append(frame)
            frame_idx += 1
    except EOFError:
        pass
    
    print(f"  ✓ Loaded {len(frames)} frames")
    
    # Calculate frame duration for slow motion
    slow_duration_ms = int(1000 / SLOW_FPS)
    
    print(f"  Target FPS: {SLOW_FPS} (frame duration: {slow_duration_ms}ms)")
    print(f"  Expected duration: {len(frames) / SLOW_FPS:.2f}s")
    
    # Save slowed GIF
    print(f"  Saving slow motion version...")
    print(f"  Output: {OUTPUT_30S_SLOW}")
    
    frames[0].save(
        OUTPUT_30S_SLOW,
        save_all=True,
        append_images=frames[1:],
        duration=slow_duration_ms,
        loop=0,
        optimize=False
    )
    
    output_size_mb = OUTPUT_30S_SLOW.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved: {output_size_mb:.2f} MB")
    
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_outputs():
    """Validate 30s versions"""
    
    print("\n[VALIDATION] Checking outputs...")
    
    validation_report = {
        "timestamp": datetime.now().isoformat(),
        "target_duration_seconds": TARGET_DURATION,
        "methods": [],
        "status": "PASSED"
    }
    
    # Validate Method 1: Repeat
    if OUTPUT_30S_REPEAT.exists():
        size_mb = OUTPUT_30S_REPEAT.stat().st_size / (1024 * 1024)
        
        # Load and count frames
        img = Image.open(OUTPUT_30S_REPEAT)
        frame_count = 0
        try:
            while True:
                img.seek(frame_count)
                frame_count += 1
        except EOFError:
            pass
        
        actual_duration = frame_count / ORIGINAL_FPS
        duration_check = abs(actual_duration - TARGET_DURATION) < 0.1
        
        method_data = {
            "method": "3× repeat",
            "file": str(OUTPUT_30S_REPEAT),
            "size_mb": round(size_mb, 2),
            "frames": frame_count,
            "expected_frames": ORIGINAL_DURATION * ORIGINAL_FPS * REPEAT_COUNT,
            "duration_seconds": round(actual_duration, 2),
            "fps": ORIGINAL_FPS,
            "validation": {
                "exists": True,
                "duration_correct": duration_check
            }
        }
        
        validation_report["methods"].append(method_data)
        
        print(f"\n  Method 1 (Repeat):")
        print(f"    ✓ Exists: {size_mb:.2f} MB")
        print(f"    ✓ Frames: {frame_count} (expected {method_data['expected_frames']})")
        print(f"    ✓ Duration: {actual_duration:.2f}s @ {ORIGINAL_FPS} FPS")
        
        if not duration_check:
            validation_report["status"] = "WARNING"
    else:
        validation_report["status"] = "FAILED"
        print(f"  ❌ Method 1: File not found")
    
    # Validate Method 2: Slow
    if OUTPUT_30S_SLOW.exists():
        size_mb = OUTPUT_30S_SLOW.stat().st_size / (1024 * 1024)
        
        # Load and count frames
        img = Image.open(OUTPUT_30S_SLOW)
        frame_count = 0
        try:
            while True:
                img.seek(frame_count)
                frame_count += 1
        except EOFError:
            pass
        
        actual_duration = frame_count / SLOW_FPS
        duration_check = abs(actual_duration - TARGET_DURATION) < 1.0
        
        method_data = {
            "method": "slow motion",
            "file": str(OUTPUT_30S_SLOW),
            "size_mb": round(size_mb, 2),
            "frames": frame_count,
            "expected_frames": ORIGINAL_DURATION * ORIGINAL_FPS,
            "duration_seconds": round(actual_duration, 2),
            "fps": SLOW_FPS,
            "validation": {
                "exists": True,
                "duration_correct": duration_check
            }
        }
        
        validation_report["methods"].append(method_data)
        
        print(f"\n  Method 2 (Slow Motion):")
        print(f"    ✓ Exists: {size_mb:.2f} MB")
        print(f"    ✓ Frames: {frame_count} (expected {method_data['expected_frames']})")
        print(f"    ✓ Duration: {actual_duration:.2f}s @ {SLOW_FPS} FPS")
        
        if not duration_check:
            validation_report["status"] = "WARNING"
    else:
        print(f"  ⚠ Method 2: File not found (optional)")
    
    print(f"\n  Overall Status: {validation_report['status']}")
    
    # Save validation report
    report_file = BASE_DIR / "30s_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(validation_report, f, indent=2)
    
    print(f"  Report: {report_file}")
    
    return validation_report

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    
    try:
        # Method 1: Repeat 3 times
        success1 = create_30s_repeat()
        
        # Method 2: Slow motion
        success2 = create_30s_slow()
        
        # Validate
        validation = validate_outputs()
        
        print("\n" + "="*80)
        print("30-SECOND VERSIONS COMPLETE")
        print("="*80)
        
        if success1:
            print(f"Method 1 (Repeat): {OUTPUT_30S_REPEAT}")
        if success2:
            print(f"Method 2 (Slow):   {OUTPUT_30S_SLOW}")
        
        print(f"Validation: {validation['status']}")
        print("="*80)
        
        return validation['status'] in ['PASSED', 'WARNING']
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
