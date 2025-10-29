#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ COMPLETE VALIDATION SUITE

Runs all SSZ validation tests for complete scientific proof:
1. Basic SSZ validation (r* intersection, neutron star effects)
2. Proper time validation (8 tests)
3. Shapiro delay proxy

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import json
import subprocess
import time
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

print("="*80)
print("SSZ COMPLETE VALIDATION SUITE")
print("="*80)
print()
print("This will run ALL validation tests:")
print("  1. Basic SSZ validation (run_ssz_validation.py)")
print("  2. Proper time validation (run_proper_time_validation.py)")
print("  3. Shapiro delay proxy (run_shapiro_delay_validation.py)")
print()
print("="*80)
print()

results = []

# ============================================================================
# TEST 1: Basic SSZ Validation
# ============================================================================
print("[1/3] Running Basic SSZ Validation...")
print("-"*80)
start = time.time()
try:
    result = subprocess.run(
        [sys.executable, 'run_ssz_validation.py'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=300
    )
    elapsed = time.time() - start
    
    # Check for PASSED in output
    passed = 'PASSED' in result.stdout or 'Overall Status: [OK]' in result.stdout
    
    results.append({
        'test': 'Basic SSZ Validation',
        'status': 'PASS' if passed and result.returncode == 0 else 'FAIL',
        'runtime_s': elapsed,
        'returncode': result.returncode
    })
    
    print(f"Status: {'PASS' if passed else 'FAIL'}")
    print(f"Runtime: {elapsed:.1f}s")
    
except subprocess.TimeoutExpired:
    results.append({
        'test': 'Basic SSZ Validation',
        'status': 'TIMEOUT',
        'runtime_s': 300,
        'returncode': -1
    })
    print("Status: TIMEOUT")
except Exception as e:
    results.append({
        'test': 'Basic SSZ Validation',
        'status': 'ERROR',
        'error': str(e),
        'returncode': -1
    })
    print(f"Status: ERROR - {e}")

print()

# ============================================================================
# TEST 2: Proper Time Validation
# ============================================================================
print("[2/3] Running Proper Time Validation...")
print("-"*80)
start = time.time()
try:
    result = subprocess.run(
        [sys.executable, 'run_proper_time_validation.py'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=300
    )
    elapsed = time.time() - start
    
    # Check for successful completion
    passed = 'PROPER TIME VALIDATION COMPLETE' in result.stdout
    
    results.append({
        'test': 'Proper Time Validation',
        'status': 'PASS' if passed and result.returncode == 0 else 'FAIL',
        'runtime_s': elapsed,
        'returncode': result.returncode
    })
    
    print(f"Status: {'PASS' if passed else 'FAIL'}")
    print(f"Runtime: {elapsed:.1f}s")
    
except subprocess.TimeoutExpired:
    results.append({
        'test': 'Proper Time Validation',
        'status': 'TIMEOUT',
        'runtime_s': 300,
        'returncode': -1
    })
    print("Status: TIMEOUT")
except Exception as e:
    results.append({
        'test': 'Proper Time Validation',
        'status': 'ERROR',
        'error': str(e),
        'returncode': -1
    })
    print(f"Status: ERROR - {e}")

print()

# ============================================================================
# TEST 3: Shapiro Delay
# ============================================================================
print("[3/3] Running Shapiro Delay Validation...")
print("-"*80)
start = time.time()
try:
    result = subprocess.run(
        [sys.executable, 'run_shapiro_delay_validation.py'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=600  # Longer timeout for path integral
    )
    elapsed = time.time() - start
    
    # Check for successful completion
    passed = 'SHAPIRO DELAY VALIDATION COMPLETE' in result.stdout
    
    results.append({
        'test': 'Shapiro Delay Validation',
        'status': 'PASS' if passed and result.returncode == 0 else 'FAIL',
        'runtime_s': elapsed,
        'returncode': result.returncode
    })
    
    print(f"Status: {'PASS' if passed else 'FAIL'}")
    print(f"Runtime: {elapsed:.1f}s")
    
except subprocess.TimeoutExpired:
    results.append({
        'test': 'Shapiro Delay Validation',
        'status': 'TIMEOUT',
        'runtime_s': 600,
        'returncode': -1
    })
    print("Status: TIMEOUT")
except Exception as e:
    results.append({
        'test': 'Shapiro Delay Validation',
        'status': 'ERROR',
        'error': str(e),
        'returncode': -1
    })
    print(f"Status: ERROR - {e}")

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("="*80)
print("COMPLETE VALIDATION SUMMARY")
print("="*80)

total_passed = sum(1 for r in results if r['status'] == 'PASS')
total_failed = sum(1 for r in results if r['status'] == 'FAIL')
total_timeout = sum(1 for r in results if r['status'] == 'TIMEOUT')
total_error = sum(1 for r in results if r['status'] == 'ERROR')
total_runtime = sum(r.get('runtime_s', 0) for r in results)

for r in results:
    status_str = r['status']
    print(f"  {r['test']:30s} [{status_str:7s}] ({r.get('runtime_s', 0):.1f}s)")

print()
print(f"Total Runtime: {total_runtime:.1f}s")
print()
print(f"Results:")
print(f"  PASSED:  {total_passed}/3")
print(f"  FAILED:  {total_failed}/3")
print(f"  TIMEOUT: {total_timeout}/3")
print(f"  ERROR:   {total_error}/3")
print()

overall_status = 'PASS' if total_passed == 3 else 'FAIL'
print(f"Overall Status: [{overall_status}]")
print("="*80)

# Save JSON report
report = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'total_runtime_s': total_runtime,
    'summary': {
        'passed': total_passed,
        'failed': total_failed,
        'timeout': total_timeout,
        'error': total_error,
        'overall': overall_status
    },
    'tests': results
}

json_path = 'outputs/COMPLETE_SSZ_VALIDATION.json'
os.makedirs('outputs', exist_ok=True)
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print()
print(f"Report saved to: {json_path}")
print()

# Exit with appropriate code
sys.exit(0 if overall_status == 'PASS' else 1)
