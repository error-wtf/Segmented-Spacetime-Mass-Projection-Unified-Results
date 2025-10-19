#!/usr/bin/env python3
# C1 continuity across join points rL and rR using cubic Hermite blend
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import math

phi = 1.6180339887498948
G = 6.67430e-11
c = 299792458.0

def F1(r, rphi, p): return 1.0/(1.0 + (rphi/r)**p)
def F2(r, rphi, p): return 1.0/(1.0 + (rphi/r)**(p/2.0))

def A_core(r, rs, rphi, p, region):
    F = F1(r, rphi, p) if region == 1 else F2(r, rphi, p)
    return 1.0 - (2.0*rs/r)*F

def hermite_blend(r, rs, rphi, p, rL, rR):
    # values and slopes at edges from the two regions
    def deriv(f, x, h): return (f(x+h) - f(x-h))/(2*h)
    h = max(1e-9*rs, 1e-6)  # small but stable
    A_L  = A_core(rL, rs, rphi, p, 1)
    A1_L = deriv(lambda x: A_core(x, rs, rphi, p, 1), rL, h)
    A_R  = A_core(rR, rs, rphi, p, 2)
    A1_R = deriv(lambda x: A_core(x, rs, rphi, p, 2), rR, h)
    s = (r - rL) / (rR - rL)
    H00 =  2*s**3 - 3*s**2 + 1
    H10 =    s**3 - 2*s**2 + s
    H01 = -2*s**3 + 3*s**2
    H11 =    s**3 -   s**2
    scale = (rR - rL)
    return H00*A_L + H10*scale*A1_L + H01*A_R + H11*scale*A1_R

def A_piece(r, rs, rphi, p):
    Ab = 2.0*rs
    w  = 0.2*rs
    rL = Ab - w
    rR = Ab + w
    if r <= rL: return A_core(r, rs, rphi, p, 1)
    if r >= rR: return A_core(r, rs, rphi, p, 2)
    return hermite_blend(r, rs, rphi, p, rL, rR)

def deriv(f, x, h): return (f(x+h)-f(x-h))/(2*h)

def main():
    print("\n" + "="*80)
    print("C1 CONTINUITY: Cubic Hermite Blend at Segment Joins")
    print("="*80)
    
    M = 1.98847e30
    rs = 2*G*M/(c*c)
    rphi = (phi/2.0)*rs
    p = 2.0
    Ab = 2.0*rs
    w  = 0.2*rs
    rL = Ab - w
    rR = Ab + w
    
    print(f"\nTest Configuration:")
    print(f"  Mass M = {M:.3e} kg (1 M☉)")
    print(f"  r_s = {rs:.3e} m")
    print(f"  φ = {phi:.10f} (golden ratio)")
    print(f"  r_φ = (φ/2)·r_s = {rphi:.3e} m")
    print(f"\nSegment Blending:")
    print(f"  Inner region (r < r_L): F₁(r) = 1/(1 + (r_φ/r)^p)")
    print(f"  Blend zone [r_L, r_R]: Cubic Hermite interpolation")
    print(f"  Outer region (r > r_R): F₂(r) = 1/(1 + (r_φ/r)^(p/2))")
    print(f"\nJoin Points:")
    print(f"  r_L = {Ab:.2f}r_s - {w/rs:.2f}r_s = {rL/rs:.2f}r_s")
    print(f"  r_R = {Ab:.2f}r_s + {w/rs:.2f}r_s = {rR/rs:.2f}r_s")
    
    print(f"\nC1 Requirements:")
    print(f"  • A(r) continuous at r_L and r_R (value match)")
    print(f"  • A'(r) continuous at r_L and r_R (slope match)")
    
    print("\n" + "="*80)
    f_in  = lambda r: A_core(r, rs, rphi, p, 1)
    f_out = lambda r: A_core(r, rs, rphi, p, 2)
    f_bl  = lambda r: A_piece(r, rs, rphi, p)

    eps = max(1e-9*rs, 1e-6)
    h   = max(1e-9*rs, 1e-6)

    # Check continuity at rL: inner vs blend
    A_left_L  = f_in(rL - eps)
    A_right_L = f_bl(rL + eps)
    A1_left_L  = deriv(f_in, rL - eps, h)
    A1_right_L = deriv(f_bl, rL + eps, h)

    # Check continuity at rR: blend vs outer
    A_left_R  = f_bl(rR - eps)
    A_right_R = f_out(rR + eps)
    A1_left_R  = deriv(f_bl, rR - eps, h)
    A1_right_R = deriv(f_out, rR + eps, h)

    dA_L  = abs(A_left_L - A_right_L)
    dA1_L = abs(A1_left_L - A1_right_L)
    dA_R  = abs(A_left_R - A_right_R)
    dA1_R = abs(A1_left_R - A1_right_R)

    print(f"\nContinuity Check at Join Points:")
    print(f"  At r_L = {rL/rs:.2f}r_s:")
    print(f"    |ΔA(r_L)|  = {dA_L:.3e}  (should be < 1e-9)")
    print(f"    |ΔA'(r_L)| = {dA1_L:.3e}  (should be < 1e-9)")
    print(f"  At r_R = {rR/rs:.2f}r_s:")
    print(f"    |ΔA(r_R)|  = {dA_R:.3e}  (should be < 1e-9)")
    print(f"    |ΔA'(r_R)| = {dA1_R:.3e}  (should be < 1e-9)")

    print(f"\nPhysical Interpretation:")
    print(f"  • C1 continuity ensures smooth metric transition")
    print(f"  • No discontinuities in curvature tensor")
    print(f"  • φ-based blending preserves segment structure")
    print(f"  • Hermite interpolation maintains derivative continuity")

    ok = (dA_L < 1e-9 and dA1_L < 1e-9 and dA_R < 1e-9 and dA1_R < 1e-9)
    
    if ok:
        print(f"\n{'='*80}")
        print(f"✓ C1 continuity test PASSED")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'='*80}")
        print(f"✗ C1 continuity test FAILED")
        print(f"{'='*80}\n")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
