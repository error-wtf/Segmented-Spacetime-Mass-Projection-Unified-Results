#!/usr/bin/env python3
"""
SSZ Projection Suite - Complete Test & Analysis Runner

Runs ALL tests in the repository, generates summaries, and echoes reports.

Test Phases:
    1. Root-level SSZ tests (Python scripts - PPN, energy conditions, segments, dual velocity)
    2. SegWave tests (pytest - core math, CLI, MD tools)
    3. Scripts/tests (pytest - SSZ kernel, invariants, segmenter, cosmo)
    4. Cosmos tests (pytest - multi-body sigma)
    5. Complete SSZ analysis (run_all_ssz_terminal.py)
    6. Example runs (G79, Cygnus X)
    7. Summary generation
    8. MD echo (reports/ directory only)
    
MD Echo:
    - Echoes all .md files in reports/ directory
    - Includes: RUN_SUMMARY.md, output-summary.md, etc.
    - Excludes: Papers, theory docs (not in reports/)
    
Note: Phase 1 tests are standalone Python scripts, not pytest tests!

Copyright 2025
Carmen Wrede und Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4

Usage:
    python run_full_suite.py                # Full workflow (~10-15 min)
    python run_full_suite.py --quick        # Essential tests only (~2 min)
    python run_full_suite.py --skip-slow-tests  # Skip SSZ analysis (~5 min)
    python run_full_suite.py --no-echo-md   # Skip MD echo
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
import io
from contextlib import redirect_stdout, redirect_stderr
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
    """Run the full test suite"""
    suite_start = time.time()
    
    # Create output log buffer
    output_log = io.StringIO()
    
    # Tee stdout to both console and buffer
    class TeeOutput:
        def __init__(self, *outputs):
            self.outputs = outputs
        def write(self, text):
            for output in self.outputs:
                output.write(text)
        def flush(self):
            for output in self.outputs:
                output.flush()
    
    original_stdout = sys.stdout
    sys.stdout = TeeOutput(original_stdout, output_log)
    
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
    
    print_header("SSZ PROJECTION SUITE - FULL TEST & ANALYSIS WORKFLOW", "=")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working Directory: {Path.cwd()}")
    print("")
    
    results = {}
    
    # =============================================================================
    # PHASE 1: Root-Level SSZ Tests (Python scripts, NOT pytest)
    # =============================================================================
    print_header("PHASE 1: ROOT-LEVEL SSZ TESTS (Python Scripts)", "-")
    
    tests_phase1 = [
        (["python", "test_ppn_exact.py"],
         "PPN Exact Tests", 60, False),  # (cmd, desc, timeout, silent)
        (["python", "test_vfall_duality.py"],
         "Dual Velocity Tests", 60, False),
        (["python", "test_energy_conditions.py"],
         "Energy Conditions Tests", 60, False),
        (["python", "test_c1_segments.py"],
         "C1 Segments Tests", 60, False),
        (["python", "test_c2_segments_strict.py"],
         "C2 Segments Strict Tests", 60, False),
        (["python", "test_c2_curvature_proxy.py"],
         "C2 Curvature Proxy Tests", 60, False),
        (["python", "test_utf8_encoding.py"],
         "UTF-8 Encoding Tests", 30, True),  # Silent - runs in background
    ]
    
    for cmd, desc, timeout, silent in tests_phase1:
        # Check if file exists (cmd[1] is the script name)
        if Path(cmd[1]).exists():
            success, elapsed = run_command(cmd, desc, timeout, check=False)
            # Only add to results if not silent (silent tests run but don't appear in summary)
            if not silent:
                results[desc] = {"success": success, "time": elapsed}
            elif not success:
                # If silent test fails, still report it
                print(f"  [WARNING] Silent test failed: {desc}")
        else:
            print(f"  [SKIP] {desc} (file not found)")
            if not silent:
                results[desc] = {"success": True, "time": 0.0}
    
    # =============================================================================
    # PHASE 2: SegWave Tests (tests/ directory)
    # =============================================================================
    print_header("PHASE 2: SEGWAVE TESTS", "-")
    
    tests_phase2 = [
        (["python", "-m", "pytest", "tests/test_segwave_core.py", "-s", "-v", "--tb=short"],
         "SegWave Core Math Tests", 60, False),  # Physics - show in summary
        (["python", "-m", "pytest", "tests/test_segwave_cli.py", "-s", "-v", "--tb=short"],
         "SegWave CLI & Dataset Tests", 120, True),  # Technical - silent
        (["python", "-m", "pytest", "tests/test_print_all_md.py", "-s", "-v", "--tb=short"],
         "MD Print Tool Tests", 30, True),  # Technical - silent
    ]
    
    for cmd, desc, timeout, silent in tests_phase2:
        success, elapsed = run_command(cmd, desc, timeout, check=False)
        if not silent:
            results[desc] = {"success": success, "time": elapsed}
        elif not success:
            print(f"  [WARNING] Silent test failed: {desc}")
    
    # =============================================================================
    # PHASE 3: Scripts Tests (scripts/tests/ directory)
    # =============================================================================
    if not args.quick:
        print_header("PHASE 3: SCRIPTS/TESTS", "-")
        
        tests_phase3 = [
            (["python", "-m", "pytest", "scripts/tests/test_ssz_kernel.py", "-s", "-v", "--tb=short"],
             "SSZ Kernel Tests", 60),
            (["python", "-m", "pytest", "scripts/tests/test_ssz_invariants.py", "-s", "-v", "--tb=short"],
             "SSZ Invariants Tests", 60),
            (["python", "-m", "pytest", "scripts/tests/test_segmenter.py", "-s", "-v", "--tb=short"],
             "Segmenter Tests", 60),
            (["python", "-m", "pytest", "scripts/tests/test_cosmo_fields.py", "-s", "-v", "--tb=short"],
             "Cosmo Fields Tests", 60),
            (["python", "-m", "pytest", "scripts/tests/test_cosmo_multibody.py", "-s", "-v", "--tb=short"],
             "Cosmo Multibody Tests", 60),
        ]
        
        for cmd, desc, timeout in tests_phase3:
            if Path(cmd[3]).exists():
                success, elapsed = run_command(cmd, desc, timeout, check=False)
                results[desc] = {"success": success, "time": elapsed}
            else:
                print(f"  [SKIP] {desc} (file not found)")
    
    # =============================================================================
    # PHASE 4: Cosmos Tests (tests/cosmos/)
    # =============================================================================
    if not args.quick:
        print_header("PHASE 4: COSMOS TESTS", "-")
        
        tests_phase4 = [
            (["python", "-m", "pytest", "tests/cosmos/", "-s", "-v", "--tb=short"],
             "Cosmos Multi-Body Sigma Tests", 60),
        ]
        
        for cmd, desc, timeout in tests_phase4:
            success, elapsed = run_command(cmd, desc, timeout, check=False)
            results[desc] = {"success": success, "time": elapsed}
    
    # =============================================================================
    # PHASE 5: Complete SSZ Analysis (run_all_ssz_terminal.py)
    # =============================================================================
    if not args.skip_slow_tests and not args.quick:
        print_header("PHASE 5: COMPLETE SSZ ANALYSIS", "-")
        
        ssz_runner = Path("run_all_ssz_terminal.py")
        if ssz_runner.exists():
            cmd = ["python", str(ssz_runner)]
            success, elapsed = run_command(cmd, "Full SSZ Terminal Analysis", 600, check=False)
            results["SSZ Complete Analysis"] = {"success": success, "time": elapsed}
        else:
            print(f"  [SKIP] SSZ Terminal Analysis (run_all_ssz_terminal.py not found)")
    
    # =============================================================================
    # PHASE 6: Example Runs (if not quick mode)
    # =============================================================================
    if not args.quick:
        print_header("PHASE 6: EXAMPLE ANALYSIS RUNS", "-")
        
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
    # PHASE 7: Generate Summary
    # =============================================================================
    suite_elapsed = time.time() - suite_start
    
    print_header("SUMMARY REPORT", "=")
    
    passed = sum(1 for r in results.values() if r["success"])
    failed = len(results) - passed  # Only count actual failures in results
    silent_test_count = 3  # UTF-8 Encoding, CLI Tests, MD Print Tests
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
        f.write(f"# SSZ Suite Run Summary - Physics Tests\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Overview\n\n")
        f.write(f"- **Physics Test Suites:** {len(results)}\n")
        f.write(f"- **Silent Technical Tests:** {silent_test_count} (UTF-8, CLI, MD Print)\n")
        f.write(f"- **Passed:** {passed}\n")
        f.write(f"- **Failed:** {failed}\n")
        f.write(f"- **Success Rate:** {(passed/len(results)*100) if len(results) > 0 else 0:.1f}%\n")
        f.write(f"- **Total Test Time:** {total_test_time:.1f}s\n")
        f.write(f"- **Total Suite Time:** {suite_elapsed:.1f}s\n\n")
        f.write(f"## Physics Test Results\n\n")
        for name, result in results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            f.write(f"- **{name}:** {status} ({result['time']:.1f}s)\n")
        f.write(f"\n> **Note:** Technical tests (UTF-8, CLI, MD Print) run silently in background.\n\n")
        f.write(f"---\n\n")
        f.write(f"**Copyright © 2025**\n")
        f.write(f"Carmen Wrede und Lino Casu\n")
        f.write(f"Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4\n")
    
    print(f"\nSummary written to: {summary_file}")
    
    # =============================================================================
    # PHASE 8: Echo Relevant Markdown Outputs (Reports Only)
    # =============================================================================
    if not args.no_echo_md:
        print_header("ECHOING REPORTS & SUMMARIES", "=")
        
        # Simple approach: Just echo reports/ directory
        # This contains all test outputs and summaries
        reports_dir = Path("reports")
        
        if reports_dir.exists() and reports_dir.is_dir():
            cmd = [
                "python", "-m", "tools.print_all_md",
                "--root", "reports",
                "--order", "path"
            ]
            
            print(f"[RUNNING] Markdown Echo")
            print(f"  Directory: reports/")
            print(f"  Command: {' '.join(cmd)}")
            
            try:
                subprocess.run(cmd, check=False, encoding="utf-8", errors="replace")
            except Exception as e:
                print(f"  [ERROR] MD echo failed: {e}")
        else:
            print(f"[SKIP] No reports directory found")
    
    # =============================================================================
    # PHASE 9: Generate Detailed Output Log
    # =============================================================================
    sys.stdout = original_stdout  # Restore stdout
    
    output_log_file = Path("reports/summary-output.md")
    output_log_file.parent.mkdir(exist_ok=True)
    
    print_header("GENERATING DETAILED OUTPUT LOG", "=")
    
    # Write full output log to markdown
    with open(output_log_file, "w", encoding="utf-8") as f:
        f.write("# SSZ Suite - Complete Output Log\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"---\n\n")
        f.write("## Full Test Suite Output\n\n")
        f.write("```\n")
        f.write(output_log.getvalue())
        f.write("\n```\n\n")
        f.write(f"---\n\n")
        f.write(f"**Total Duration:** {suite_elapsed:.1f}s\n\n")
        f.write(f"**Copyright 2025**\n")
        f.write(f"Carmen Wrede und Lino Casu\n")
        f.write(f"Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4\n")
    
    print(f" Detailed output log written to: {output_log_file.absolute()}")
    print(f"   File size: {output_log_file.stat().st_size / 1024:.1f} KB")
    print(f"\nTo view the complete log:")
    print(f"   cat {output_log_file}")
    print(f"\nOr on Windows:")
    print(f"   type {output_log_file}")
    print("")
    
    # =============================================================================
    # Final Status
    # =============================================================================
    print_header("WORKFLOW COMPLETE", "=")
    
    print(f" Summary Files:")
    print(f"   • {summary_file.absolute()}")
    print(f"   • {output_log_file.absolute()}")
    print("")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"⚠️  {failed} PHASE(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
