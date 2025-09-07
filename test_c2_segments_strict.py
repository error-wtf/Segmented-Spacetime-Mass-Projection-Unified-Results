#!/usr/bin/env python3
# Strict C2 continuity with analytic derivatives for A(r) and the quintic blend.
import math

phi = 1.6180339887498948
G = 6.67430e-11
c = 299792458.0

def q_of(r, rphi, p):
    return (rphi / r)**p

def F_series(r, rphi, p):
    q = q_of(r, rphi, p)
    F = 1.0 / (1.0 + q)
    # F' = p*q / ( r * (1+q)^2 )
    F1 = p * q / ( r * (1.0 + q)**2 )
    # F'' = p / r^2 * ( -(p+1) q + (p-1) q^2 ) / (1+q)^3
    F2 = (p / (r*r)) * ( (-(p+1.0) * q) + ((p - 1.0) * q*q) ) / (1.0 + q)**3
    return F, F1, F2

def A_core_all(r, rs, rphi, p_eff):
    F, F1, F2 = F_series(r, rphi, p_eff)
    # A = 1 - (2rs/r) F
    A  = 1.0 - (2.0*rs/r) * F
    # A' = 2rs [ F/r^2 - F'/r ]
    A1 = 2.0*rs * ( F/(r*r) - F1/r )
    # A'' = 2rs [ 2F'/r^2 - 2F/r^3 - F''/r ]
    A2 = 2.0*rs * ( 2.0*F1/(r*r) - 2.0*F/(r**3) - F2/r )
    return A, A1, A2

def A_core_region(r, rs, rphi, p, region):
    p_eff = p if region == 1 else (p/2.0)
    return A_core_all(r, rs, rphi, p_eff)

# Quintic Hermite basis and their s-derivatives
def H00(s): return 1 - 10*s**3 + 15*s**4 - 6*s**5
def H10(s): return s - 6*s**3 + 8*s**4 - 3*s**5
def H20(s): return 0.5*s**2 - 1.5*s**3 + 1.5*s**4 - 0.5*s**5
def H01(s): return 10*s**3 - 15*s**4 + 6*s**5
def H11(s): return -4*s**3 + 7*s**4 - 3*s**5
def H21(s): return 0.5*s**3 - 1.0*s**4 + 0.5*s**5

def dH00(s): return -30*s**2 + 60*s**3 - 30*s**4
def dH10(s): return 1 - 18*s**2 + 32*s**3 - 15*s**4
def dH20(s): return s - 4.5*s**2 + 6*s**3 - 2.5*s**4
def dH01(s): return 30*s**2 - 60*s**3 + 30*s**4
def dH11(s): return -12*s**2 + 28*s**3 - 15*s**4
def dH21(s): return 1.5*s**2 - 4*s**3 + 2.5*s**4

def ddH00(s): return -60*s + 180*s**2 - 120*s**3
def ddH10(s): return -36*s + 96*s**2 - 60*s**3
def ddH20(s): return 1 - 9*s + 18*s**2 - 10*s**3
def ddH01(s): return 60*s - 180*s**2 + 120*s**3
def ddH11(s): return -24*s + 84*s**2 - 60*s**3
def ddH21(s): return 3*s - 12*s**2 + 10*s**3

def A_blend_all(r, rs, rphi, p, rL, rR):
    L = (rR - rL)
    s = (r - rL) / L
    # boundary data from analytic core
    A_L, A1_L, A2_L = A_core_region(rL, rs, rphi, p, 1)
    A_R, A1_R, A2_R = A_core_region(rR, rs, rphi, p, 2)
    # scale derivatives for s-domain
    m0 = L * A1_L; m1 = L * A1_R
    k0 = (L*L) * A2_L; k1 = (L*L) * A2_R
    # value
    A  = (A_L*H00(s) + m0*H10(s) + k0*H20(s) +
          A_R*H01(s) + m1*H11(s) + k1*H21(s))
    # first derivative dA/dr = (1/L) * dA/ds
    dAds = (A_L*dH00(s) + m0*dH10(s) + k0*dH20(s) +
            A_R*dH01(s) + m1*dH11(s) + k1*dH21(s))
    A1 = dAds / L
    # second derivative d2A/dr2 = (1/L^2) * d2A/ds2
    d2Ads2 = (A_L*ddH00(s) + m0*ddH10(s) + k0*ddH20(s) +
              A_R*ddH01(s) + m1*ddH11(s) + k1*ddH21(s))
    A2 = d2Ads2 / (L*L)
    return A, A1, A2

def main():
    # setup
    M = 1.98847e30
    rs = 2*G*M/(c*c)
    rphi = (phi/2.0)*rs
    p = 2.0
    Ab = 2.0*rs; w = 0.2*rs
    rL = Ab - w; rR = Ab + w

    # Evaluate left and right limits at the join points analytically
    A_L, A1_L, A2_L = A_core_region(rL, rs, rphi, p, 1)
    AbL, Ab1L, Ab2L = A_blend_all(rL, rs, rphi, p, rL, rR)
    print(f"rL: |ΔA|={abs(A_L-AbL):.3e} |ΔA'|={abs(A1_L-Ab1L):.3e} |ΔA''|={abs(A2_L-Ab2L):.3e}")

    A_R, A1_R, A2_R = A_core_region(rR, rs, rphi, p, 2)
    AbR, Ab1R, Ab2R = A_blend_all(rR, rs, rphi, p, rL, rR)
    print(f"rR: |ΔA|={abs(AbR-A_R):.3e} |ΔA'|={abs(Ab1R-A1_R):.3e} |ΔA''|={abs(Ab2R-A2_R):.3e}")

    ok = (abs(A_L-AbL) < 1e-12 and abs(A1_L-Ab1L) < 1e-12 and abs(A2_L-Ab2L) < 1e-12 and
          abs(AbR-A_R) < 1e-12 and abs(Ab1R-A1_R) < 1e-12 and abs(Ab2R-A2_R) < 1e-12)
    print("C2 strict (analytic) ->", "PASS" if ok else "FAIL")
    if not ok:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
