#!/usr/bin/env python3
# Eikonal QNM estimate from photon sphere (l>>1 approx)
import math

G = 6.67430e-11
c = 299792458.0
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

def photon_sphere(M):
    rs = 2*G*M/(c*c)
    a, b = 1.0001*rs, 50.0*rs
    def f(r): return 2.0*A_of_r(r,M) - r*dA_dr(r,M)
    xs = [a*(b/a)**(i/1999) for i in range(2000)]
    ys = [f(x) for x in xs]
    br=None
    for i in range(len(xs)-1):
        if ys[i]*ys[i+1] <= 0: br=(xs[i],xs[i+1]);break
    if br is None: return float('nan'), float('nan')
    a,b=br
    for _ in range(120):
        m=0.5*(a+b); fm=f(m)
        if abs(fm) < 1e-12 or (b-a)/max(m,1.0) < 1e-12:
            rph=m
            return rph, A_of_r(rph,M)
        if ys[0]*fm <= 0: b=m
        else: a=m
    return 0.5*(a+b), A_of_r(0.5*(a+b),M)

def eikonal_qnm(M):
    rph, A = photon_sphere(M)
    Omega_c = math.sqrt(A) * c / rph
    App = d2A_dr2(rph, M)
    lam = c * math.sqrt( (A) * ( (2*A) - 0.5*(rph**2)*App ) ) / (rph*math.sqrt(2.0))
    return Omega_c, lam

def main():
    Msun = 1.98847e30
    M = 30.0 * Msun
    Oc, lam = eikonal_qnm(M)
    print(f"Eikonal QNM (l>>1) for M=30 Msun: Omega_c={Oc:.6e}  lambda={lam:.6e} [1/s]")

if __name__ == "__main__":
    main()
