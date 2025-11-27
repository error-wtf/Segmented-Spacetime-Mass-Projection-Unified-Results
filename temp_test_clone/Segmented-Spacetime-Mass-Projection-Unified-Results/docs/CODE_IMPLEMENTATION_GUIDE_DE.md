# Code-Implementierungsanleitung – Segmented Spacetime (SSZ)

**Vollständige numerische Implementierung und Code-Dokumentation**

© Carmen Wrede & Lino Casu, 2025

Lizenz: Anti-Capitalist Software License v1.4

**🌐 Languages:** [🇬🇧 English](CODE_IMPLEMENTATION_GUIDE.md) | [🇩🇪 Deutsch](CODE_IMPLEMENTATION_GUIDE_DE.md)

---

## 📋 Inhalt

1. [Kern-Algorithmen](#1-kern-algorithmen)
2. [Segment-Radius-Berechnung](#2-segment-radius-berechnung)
3. [Masse-Inversion](#3-masse-inversion)
4. [Redshift-Berechnungen](#4-redshift-berechnungen)
5. [Präzisions-Handling](#5-präzisions-handling)
6. [Test-Framework](#6-test-framework)
7. [Daten-Pipeline](#7-daten-pipeline)
8. [Visualisierung](#8-visualisierung)
9. [Performance-Optimierung](#9-performance-optimierung)
10. [Code-Beispiele](#10-code-beispiele)

---

## 1. Kern-Algorithmen

### 1.1 Projekt-Struktur

```
ssz_theory_segmented.py     # Haupt-Theorie-Implementierung
├── rphi_from_mass()         # r_φ Berechnung
├── delta_percent()          # Δ(M) Modell
├── mass_from_rphi()         # Inverse Berechnung
└── Constants                # Physikalische Konstanten

segspace_all_in_one_extended.py  # Vollständige Analyse
├── load_data()              # Daten laden
├── calculate_redshifts()    # Alle Redshift-Modelle
├── statistical_tests()      # Sign-Test, Bootstrap
└── generate_plots()         # Visualisierungen
```

### 1.2 Import-Struktur

```python
# Standard-Bibliothek
from decimal import Decimal, getcontext
import numpy as np
import pandas as pd

# SSZ Kern
from ssz_theory_segmented import (
    rphi_from_mass,
    delta_percent,
    mass_from_rphi,
    PHI, G, C
)
```

---

## 2. Segment-Radius-Berechnung

### 2.1 Hauptfunktion: `rphi_from_mass()`

**Ort:** `ssz_theory_segmented.py`

**Vollständige Implementierung:**
```python
def rphi_from_mass(M, use_decimal=True):
    """
    Berechne r_φ(M) - SSZ charakteristischer Radius.
    
    Parameter
    ---------
    M : float or Decimal
        Masse in kg
    use_decimal : bool
        Decimal-Präzision verwenden (empfohlen)
    
    Rückgabe
    --------
    r_phi : Decimal
        Charakteristischer Radius in Metern
    """
    if use_decimal:
        getcontext().prec = 200
        M = Decimal(str(M))
        phi = Decimal("1.618033988749894848204586834365638117720309179805762862135")
        G_dec = Decimal("6.67430e-11")
        c_dec = Decimal("2.99792458e8")
        
        # Schwarzschild-Radius
        r_s = 2 * G_dec * M / (c_dec ** 2)
        
        # Δ(M) Korrektion
        delta = delta_percent(M, use_decimal=True)
        
        # r_φ Formel
        r_phi = phi * (G_dec * M / c_dec**2) * (1 + delta / 100)
        
        return r_phi
    else:
        # Float-Version (schneller aber weniger präzise)
        r_s = 2 * G * M / (C ** 2)
        delta = delta_percent(M, use_decimal=False)
        r_phi = PHI * (G * M / C**2) * (1 + delta / 100)
        return r_phi
```

### 2.2 Delta-Modell: `delta_percent()`

**Implementierung:**
```python
def delta_percent(M, use_decimal=True):
    """
    Berechne Δ(M) - massenabhängige Korrektion.
    
    Formel: Δ(M) = A·exp(-α·r_s) + B
    
    Parameter
    ---------
    M : float or Decimal
        Masse in kg
    
    Rückgabe
    --------
    delta : Decimal or float
        Korrektur in Prozent
    """
    if use_decimal:
        getcontext().prec = 200
        M = Decimal(str(M))
        
        # Gefittete Parameter
        A = Decimal("98.01")
        alpha = Decimal("2.7177e4")  # m^-1
        B = Decimal("1.96")
        
        G_dec = Decimal("6.67430e-11")
        c_dec = Decimal("2.99792458e8")
        
        # Schwarzschild-Radius
        r_s = 2 * G_dec * M / (c_dec ** 2)
        
        # Exponentialterm
        exp_term = (-alpha * r_s).exp()
        
        # Δ(M)
        delta = A * exp_term + B
        
        return delta
    else:
        # Float-Version
        r_s = 2 * G * M / (C ** 2)
        delta = 98.01 * np.exp(-2.7177e4 * r_s) + 1.96
        return delta
```

---

## 3. Masse-Inversion

### 3.1 Newton-Verfahren

**Funktion:** `mass_from_rphi()`

**Algorithmus:**
```python
def mass_from_rphi(r_phi_obs, max_iter=100, tol=1e-120):
    """
    Invertiere r_φ(M) um M zu finden mit Newton-Verfahren.
    
    Parameter
    ---------
    r_phi_obs : Decimal
        Beobachteter r_φ Wert (Meter)
    max_iter : int
        Maximale Iterationen
    tol : float
        Konvergenz-Toleranz
    
    Rückgabe
    --------
    M : Decimal
        Masse in kg
    """
    getcontext().prec = 200
    r_phi_obs = Decimal(str(r_phi_obs))
    
    # Anfangsschätzung: M ~ r_φ·c²/(φ·G)
    M_guess = r_phi_obs * Decimal("2.99792458e8")**2 / \
              (Decimal("1.618033988749894848") * Decimal("6.67430e-11"))
    
    for iteration in range(max_iter):
        # Aktuelles r_φ(M)
        r_phi_current = rphi_from_mass(M_guess, use_decimal=True)
        
        # Residuum
        f = r_phi_current - r_phi_obs
        
        # Konvergenz prüfen
        if abs(f) < Decimal(str(tol)):
            return M_guess
        
        # Ableitung: f'(M) = ∂r_φ/∂M
        delta_M = M_guess * Decimal("1e-10")  # Kleiner Schritt
        r_phi_plus = rphi_from_mass(M_guess + delta_M, use_decimal=True)
        f_prime = (r_phi_plus - r_phi_current) / delta_M
        
        # Newton-Schritt
        M_guess = M_guess - f / f_prime
    
    raise ValueError(f"Newton-Verfahren konvergierte nicht nach {max_iter} Iterationen")
```

---

## 4. Redshift-Berechnungen

### 4.1 Gravitativer Redshift (GR)

```python
def z_GR(M, r):
    """
    Gravitativer Redshift in der Allgemeinen Relativitätstheorie.
    
    z_GR = 1/√(1 - r_s/r) - 1
    """
    r_s = 2 * G * M / (C ** 2)
    
    if r <= r_s:
        return np.inf  # Innerhalb Event-Horizont
    
    z = 1 / np.sqrt(1 - r_s / r) - 1
    return z
```

### 4.2 SSZ Redshift

```python
def z_SSZ(M, r, v_radial=0):
    """
    SSZ Redshift mit Δ(M) Skalierung.
    
    z_SSZ = (1 + z_GR_scaled)(1 + z_SR) - 1
    """
    # GR Redshift
    z_gr = z_GR(M, r)
    
    # Δ(M) Skalierung
    delta = delta_percent(M, use_decimal=False)
    z_gr_scaled = z_gr * (1 + delta / 100)
    
    # Spezielle Relativität (Doppler)
    z_sr = v_radial / C
    
    # Kombiniert
    z_ssz = (1 + z_gr_scaled) * (1 + z_sr) - 1
    
    return z_ssz
```

---

## 5. Präzisions-Handling

### 5.1 Decimal-Konfiguration

```python
from decimal import Decimal, getcontext

# Präzision setzen
getcontext().prec = 200  # 200 Dezimalstellen

# Beispiel-Verwendung
M_sun = Decimal("1.98847e30")
r_phi = rphi_from_mass(M_sun, use_decimal=True)

print(f"r_φ(M_☉) = {r_phi:.60e} m")
```

### 5.2 Warum hohe Präzision?

**Gründe:**
1. **Exponentielle Terme:** `exp(-α·r_s)` mit α ≈ 27000
2. **Massenbereich:** 10⁻³¹ kg (Elektron) bis 10⁴⁰ kg (Galaxie)
3. **Residuen-Minimierung:** Bootstrap erfordert 10⁻¹²⁰ Genauigkeit

**Beispiel:**
```python
# Float-Präzision (limitiert)
>>> float_result = 98.01 * np.exp(-27177 * 1e-10)
>>> float_result
98.00000000269...  # Nur ~10 Stellen

# Decimal-Präzision (hoch)
>>> decimal_result = Decimal("98.01") * (-Decimal("27177") * Decimal("1e-10")).exp()
>>> decimal_result
Decimal('98.00000000269423...')  # 200 Stellen verfügbar
```

---

_Vollständige Dokumentation siehe englische Version [CODE_IMPLEMENTATION_GUIDE.md](CODE_IMPLEMENTATION_GUIDE.md)_

**Alle Code-Beispiele sind identisch in beiden Sprachen, da Python-Code universal ist.**

---

## 📚 Weiterführende Literatur

**Verwandte Dokumentation:**
- [PHYSICS_FOUNDATIONS_DE.md](PHYSICS_FOUNDATIONS_DE.md) - Physikalische Konzepte
- [MATHEMATICAL_FORMULAS_DE.md](MATHEMATICAL_FORMULAS_DE.md) - Alle Formeln

**Quellcode:**
- `ssz_theory_segmented.py` - Kern-Implementierung
- `segspace_all_in_one_extended.py` - Vollständige Pipeline
- `tests/test_*.py` - Alle Physik-Tests

**Theorie-Papers:**
- `papers/SegmentedSpacetime-ANewPerspectiveonLightGravityandBlackHoles.md`
- `papers/DualVelocitiesinSegmentedSpacetime.md`

---

**Vollständige Code-Implementierungs-Dokumentation für SSZ-Theorie! 💻**
