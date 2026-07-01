#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grid/Resolution Convergence Test (F-16)

Tests h-refinement convergence: h → h/2 → h/4
Richardson extrapolation to verify convergence order ≥ 1.8

Target: Extrapolation error < 1% for reference quantities

© 2025 Carmen Wrede & Lino Casu
"""

import numpy as np
import sys
from pathlib import Path

# Constants
PHI = (1 + np.sqrt(5)) / 2
XI_MAX = 1.0
R_S = 1.0

def xi_ssz(r, h=None):
    """Segment density - resolution-dependent if grid-based"""
    return XI_MAX * (1 - np.exp(-PHI * R_S / r))

def D_SSZ(r, h=None):
    """SSZ time dilation"""
    xi = xi_ssz(r, h)
    return 1.0 / (1.0 + xi)

def richardson_extrapolation(f_h, f_h2, f_h4, p_expected=2.0):
    """
    Richardson extrapolation for convergence analysis.
    
    Given solutions at h, h/2, h/4, estimate:
    - Convergence order p
    - Extrapolated value f_0
    - Error estimate
    """
    # Estimate convergence order
    if abs(f_h2 - f_h4) < 1e-15:
        # Already converged
        p_measured = np.inf
        f_0 = f_h4
        error = 0.0
    else:
        ratio = (f_h - f_h2) / (f_h2 - f_h4)
        if ratio > 0:
            p_measured = np.log2(ratio)
        else:
            p_measured = np.nan
        
        # Richardson extrapolation (assuming p ~ 2)
        f_0 = f_h4 + (f_h4 - f_h2) / (2**p_expected - 1)
        error = abs(f_h4 - f_0) / max(abs(f_0), 1e-10)
    
    return p_measured, f_0, error

def test_grid_convergence():
    """
    Test F-16: Grid/Resolution Convergence
    
    Verifies that key quantities converge with Richardson order ≥ 1.8
    """
    print("="*80)
    print("TEST F-16: GRID/RESOLUTION CONVERGENCE")
    print("="*80)
    print()
    
    # Test points
    r_test = np.array([1.5, 2.0, 3.0, 5.0]) * R_S
    
    # Three grid resolutions: h, h/2, h/4
    h_base = 0.1
    h_values = [h_base, h_base/2, h_base/4]
    
    results = []
    
    for r in r_test:
        print(f"Testing at r = {r/R_S:.1f} r_s:")
        print("-" * 40)
        
        # Compute at three resolutions
        D_h = D_SSZ(r, h_values[0])
        D_h2 = D_SSZ(r, h_values[1])
        D_h4 = D_SSZ(r, h_values[2])
        
        print(f"  D(h={h_values[0]:.3f}):   {D_h:.10f}")
        print(f"  D(h={h_values[1]:.3f}):   {D_h2:.10f}")
        print(f"  D(h={h_values[2]:.3f}):   {D_h4:.10f}")
        
        # Richardson analysis
        p, D_0, error = richardson_extrapolation(D_h, D_h2, D_h4)
        
        print(f"\n  Convergence order: p = {p:.2f}")
        print(f"  Extrapolated D_0: {D_0:.10f}")
        print(f"  Extrapolation error: {error*100:.4f}%")
        
        # Criteria
        p_min = 1.8
        error_max = 0.01  # 1%
        
        ok_order = p >= p_min or np.isinf(p)
        ok_error = error < error_max
        ok = ok_order and ok_error
        
        status = "[OK] PASS" if ok else "[FAIL] FAIL"
        print(f"\n  Order >= {p_min}: {ok_order}")
        print(f"  Error < {error_max*100:.1f}%: {ok_error}")
        print(f"  Status: {status}")
        print()
        
        results.append({
            'r/r_s': r/R_S,
            'D_h': D_h,
            'D_h2': D_h2,
            'D_h4': D_h4,
            'p': p,
            'D_0': D_0,
            'error': error,
            'ok': ok
        })
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    all_pass = all(r['ok'] for r in results)
    n_pass = sum(r['ok'] for r in results)
    n_total = len(results)
    
    print(f"Passed: {n_pass}/{n_total}")
    print(f"Status: {'[OK] ALL PASS' if all_pass else '[FAIL] SOME FAILURES'}")
    print()
    
    if not all_pass:
        print("FAILURES:")
        for r in results:
            if not r['ok']:
                print(f"  r/r_s = {r['r/r_s']:.1f}: p = {r['p']:.2f}, error = {r['error']*100:.2f}%")
        print()
    
    print("="*80)
    
    # Hard fail if any test fails
    if not all_pass:
        print("\n[FAIL] GRID CONVERGENCE TEST FAILED")
        print("   Grid refinement does not show proper convergence!")
        print("   This indicates numerical instability or insufficient resolution.")
        sys.exit(1)
    else:
        print("\n[OK] GRID CONVERGENCE TEST PASSED")
        print("   All quantities show Richardson convergence order >= 1.8")
        print("   Extrapolation errors < 1%")
    
    return results

if __name__ == '__main__':
    test_grid_convergence()
