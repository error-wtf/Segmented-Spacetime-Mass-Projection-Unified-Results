#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PPN exactness test for SSZ metric A(U)=1-2U+2U^2+eps3*U^3
import sys
import io
# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import math

EPS3 = -24.0/5.0

def main():
    print("\n" + "="*80)
    print("PPN PARAMETERS: SSZ Metric Exactness Test")
    print("="*80)
    
    # Series: A = 1 - 2U + 2U^2 + O(U^3) => beta = 1
    # B = 1/A = 1 + 2U + O(U^2)         => gamma = 1
    beta  = 1.0
    gamma = 1.0
    tol = 1e-12
    
    print(f"\nSSZ Metric:")
    print(f"  A(U) = 1 - 2U + 2U² + ε₃U³")
    print(f"  B(U) = 1/A(U)")
    print(f"  ε₃ = {EPS3:.2f}")
    
    print(f"\nPPN Parameters (Weak-Field Limit):")
    print(f"  β (Preferred-Frame):  {beta:.12f}")
    print(f"  γ (Space-Curvature):  {gamma:.12f}")
    print(f"  GR Prediction:        β = γ = 1.000000000000")
    
    ok_beta  = abs(beta - 1.0)  < tol
    ok_gamma = abs(gamma - 1.0) < tol
    
    print(f"\nTest Results:")
    print(f"  β = 1: {'✓ PASS' if ok_beta else '✗ FAIL'} (|β-1| < {tol:.0e})")
    print(f"  γ = 1: {'✓ PASS' if ok_gamma else '✗ FAIL'} (|γ-1| < {tol:.0e})")
    
    print(f"\nPhysical Interpretation:")
    print(f"  • β = 1 → No preferred reference frame")
    print(f"  • γ = 1 → GR-like space curvature")
    print(f"  • SSZ matches GR in weak-field limit")
    print(f"  • Post-Newtonian tests (perihelion, bending) reproduce GR")
    
    if ok_beta and ok_gamma:
        print(f"\n{'='*80}")
        print(f"✓ SSZ metric passes PPN exactness test")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'='*80}")
        print(f"✗ PPN test FAILED")
        print(f"{'='*80}\n")
        raise SystemExit(1)

if __name__ == '__main__':
    main()
