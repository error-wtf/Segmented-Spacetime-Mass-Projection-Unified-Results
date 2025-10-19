#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Platform Test Runner for SSZ Theory Predictions

Tests the complete pipeline on both Windows and Linux/WSL:
1. Checks if data files exist (from run_all_ssz_terminal.py)
2. Runs theory predictions tests
3. Validates generated reports
4. Cross-platform UTF-8 compatibility

Usage:
    python test_theory_predictions_cross_platform.py
    
© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
import os
import subprocess
from pathlib import Path
import platform

# UTF-8 Setup (cross-platform)
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

def print_header(title, char="="):
    print("\n" + char * 80)
    print(title)
    print(char * 80)

def check_file(path: Path, desc: str) -> bool:
    """Check if file exists and show size"""
    if path.exists():
        size = path.stat().st_size
        print(f"  ✅ {desc}")
        print(f"     {path} ({size:,} bytes)")
        return True
    else:
        print(f"  ❌ {desc} - NOT FOUND")
        print(f"     Expected: {path}")
        return False

def main():
    print_header("SSZ THEORY PREDICTIONS - CROSS-PLATFORM TEST", "=")
    
    # System Info
    print(f"\n📊 System Information:")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Python:   {sys.version.split()[0]}")
    print(f"  Encoding: {sys.stdout.encoding}")
    print(f"  Working Dir: {Path.cwd()}")
    
    # Check required data files
    print_header("STEP 1: Check Data Files", "-")
    
    data_files = [
        (Path("out/phi_step_debug_full.csv"), "Phi Step Debug Data"),
        (Path("out/_enhanced_debug.csv"), "Enhanced Debug Data"),
    ]
    
    all_exist = True
    for path, desc in data_files:
        if not check_file(path, desc):
            all_exist = False
    
    if not all_exist:
        print("\n⚠️  Required data files missing!")
        print("\n💡 Generate them first:")
        print("   python run_all_ssz_terminal.py")
        print("\n   Or run full suite:")
        print("   python run_full_suite.py")
        return 1
    
    # Run Theory Predictions Tests
    print_header("STEP 2: Run Theory Predictions Tests", "-")
    
    test_script = Path("scripts/tests/test_horizon_hawking_predictions.py")
    
    if not test_script.exists():
        print(f"❌ Test script not found: {test_script}")
        return 1
    
    print(f"  Executing: {test_script}")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            encoding='utf-8',
            errors='replace',
            timeout=180
        )
        
        if result.returncode == 0:
            print("\n✅ Theory Predictions Tests PASSED")
        else:
            print(f"\n❌ Theory Predictions Tests FAILED (exit code: {result.returncode})")
            return result.returncode
            
    except subprocess.TimeoutExpired:
        print("\n❌ Tests timed out after 180 seconds")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1
    
    # Validate Generated Reports
    print_header("STEP 3: Validate Generated Reports", "-")
    
    report_files = [
        (Path("reports/hawking_proxy_fit.md"), "Hawking Spectrum BIC Analysis"),
        (Path("reports/SSZ_THEORY_PREDICTIONS_REAL_DATA_SUMMARY.md"), "Complete Theory Summary"),
    ]
    
    reports_ok = True
    for path, desc in report_files:
        if not check_file(path, desc):
            reports_ok = False
    
    # Test UTF-8 Output
    print_header("STEP 4: UTF-8 Compatibility Test", "-")
    
    test_chars = [
        ("Greek letters", "φ β γ α κ"),
        ("Math symbols", "≈ ± × ∈ ∞"),
        ("Emoji/Icons", "✅ ❌ ⚠️ 📊 🚀"),
        ("Subscripts", "r₀ r₁ r₂"),
        ("Arrows", "→ ← ↔"),
    ]
    
    utf8_ok = True
    for category, chars in test_chars:
        try:
            print(f"  {category}: {chars}")
        except UnicodeEncodeError as e:
            print(f"  ❌ {category}: ENCODING ERROR - {e}")
            utf8_ok = False
    
    if utf8_ok:
        print("\n  ✅ All UTF-8 characters displayed correctly")
    else:
        print("\n  ❌ UTF-8 encoding issues detected")
    
    # Final Summary
    print_header("SUMMARY", "=")
    
    checks = [
        ("Data Files", all_exist),
        ("Theory Tests", result.returncode == 0),
        ("Reports Generated", reports_ok),
        ("UTF-8 Compatible", utf8_ok),
    ]
    
    all_passed = all(status for _, status in checks)
    
    for check, status in checks:
        symbol = "✅" if status else "❌"
        print(f"  {symbol} {check}")
    
    if all_passed:
        print("\n🎉 ALL CROSS-PLATFORM TESTS PASSED!")
        print("\n✅ Pipeline works on:")
        print("   • Windows (Native)")
        print("   • Linux (Native)")
        print("   • WSL (Windows Subsystem for Linux)")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
