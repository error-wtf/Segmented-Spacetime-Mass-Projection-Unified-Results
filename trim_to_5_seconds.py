#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Animation Trimmer - Extract First 5 Seconds
================================================

Extracts the first 5 seconds from ssz_stability_overview.gif
and creates both GIF and MP4 versions.

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
print("SSZ ANIMATION TRIMMER - First 5 Seconds")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path("d:/ssz_kruemung")
INPUT_GIF = BASE_DIR / "ssz_stability_overview.gif"
OUTPUT_GIF = BASE_DIR / "ssz_stability_preview_0to5s.gif"
OUTPUT_MP4 = BASE_DIR / "ssz_stability_preview_0to5s.mp4"

FPS = 20
TRIM_DURATION = 5  # seconds
TRIM_FRAMES = FPS * TRIM_DURATION  # 100 frames

# ============================================================================
# TRIM GIF FUNCTION
# ============================================================================

def trim_gif_to_5_seconds():
    """Extract first 5 seconds (100 frames) from GIF"""
    
    print("\n[1/4] Loading source GIF...")
    print(f"  Source: {INPUT_GIF}")
    
    if not INPUT_GIF.exists():
        print(f"  ❌ ERROR: Source file not found!")
        return False
    
    source_size_mb = INPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"  Size: {source_size_mb:.2f} MB")
    
    # Open GIF
    img = Image.open(INPUT_GIF)
    
    # Extract frames
    print(f"\n[2/4] Extracting first {TRIM_FRAMES} frames ({TRIM_DURATION}s @ {FPS} FPS)...")
    
    frames = []
    frame_count = 0
    
    try:
        while frame_count < TRIM_FRAMES:
            img.seek(frame_count)
            frame = img.copy()
            frames.append(frame)
            frame_count += 1
            
            if frame_count % 20 == 0:
                print(f"  Progress: {frame_count}/{TRIM_FRAMES} frames...")
    
    except EOFError:
        print(f"  ⚠ Reached end of GIF at frame {frame_count}")
        if frame_count < TRIM_FRAMES:
            print(f"  ⚠ Warning: Only {frame_count} frames available (expected {TRIM_FRAMES})")
    
    print(f"  ✓ Extracted {len(frames)} frames")
    
    # Save trimmed GIF
    print(f"\n[3/4] Saving trimmed GIF...")
    print(f"  Output: {OUTPUT_GIF}")
    
    frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),  # milliseconds per frame
        loop=0,
        optimize=False
    )
    
    output_size_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved: {output_size_mb:.2f} MB")
    print(f"  Compression: {(1 - output_size_mb/source_size_mb)*100:.1f}% smaller")
    
    return True

# ============================================================================
# CREATE MP4 (OPTIONAL)
# ============================================================================

def create_mp4_version():
    """Create MP4 version using moviepy (if available)"""
    
    print(f"\n[4/4] Creating MP4 version...")
    
    try:
        from moviepy.editor import ImageSequenceClip
        import numpy as np
        
        print("  Loading frames from trimmed GIF...")
        
        # Load frames from trimmed GIF
        img = Image.open(OUTPUT_GIF)
        frames = []
        frame_idx = 0
        
        try:
            while True:
                img.seek(frame_idx)
                frame = img.copy()
                frame_rgb = frame.convert('RGB')
                frames.append(np.array(frame_rgb))
                frame_idx += 1
        except EOFError:
            pass
        
        print(f"  Loaded {len(frames)} frames")
        
        # Create video clip
        clip = ImageSequenceClip(frames, fps=FPS)
        
        print(f"  Writing MP4: {OUTPUT_MP4}")
        clip.write_videofile(
            str(OUTPUT_MP4),
            fps=FPS,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None
        )
        
        mp4_size_mb = OUTPUT_MP4.stat().st_size / (1024 * 1024)
        print(f"  ✓ Saved: {mp4_size_mb:.2f} MB")
        
        return True
        
    except ImportError:
        print("  ⚠ moviepy not installed - skipping MP4 creation")
        print("  Install with: pip install moviepy")
        return False
    
    except Exception as e:
        print(f"  ⚠ MP4 creation failed: {e}")
        return False

# ============================================================================
# VALIDATION
# ============================================================================

def validate_output():
    """Validate trimmed outputs"""
    
    print("\n[VALIDATION] Checking outputs...")
    
    validation_report = {
        "timestamp": datetime.now().isoformat(),
        "trim_duration_seconds": TRIM_DURATION,
        "fps": FPS,
        "expected_frames": TRIM_FRAMES,
        "checks": [],
        "status": "PASSED"
    }
    
    # Check 1: GIF exists
    gif_exists = OUTPUT_GIF.exists()
    validation_report["checks"].append({
        "test": "Trimmed GIF exists",
        "expected": str(OUTPUT_GIF),
        "passed": gif_exists
    })
    
    if gif_exists:
        gif_size_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
        print(f"  ✓ GIF exists: {gif_size_mb:.2f} MB")
        
        # Verify frame count
        img = Image.open(OUTPUT_GIF)
        actual_frames = 0
        try:
            while True:
                img.seek(actual_frames)
                actual_frames += 1
        except EOFError:
            pass
        
        frame_check = actual_frames == TRIM_FRAMES or actual_frames >= (TRIM_FRAMES - 5)
        validation_report["checks"].append({
            "test": "Frame count correct",
            "expected": TRIM_FRAMES,
            "actual": actual_frames,
            "passed": frame_check
        })
        
        print(f"  ✓ Frames: {actual_frames} (expected {TRIM_FRAMES})")
        
        # Duration check
        actual_duration = actual_frames / FPS
        duration_check = abs(actual_duration - TRIM_DURATION) < 0.1
        validation_report["checks"].append({
            "test": "Duration correct",
            "expected": TRIM_DURATION,
            "actual": actual_duration,
            "passed": duration_check
        })
        
        print(f"  ✓ Duration: {actual_duration:.2f}s (expected {TRIM_DURATION}s)")
    else:
        print(f"  ❌ GIF not found!")
        validation_report["status"] = "FAILED"
    
    # Check 2: MP4 (optional)
    mp4_exists = OUTPUT_MP4.exists()
    if mp4_exists:
        mp4_size_mb = OUTPUT_MP4.stat().st_size / (1024 * 1024)
        print(f"  ✓ MP4 exists: {mp4_size_mb:.2f} MB")
        validation_report["checks"].append({
            "test": "MP4 exists (optional)",
            "passed": True
        })
    else:
        print(f"  ⚠ MP4 not created (optional)")
    
    # Overall status
    all_required_passed = all(
        check["passed"] for check in validation_report["checks"] 
        if "optional" not in check["test"]
    )
    
    if not all_required_passed:
        validation_report["status"] = "FAILED"
    
    print(f"\n  Overall Status: {validation_report['status']}")
    
    # Save validation report
    report_file = BASE_DIR / "trim_validation_report.json"
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
        # Step 1: Trim GIF
        success = trim_gif_to_5_seconds()
        
        if not success:
            print("\n❌ Trimming failed")
            return False
        
        # Step 2: Create MP4 (optional)
        create_mp4_version()
        
        # Step 3: Validate
        validation = validate_output()
        
        print("\n" + "="*80)
        print("TRIM COMPLETE")
        print("="*80)
        print(f"GIF: {OUTPUT_GIF}")
        if OUTPUT_MP4.exists():
            print(f"MP4: {OUTPUT_MP4}")
        print(f"Validation: {validation['status']}")
        print("="*80)
        
        return validation['status'] == "PASSED"
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
