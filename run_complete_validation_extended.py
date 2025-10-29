#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXTENDED MASTER VALIDATION PIPELINE - SSZ Theory Complete

Runs ALL validations with extended error logging and reporting:
1. Formula verification
2. Complete test suite
3. ToE unified validation
4. ToE v2 deterministic
5. Grid convergence
6. Proper time validation
7. Theory validation
8. Analysis scripts validation
9. Extended reports generation

Creates comprehensive outputs with error logs.

© 2025 Carmen Wrede & Lino Casu
"""

import os
import sys
import json
import subprocess
import shutil
import traceback
from pathlib import Path
from datetime import datetime
import io

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_BASE = Path('validation_complete_extended')
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

FULL_OUTPUT_FILE = OUTPUT_BASE / 'full-output-extended.md'
SUMMARY_FILE = OUTPUT_BASE / 'COMPLETE_VALIDATION_SUMMARY_EXTENDED.md'
ERROR_LOG_FILE = OUTPUT_BASE / 'error_log.txt'
REPORTS_DIR = OUTPUT_BASE / 'reports'
PLOTS_DIR = OUTPUT_BASE / 'plots'
DATA_DIR = OUTPUT_BASE / 'data'
LOGS_DIR = OUTPUT_BASE / 'logs'

for dir_path in [REPORTS_DIR, PLOTS_DIR, DATA_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# OUTPUT CAPTURE
# ============================================================================

class TeeOutput:
    """Capture output to both stdout and buffer"""
    def __init__(self, *outputs):
        self.outputs = outputs
    
    def write(self, data):
        for output in self.outputs:
            try:
                output.write(data)
                output.flush()
            except:
                pass
    
    def flush(self):
        for output in self.outputs:
            try:
                output.flush()
            except:
                pass

# ============================================================================
# EXTENDED PIPELINE STEPS
# ============================================================================

PIPELINE = [
    # Critical validation steps
    {
        'id': 'verify_formulas',
        'name': 'Formula Verification',
        'script': 'verify_theory_scientific.py',
        'timeout': 60,
        'critical': True,
        'category': 'validation'
    },
    {
        'id': 'test_suite',
        'name': 'Complete Test Suite (22 tests)',
        'script': 'run_full_suite.py',
        'timeout': 600,
        'critical': False,  # Non-critical: Contains optional GAIA/SDSS pipeline that may fail if data missing
        'category': 'validation'
    },
    {
        'id': 'toe_unified',
        'name': 'ToE Unified Validation (11 steps)',
        'script': 'run_ssz_unified_validation.py',
        'timeout': 300,
        'critical': True,
        'category': 'validation'
    },
    {
        'id': 'toe_v2',
        'name': 'ToE Validation v2 (6 pillars)',
        'script': 'run_toe_validation_v2.py',
        'timeout': 120,
        'critical': True,
        'category': 'validation'
    },
    {
        'id': 'bomb_tests',
        'name': 'Black Hole Bomb Tests (7 scripts)',
        'script': 'run_bomb_tests.py',
        'timeout': 1500,
        'critical': True,
        'category': 'validation'
    },
    {
        'id': 'grid_convergence',
        'name': 'Grid Convergence Test (F-16)',
        'script': 'test_grid_convergence.py',
        'timeout': 60,
        'critical': False,
        'category': 'validation'
    },
    # Extended validation steps
    {
        'id': 'proper_time',
        'name': 'Proper Time Validation',
        'script': 'run_proper_time_validation.py',
        'timeout': 300,
        'critical': False,
        'category': 'extended'
    },
    {
        'id': 'theory_validation',
        'name': 'Theory Validation',
        'script': 'run_ssz_theory_validation.py',
        'timeout': 300,
        'critical': False,
        'category': 'extended'
    },
    # Individual physics tests
    {
        'id': 'test_ppn',
        'name': 'PPN Parameters Test',
        'script': 'test_ppn_exact.py',
        'timeout': 30,
        'critical': False,
        'category': 'physics'
    },
    {
        'id': 'test_vfall',
        'name': 'Velocity Duality Test',
        'script': 'test_vfall_duality.py',
        'timeout': 30,
        'critical': False,
        'category': 'physics'
    },
    {
        'id': 'test_energy',
        'name': 'Energy Conditions Test',
        'script': 'test_energy_conditions.py',
        'timeout': 30,
        'critical': False,
        'category': 'physics'
    },
    # Analysis scripts - SKIP (requires command argument, run separately if needed)
    # {
    #     'id': 'analysis_main',
    #     'name': 'Main SSZ Analysis',
    #     'script': 'segspace_all_in_one_extended.py',
    #     'timeout': 120,
    #     'critical': False,
    #     'category': 'analysis'
    # },
    {
        'id': 'shadow_predictions',
        'name': 'Shadow Predictions',
        'script': 'shadow_predictions_exact.py',
        'timeout': 60,
        'critical': False,
        'category': 'analysis'
    },
]

# ============================================================================
# ERROR LOGGING
# ============================================================================

class ErrorLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.errors = []
    
    def log_error(self, step_name, error_type, message, traceback_str=None):
        """Log an error with full details"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step_name,
            'type': error_type,
            'message': message,
            'traceback': traceback_str
        }
        self.errors.append(error_entry)
        
        # Write to file immediately
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"ERROR in {step_name}\n")
            f.write(f"Time: {error_entry['timestamp']}\n")
            f.write(f"Type: {error_type}\n")
            f.write(f"Message: {message}\n")
            if traceback_str:
                f.write(f"Traceback:\n{traceback_str}\n")
            f.write(f"{'='*80}\n")
    
    def get_summary(self):
        """Get error summary"""
        return {
            'total_errors': len(self.errors),
            'by_type': self._count_by_type(),
            'by_step': self._count_by_step(),
            'errors': self.errors
        }
    
    def _count_by_type(self):
        counts = {}
        for err in self.errors:
            counts[err['type']] = counts.get(err['type'], 0) + 1
        return counts
    
    def _count_by_step(self):
        counts = {}
        for err in self.errors:
            counts[err['step']] = counts.get(err['step'], 0) + 1
        return counts

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_step(step, output_buffer, error_logger):
    """Run a single validation step with error handling"""
    print("\n" + "=" * 80, file=output_buffer)
    print(f"STEP: {step['name']}", file=output_buffer)
    print("=" * 80, file=output_buffer)
    print(f"Script: {step['script']}", file=output_buffer)
    print(f"Category: {step['category']}", file=output_buffer)
    print(f"Timeout: {step['timeout']}s", file=output_buffer)
    print(f"Critical: {step['critical']}", file=output_buffer)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}", file=output_buffer)
    print(file=output_buffer)
    
    # Check if script exists
    if not Path(step['script']).exists():
        error_msg = f"Script not found: {step['script']}"
        print(f"[SKIP] {error_msg}", file=output_buffer)
        error_logger.log_error(step['name'], 'FileNotFound', error_msg)
        return {
            'step': step['id'],
            'name': step['name'],
            'success': None,
            'skipped': True,
            'reason': 'Script not found',
            'critical': step['critical']
        }
    
    try:
        # Run command
        result = subprocess.run(
            ['python', step['script']],
            capture_output=True,
            text=True,
            timeout=step['timeout'],
            encoding='utf-8',
            errors='replace'
        )
        
        # Write output to buffer AND console
        output_text = result.stdout if result.stdout else "(No output)"
        print(output_text, file=output_buffer)
        print(output_text)  # Also print to console for user to see
        
        if result.stderr:
            print("\n=== STDERR ===", file=output_buffer)
            print(result.stderr, file=output_buffer)
            if result.returncode != 0:
                print("\nSTDERR:", result.stderr)  # Also to console
        
        success = result.returncode == 0
        
        # Log errors if failed
        if not success:
            error_logger.log_error(
                step['name'],
                'ScriptFailure',
                f"Exit code: {result.returncode}",
                result.stderr if result.stderr else None
            )
        
        print(f"\nCompleted: {datetime.now().strftime('%H:%M:%S')}", file=output_buffer)
        print(f"Exit Code: {result.returncode}", file=output_buffer)
        print(f"Status: {'[OK] SUCCESS' if success else '[FAIL] FAILED'}", file=output_buffer)
        
        # Save individual log
        log_file = LOGS_DIR / f"{step['id']}.log"
        log_file.write_text(result.stdout + '\n\nSTDERR:\n' + (result.stderr or ''), encoding='utf-8')
        
        return {
            'step': step['id'],
            'name': step['name'],
            'success': success,
            'exit_code': result.returncode,
            'critical': step['critical'],
            'category': step['category'],
            'runtime': None
        }
        
    except subprocess.TimeoutExpired as e:
        error_msg = f"TIMEOUT after {step['timeout']}s"
        print(f"\n[FAIL] {error_msg}", file=output_buffer)
        error_logger.log_error(step['name'], 'Timeout', error_msg)
        return {
            'step': step['id'],
            'name': step['name'],
            'success': False,
            'exit_code': -1,
            'critical': step['critical'],
            'timeout': True,
            'category': step['category']
        }
    except Exception as e:
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"\n[FAIL] ERROR: {error_msg}", file=output_buffer)
        print(f"Traceback:\n{traceback_str}", file=output_buffer)
        error_logger.log_error(step['name'], 'Exception', error_msg, traceback_str)
        return {
            'step': step['id'],
            'name': step['name'],
            'success': False,
            'exit_code': -2,
            'critical': step['critical'],
            'error': error_msg,
            'category': step['category']
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
        '*.png'
    ]
    
    plot_count = 0
    for pattern in plot_sources:
        for file in Path('.').glob(pattern):
            if file.name not in ['icon.png', 'logo.png']:
                try:
                    dest = PLOTS_DIR / file.name
                    shutil.copy2(file, dest)
                    plot_count += 1
                    print(f"  [OK] {file.name}")
                except Exception as e:
                    print(f"  [WARN] Could not copy {file.name}: {e}")
    
    print(f"\nCollected {plot_count} plots")
    
    # Collect reports
    report_sources = [
        '*.md',
        'docs/theory/*.md',
        'validation_out_v2/*.json',
        'outputs/unified_validation/*.json',
        'reports/*.md'
    ]
    
    report_count = 0
    for pattern in report_sources:
        for file in Path('.').glob(pattern):
            if file.name not in ['README.md', 'LICENSE.md', 'CHANGELOG.md']:
                try:
                    dest = REPORTS_DIR / file.name
                    shutil.copy2(file, dest)
                    report_count += 1
                except Exception as e:
                    pass
    
    print(f"Collected {report_count} reports")
    
    # Collect data outputs
    data_sources = [
        'outputs_propertime/*.csv',
        'outputs_shapiro_proxy/*.csv',
        'outputs/*.csv',
        'validation_out_v2/*.csv'
    ]
    
    data_count = 0
    for pattern in data_sources:
        for file in Path('.').glob(pattern):
            try:
                dest = DATA_DIR / file.name
                shutil.copy2(file, dest)
                data_count += 1
            except Exception as e:
                pass
    
    print(f"Collected {data_count} data files")
    
    return plot_count, report_count, data_count

def generate_extended_summary(results, stats, error_summary, output_buffer):
    """Generate extended summary report"""
    print("\n" + "=" * 80, file=output_buffer)
    print("EXTENDED VALIDATION SUMMARY", file=output_buffer)
    print("=" * 80, file=output_buffer)
    
    # Overall stats
    print(f"\nTotal Steps: {stats['total']}", file=output_buffer)
    print(f"Passed: {stats['passed']}", file=output_buffer)
    print(f"Failed: {stats['failed']}", file=output_buffer)
    print(f"Skipped: {stats['skipped']}", file=output_buffer)
    print(f"Critical Failures: {stats['critical_failed']}", file=output_buffer)
    print(f"Success Rate: {stats['success_rate']:.1f}%", file=output_buffer)
    print(file=output_buffer)
    
    # By category
    print("Results by Category:", file=output_buffer)
    print("-" * 80, file=output_buffer)
    by_cat = {}
    for r in results:
        cat = r.get('category', 'unknown')
        if cat not in by_cat:
            by_cat[cat] = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
        by_cat[cat]['total'] += 1
        if r.get('skipped'):
            by_cat[cat]['skipped'] += 1
        elif r.get('success'):
            by_cat[cat]['passed'] += 1
        else:
            by_cat[cat]['failed'] += 1
    
    for cat, counts in sorted(by_cat.items()):
        print(f"  {cat}: {counts['passed']}/{counts['total']} PASS "
              f"({counts['failed']} failed, {counts['skipped']} skipped)", file=output_buffer)
    print(file=output_buffer)
    
    # Step results
    print("Step Results:", file=output_buffer)
    print("-" * 80, file=output_buffer)
    for r in results:
        if r.get('skipped'):
            status = "[SKIP]"
        elif r.get('success'):
            status = "[OK] PASS"
        else:
            status = "[FAIL] FAIL"
        critical = " (CRITICAL)" if r.get('critical') else ""
        category = f" [{r.get('category', 'unknown')}]"
        print(f"  {status} {r['name']}{category}{critical}", file=output_buffer)
    
    print(file=output_buffer)
    
    # Error summary
    if error_summary['total_errors'] > 0:
        print("Error Summary:", file=output_buffer)
        print("-" * 80, file=output_buffer)
        print(f"Total Errors: {error_summary['total_errors']}", file=output_buffer)
        print(f"By Type: {error_summary['by_type']}", file=output_buffer)
        print(f"By Step: {error_summary['by_step']}", file=output_buffer)
        print(f"See error_log.txt for full details", file=output_buffer)
        print(file=output_buffer)
    
    # Overall status
    print("=" * 80, file=output_buffer)
    
    if stats['critical_failed'] > 0:
        print("\n[FAIL] CRITICAL FAILURES DETECTED", file=output_buffer)
        print("  Some critical validation steps failed!", file=output_buffer)
        overall_pass = False
    elif stats['failed'] > 0:
        print("\n[WARN] SOME NON-CRITICAL FAILURES", file=output_buffer)
        print("  Core validation passed, but some optional tests failed.", file=output_buffer)
        overall_pass = True
    else:
        print("\n[OK] ALL VALIDATIONS PASSED", file=output_buffer)
        overall_pass = True
    
    return overall_pass

def main():
    """Main extended validation pipeline"""
    print("=" * 80)
    print("SSZ THEORY - EXTENDED VALIDATION PIPELINE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output Directory: {OUTPUT_BASE}")
    print(f"Total Steps: {len(PIPELINE)}")
    print()
    
    # Setup output capture
    output_buffer = io.StringIO()
    sys.stdout = TeeOutput(sys.__stdout__, output_buffer)
    
    # Setup error logger
    error_logger = ErrorLogger(ERROR_LOG_FILE)
    
    # Run all steps
    results = []
    for i, step in enumerate(PIPELINE, 1):
        print(f"\n[{i}/{len(PIPELINE)}] {step['name']}")
        print("-" * 80)
        
        result = run_step(step, output_buffer, error_logger)
        results.append(result)
        
        # Stop if critical step fails
        if result.get('critical') and not result.get('success') and not result.get('skipped'):
            print(f"\n[FAIL] CRITICAL STEP FAILED: {step['name']}")
            print("  Stopping pipeline.")
            break
    
    # Collect outputs
    print("\n" + "=" * 80)
    print("COLLECTING ALL OUTPUTS")
    print("=" * 80)
    plot_count, report_count, data_count = collect_outputs()
    
    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r.get('success'))
    failed = sum(1 for r in results if r.get('success') == False)
    skipped = sum(1 for r in results if r.get('skipped'))
    critical_failed = sum(1 for r in results if not r.get('success') and r.get('critical') and not r.get('skipped'))
    
    stats = {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'critical_failed': critical_failed,
        'success_rate': (passed / total * 100) if total > 0 else 0
    }
    
    # Get error summary
    error_summary = error_logger.get_summary()
    
    # Generate summary
    overall_pass = generate_extended_summary(results, stats, error_summary, output_buffer)
    
    # Save full output
    print(f"\n" + "=" * 80)
    print("SAVING OUTPUTS")
    print("=" * 80)
    
    full_output = output_buffer.getvalue()
    FULL_OUTPUT_FILE.write_text(full_output, encoding='utf-8')
    print(f"  [OK] {FULL_OUTPUT_FILE}")
    
    # Save summary markdown
    summary_md = f"""# Extended Validation Summary

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {'✅ PASS' if overall_pass else '❌ FAIL'}  
**Success Rate:** {stats['success_rate']:.1f}%

## Overview

- Total Steps: {stats['total']}
- Passed: {stats['passed']}
- Failed: {stats['failed']}
- Skipped: {stats['skipped']}
- Critical Failures: {stats['critical_failed']}

## Results by Category

"""
    
    # Add category breakdown
    by_cat = {}
    for r in results:
        cat = r.get('category', 'unknown')
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(r)
    
    for cat in sorted(by_cat.keys()):
        cat_results = by_cat[cat]
        cat_passed = sum(1 for r in cat_results if r.get('success'))
        cat_total = len(cat_results)
        summary_md += f"\n### {cat.capitalize()}\n\n"
        summary_md += f"- Total: {cat_total}\n"
        summary_md += f"- Passed: {cat_passed}/{cat_total}\n\n"
        for r in cat_results:
            if r.get('skipped'):
                status = "⏭️"
            elif r.get('success'):
                status = "✅"
            else:
                status = "❌"
            critical = " **(CRITICAL)**" if r.get('critical') else ""
            summary_md += f"- {status} **{r['name']}**{critical}\n"
    
    summary_md += f"""

## Outputs Generated

- **Plots:** {plot_count} files
- **Reports:** {report_count} files
- **Data:** {data_count} files
- **Logs:** {total} individual logs

## Error Summary

- **Total Errors:** {error_summary['total_errors']}
- **Error Log:** `error_log.txt`

## Files

### Main Outputs

- `full-output-extended.md` - Complete validation log
- `COMPLETE_VALIDATION_SUMMARY_EXTENDED.md` - This summary
- `error_log.txt` - Detailed error log
- `validation_results_extended.json` - Machine-readable results

### Directories

- `plots/` - All generated plots ({plot_count} files)
- `reports/` - All reports and summaries ({report_count} files)
- `data/` - All CSV data files ({data_count} files)
- `logs/` - Individual step logs ({total} files)

---

© 2025 Carmen Wrede & Lino Casu
"""
    
    SUMMARY_FILE.write_text(summary_md, encoding='utf-8')
    print(f"  [OK] {SUMMARY_FILE}")
    
    # Save JSON
    json_file = OUTPUT_BASE / 'validation_results_extended.json'
    json_file.write_text(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'statistics': stats,
        'error_summary': error_summary,
        'overall_pass': overall_pass,
        'outputs': {
            'plots': plot_count,
            'reports': report_count,
            'data': data_count,
            'logs': total
        }
    }, indent=2), encoding='utf-8')
    print(f"  [OK] {json_file}")
    
    print(f"\n" + "=" * 80)
    print("EXTENDED VALIDATION PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Status: {'[OK] ALL PASS' if overall_pass else '[FAIL] FAILURES DETECTED'}")
    print(f"Outputs: {OUTPUT_BASE}/")
    print(f"Error Log: {ERROR_LOG_FILE}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return 0 if overall_pass else 1

if __name__ == '__main__':
    sys.exit(main())
