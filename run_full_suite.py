#!/usr/bin/env python3
"""
SSZ Projection Suite - Complete Test & Analysis Runner

Runs all tests, generates summaries, and echoes all Markdown outputs.

Copyright © 2025
Carmen Wrede und Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4

Usage:
    python run_full_suite.py
    python run_full_suite.py --skip-slow-tests
    python run_full_suite.py --quick
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
import argparse


def print_header(title, char="=", length=100):
    """Print formatted section header"""
    print("\n" + char * length)
    print(title)
    print(char * length + "\n")


def run_command(cmd, desc, timeout=None, check=True):
    """Run command and report status"""
    print(f"[RUNNING] {desc}")
    print(f"  Command: {' '.join(cmd)}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            timeout=timeout,
            check=check
        )
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"  [OK] {desc} (took {elapsed:.1f}s)")
            return True, elapsed
        else:
            print(f"  [FAILED] {desc} (exit code: {result.returncode})")
            return False, elapsed
            
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"  [TIMEOUT] {desc} (exceeded {timeout}s)")
        return False, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  [ERROR] {desc}: {e}")
        return False, elapsed


def main():
    parser = argparse.ArgumentParser(
        description="Run complete SSZ Suite test & analysis workflow"
    )
    parser.add_argument(
        "--skip-slow-tests",
        action="store_true",
        help="Skip slow/long-running tests"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: only essential tests"
    )
    parser.add_argument(
        "--no-echo-md",
        action="store_true",
        help="Skip MD echo at end"
    )
    
    args = parser.parse_args()
    
    # Start time
    suite_start = time.time()
    
    print_header("SSZ PROJECTION SUITE - FULL TEST & ANALYSIS WORKFLOW", "=")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working Directory: {Path.cwd()}")
    print("")
    
    results = {}
    
    # =============================================================================
    # PHASE 1: Core Unit Tests
    # =============================================================================
    print_header("PHASE 1: CORE UNIT TESTS", "-")
    
    tests_phase1 = [
        (["python", "-m", "pytest", "tests/test_segwave_core.py", "-v"], 
         "SegWave Core Math Tests", 60),
        (["python", "-m", "pytest", "tests/test_print_all_md.py", "-v"],
         "MD Print Tool Tests", 30),
    ]
    
    for cmd, desc, timeout in tests_phase1:
        success, elapsed = run_command(cmd, desc, timeout, check=False)
        results[desc] = {"success": success, "time": elapsed}
    
    # =============================================================================
    # PHASE 2: CLI & Integration Tests
    # =============================================================================
    print_header("PHASE 2: CLI & INTEGRATION TESTS", "-")
    
    tests_phase2 = [
        (["python", "-m", "pytest", "tests/test_segwave_cli.py", "-v"],
         "SegWave CLI & Dataset Tests", 120),
    ]
    
    for cmd, desc, timeout in tests_phase2:
        success, elapsed = run_command(cmd, desc, timeout, check=False)
        results[desc] = {"success": success, "time": elapsed}
    
    # =============================================================================
    # PHASE 3: Cosmos Tests (if not quick mode)
    # =============================================================================
    if not args.quick:
        print_header("PHASE 3: COSMOS TESTS", "-")
        
        tests_phase3 = [
            (["python", "-m", "pytest", "tests/cosmos/", "-v"],
             "Cosmos Multi-Body Tests", 60),
        ]
        
        for cmd, desc, timeout in tests_phase3:
            success, elapsed = run_command(cmd, desc, timeout, check=False)
            results[desc] = {"success": success, "time": elapsed}
    
    # =============================================================================
    # PHASE 4: Complete Test Suite (all together)
    # =============================================================================
    if not args.skip_slow_tests and not args.quick:
        print_header("PHASE 4: COMPLETE TEST SUITE", "-")
        
        cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
        success, elapsed = run_command(cmd, "All Tests Combined", 300, check=False)
        results["Complete Test Suite"] = {"success": success, "time": elapsed}
    
    # =============================================================================
    # PHASE 5: Example Runs (if not quick mode)
    # =============================================================================
    if not args.quick:
        print_header("PHASE 5: EXAMPLE ANALYSIS RUNS", "-")
        
        # Check if example data exists
        g79_data = Path("data/observations/G79_29+0_46_CO_NH3_rings.csv")
        cygx_data = Path("data/observations/CygnusX_DiamondRing_CII_rings.csv")
        
        if g79_data.exists():
            cmd = [
                "python", "-m", "cli.ssz_rings",
                "--csv", str(g79_data),
                "--v0", "12.5",
                "--fit-alpha",
                "--out-table", "reports/g79_test.csv",
                "--out-report", "reports/g79_test.txt"
            ]
            success, elapsed = run_command(cmd, "G79 Example Run", 30, check=False)
            results["G79 Analysis"] = {"success": success, "time": elapsed}
        
        if cygx_data.exists():
            cmd = [
                "python", "-m", "cli.ssz_rings",
                "--csv", str(cygx_data),
                "--v0", "1.3",
                "--alpha", "1.0",
                "--out-table", "reports/cygx_test.csv",
                "--out-report", "reports/cygx_test.txt"
            ]
            success, elapsed = run_command(cmd, "Cygnus X Example Run", 30, check=False)
            results["Cygnus X Analysis"] = {"success": success, "time": elapsed}
    
    # =============================================================================
    # PHASE 6: Generate Summary
    # =============================================================================
    suite_elapsed = time.time() - suite_start
    
    print_header("SUMMARY REPORT", "=")
    
    passed = sum(1 for r in results.values() if r["success"])
    failed = len(results) - passed
    total_test_time = sum(r["time"] for r in results.values())
    
    print(f"Total Phases: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(results)*100:.1f}%")
    print(f"Total Test Time: {total_test_time:.1f}s")
    print(f"Total Suite Time: {suite_elapsed:.1f}s")
    print("")
    
    print("Detailed Results:")
    for name, result in results.items():
        status = "[PASS]" if result["success"] else "[FAIL]"
        print(f"  {status} {name:40s} ({result['time']:.1f}s)")
    
    # Write summary to file
    summary_file = Path("reports/RUN_SUMMARY.md")
    summary_file.parent.mkdir(exist_ok=True)
    
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"# SSZ Suite Run Summary\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Overview\n\n")
        f.write(f"- **Total Phases:** {len(results)}\n")
        f.write(f"- **Passed:** {passed}\n")
        f.write(f"- **Failed:** {failed}\n")
        f.write(f"- **Success Rate:** {passed/len(results)*100:.1f}%\n")
        f.write(f"- **Total Test Time:** {total_test_time:.1f}s\n")
        f.write(f"- **Total Suite Time:** {suite_elapsed:.1f}s\n\n")
        f.write(f"## Detailed Results\n\n")
        for name, result in results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            f.write(f"- **{name}:** {status} ({result['time']:.1f}s)\n")
        f.write(f"\n---\n\n")
        f.write(f"**Copyright © 2025**\n")
        f.write(f"Carmen Wrede und Lino Casu\n")
        f.write(f"Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4\n")
    
    print(f"\nSummary written to: {summary_file}")
    
    # =============================================================================
    # PHASE 7: Echo All Markdown Outputs
    # =============================================================================
    if not args.no_echo_md:
        print_header("ECHOING ALL MARKDOWN OUTPUTS", "=")
        
        cmd = ["python", "-m", "tools.print_all_md", "--root", ".", "--order", "path"]
        print(f"[RUNNING] Markdown Echo")
        print(f"  Command: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"  [ERROR] MD echo failed: {e}")
    
    # =============================================================================
    # Final Status
    # =============================================================================
    print_header("WORKFLOW COMPLETE", "=")
    
    if failed == 0:
        print("✅ ALL PHASES PASSED")
        print(f"\nSuite completed successfully in {suite_elapsed:.1f}s")
        return 0
    else:
        print(f"⚠️  {failed} PHASE(S) FAILED")
        print(f"\nSuite completed with failures in {suite_elapsed:.1f}s")
        return 1


if __name__ == "__main__":
    sys.exit(main())
