#!/usr/bin/env python3
# Effective energy conditions from metric A, B=1/A
import math

G  = 6.67430e-11
c  = 299792458.0
phi = 1.6180339887498948
EPS3 = -24.0/5.0

def A_of_U(U): return 1.0 - 2.0*U + 2.0*(U*U) + EPS3*(U**3)
def U_of(r,M): return G*M/(r*c*c)
def A_of_r(r,M): return A_of_U(U_of(r,M))

def dA_dr(r,M,h=None):
    if h is None: h = max(1e-6*r, 1e-3)
    return (A_of_r(r+h,M)-A_of_r(r-h,M))/(2*h)
def d2A_dr2(r,M,h=None):
    if h is None: h = max(1e-6*r, 1e-3)
    return (A_of_r(r+h,M)-2*A_of_r(r,M)+A_of_r(r-h,M))/(h*h)

# 8πρ = (1 - A)/r^2 - A'/r
# 8πp_r = A'/r + (A - 1)/r^2  -> p_r = -ρ
# 8πp_t = A''/2 + A'/r
def rho_pr_pt(r,M):
    A = A_of_r(r,M); Ap = dA_dr(r,M); App = d2A_dr2(r,M)
    rho = ((1.0 - A)/r**2 - Ap/r) / (8*math.pi)
    pr  = (Ap/r + (A - 1.0)/r**2) / (8*math.pi)
    pt  = (0.5*App + Ap/r) / (8*math.pi)
    return rho, pr, pt

def main():
    M  = 4.297e6 * 1.98847e30  # Sgr A*
    rs = 2*G*M/(c*c)
    radii = [x*rs for x in [1.2,1.5,2,3,5,10]]
    all_ok_outside = True
    for r in radii:
        rho, pr, pt = rho_pr_pt(r,M)
        nec = rho + pr                    # = 0 analytically here
        wec = (rho >= 0) and (rho + pt >= 0)
        dec = (rho >= abs(pr)) and (rho >= abs(pt))
        sec = (rho + pr + 2*pt) >= 0
        print(f"r/rs={r/rs:5.2f}  rho={rho:.3e}  pr={pr:.3e}  pt={pt:.3e}  WEC={wec} DEC={dec} SEC={sec}")
        if r/rs >= 5.0:
            all_ok_outside = all_ok_outside and wec and sec
    print("Energy conditions (r>=5 rs) ->", "PASS" if all_ok_outside else "FAIL")
    if not all_ok_outside:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
