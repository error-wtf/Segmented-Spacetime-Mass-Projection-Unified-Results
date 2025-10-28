#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Black Hole Stability - Animated Overview Generator
========================================================

Creates an animated GIF sequence showing all three main figures
with smooth transitions, captions, and zoom effects.

© 2025 Carmen Wrede & Lino Casu
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import json
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

print("="*80)
print("SSZ ANIMATED OVERVIEW GENERATOR")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path("d:/ssz_kruemung")

INPUT_IMAGES = [
    BASE_DIR / "ssz_formal_fig_Xi_Rproxy.png",
    BASE_DIR / "ssz_formal_fig_stability_map.png",
    BASE_DIR / "ssz_formal_fig_energy_series.png"
]

CAPTIONS = [
    "Segmentation Density Ξ(r) and Curvature Indicator R_proxy(r)",
    "Stability Phase Diagram – λ_A < 1/K² (Critical Threshold)",
    "Energy Evolution: Stable vs. Unstable Case (Damping η = 4.9×10³⁷)"
]

OUTPUT_GIF = BASE_DIR / "ssz_stability_overview.gif"
OUTPUT_RESOLUTION = (1920, 1080)
FPS = 20
DURATION_PER_IMAGE = 3.5  # seconds
TRANSITION_DURATION = 0.8  # seconds
TOTAL_DURATION = 10  # seconds

# ============================================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================================

def load_and_resize(img_path, target_size):
    """Load image and resize to target resolution"""
    img = Image.open(img_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Calculate aspect ratio preserving resize
    img_aspect = img.width / img.height
    target_aspect = target_size[0] / target_size[1]
    
    if img_aspect > target_aspect:
        # Image is wider - fit to width
        new_width = target_size[0]
        new_height = int(new_width / img_aspect)
    else:
        # Image is taller - fit to height
        new_height = target_size[1]
        new_width = int(new_height * img_aspect)
    
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create canvas with dark background
    canvas = Image.new('RGB', target_size, (10, 10, 30))
    
    # Center image on canvas
    x_offset = (target_size[0] - new_width) // 2
    y_offset = (target_size[1] - new_height) // 2
    canvas.paste(img, (x_offset, y_offset))
    
    return canvas

def add_caption(img, text, position='bottom', font_size=28):
    """Add caption overlay to image"""
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Try to use a nice font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position
    margin = 50
    if position == 'bottom':
        x = (img.width - text_width) // 2
        y = img.height - text_height - margin - 20
    elif position == 'top':
        x = (img.width - text_width) // 2
        y = margin
    else:
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2
    
    # Draw semi-transparent background
    padding = 20
    bg_box = [
        x - padding,
        y - padding // 2,
        x + text_width + padding,
        y + text_height + padding
    ]
    draw.rectangle(bg_box, fill=(10, 10, 10, 200))
    
    # Draw text
    draw.text((x, y), text, font=font, fill=(234, 242, 255, 255))
    
    return img

def apply_zoom(img, zoom_factor):
    """Apply zoom effect to image"""
    if abs(zoom_factor - 1.0) < 0.001:
        return img
    
    width, height = img.size
    new_width = int(width / zoom_factor)
    new_height = int(height / zoom_factor)
    
    # Calculate crop box (centered)
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = left + new_width
    bottom = top + new_height
    
    cropped = img.crop((left, top, right, bottom))
    return cropped.resize((width, height), Image.Resampling.LANCZOS)

def blend_images(img1, img2, alpha):
    """Blend two images with alpha transparency"""
    return Image.blend(img1, img2, alpha)

# ============================================================================
# ANIMATION GENERATION
# ============================================================================

def generate_animation():
    """Generate animated overview GIF"""
    
    print("\n[1/4] Loading images...")
    
    # Verify all input images exist
    for img_path in INPUT_IMAGES:
        if not img_path.exists():
            print(f"  ❌ ERROR: Image not found: {img_path}")
            return None
        print(f"  ✓ Found: {img_path.name}")
    
    # Load and resize images
    images = []
    for img_path in INPUT_IMAGES:
        img = load_and_resize(img_path, OUTPUT_RESOLUTION)
        images.append(img)
    
    print(f"\n[2/4] Generating animation frames...")
    print(f"  Resolution: {OUTPUT_RESOLUTION[0]}x{OUTPUT_RESOLUTION[1]}")
    print(f"  FPS: {FPS}")
    print(f"  Duration: {TOTAL_DURATION}s")
    
    frames = []
    total_frames = int(TOTAL_DURATION * FPS)
    
    frames_per_image = int(DURATION_PER_IMAGE * FPS)
    transition_frames = int(TRANSITION_DURATION * FPS)
    
    for i, (img, caption) in enumerate(zip(images, CAPTIONS)):
        print(f"\n  Processing image {i+1}/3: {INPUT_IMAGES[i].name}")
        
        # Add caption
        img_with_caption = add_caption(img.copy(), caption)
        
        # Hold frames (with subtle zoom)
        hold_frames = frames_per_image - transition_frames
        for frame_idx in range(hold_frames):
            # Subtle zoom in/out effect
            t = frame_idx / hold_frames
            zoom = 1.0 + 0.05 * np.sin(2 * np.pi * t)
            zoomed = apply_zoom(img_with_caption.copy(), zoom)
            frames.append(zoomed)
        
        # Transition to next image (if not last)
        if i < len(images) - 1:
            next_img = add_caption(images[i+1].copy(), CAPTIONS[i+1])
            
            for frame_idx in range(transition_frames):
                alpha = frame_idx / transition_frames
                # Smooth easing
                alpha = 0.5 - 0.5 * np.cos(np.pi * alpha)
                blended = blend_images(img_with_caption, next_img, alpha)
                frames.append(blended)
    
    print(f"\n  Total frames generated: {len(frames)}")
    
    # Pad to exact total duration
    while len(frames) < total_frames:
        frames.append(frames[-1])
    
    frames = frames[:total_frames]
    
    print(f"\n[3/4] Saving GIF...")
    print(f"  Output: {OUTPUT_GIF}")
    
    # Save as GIF
    frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),  # milliseconds per frame
        loop=0,
        optimize=False
    )
    
    file_size_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved: {file_size_mb:.2f} MB")
    
    return OUTPUT_GIF

# ============================================================================
# VALIDATION
# ============================================================================

def validate_results():
    """Validate simulation results and files"""
    
    print("\n[4/4] Validating results...")
    
    validation_report = {
        "timestamp": datetime.now().isoformat(),
        "validation_checks": [],
        "status": "PASSED"
    }
    
    # Check 1: TEST_SUMMARY.json exists and contains expected values
    summary_file = BASE_DIR / "TEST_SUMMARY.json"
    
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        phi = summary.get("phi")
        phi_squared = summary.get("phi_squared")
        
        PHI_EXPECTED = (1 + np.sqrt(5)) / 2
        PHI_SQ_EXPECTED = PHI_EXPECTED ** 2
        
        phi_check = abs(phi - PHI_EXPECTED) < 1e-8 if phi else False
        phi_sq_check = abs(phi_squared - PHI_SQ_EXPECTED) < 1e-8 if phi_squared else False
        
        validation_report["validation_checks"].append({
            "test": "TEST_SUMMARY.json - phi value",
            "expected": float(PHI_EXPECTED),
            "actual": float(phi) if phi else None,
            "passed": bool(phi_check)
        })
        
        validation_report["validation_checks"].append({
            "test": "TEST_SUMMARY.json - phi_squared value",
            "expected": float(PHI_SQ_EXPECTED),
            "actual": float(phi_squared) if phi_squared else None,
            "passed": bool(phi_sq_check)
        })
        
        print(f"  ✓ phi = {phi:.10f} (expected: {PHI_EXPECTED:.10f})")
        print(f"  ✓ phi² = {phi_squared:.10f} (expected: {PHI_SQ_EXPECTED:.10f})")
    else:
        validation_report["status"] = "FAILED"
        validation_report["validation_checks"].append({
            "test": "TEST_SUMMARY.json exists",
            "passed": False
        })
        print(f"  ❌ TEST_SUMMARY.json not found")
    
    # Check 2: All required files exist
    required_files = INPUT_IMAGES + [OUTPUT_GIF]
    
    for file_path in required_files:
        exists = file_path.exists()
        validation_report["validation_checks"].append({
            "test": f"File exists: {file_path.name}",
            "passed": bool(exists)
        })
        
        if exists:
            size_kb = file_path.stat().st_size / 1024
            print(f"  ✓ {file_path.name} ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ {file_path.name} MISSING")
            validation_report["status"] = "FAILED"
    
    # Check 3: All tests from test results
    all_passed = all(check["passed"] for check in validation_report["validation_checks"])
    if not all_passed:
        validation_report["status"] = "FAILED"
    
    # Save validation report
    report_file = BASE_DIR / "ssz_gif_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(validation_report, f, indent=2)
    
    print(f"\n  Validation report: {report_file}")
    print(f"  Status: {validation_report['status']}")
    
    # Generate Markdown report
    generate_markdown_report(validation_report)
    
    return validation_report

def generate_markdown_report(validation_data):
    """Generate Markdown validation report"""
    
    md_file = BASE_DIR / "ssz_gif_validation_report.md"
    
    md_content = f"""# SSZ Black Hole Stability - GIF Validation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {validation_data['status']}

---

## Validation Checks

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
"""
    
    for check in validation_data["validation_checks"]:
        test_name = check["test"]
        passed = check["passed"]
        status = "✅ PASS" if passed else "❌ FAIL"
        
        if "expected" in check and "actual" in check:
            expected = f"{check['expected']:.10f}" if isinstance(check['expected'], float) else check['expected']
            actual = f"{check['actual']:.10f}" if isinstance(check['actual'], float) else check['actual']
            md_content += f"| {test_name} | {expected} | {actual} | {status} |\n"
        else:
            md_content += f"| {test_name} | - | - | {status} |\n"
    
    md_content += f"""
---

## Generated Files

- `ssz_stability_overview.gif` - Animated overview ({TOTAL_DURATION}s, {FPS} FPS)
- `ssz_gif_validation_report.json` - Validation data (JSON)
- `ssz_gif_validation_report.md` - This report (Markdown)

---

## Configuration

- **Resolution:** {OUTPUT_RESOLUTION[0]} × {OUTPUT_RESOLUTION[1]}
- **FPS:** {FPS}
- **Duration:** {TOTAL_DURATION} seconds
- **Frames:** {int(TOTAL_DURATION * FPS)}
- **Transition:** {TRANSITION_DURATION}s
- **Hold time:** {DURATION_PER_IMAGE}s per image

---

## Images Included

1. **Segmentation & Curvature** (`ssz_formal_fig_Xi_Rproxy.png`)
   - Shows Ξ(r) and R_proxy(r)
   - Demonstrates finite curvature at r→0

2. **Stability Phase Diagram** (`ssz_formal_fig_stability_map.png`)
   - Critical threshold: λ_A = 1/K²
   - Stable/unstable regions clearly marked

3. **Energy Evolution** (`ssz_formal_fig_energy_series.png`)
   - Comparison: Stable vs. Unstable cases
   - Damping factor: η = 4.9×10³⁷

---

**© 2025 Carmen Wrede & Lino Casu**  
**Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4**
"""
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"  ✓ Markdown report: {md_file}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    
    try:
        # Generate animation
        output_file = generate_animation()
        
        if output_file:
            # Validate results
            validation = validate_results()
            
            print("\n" + "="*80)
            print("ANIMATION GENERATION COMPLETE")
            print("="*80)
            print(f"Output: {output_file}")
            print(f"Validation: {validation['status']}")
            print("="*80)
            
            return validation['status'] == "PASSED"
        else:
            print("\n❌ Animation generation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
