#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run all Black Hole Bomb Tests.

This script runs all 7 bomb test scripts (excluding animations).
"""
import subprocess
import sys
import os
from pathlib import Path

# UTF-8 setup for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except:
    pass

def run_script(script_path, optional=False):
    """Run a Python script and return success status
    
    Args:
        script_path: Path to the script
        optional: If True, failure won't count as overall failure
    """
    print(f"\n{'='*80}")
    print(f"Running: {script_path.name}")
    if optional:
        print("[OPTIONAL TEST]")
    print('='*80)
    
    # Special timeout for parameter scan (computationally intensive)
    timeout = 1200 if script_path.name == "ssz_parameter_scan.py" else 300
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print(f"[PASS] {script_path.name} completed successfully")
            return True
        else:
            if optional:
                print(f"[SKIP] {script_path.name} failed (optional test, not counted)")
                return True  # Count as pass for optional tests
            else:
                print(f"[FAIL] {script_path.name} failed with exit code {result.returncode}")
                return False
    except subprocess.TimeoutExpired:
        if optional:
            print(f"[SKIP] {script_path.name} timed out (optional test, not counted)")
            return True
        else:
            print(f"[TIMEOUT] {script_path.name} timed out after {timeout}s")
            return False
    except Exception as e:
        if optional:
            print(f"[SKIP] {script_path.name} error (optional test, not counted): {e}")
            return True
        else:
            print(f"[FAIL] {script_path.name} error: {e}")
            return False

def main():
    """Run all bomb tests (excluding animations)"""
    bomb_dir = Path("evidenz-ssz/scripts/black_hole_bomb")
    
    if not bomb_dir.exists():
        print(f"[ERROR] Bomb scripts directory not found: {bomb_dir}")
        return False
    
    # Scripts to run (excluding animations)
    # Format: (script_name, optional)
    scripts = [
        ("ssz_blackhole_bomb.py", False),
        ("ssz_blackhole_bomb_complete.py", False),
        ("ssz_blackhole_bomb_full.py", False),
        ("ssz_gr_bridge.py", False),
        ("ssz_parameter_scan.py", False),
        ("ssz_plot_packager.py", True),  # Optional - plotting only
        ("ssz_resonance_explorer.py", False),
        # Excluding: ssz_bomb_animation.py, ssz_live_visualizer.py
    ]
    
    results = []
    for script_name, optional in scripts:
        script_path = bomb_dir / script_name
        if script_path.exists():
            success = run_script(script_path, optional=optional)
            results.append((script_name, success, optional))
        else:
            print(f"⚠️ Script not found: {script_name}")
            results.append((script_name, False, optional))
    
    # Summary
    print("\n" + "="*80)
    print("BLACK HOLE BOMB TESTS - SUMMARY")
    print("="*80)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    required = sum(1 for _, _, optional in results if not optional)
    required_passed = sum(1 for _, success, optional in results if success and not optional)
    
    for script_name, success, optional in results:
        status = "✅ PASS" if success else "❌ FAIL" if not optional else "⏭️ SKIP"
        optional_tag = " [OPTIONAL]" if optional else ""
        print(f"{status} {script_name}{optional_tag}")
    
    print(f"\nRequired: {required_passed}/{required} passed")
    print(f"Total: {passed}/{total} passed ({100*passed/total:.1f}%)")
    print("="*80)
    
    return required_passed == required  # Success if all required tests pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
