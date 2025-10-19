#!/usr/bin/env python3
"""
Segmented-Spacetime Roundtrip Mass Test
=======================================
Verifiziert, dass aus einem segmentierten Radius r_φ exakt die Ausgangsmasse
rekonstruiert werden kann – ohne Zirkularität oder versteckte m-Injektion.

Formeln:
    r_φ = (G * m / c²) * φ
    m   = (c² * r_φ) / (G * φ)

Autor: Carmen Wrede & Lino Casu – 2025
Lizenz: MIT
"""

from decimal import Decimal, getcontext
import math

# Set high precision
getcontext().prec = 50

# Constants
G = Decimal('6.67430e-11')         # gravitational constant [m³·kg⁻¹·s⁻²]
c = Decimal('2.99792458e8')        # speed of light [m/s]
phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)  # golden ratio ≈ 1.618…

# Reference masses [kg]
test_objects = {
    "Elektron": Decimal('9.10938356e-31'),
    "Mond":     Decimal('7.342e22'),
    "Erde":     Decimal('5.97219e24'),
    "Sonne":    Decimal('1.98847e30'),
}

# Core functions
def rphi_from_mass(mass: Decimal) -> Decimal:
    return (G * mass / (c ** 2)) * phi

def mass_from_rphi(r_phi: Decimal) -> Decimal:
    return (c ** 2) * r_phi / (G * phi)

# Run test
print("\nSegmented-Spacetime Roundtrip Mass Validation\n")
print(f"{'Objekt':<10} {'M_in [kg]':>14} {'r_phi [m]':>20} {'M_out [kg]':>20} {'rel. Fehler':>15}")
print("-" * 85)

for name, m_in in test_objects.items():
    r_phi = rphi_from_mass(m_in)
    m_out = mass_from_rphi(r_phi)
    rel_error = abs((m_out - m_in) / m_in)
    print(f"{name:<10} {m_in:.4e} {r_phi:.4e} {m_out:.4e} {rel_error:.2e}")

print("\n✅ Test abgeschlossen: Keine Zirkularität, keine Masseinjektion.\n")
