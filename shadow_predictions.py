#!/usr/bin/env python3
# Shadow diameter predictions for Sgr A* and M87*
import math

G = 6.67430e-11
c = 299792458.0
pi = math.pi
EPS3 = -24.0/5.0

def A_of_U(U): return 1.0 - 2.0*U + 2.0*(U*U) + EPS3*(U**3)
def U_of(r,M): return G*M/(r*c*c)
def A_of_r(r,M): return A_of_U(U_of(r,M))

def dA_dr(r,M,h=None):
    if h is None: h = max(1e-6*r, 1e-3)
    return (A_of_r(r+h,M)-A_of_r(r-h,M))/(2*h)

def photon_sphere(M):
    rs = 2*G*M/(c*c)
    a, b = 1.0001*rs, 50.0*rs
    def f(r): return 2.0*A_of_r(r,M) - r*dA_dr(r,M)
    xs = [a*(b/a)**(i/1999) for i in range(2000)]
    ys = [f(x) for x in xs]
    br = None
    for i in range(len(xs)-1):
        if ys[i]*ys[i+1] <= 0: br = (xs[i], xs[i+1]); break
    if br is None: return float('nan'), float('nan')
    a, b = br
    for _ in range(120):
        m = 0.5*(a+b); fm = f(m)
        if abs(fm) < 1e-12 or (b-a)/max(m,1.0) < 1e-12:
            rph = m; Aph = A_of_r(rph,M); bph = rph/math.sqrt(max(Aph,1e-300))
            return rph, bph
        if ys[0]*fm <= 0: b = m
        else: a = m
    rph = 0.5*(a+b); Aph = A_of_r(rph,M); bph = rph/math.sqrt(max(Aph,1e-300))
    return rph, bph

def theta_microarcsec(b, D):
    # angular radius in microarcsec
    rad = b / D
    return rad * (180/pi) * 3.6e9   # corrected: arcsec->µas factor

def run(name, M, D_pc):
    D = D_pc * 3.085677581491367e16
    rph, bph = photon_sphere(M)
    theta = theta_microarcsec(bph, D)
    print(f"{name}: theta_shadow ≈ {2*theta:.3f} µas (diameter), r_ph={rph:.3e} m, b_ph={bph:.3e} m")

def main():
    Msun = 1.98847e30
    run("Sgr A*", 4.297e6*Msun, 8277.0)
    run("M87*",   6.5e9*Msun, 1.68e7)

if __name__ == "__main__":
    main()
