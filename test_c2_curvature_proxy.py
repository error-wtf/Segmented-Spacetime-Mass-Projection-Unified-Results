#!/usr/bin/env python3
# C2 continuity and curvature-proxy check for piecewise A(r), with C2 blend
import math

phi = 1.6180339887498948
G = 6.67430e-11
c = 299792458.0

# --- region factors (Innen/Übergang/ Außen) ---
def F1(r, rphi, p):  # inner branch
    return 1.0 / (1.0 + (rphi / r) ** p)

def F2(r, rphi, p):  # outer branch (shallower)
    return 1.0 / (1.0 + (rphi / r) ** (p / 2.0))

def A_core(r, rs, rphi, p, region):
    F = F1(r, rphi, p) if region == 1 else F2(r, rphi, p)
    return 1.0 - (2.0 * rs / r) * F

# --- high-accuracy derivatives (Richardson 5-Punkt) ---
def d1(f, x, h):
    # O(h^4) centered first derivative
    return (-f(x + 2*h) + 8*f(x + h) - 8*f(x - h) + f(x - 2*h)) / (12*h)

def d2(f, x, h):
    # O(h^4) centered second derivative
    return (-f(x + 2*h) + 16*f(x + h) - 30*f(x) + 16*f(x - h) - f(x - 2*h)) / (12*h*h)

# --- C2 Hermite (quintic) blend on [rL, rR] ---
def hermite5_A(r, rs, rphi, p, rL, rR):
    # Werte und Ableitungen an den Rändern (aus den Kernästen)
    h = max(1e-9 * rs, 1e-6)
    AL  = A_core(rL, rs, rphi, p, 1)
    A1L = d1(lambda x: A_core(x, rs, rphi, p, 1), rL, h)
    A2L = d2(lambda x: A_core(x, rs, rphi, p, 1), rL, h)

    AR  = A_core(rR, rs, rphi, p, 2)
    A1R = d1(lambda x: A_core(x, rs, rphi, p, 2), rR, h)
    A2R = d2(lambda x: A_core(x, rs, rphi, p, 2), rR, h)

    s = (r - rL) / (rR - rL)   # normierter Parameter in [0,1]
    Δ = (rR - rL)

    # Quintische Hermite-Basisfunktionen (C2)
    H00 = 1 - 10*s**3 + 15*s**4 - 6*s**5
    H10 =     s      - 6*s**3 +  8*s**4 - 3*s**5
    H20 = 0.5*s**2   - 1.5*s**3 + 1.5*s**4 - 0.5*s**5

    H01 =      10*s**3 - 15*s**4 + 6*s**5
    H11 =     -4*s**3 +  7*s**4 - 3*s**5
    H21 = 0.5*s**3   -   1*s**4 + 0.5*s**5

    return (H00*AL + H10*Δ*A1L + H20*(Δ**2)*A2L
                 + H01*AR + H11*Δ*A1R + H21*(Δ**2)*A2R)

def A_piece(r, rs, rphi, p):
    # Übergangsfenster um r = 2rs (Breite 2w)
    Ab = 2.0 * rs
    w  = 0.2 * rs
    rL = Ab - w
    rR = Ab + w
    if r <= rL:
        return A_core(r, rs, rphi, p, 1)
    if r >= rR:
        return A_core(r, rs, rphi, p, 2)
    return hermite5_A(r, rs, rphi, p, rL, rR)

def curvature_proxy(A, A1, r):
    # einfacher glatter Krümmungsindikator (dimensionslos)
    return (A1/r)**2 + ((1.0 - A)/r**2)**2

def main():
    # Test set-up
    M = 1.98847e30
    rs = 2 * G * M / (c * c)
    rphi = (phi / 2.0) * rs
    p = 2.0

    Ab = 2.0 * rs
    w  = 0.2 * rs
    rL = Ab - w
    rR = Ab + w

    f = lambda r: A_piece(r, rs, rphi, p)
    h = max(1e-6 * rs, 1e-5)

    print("C2 strict (analytic) -> CHECK")
    # Sprungfreiheit an den Stößen (A, A', A'')
    for label, r0, f_left, f_right in [
        ("rL", rL, lambda r: A_core(r, rs, rphi, p, 1), lambda r: A_piece(r, rs, rphi, p)),
        ("rR", rR, lambda r: A_piece(r, rs, rphi, p), lambda r: A_core(r, rs, rphi, p, 2)),
    ]:
        eps = 1e-6 * rs
        A_l, A_r = f_left(r0 - eps), f_right(r0 + eps)
        A1_l, A1_r = d1(f_left,  r0 - eps, h), d1(f_right, r0 + eps, h)
        A2_l, A2_r = d2(f_left,  r0 - eps, h), d2(f_right, r0 + eps, h)
        print(f"{label}: |ΔA|={abs(A_l-A_r):.3e} |ΔA'|={abs(A1_l-A1_r):.3e} |ΔA''|={abs(A2_l-A2_r):.3e}")

    # Krümmungs-Proxy in Nähe der Stöße (soll glatt sein)
    xs = [rL*0.999, rL*1.001, Ab, rR*0.999, rR*1.001]
    for r in xs:
        A  = f(r)
        A1 = d1(f, r, h)
        Kp = curvature_proxy(A, A1, r)
        print(f"r/rs={r/rs:6.3f}  A={A:.6e}  K_proxy={Kp:.6e}")

    # harte Kriterien (engen Toleranzen, C2)
    eps = 1e-6 * rs
    ok = True

    A_l, A_r = A_core(rL - eps, rs, rphi, p, 1), A_piece(rL + eps, rs, rphi, p)
    A1_l, A1_r = d1(lambda r: A_core(r, rs, rphi, p, 1), rL - eps, h), d1(lambda r: A_piece(r, rs, rphi, p), rL + eps, h)
    A2_l, A2_r = d2(lambda r: A_core(r, rs, rphi, p, 1), rL - eps, h), d2(lambda r: A_piece(r, rs, rphi, p), rL + eps, h)
    ok &= abs(A_l - A_r)  < 1e-9  and abs(A1_l - A1_r) < 1e-9  and abs(A2_l - A2_r) < 1e-6

    A_l, A_r = A_piece(rR - eps, rs, rphi, p), A_core(rR + eps, rs, rphi, p, 2)
    A1_l, A1_r = d1(lambda r: A_piece(r, rs, rphi, p), rR - eps, h), d1(lambda r: A_core(r, rs, rphi, p, 2), rR + eps, h)
    A2_l, A2_r = d2(lambda r: A_piece(r, rs, rphi, p), rR - eps, h), d2(lambda r: A_core(r, rs, rphi, p, 2), rR + eps, h)
    ok &= abs(A_l - A_r)  < 1e-9  and abs(A1_l - A1_r) < 1e-9  and abs(A2_l - A2_r) < 1e-6

    print("C2 + curvature-proxy ->", "PASS" if ok else "WARN")
    if not ok:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
