#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick pipeline test - Generates single-language demo without full rendering
Tests TTS, audio analysis, and timeline generation only

© 2025 Carmen Wrede, Lino Casu
"""

import sys
import subprocess
from pathlib import Path

# UTF-8 setup
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

print("="*70)
print("SSZ Animation Pipeline - Quick Test")
print("="*70)

# Test espeak-ng availability
print("\n[1/4] Checking espeak-ng...")
try:
    result = subprocess.run(
        ['espeak-ng', '--version'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode == 0:
        print(f"✓ espeak-ng version: {result.stdout.split()[1]}")
        use_wsl = False
    else:
        raise FileNotFoundError
except FileNotFoundError:
    print("  espeak-ng not found in PATH, trying WSL...")
    try:
        result = subprocess.run(
            ['wsl', 'espeak-ng', '--version'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            print(f"✓ espeak-ng via WSL: {result.stdout.split()[1]}")
            use_wsl = True
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("✗ espeak-ng not available!")
        print("  Install: choco install espeak-ng")
        print("  Or WSL: wsl sudo apt install espeak-ng")
        sys.exit(1)

# Test FFmpeg
print("\n[2/4] Checking FFmpeg...")
try:
    result = subprocess.run(
        ['ffmpeg', '-version'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        print(f"✓ {version_line}")
    else:
        raise FileNotFoundError
except FileNotFoundError:
    print("✗ FFmpeg not found!")
    print("  Install: choco install ffmpeg")
    sys.exit(1)

# Test Python dependencies
print("\n[3/4] Checking Python packages...")
required_packages = ['matplotlib', 'numpy', 'yaml']
missing = []

for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        missing.append(pkg)
        print(f"  ✗ {pkg}")

if missing:
    print(f"\n  Installing missing packages: {', '.join(missing)}")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q'] + missing)
    print("  ✓ Installation complete")

# Run quick test (German only, skip rendering)
print("\n[4/4] Running quick pipeline test...")
print("  Language: German (DE)")
print("  Skipping video rendering (audio + timeline only)\n")

cmd = [
    sys.executable,
    str(Path(__file__).parent / 'ssz_animation_master.py'),
    '--languages', 'de',
    '--skip-render'
]

if use_wsl:
    cmd.append('--use-wsl')

result = subprocess.run(cmd, encoding='utf-8', errors='replace')

if result.returncode == 0:
    print("\n" + "="*70)
    print("✓ QUICK TEST PASSED")
    print("="*70)
    print("\nGenerated files:")
    print("  D:\\SSZ_Render\\audio\\ssz_intro_de.wav")
    print("  D:\\SSZ_Render\\timelines\\ssz_anim_de.yaml")
    print("  D:\\SSZ_Render\\durations.json")
    print("\nTo render full video, run:")
    print("  python ssz_animation_master.py")
    print("="*70)
    sys.exit(0)
else:
    print("\n" + "="*70)
    print("✗ QUICK TEST FAILED")
    print("="*70)
    print("\nCheck logs in: D:\\SSZ_Render\\logs\\")
    sys.exit(1)
