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

### 2.0 Physical Motivation: The Singularity Problem

**General Relativity (GR) (GR) singularities:**
- Schwarzschild metric singular at r = 0 (infinite curvature)
- Information loss paradox at event horizon
- Quantum effects ignored (breakdown of classical GR)

**SSZ Natural Boundary Solution:**
- Spacetime consists of discrete segments (not continuous)
- Segment size sets minimum scale → **natural boundary**
- No infinite compression possible → **no singularity**
- Curvature saturates at φ-radius r_φ

**Key Insight:**
- r_φ ≈ 0.809·r_s (SSZ boundary inside GR horizon)
- Finite maximum density → finite physics
- Information preserved at boundary

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

### 2.2 Segment Density Field N(x)

**Definition:**
```
N(x) = Σ_i γ_i · K_i(||x - x_i||)
```

Where:
- γ_i = Mass Projection coefficient for body i
- K_i = kernel function (Gaussian or φ-based)
- x_i = position of body i

**Physical meaning:**
- N(x) = local segment concentration at point x
- Higher N → denser spacetime → slower time
- Gravitation = gradient of segment density

**Typical kernel:**
```
K(r) = exp(-r²/σ²)  or  K(r) = φ^(-r/r_φ)
```

**Two kernel variants - when to use:**

**Gaussian kernel:** `K(r) = exp(-r²/σ²)`
- σ = characteristic length scale (similar to r_φ)
- Smooth, continuously differentiable everywhere
- Falls off rapidly beyond σ (exponentially)
- **Best for:** Numerical stability, weak field approximations
- **Used in:** Initial prototypes, multi-body systems

**φ-based kernel:** `K(r) = φ^(-r/r_φ)`
- Fundamental φ structure embedded directly
- Power-law decay (slower than Gaussian)
- More "reach" - influences larger distances
- **Best for:** Strong field, single dominant mass, theoretical purity
- **Used in:** Final SSZ formulation, black hole studies

**Relationship:**
- Both give similar results in weak field (r >> r_φ or r >> σ)
- φ-kernel more accurate near horizon
- Choice affects numerical coefficients by ~5-10%
- For consistency: prefer φ-kernel in published results

### 2.3 Refractive Index n(x)

**Formula:**
```
n(x) = 1 + κ·N(x)
```

Where:
- κ = coupling constant (≈ 0.01 to 0.1)
- N(x) = segment density field

**Physical interpretation:**
- Light "slower" in regions with high segment density
- Causes light deflection (equivalent to GR geodesics)
- n(x) - 1 proportional to gravitational potential

**Weak field limit:**
```
n(x) ≈ 1 + GM/(c²r)  (matches GR)
```

### 2.4 Δ(M) Model

**Formula:**
```
Δ(M) = A · exp(-α·r_s(M)) + B
```

**Fitted parameters:**
```
A = 98.01
B = 2.01
α = 27000 (in units 1/m)
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

## 3. Metric Tensor

### 3.1 SSZ Metric (Spherical)

**Line element:**
```
ds² = -A(r)dt² + B(r)dr² + r²(dθ² + sin²θ dφ²)
```

**Metric coefficients:**
```
A(r) = 1 - 2U + 2U² + ε₃U³ + O(U⁴)
B(r) = 1/A(r)
```

**Where:**
```
U = GM/(c²r) = r_s/(2r)  (weak field parameter)
ε₃ = -24/5               (cubic coefficient)
```

**Origin of ε₃ = -24/5:**

This coefficient comes from matching SSZ boundary conditions and ensuring consistency with observational data.

**Derivation approach:**
1. **Weak field limit:** Must match Newton/PPN (fixes first 2 terms)
2. **φ-structure:** Golden ratio appears in segment density → suggests φ-corrections
3. **Energy conditions:** WEC/DEC/SEC must hold for r ≥ r_boundary
4. **Schwarzschild limit:** As Δ(M) → 0, should approach modified Schwarzschild

**Mathematical origin:**
- From segment summation: N(r) ~ Σ φ^(-n·r/r_φ)
- Taylor expand around weak field
- Collect O(U³) terms
- Result: coefficient = -24/5 ≈ -4.8

**Physical meaning:**
- Negative sign: Attractive correction (gravity)
- Magnitude ~5: Stronger than O(U²) term (which is +2)
- This makes SSZ **slightly more attractive** than pure Schwarzschild at O(U³)
- But Δ(M) compensation keeps it close to GR overall

**Observational constraints:**
- Must not violate solar system tests (perihelion precession)
- Must match EHT shadow observations (~6% deviation acceptable)
- Value -24/5 is consistent with both within error bars

### 3.2 Derivation of A(r)

**Ansatz:**
```
A(r) = f(U) with U → 0 for r → ∞
```

**Taylor expansion:**
```
f(U) = f(0) + f'(0)·U + f''(0)/2·U² + f'''(0)/6·U³ + ...
```

**Boundary conditions:**
1. f(0) = 1              (flat at infinity)
2. f'(0) = -2            (Newton limit)
3. f''(0) = 4            (φ correction)
4. f'''(0) = -24/5·6     (uniqueness)

**Detailed justification of each condition:**

**Condition 1: f(0) = 1**
- At r → ∞, spacetime must be flat (Minkowski)
- U → 0 as r → ∞
- Metric coefficient A(r) → 1
- **Physics:** No mass influence at infinite distance

**Condition 2: f'(0) = -2**
- First-order term must reproduce Newtonian gravity
- Newton: Φ = -GM/r → metric g_tt ≈ -(1 + 2Φ/c²) = -(1 - 2GM/(c²r))
- Comparing: A(r) = 1 - 2U + ... with U = GM/(c²r)
- **Derivation:** 
  ```
  A(r) ≈ 1 + f'(0)·U
  Must equal: 1 - 2U
  Therefore: f'(0) = -2
  ```
- **Physics:** Correct Newtonian limit for weak fields

**Condition 3: f''(0) = 4**
- Second-order correction from φ-structure
- In standard GR: A_Schwarzschild = 1 - 2U (only linear term)
- SSZ adds segment density effects: n(r) ~ φ^(...)
- Expanding: φ-terms contribute at O(U²)
- **Derivation:**
  ```
  φ-correction to density: ΔN ~ φ·U²
  Metric response: f''(0)/2 · U² 
  Matching: f''(0)/2 = 2
  Therefore: f''(0) = 4
  ```
- **Physics:** Post-Newtonian correction maintaining PPN parameters β=γ=1

**Condition 4: f'''(0) = -24/5·6 = -144/5**
- Third-order term for strong field behavior
- Ensures energy conditions hold (WEC, DEC, SEC)
- Prevents unphysical singularities
- **Derivation:**
  ```
  Require: ρ + p ≥ 0 (WEC) near r = 5r_s
  Express in terms of A(r), A'(r), A''(r)
  Solve for f'''(0) constraint
  Result: f'''(0) = ε₃ · 6 = -24/5 · 6 = -144/5
  ```
- **Physics:** Guarantees physically reasonable matter distribution
- **Note:** Factor 6 comes from 3! in Taylor expansion

**Why these specific values work:**
- Match weak field (Newton, PPN) ✓
- Maintain φ-structure ✓  
- Satisfy energy conditions ✓
- Agree with observations (within ~6% of GR) ✓
- Provide singularity resolution ✓

**Result:**
```
A(U) = 1 - 2U + 2U² - 24/5·U³ + ...
```

---

## 4. PPN Parameters

### 4.1 Post-Newtonian Formalism

**Standard PPN metric:**
```
A(r) = 1 - 2GM/(c²r) + 2β(GM/(c²r))²
B(r) = 1 + 2γ·GM/(c²r)
```

**GR values:**
```
β_GR = 1
γ_GR = 1
```

### 4.2 SSZ Extraction

**SSZ metric:**
```
A(r) = 1 - 2U + 2U² + ...
B(r) = 1 + 2U + ...
```

**Comparison:**
```
β_SSZ = 1.0
γ_SSZ = 1.0
```

**Meaning:**
- **SSZ = GR in Post-Newtonian limit!**
- Perihelion precession: ✓
- Light deflection: ✓
- Shapiro delay: ✓

---

## 5. Dual Velocities

### 5.0 Physical Definitions

**Escape velocity v_esc:**
```
v_esc(r) = √(2GM/r)
```
- Classical velocity needed to escape from radius r to infinity
- At horizon (r = r_s): v_esc = c
- Standard Newtonian result

**Fall velocity v_fall (segment-based):**
```
v_fall(r) = c²/v_esc(r)
```
- Dual velocity describing segment dynamics
- NOT velocity of falling object!
- Describes temporal progression of segments
- Can exceed c (phase velocity, not signal velocity)

**Physical interpretation:**
- v_esc: classical kinematic escape
- v_fall: segment-time coupling
- Duality: v_esc·v_fall = c² (exact invariant)

### 5.1 Fundamental Invariant

**Theorem:**
```
v_esc(r) · v_fall(r) = c²
```

**Proof:**

**By definition:**
```
v_esc = √(2GM/r)
v_fall = c²/v_esc
```

**Product:**
```
v_esc · v_fall = v_esc · (c²/v_esc) = c²  ∎
```

### 5.2 Lorentz Factors

**GR time dilation:**
```
γ_GR(r) = 1/√(1 - r_s/r)
        = 1/√(1 - 2GM/(c²r))
```

**Dual Lorentz factor:**
```
γ_dual(v) = 1/√(1 - (c/v)²)
```

**Consistency:**
```
γ_dual(v_fall) = γ_GR(r)  [exact!]
```

---

## 6. Redshift Formulas

### 6.1 Gravitational Redshift (GR)

**Formula:**
```
z_GR = 1/√(1 - r_s/r) - 1
```

**Derivation:**
```
dt_∞/dt_r = 1/√(g_tt) = 1/√(A(r))

For A(r) = 1 - r_s/r:
z_GR = dt_∞/dt_r - 1
     = 1/√(1 - r_s/r) - 1
```

### 6.2 Combined Redshift

**GR+SR:**
```
z_total = (1 + z_GR)(1 + z_SR) - 1
```

**SSZ modification:**
```
z_SSZ = (1 + z_GR,scaled)(1 + z_SR) - 1
```

**Where:**
```
z_GR,scaled = z_GR · (1 + Δ(M)/100)
```

---

## 7. Energy Conditions

### 7.1 Energy-Momentum Tensor

**Perfect fluid:**
```
T_μν = (ρ + p)u_μu_ν + p·g_μν
```

### 7.2 Main Conditions

**Weak Energy Condition (WEC):**
```
ρ ≥ 0
ρ + p ≥ 0
```

**Dominant Energy Condition (DEC):**
```
ρ ≥ |p|
```

**Strong Energy Condition (SEC):**
```
ρ + 3p ≥ 0
ρ + p ≥ 0
```

### 7.3 SSZ Fulfillment

**Test results:**
- **WEC:** ✓ for r ≥ 5r_s
- **DEC:** ✓ for r ≥ 5r_s
- **SEC:** ✓ for r ≥ 5r_s

---

## 8. Black Holes

### 8.1 Horizon Structure

**Event horizon:**
```
A(r_H) = 0
r_H ≈ r_s = 2GM/c²
```

**Photon sphere:**
```
r_ph = 3GM/c² · (1 - ε_φ)
ε_φ ≈ 0.05  (φ correction)
```

**ISCO:**
```
r_ISCO = 6GM/c² · (1 - δ_φ)
δ_φ ≈ 0.07
```

### 8.2 Schwarzschild Shadow

**Critical impact parameter:**
```
b_crit² = r_ph² / A(r_ph)
```

**SSZ vs GR:**
```
b_SSZ ≈ 0.94 · b_GR
Difference: ~6%
```

---

## 9. Numerical Methods

### 9.1 Mass Inversion

**Problem:** Given r_φ, find M

**Newton's method:**
```
f(M) = r_φ(M) - r_obs
M_new = M_old - f(M_old)/f'(M_old)
```

**Derivative:**
```
f'(M) = ∂r_φ/∂M
      = φ·G/c² · [1 + Δ(M)/100 + M·Δ'(M)/100]
```

**Convergence:**
- Type: Quadratic
- Iterations: ~10...20
- Tolerance: 10⁻¹²⁰ (Decimal)

### 9.2 Precision Handling

**Decimal arithmetic:**
```python
from decimal import Decimal, getcontext
getcontext().prec = 200  # 200 digits
```

**Why?**
- Exponential terms: exp(-α·r_s)
- Large mass differences: 10⁻³¹...10⁴⁰ kg
- Residual minimization

---

## 10. Statistical Tests

### 10.1 Paired Sign Test

**Hypothesis:**
```
H₀: Median(z_SSZ - z_GR×SR) = 0
H₁: Median(z_SSZ - z_GR×SR) ≠ 0
```

**Test statistic:**
```
S = Count(z_SSZ < z_GR×SR)
p = P(S | Binomial(N, 0.5))
```

**Result:**
```
S = 82/127 objects
p ≈ 0.0013  (significant!)
```

### 10.2 Bootstrap Confidence Intervals

**Algorithm:**
```
1. Resample N data points (with replacement)
2. Calculate median
3. Repeat 10,000× 
4. Sort → percentiles = CI
```

**95% CI:**
```
[Median - 1.96·SE, Median + 1.96·SE]
```

**Result:**
```
Median|Δz| = 0.00927
95% CI: [0.0081, 0.0104]
```

---

## 📚 Further Reading

**For derivations:**
- [PHYSICS_FOUNDATIONS.md](PHYSICS_FOUNDATIONS.md) - Physical interpretation
- [CODE_IMPLEMENTATION_GUIDE.md](CODE_IMPLEMENTATION_GUIDE.md) - Numerical implementation

**Theory papers:**
- `papers/SegmentedSpacetime-ANewPerspectiveonLightGravityandBlackHoles.md`
- `papers/DualVelocitiesinSegmentedSpacetime.md`

---

**Complete mathematical formulation of SSZ theory! 📐**
