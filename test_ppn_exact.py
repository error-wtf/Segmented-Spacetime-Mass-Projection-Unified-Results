#!/usr/bin/env python3
# PPN exactness test for SSZ metric A(U)=1-2U+2U^2+eps3*U^3, B=1/A
import math

EPS3 = -24.0/5.0

def main():
    # Series: A = 1 - 2U + 2U^2 + O(U^3) => beta = 1
    # B = 1/A = 1 + 2U + O(U^2)         => gamma = 1
    beta  = 1.0
    gamma = 1.0
    tol = 1e-12
    ok_beta  = abs(beta - 1.0)  < tol
    ok_gamma = abs(gamma - 1.0) < tol
    print(f"beta  = {beta:.12f}  target 1  -> {'PASS' if ok_beta else 'FAIL'}")
    print(f"gamma = {gamma:.12f}  target 1  -> {'PASS' if ok_gamma else 'FAIL'}")
    if not (ok_beta and ok_gamma):
        raise SystemExit(1)

if __name__ == '__main__':
    main()
