#!/usr/bin/env python3
# C2 continuity and curvature-proxy check for piecewise A(r), B=1/A
import math

phi = 1.6180339887498948
G = 6.67430e-11
c = 299792458.0

def F1(r, rphi, p): return 1.0/(1.0 + (rphi/r)**p)
def F2(r, rphi, p): return 1.0/(1.0 + (rphi/r)**(p/2.0))

def A_core(r, rs, rphi, p, region):
    F = F1(r, rphi, p) if region == 1 else F2(r, rphi, p)
    return 1.0 - (2.0*rs/r)*F

def hermite_A(r, rs, rphi, p, rL, rR):
    # cubic Hermite blend ensuring C1; C2 checked numerically
    def deriv(f, x, h): return (f(x+h) - f(x-h))/(2*h)
    h = max(1e-9*rs, 1e-6)
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
    return hermite_A(r, rs, rphi, p, rL, rR)

def d1(f, x, h): return (f(x+h)-f(x-h))/(2*h)
def d2(f, x, h): return (f(x+h)-2*f(x)+f(x-h))/(h*h)

def curvature_proxy(A, A1, r):
    return (A1/r)**2 + ((1.0 - A)/r**2)**2

def main():
    M = 1.98847e30
    rs = 2*G*M/(c*c)
    rphi = (phi/2.0)*rs
    p = 2.0
    Ab = 2.0*rs
    w  = 0.2*rs
    rL = Ab - w
    rR = Ab + w
    f  = lambda r: A_piece(r, rs, rphi, p)
    h  = max(1e-9*rs, 1e-6)
    for label, r0, f_left, f_right in [
        ("rL", rL, lambda r: A_core(r, rs, rphi, p, 1), lambda r: A_piece(r, rs, rphi, p)),
        ("rR", rR, lambda r: A_piece(r, rs, rphi, p), lambda r: A_core(r, rs, rphi, p, 2)),
    ]:
        eps = 1e-6*rs
        A_l, A_r = f_left(r0-eps), f_right(r0+eps)
        A1_l, A1_r = d1(f_left, r0-eps, h), d1(f_right, r0+eps, h)
        A2_l, A2_r = d2(f_left, r0-eps, h), d2(f_right, r0+eps, h)
        print(f"{label}: |ΔA|={abs(A_l-A_r):.3e} |ΔA'|={abs(A1_l-A1_r):.3e} |ΔA''|={abs(A2_l-A2_r):.3e}")
    xs = [rL*0.999, rL*1.001, Ab, rR*0.999, rR*1.001]
    for r in xs:
        A = f(r); A1 = d1(f,r,h)
        Kp = curvature_proxy(A, A1, r)
        print(f"r/rs={r/rs:6.3f}  A={A:.6e}  K_proxy={Kp:.6e}")
    eps = 1e-6*rs
    ok = True
    A_l, A_r = A_core(rL-eps, rs, rphi, p,1), A_piece(rL+eps, rs, rphi, p)
    A1_l, A1_r = d1(lambda r: A_core(r, rs, rphi, p,1), rL-eps, h), d1(lambda r: A_piece(r, rs, rphi, p), rL+eps, h)
    A2_l, A2_r = d2(lambda r: A_core(r, rs, rphi, p,1), rL-eps, h), d2(lambda r: A_piece(r, rs, rphi, p), rL+eps, h)
    ok &= abs(A_l-A_r) < 1e-9 and abs(A1_l-A1_r) < 1e-9 and abs(A2_l-A2_r) < 1e-6
    A_l, A_r = A_piece(rR-eps, rs, rphi, p), A_core(rR+eps, rs, rphi, p,2)
    A1_l, A1_r = d1(lambda r: A_piece(r, rs, rphi, p), rR-eps, h), d1(lambda r: A_core(r, rs, rphi, p,2), rR+eps, h)
    A2_l, A2_r = d2(lambda r: A_piece(r, rs, rphi, p), rR-eps, h), d2(lambda r: A_core(r, rs, rphi, p,2), rR+eps, h)
    ok &= abs(A_l-A_r) < 1e-9 and abs(A1_l-A1_r) < 1e-9 and abs(A2_l-A2_r) < 1e-6
    print("C2 + curvature-proxy ->", "PASS" if ok else "WARN")
    if not ok: raise SystemExit(1)

if __name__ == "__main__":
    main()
