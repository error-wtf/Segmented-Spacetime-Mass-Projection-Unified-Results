# Mathematische Formeln – Segmented Spacetime (SSZ)

**Vollständige mathematische Formulierung mit Herleitungen**

© Carmen Wrede & Lino Casu, 2025

Lizenz: Anti-Capitalist Software License v1.4

---

## 📋 Inhalt

1. [Fundamentale Konstanten](#1-fundamentale-konstanten)
2. [Segment-Radius](#2-segment-radius-rphi)
3. [Metrischer Tensor](#3-metrischer-tensor)
4. [PPN-Parameter](#4-ppn-parameter)
5. [Dual-Geschwindigkeiten](#5-dual-geschwindigkeiten)
6. [Redshift-Formeln](#6-redshift-formeln)
7. [Energie-Bedingungen](#7-energie-bedingungen)
8. [Schwarze Löcher](#8-schwarze-löcher)
9. [Numerische Methoden](#9-numerische-methoden)
10. [Statistische Tests](#10-statistische-tests)

---

## 1. Fundamentale Konstanten

### Physikalische Konstanten

```
G = 6.67430 × 10^(-11) m³ kg^(-1) s^(-2)    Gravitationskonstante
c = 2.99792458 × 10^8 m/s                    Lichtgeschwindigkeit  
ℏ = 1.054571817 × 10^(-34) J·s              Reduzierte Planck-Konstante
k_B = 1.380649 × 10^(-23) J/K               Boltzmann-Konstante
M_☉ = 1.98847 × 10^30 kg                    Sonnenmasse
```

### Der Goldene Schnitt φ

**Definition:**
```
φ = (1 + √5)/2 ≈ 1.618033988749894...
```

**Fundamentale Eigenschaft:**
```
φ² = φ + 1
```

**Weitere Relationen:**
```
1/φ = φ - 1 ≈ 0.618...
φ^n = F_n·φ + F_(n-1)    (Fibonacci-Zahlen)
```

**Warum φ?**
- Selbstähnliche Raumzeit-Struktur
- Optimale Segment-Packung
- Algebraisch einfach (√5)
- Natürliche Zeitbasis

---

## 2. Segment-Radius r_φ

### 2.1 Hauptformel

**SSZ-Charakteristischer Radius:**
```
r_φ(M) = φ · (GM/c²) · (1 + Δ(M)/100)
```

**Vergleich Schwarzschild:**
```
r_s(M) = 2 · (GM/c²)
```

**Verhältnis:**
```
r_φ/r_s = (φ/2) · (1 + Δ(M)/100)
        ≈ 0.809 · (1 + Δ/100)
```

**Bedeutung:**
- r_φ: Charakteristische Längenskala der Masse M
- φ statt 2: Fundamentale SSZ-Struktur
- Δ(M): Massenabhängige Korrektion

### 2.2 Δ(M)-Modell

**Formel:**
```
Δ(M) = A · exp(-α·r_s(M)) + B
```

**Gefittete Parameter:**
```
A = 98.01
α = 2.7177 × 10^4 m^(-1) 
B = 1.96
```

**Wobei:**
```
r_s(M) = 2GM/c²   (Schwarzschild-Radius)
```

**Grenzfälle:**

**Kleine Massen (r_s → 0):**
```
exp(-α·r_s) → 1
Δ(M) → A + B ≈ 100%
r_φ ≈ φ·(GM/c²)·2 ≈ 1.62·r_s  (nahe GR!)
```

**Große Massen (r_s >> 1/α):**
```
exp(-α·r_s) → 0  
Δ(M) → B ≈ 2%
r_φ ≈ φ·(GM/c²)·1.02 ≈ 0.83·r_s  (SSZ-Effekte)
