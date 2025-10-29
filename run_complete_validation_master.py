#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER VALIDATION PIPELINE - SSZ Theory Complete

Runs ALL validations from A to Z:
1. Formula verification
2. Test suite (22 tests)
3. ToE validation (11 steps)
4. ToE v2 (6 pillars)
5. Grid convergence
6. Generates ALL outputs, reports, plots

Creates:
- full-output.md (complete log)
- All summary files
- All reports
- All plots
- Updates documentation

© 2025 Carmen Wrede & Lino Casu
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import io

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_BASE = Path('validation_complete')
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

FULL_OUTPUT_FILE = OUTPUT_BASE / 'full-output.md'
SUMMARY_FILE = OUTPUT_BASE / 'COMPLETE_VALIDATION_SUMMARY.md'
REPORTS_DIR = OUTPUT_BASE / 'reports'
PLOTS_DIR = OUTPUT_BASE / 'plots'

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# OUTPUT CAPTURE
# ============================================================================

class TeeOutput:
    """Capture output to both stdout and buffer"""
    def __init__(self, *outputs):
        self.outputs = outputs
    
    def write(self, data):
        for output in self.outputs:
            output.write(data)
            output.flush()
    
    def flush(self):
        for output in self.outputs:
            output.flush()

# ============================================================================
# PIPELINE STEPS
# ============================================================================

PIPELINE = [
    {
        'id': 'verify_formulas',
        'name': 'Formula Verification',
        'script': 'verify_theory_scientific.py',
        'timeout': 60,
        'critical': True
    },
    {
        'id': 'test_suite',
        'name': 'Complete Test Suite (22 tests)',
        'script': 'run_full_suite.py',
        'timeout': 600,
        'critical': True
    },
    {
        'id': 'toe_unified',
        'name': 'ToE Unified Validation (11 steps)',
        'script': 'run_ssz_unified_validation.py',
        'timeout': 300,
        'critical': True
    },
    {
        'id': 'toe_v2',
        'name': 'ToE Validation v2 (6 pillars)',
        'script': 'run_toe_validation_v2.py',
        'timeout': 120,
        'critical': True
    },
    {
        'id': 'grid_convergence',
        'name': 'Grid Convergence Test (F-16)',
        'script': 'test_grid_convergence.py',
        'timeout': 60,
        'critical': False
    },
    {
        'id': 'proper_time',
        'name': 'Proper Time Validation',
        'script': 'run_proper_time_validation.py',
        'timeout': 300,
        'critical': False
    },
    {
        'id': 'theory_validation',
        'name': 'Theory Validation',
        'script': 'run_ssz_theory_validation.py',
        'timeout': 300,
        'critical': False
    },
]

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_step(step, output_buffer):
    """Run a single validation step"""
    print("\n" + "=" * 80, file=output_buffer)
    print(f"STEP: {step['name']}", file=output_buffer)
    print("=" * 80, file=output_buffer)
    print(f"Script: {step['script']}", file=output_buffer)
    print(f"Timeout: {step['timeout']}s", file=output_buffer)
    print(f"Critical: {step['critical']}", file=output_buffer)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}", file=output_buffer)
    print(file=output_buffer)
    
    try:
        result = subprocess.run(
            [sys.executable, step['script']],
            capture_output=True,
            text=True,
            timeout=step['timeout'],
            encoding='utf-8',
            errors='replace'
        )
        
        # Write output
        print(result.stdout, file=output_buffer)
        if result.stderr:
            print("\nSTDERR:", file=output_buffer)
            print(result.stderr, file=output_buffer)
        
        success = result.returncode == 0
        
        print(f"\nCompleted: {datetime.now().strftime('%H:%M:%S')}", file=output_buffer)
        print(f"Exit Code: {result.returncode}", file=output_buffer)
        print(f"Status: {'[OK] SUCCESS' if success else '[FAIL] FAILED'}", file=output_buffer)
        
        return {
            'step': step['id'],
            'name': step['name'],
            'success': success,
            'exit_code': result.returncode,
            'critical': step['critical']
        }
        
    except subprocess.TimeoutExpired:
        print(f"\n[FAIL] TIMEOUT after {step['timeout']}s", file=output_buffer)
        return {
            'step': step['id'],
            'name': step['name'],
            'success': False,
            'exit_code': -1,
            'critical': step['critical'],
            'timeout': True
        }
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}", file=output_buffer)
        return {
            'step': step['id'],
            'name': step['name'],
            'success': False,
            'exit_code': -2,
            'critical': step['critical'],
            'error': str(e)
        }

def collect_outputs():
    """Collect all generated outputs, plots, reports"""
    print("\n" + "=" * 80)
    print("COLLECTING OUTPUTS")
    print("=" * 80)
    
    # Collect plots
    plot_sources = [
        'outputs/unified_validation/*.png',
        'outputs_propertime/*.png',
        'outputs_shapiro_proxy/*.png',
        'validation_out_v2/*.png',
        'outputs/*.png',
    ]
    
    plot_count = 0
    for pattern in plot_sources:
        for file in Path('.').glob(pattern):
            dest = PLOTS_DIR / file.name
            shutil.copy2(file, dest)
            plot_count += 1
            print(f"  [OK] {file.name}")
    
    print(f"\nCollected {plot_count} plots")
    
    # Collect reports
    report_sources = [
        '*.md',
        'docs/theory/*.md',
        'validation_out_v2/*.json',
        'outputs/unified_validation/*.json',
    ]
    
    report_count = 0
    for pattern in report_sources:
        for file in Path('.').glob(pattern):
            if file.name not in ['README.md', 'LICENSE.md']:
                try:
                    dest = REPORTS_DIR / file.name
                    shutil.copy2(file, dest)
                    report_count += 1
                except:
                    pass
    
    print(f"Collected {report_count} reports")
    
    # Collect data outputs
    data_sources = [
        'outputs_propertime/*.csv',
        'outputs_shapiro_proxy/*.csv',
        'outputs/*.csv',
    ]
    
    data_count = 0
    for pattern in data_sources:
        for file in Path('.').glob(pattern):
            dest = OUTPUT_BASE / 'data' / file.name
            dest.parent.mkdir(exist_ok=True)
            shutil.copy2(file, dest)
            data_count += 1
    
    print(f"Collected {data_count} data files")
    
    return plot_count, report_count, data_count

def generate_summary(results, output_buffer):
    """Generate summary report"""
    print("\n" + "=" * 80, file=output_buffer)
    print("VALIDATION SUMMARY", file=output_buffer)
    print("=" * 80, file=output_buffer)
    
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    critical_failed = sum(1 for r in results if not r['success'] and r['critical'])
    
    print(f"\nTotal Steps: {total}", file=output_buffer)
    print(f"Passed: {passed}", file=output_buffer)
    print(f"Failed: {failed}", file=output_buffer)
    print(f"Critical Failures: {critical_failed}", file=output_buffer)
    print(f"Success Rate: {passed/total*100:.1f}%", file=output_buffer)
    print(file=output_buffer)
    
    print("Step Results:", file=output_buffer)
    print("-" * 80, file=output_buffer)
    for r in results:
        status = "[OK] PASS" if r['success'] else "[FAIL] FAIL"
        critical = " (CRITICAL)" if r['critical'] else ""
        print(f"  {status} {r['name']}{critical}", file=output_buffer)
    
    print(file=output_buffer)
    print("=" * 80, file=output_buffer)
    
    if critical_failed > 0:
        print("\n[FAIL] CRITICAL FAILURES DETECTED", file=output_buffer)
        print("  Some critical validation steps failed!", file=output_buffer)
        overall_pass = False
    elif failed > 0:
        print("\n[WARN] SOME NON-CRITICAL FAILURES", file=output_buffer)
        print("  Core validation passed, but some optional tests failed.", file=output_buffer)
        overall_pass = True
    else:
        print("\n[OK] ALL VALIDATIONS PASSED", file=output_buffer)
        overall_pass = True
    
    return overall_pass, {
        'total': total,
        'passed': passed,
        'failed': failed,
        'critical_failed': critical_failed,
        'success_rate': passed/total*100
    }

def main():
    """Main validation pipeline"""
    print("=" * 80)
    print("SSZ THEORY - COMPLETE VALIDATION PIPELINE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output Directory: {OUTPUT_BASE}")
    print()
    
    # Setup output capture
    output_buffer = io.StringIO()
    sys.stdout = TeeOutput(sys.__stdout__, output_buffer)
    
    # Run all steps
    results = []
    for i, step in enumerate(PIPELINE, 1):
        print(f"\n[{i}/{len(PIPELINE)}] {step['name']}")
        print("-" * 80)
        
        result = run_step(step, output_buffer)
        results.append(result)
        
        # Stop if critical step fails
        if result['critical'] and not result['success']:
            print(f"\n[FAIL] CRITICAL STEP FAILED: {step['name']}")
            print("  Stopping pipeline.")
            break
    
    # Collect outputs
    print("\n" + "=" * 80)
    print("COLLECTING ALL OUTPUTS")
    print("=" * 80)
    plot_count, report_count, data_count = collect_outputs()
    
    # Generate summary
    overall_pass, stats = generate_summary(results, output_buffer)
    
    # Save full output
    print(f"\n" + "=" * 80)
    print("SAVING OUTPUTS")
    print("=" * 80)
    
    full_output = output_buffer.getvalue()
    FULL_OUTPUT_FILE.write_text(full_output, encoding='utf-8')
    print(f"  [OK] {FULL_OUTPUT_FILE}")
    
    # Save summary
    summary_md = f"""# Complete Validation Summary

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {'✅ PASS' if overall_pass else '❌ FAIL'}  
**Success Rate:** {stats['success_rate']:.1f}%

## Overview

- Total Steps: {stats['total']}
- Passed: {stats['passed']}
- Failed: {stats['failed']}
- Critical Failures: {stats['critical_failed']}

## Step Results

"""
    
    for r in results:
        status = "✅" if r['success'] else "❌"
        critical = " **(CRITICAL)**" if r['critical'] else ""
        summary_md += f"- {status} **{r['name']}**{critical}\n"
    
    summary_md += f"""

## Outputs Generated

- **Plots:** {plot_count} files
- **Reports:** {report_count} files
- **Data:** {data_count} files

## Files

### Main Outputs

- `full-output.md` - Complete validation log
- `COMPLETE_VALIDATION_SUMMARY.md` - This summary
- `reports/` - All reports and JSON files
- `plots/` - All generated plots
- `data/` - All CSV data files

### Key Reports

- Formula Verification Results
- Test Suite Results (22 tests)
- ToE Validation Results (11 steps)
- ToE v2 Results (6 pillars)
- Grid Convergence Results

---

© 2025 Carmen Wrede & Lino Casu
"""
    
    SUMMARY_FILE.write_text(summary_md, encoding='utf-8')
    print(f"  [OK] {SUMMARY_FILE}")
    
    # Save JSON
    json_file = OUTPUT_BASE / 'validation_results.json'
    json_file.write_text(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'statistics': stats,
        'overall_pass': overall_pass
    }, indent=2), encoding='utf-8')
    print(f"  [OK] {json_file}")
    
    print(f"\n" + "=" * 80)
    print("VALIDATION PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Status: {'[OK] ALL PASS' if overall_pass else '[FAIL] FAILURES DETECTED'}")
    print(f"Outputs: {OUTPUT_BASE}/")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return 0 if overall_pass else 1

if __name__ == '__main__':
    sys.exit(main())
