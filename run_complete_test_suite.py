#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete SSZ Test Suite Runner

Runs ALL tests in the repository and generates comprehensive summaries.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import traceback

# UTF-8 encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Output directory
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

print("="*80)
print("COMPLETE SSZ TEST SUITE")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ============================================================================
# DISCOVER ALL TEST FILES
# ============================================================================
print("[1/5] Discovering all test files...")

ROOT = Path(__file__).parent

test_files = {
    'root_level': [],
    'scripts': [],
    'experiments': [],
    'validation': [],
    'animations': []
}

# Root level Python tests
for f in ROOT.glob('*.py'):
    if 'test' in f.name.lower() or f.name.startswith('ssz_'):
        if f.name != Path(__file__).name:  # Skip self
            test_files['root_level'].append(f)

# Scripts tests
scripts_dir = ROOT / 'scripts'
if scripts_dir.exists():
    for f in scripts_dir.rglob('*.py'):
        if 'test' in f.name.lower():
            test_files['scripts'].append(f)

# Experiments
exp_dir = ROOT / 'experiments'
if exp_dir.exists():
    for f in exp_dir.glob('*.py'):
        test_files['experiments'].append(f)

# Validation scripts
val_scripts = [
    ROOT / 'run_ssz_validation.py',
    ROOT / 'gr_ssz_intersection_analysis.py',
    ROOT / 'gr_vs_ssz_time_dilation.py'
]
for f in val_scripts:
    if f.exists():
        test_files['validation'].append(f)

# Animation generators
anim_scripts = [
    'ssz_time_segmentation_animation.py',
    'ssz_time_chaos_animation.py',
    'ssz_time_stability_combined.py',
    'generate_animated_overview.py'
]
for name in anim_scripts:
    f = ROOT / name
    if f.exists():
        test_files['animations'].append(f)

total_files = sum(len(files) for files in test_files.values())
print(f"  Found {total_files} test/analysis files:")
for category, files in test_files.items():
    if files:
        print(f"    - {category}: {len(files)} files")
print()

# ============================================================================
# RUN ALL TESTS
# ============================================================================
print("[2/5] Running all tests...")
print()

results = {
    'timestamp': datetime.now().isoformat(),
    'categories': {},
    'summary': {},
    'failures': [],
    'interpretations': []
}

def run_script(script_path, category, timeout=300):
    """Run a Python script and capture results"""
    print(f"  [{category}] Running: {script_path.name}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout,
            cwd=str(ROOT)
        )
        
        duration = time.time() - start_time
        
        status = 'PASSED' if result.returncode == 0 else 'FAILED'
        
        # Extract interpretations from output
        interpretation = None
        if 'Physical Interpretation:' in result.stdout or 'INTERPRETATION' in result.stdout.upper():
            lines = result.stdout.split('\n')
            interp_lines = []
            capture = False
            for line in lines:
                if 'interpretation' in line.lower() or 'result:' in line.lower():
                    capture = True
                if capture:
                    interp_lines.append(line)
                if capture and line.strip() == '':
                    break
            if interp_lines:
                interpretation = '\n'.join(interp_lines[:10])  # First 10 lines
        
        test_result = {
            'file': script_path.name,
            'category': category,
            'status': status,
            'duration': f"{duration:.2f}s",
            'returncode': result.returncode,
            'stdout_length': len(result.stdout),
            'stderr_length': len(result.stderr),
            'interpretation': interpretation
        }
        
        if status == 'FAILED':
            test_result['error'] = result.stderr[-500:] if result.stderr else 'Unknown error'
            results['failures'].append(test_result)
            print(f"    ❌ FAILED (exit code: {result.returncode})")
        else:
            print(f"    ✅ PASSED ({duration:.1f}s)")
        
        if interpretation:
            results['interpretations'].append({
                'file': script_path.name,
                'interpretation': interpretation
            })
        
        return test_result
        
    except subprocess.TimeoutExpired:
        print(f"    ⏱️ TIMEOUT ({timeout}s)")
        return {
            'file': script_path.name,
            'category': category,
            'status': 'TIMEOUT',
            'duration': f'{timeout}s',
            'error': f'Exceeded {timeout}s timeout'
        }
    except Exception as e:
        print(f"    ❌ ERROR: {str(e)}")
        return {
            'file': script_path.name,
            'category': category,
            'status': 'ERROR',
            'error': str(e)
        }

# Run tests by category
for category, files in test_files.items():
    if not files:
        continue
    
    print(f"\n--- {category.upper().replace('_', ' ')} ---\n")
    
    category_results = []
    for f in files:
        result = run_script(f, category)
        category_results.append(result)
        time.sleep(0.5)  # Brief pause between tests
    
    results['categories'][category] = category_results
    print()

# ============================================================================
# GENERATE SUMMARY STATISTICS
# ============================================================================
print("[3/5] Generating summary statistics...")

all_results = []
for cat_results in results['categories'].values():
    all_results.extend(cat_results)

passed = sum(1 for r in all_results if r['status'] == 'PASSED')
failed = sum(1 for r in all_results if r['status'] == 'FAILED')
timeout = sum(1 for r in all_results if r['status'] == 'TIMEOUT')
error = sum(1 for r in all_results if r['status'] == 'ERROR')
total = len(all_results)

results['summary'] = {
    'total_tests': total,
    'passed': passed,
    'failed': failed,
    'timeout': timeout,
    'error': error,
    'success_rate': f"{(passed/total*100):.1f}%" if total > 0 else "0%"
}

print(f"  Total: {total}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Timeout: {timeout}")
print(f"  Error: {error}")
print(f"  Success Rate: {results['summary']['success_rate']}")
print()

# ============================================================================
# SAVE JSON RESULTS
# ============================================================================
print("[4/5] Saving detailed results...")

with open(OUTPUT_DIR / 'complete_test_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"  ✓ Saved: complete_test_results.json")
print()

# ============================================================================
# GENERATE MARKDOWN REPORTS
# ============================================================================
print("[5/5] Generating Markdown reports...")

# MAIN SUMMARY REPORT
summary_md = f"""# Complete SSZ Test Suite - Summary Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

© 2025 Carmen Wrede & Lino Casu

---

## Executive Summary

**Overall Status:** {'✅ ALL PASSED' if failed == 0 and timeout == 0 and error == 0 else '⚠️ SOME ISSUES'}

All tests, validations, and analysis scripts in the repository were executed.

---

## Test Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Tests** | {total} | 100% |
| **Passed** | {passed} | {(passed/total*100):.1f}% |
| **Failed** | {failed} | {(failed/total*100):.1f}% |
| **Timeout** | {timeout} | {(timeout/total*100):.1f}% |
| **Error** | {error} | {(error/total*100):.1f}% |

**Success Rate:** {results['summary']['success_rate']}

---

## Results by Category

"""

for category, cat_results in results['categories'].items():
    cat_passed = sum(1 for r in cat_results if r['status'] == 'PASSED')
    cat_total = len(cat_results)
    
    summary_md += f"""### {category.replace('_', ' ').title()}

**Tests:** {cat_total} | **Passed:** {cat_passed} | **Rate:** {(cat_passed/cat_total*100):.1f}%

| File | Status | Duration |
|------|--------|----------|
"""
    
    for r in cat_results:
        status_icon = '✅' if r['status'] == 'PASSED' else '❌' if r['status'] == 'FAILED' else '⏱️' if r['status'] == 'TIMEOUT' else '⚠️'
        summary_md += f"| {r['file']} | {status_icon} {r['status']} | {r.get('duration', 'N/A')} |\n"
    
    summary_md += "\n"

# Failures section
if results['failures']:
    summary_md += f"""---

## Failed Tests

{len(results['failures'])} test(s) failed or encountered errors:

"""
    for fail in results['failures']:
        summary_md += f"""### {fail['file']}

**Category:** {fail['category']}  
**Status:** {fail['status']}  
**Error:**
```
{fail.get('error', 'No error message available')[:500]}
```

"""

summary_md += f"""---

## Next Steps

"""

if failed > 0 or timeout > 0 or error > 0:
    summary_md += f"""**Action Required:**
- Review {failed + timeout + error} failed/timeout/error test(s)
- Check error messages above
- Fix issues and re-run: `python run_complete_test_suite.py`
"""
else:
    summary_md += """**✅ All Clear:**
- All tests passed successfully
- Repository is in good state
- Ready for deployment/release
"""

summary_md += f"""
---

**Generated by:** `run_complete_test_suite.py`  
**License:** ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

with open(OUTPUT_DIR / 'COMPLETE_TEST_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write(summary_md)

print(f"  ✓ Saved: COMPLETE_TEST_SUMMARY.md")

# INTERPRETATIONS REPORT
if results['interpretations']:
    interp_md = f"""# SSZ Test Suite - Scientific Interpretations

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This report compiles all scientific interpretations extracted from test outputs.

---

## Interpretations by Test

"""
    
    for interp in results['interpretations']:
        interp_md += f"""### {interp['file']}

```
{interp['interpretation']}
```

---

"""
    
    interp_md += f"""
**Total Interpretations:** {len(results['interpretations'])}

---

**Generated by:** `run_complete_test_suite.py`  
**License:** ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
    
    with open(OUTPUT_DIR / 'TEST_INTERPRETATIONS.md', 'w', encoding='utf-8') as f:
        f.write(interp_md)
    
    print(f"  ✓ Saved: TEST_INTERPRETATIONS.md ({len(results['interpretations'])} interpretations)")
else:
    print(f"  ℹ️ No interpretations found")

print()

# ============================================================================
# FINAL OUTPUT
# ============================================================================
print("="*80)
print("TEST SUITE COMPLETE")
print("="*80)
print()
print(f"Status: {'✅ ALL PASSED' if failed == 0 and timeout == 0 and error == 0 else '⚠️ SOME ISSUES'}")
print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Timeout: {timeout} | Error: {error}")
print(f"Success Rate: {results['summary']['success_rate']}")
print()
print("Generated Files:")
print(f"  - complete_test_results.json ({len(json.dumps(results))} bytes)")
print(f"  - COMPLETE_TEST_SUMMARY.md")
if results['interpretations']:
    print(f"  - TEST_INTERPRETATIONS.md ({len(results['interpretations'])} interpretations)")
print()
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Exit with appropriate code
sys.exit(0 if (failed == 0 and timeout == 0 and error == 0) else 1)
