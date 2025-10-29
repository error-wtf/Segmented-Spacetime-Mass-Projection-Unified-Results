#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLACK HOLE BOMB TESTS - SSZ Framework Validation
Run all black hole bomb scripts (non-animation) for scientific validation

© 2025 Carmen Wrede, Lino Casu
"""
import subprocess
import sys
from pathlib import Path

def run_script(script_path):
    """Run a Python script and return success status"""
    print(f"\n{'='*80}")
    print(f"Running: {script_path.name}")
    print('='*80)
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"✅ {script_path.name} completed successfully")
            return True
        else:
            print(f"❌ {script_path.name} failed with exit code {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ {script_path.name} timed out (>5 min)")
        return False
    except Exception as e:
        print(f"❌ {script_path.name} error: {e}")
        return False

def main():
    """Run all bomb tests (excluding animations)"""
    bomb_dir = Path("evidenz-ssz/scripts/black_hole_bomb")
    
    if not bomb_dir.exists():
        print(f"❌ Bomb scripts directory not found: {bomb_dir}")
        return False
    
    # Scripts to run (excluding animations)
    scripts = [
        "ssz_blackhole_bomb.py",
        "ssz_blackhole_bomb_complete.py",
        "ssz_blackhole_bomb_full.py",
        "ssz_gr_bridge.py",
        "ssz_parameter_scan.py",
        "ssz_plot_packager.py",
        "ssz_resonance_explorer.py",
        # Excluding: ssz_bomb_animation.py, ssz_live_visualizer.py
    ]
    
    results = []
    for script_name in scripts:
        script_path = bomb_dir / script_name
        if script_path.exists():
            success = run_script(script_path)
            results.append((script_name, success))
        else:
            print(f"⚠️ Script not found: {script_name}")
            results.append((script_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("BLACK HOLE BOMB TESTS - SUMMARY")
    print("="*80)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for script_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {script_name}")
    
    print(f"\nTotal: {passed}/{total} passed ({100*passed/total:.1f}%)")
    print("="*80)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
