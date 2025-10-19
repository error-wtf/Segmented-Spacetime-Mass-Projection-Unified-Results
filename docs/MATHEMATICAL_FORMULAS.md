# Mathematical Formulas – Segmented Spacetime (SSZ)

**Complete mathematical formulation with derivations**

© Carmen Wrede & Lino Casu, 2025

License: Anti-Capitalist Software License v1.4

**🌐 Languages:** [🇬🇧 English](MATHEMATICAL_FORMULAS.md) | [🇩🇪 Deutsch](MATHEMATICAL_FORMULAS_DE.md)

---

## 📋 Contents

1. [Fundamental Constants](#1-fundamental-constants)
2. [Segment Radius](#2-segment-radius-rphi)
3. [Metric Tensor](#3-metric-tensor)
4. [PPN Parameters](#4-ppn-parameters)
5. [Dual Velocities](#5-dual-velocities)
6. [Redshift Formulas](#6-redshift-formulas)
7. [Energy Conditions](#7-energy-conditions)
8. [Black Holes](#8-black-holes)
9. [Numerical Methods](#9-numerical-methods)
10. [Statistical Tests](#10-statistical-tests)

---

## 1. Fundamental Constants

### Physical Constants

```
G = 6.67430 × 10^(-11) m³ kg^(-1) s^(-2)    Gravitational constant
c = 2.99792458 × 10^8 m/s                    Speed of light  
ℏ = 1.054571817 × 10^(-34) J·s              Reduced Planck constant
k_B = 1.380649 × 10^(-23) J/K               Boltzmann constant
M_☉ = 1.98847 × 10^30 kg                    Solar mass
```

### The Golden Ratio

**Definition:**
```
φ = (1 + √5)/2 ≈ 1.618033988749894...
```

**Fundamental property:**
```
φ² = φ + 1
```

**Additional relations:**
```
1/φ = φ - 1 ≈ 0.618...
φ^n = F_n·φ + F_(n-1)    (Fibonacci numbers)
```

**Why φ?**
- Self-similar spacetime structure
- Optimal segment packing
- Algebraically simple (√5)
- Natural time basis

---

## 2. Segment Radius r_φ

### 2.1 Main Formula

**SSZ characteristic radius:**
```
r_φ(M) = φ · (GM/c²) · (1 + Δ(M)/100)
```

**Schwarzschild comparison:**
```
r_s(M) = 2 · (GM/c²)
```

**Ratio:**
```
r_φ/r_s = (φ/2) · (1 + Δ(M)/100)
        ≈ 0.809 · (1 + Δ/100)
```

**Meaning:**
- r_φ: Characteristic length scale of mass M
- φ instead of 2: Fundamental SSZ structure
- Δ(M): Mass-dependent correction

### 2.2 Δ(M) Model

**Formula:**
```
Δ(M) = A · exp(-α·r_s(M)) + B
```

**Fitted parameters:**
```
A = 98.01
α = 2.7177 × 10^4 m^(-1) 
B = 1.96
```

**Where:**
```
r_s(M) = 2GM/c²   (Schwarzschild radius)
```

**Limiting cases:**

**Small masses (r_s → 0):**
```
exp(-α·r_s) → 1
Δ(M) → A + B ≈ 100%
r_φ ≈ φ·(GM/c²)·2 ≈ 1.62·r_s  (close to GR!)
```

**Large masses (r_s >> 1/α):**
```
exp(-α·r_s) → 0  
Δ(M) → B ≈ 2%
r_φ ≈ φ·(GM/c²)·1.02 ≈ 0.83·r_s  (SSZ effects)
```

---

See [CODE_IMPLEMENTATION_GUIDE.md](CODE_IMPLEMENTATION_GUIDE.md) for implementation details and [PHYSICS_FOUNDATIONS.md](PHYSICS_FOUNDATIONS.md) for physical interpretation.

For complete mathematical derivations, see the theory papers in `papers/`.
