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
    M = 1.98847e30
    rs = 2*G*M/(c*c)
    rphi = (phi/2.0)*rs
    p = 2.0
    Ab = 2.0*rs
    w  = 0.2*rs
    rL = Ab - w
    rR = Ab + w
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

    print(f"rL:  |ΔA|={dA_L:.3e}  |ΔA'|={dA1_L:.3e}")
    print(f"rR:  |ΔA|={dA_R:.3e}  |ΔA'|={dA1_R:.3e}")

    ok = (dA_L < 1e-9 and dA1_L < 1e-9 and dA_R < 1e-9 and dA1_R < 1e-9)
    print("C1 match at joins ->", "PASS" if ok else "FAIL")
    if not ok: raise SystemExit(1)

if __name__ == "__main__":
    main()
