#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Runner for Comprehensive SSZ Real Data Tests

This script runs the comprehensive test suite and generates a detailed report
with all physical interpretations and results.

Cross-platform compatible: Works on Linux, macOS, and Windows.

Usage:
    python run_comprehensive_tests.py
    python run_comprehensive_tests.py --html  # Generate HTML report
    python run_comprehensive_tests.py --object SgrA*  # Test specific object
"""

import sys
import os
import subprocess
import argparse
import platform
from pathlib import Path
from datetime import datetime

# Force UTF-8 (cross-platform)
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Detect Python command (python3 on Linux, python on Windows)
PYTHON_CMD = sys.executable  # Use same Python that's running this script

def main():
    parser = argparse.ArgumentParser(
        description="Run Comprehensive SSZ Real Data Tests"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report"
    )
    parser.add_argument(
        "--object",
        type=str,
        help="Test specific astronomical object (Sun, SgrA*, M87*, etc.)"
    )
    parser.add_argument(
        "--radius",
        type=float,
        help="Test specific radius multiplier (e.g. 2.0 for 2r_s)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="test_results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output (show all physical interpretations)"
    )
    args = parser.parse_args()
    
    print("="*80)
    print("SEGMENTED SPACETIME - COMPREHENSIVE TEST RUNNER")
    print("="*80)
    print(f"Platform:  {platform.system()} {platform.release()}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python:    {sys.version.split()[0]} ({PYTHON_CMD})")
    print("="*80 + "\n")
    
    # Build pytest command (cross-platform)
    test_file = Path("tests") / "test_ssz_real_data_comprehensive.py"
    cmd = [PYTHON_CMD, "-X", "utf8", "-m", "pytest"]
    cmd.append(str(test_file))  # Convert Path to string for subprocess
    
    # Add filters
    if args.object:
        cmd.extend(["-k", args.object])
        print(f"→ Filtering for object: {args.object}")
    
    if args.radius:
        cmd.extend(["-k", str(args.radius)])
        print(f"→ Filtering for radius: {args.radius}r_s")
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
        cmd.append("-s")  # Don't capture output
        print("→ Verbose mode enabled")
    else:
        cmd.append("-v")
    
    # Setup output directory (cross-platform)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Add HTML report
    if args.html:
        html_path = output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        cmd.extend(["--html", str(html_path), "--self-contained-html"])
        print(f"→ HTML report will be saved to: {html_path}")
    
    # Add JUnit XML
    junit_path = output_dir / f"junit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    cmd.extend(["--junitxml", str(junit_path)])
    print(f"→ JUnit XML will be saved to: {junit_path}")
    
    print("\n" + "="*80)
    print("RUNNING TESTS")
    print("="*80)
    print(f"Command: {' '.join(cmd)}")
    print("="*80 + "\n")
    
    # Run tests
    try:
        result = subprocess.run(
            cmd,
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        print("\n" + "="*80)
        print("TEST EXECUTION COMPLETE")
        print("="*80)
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("Status: ✓ ALL TESTS PASSED")
        else:
            print("Status: ✗ SOME TESTS FAILED")
        
        if args.html and html_path.exists():
            print(f"\n→ HTML report: {html_path}")
            print(f"  Open with: start {html_path}")
        
        print(f"→ JUnit XML: {junit_path}")
        print("="*80 + "\n")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n\n→ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n✗ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
