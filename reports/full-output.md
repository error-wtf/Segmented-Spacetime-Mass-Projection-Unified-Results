# SSZ Suite - Complete Full Output Log

**Generated:** 2025-10-19 13:43:58

This file contains the COMPLETE output from all test phases.

---

## Full Test Suite Output

```

====================================================================================================
SSZ PROJECTION SUITE - FULL TEST & ANALYSIS WORKFLOW
====================================================================================================

Started: 2025-10-19 13:43:09
Python: 3.10.11
Working Directory: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00


----------------------------------------------------------------------------------------------------
[INFO] ABOUT WARNINGS IN TEST SUITE
----------------------------------------------------------------------------------------------------

The test suite may show warnings. Most are EXPECTED:

  * 'Insufficient data for kappa_seg' -> Expected! Needs r < 3 r_s observations
    Most data is weak-field. Tests will PASS with warning.

  * 'Insufficient data for Hawking spectrum' -> Expected! Needs horizon thermal data
    Current dataset focuses on orbital/spectroscopic obs. Tests PASS.

  * '[CHECK] r_eff suspiciously small' -> Compact objects (pulsars, neutron stars)
    Physically correct! r < 100 km expected for compact remnants.

  * '[CHECK] r_eff <= r_s; v_tot > c' -> Near-horizon observations
    M87* (EHT), S2 (GRAVITY) data. SSZ dual velocity framework. Expected!

  * 'DeprecationWarning' -> Third-party packages, not our code. Safe to ignore.

  * '[WARNING] Silent test failed' -> Technical tests that don't affect physics

Tests show detailed 'Physical Interpretation' sections - these are features!
Warnings are informative, not errors. Suite continues through all phases.
Only STOP if you see ERROR with exit code != 0


----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------



----------------------------------------------------------------------------------------------------
PHASE 1: ROOT-LEVEL SSZ TESTS (Python Scripts)
----------------------------------------------------------------------------------------------------

[RUNNING] PPN Exact Tests
  Command: python test_ppn_exact.py

================================================================================
PPN PARAMETERS: SSZ Metric Exactness Test
================================================================================

SSZ Metric:
  A(U) = 1 - 2U + 2U² + ε₃U³
  B(U) = 1/A(U)
  ε₃ = -4.80

PPN Parameters (Weak-Field Limit):
  β (Preferred-Frame):  1.000000000000
  γ (Space-Curvature):  1.000000000000
  GR Prediction:        β = γ = 1.000000000000

Test Results:
  β = 1: ✓ PASS (|β-1| < 1e-12)
  γ = 1: ✓ PASS (|γ-1| < 1e-12)

Physical Interpretation:
  • β = 1 → No preferred reference frame
  • γ = 1 → GR-like space curvature
  • SSZ matches GR in weak-field limit
  • Post-Newtonian tests (perihelion, bending) reproduce GR

================================================================================
✓ SSZ metric passes PPN exactness test
================================================================================

  [OK] PPN Exact Tests (took 0.1s)
[RUNNING] Dual Velocity Tests
  Command: python test_vfall_duality.py

======================================================================================
DUAL VELOCITY INVARIANT: v_esc × v_fall = c²
======================================================================================

Test Configuration:
  Mass M = 5.972190e+24 kg
  Schwarzschild radius r_s = 8.870088e-03 m

Physical Meaning:
  v_esc(r)  = √(2GM/r)           (escape velocity)
  v_fall(r) = c²/v_esc(r)        (dual fall velocity)
  Invariant: v_esc × v_fall = c² (should be exact)
  γ_GR(r)   = 1/√(1 - r_s/r)     (GR time dilation)
  γ_dual(v) = 1/√(1 - (c/v)²)    (dual Lorentz factor)
======================================================================================
      r/rs              r [m]      v_esc/c     v_fall/c   (v_esc*v_fall)/c^2         γ_GR       γ_dual    rel.err γ
--------------------------------------------------------------------------------------
    1.1000       9.757097e-03 9.534626e-01 1.048809e+00   1.000000000000e+00 3.316625e+00 3.316625e+00     1.74e-15
    1.2000       1.064411e-02 9.128709e-01 1.095445e+00   1.000000000000e+00 2.449490e+00 2.449490e+00     7.25e-16
    2.0000       1.774018e-02 7.071068e-01 1.414214e+00   1.000000000000e+00 1.414214e+00 1.414214e+00     1.57e-16
    5.0000       4.435044e-02 4.472136e-01 2.236068e+00   1.000000000000e+00 1.118034e+00 1.118034e+00     0.00e+00
   10.0000       8.870088e-02 3.162278e-01 3.162278e+00   1.000000000000e+00 1.054093e+00 1.054093e+00     0.00e+00
  100.0000       8.870088e-01 1.000000e-01 1.000000e+01   1.000000000000e+00 1.005038e+00 1.005038e+00     0.00e+00
 1000.0000       8.870088e+00 3.162278e-02 3.162278e+01   1.000000000000e+00 1.000500e+00 1.000500e+00     0.00e+00
1000000.0000       8.870088e+03 1.000000e-03 1.000000e+03   1.000000000000e+00 1.000001e+00 1.000001e+00     0.00e+00
--------------------------------------------------------------------------------------

Test Results:
  Max |(v_esc·v_fall)/c² - 1| = 0.000e+00
  Max |γ_dual - γ_GR|/γ_GR    = 1.741e-15
  Tolerance:                    1e-12

Physical Interpretation:
  • Dual velocity invariant holds to machine precision
  • v_fall can exceed c (dual scaling, not physical velocity)
  • γ_GR and γ_dual match exactly (consistent kinematics)
  • Validates SSZ segment-based gravity formulation

======================================================================================
✓ Dual velocity invariant test PASSED
======================================================================================

  [OK] Dual Velocity Tests (took 0.2s)
[RUNNING] Energy Conditions Tests
  Command: python test_energy_conditions.py

================================================================================
ENERGY CONDITIONS: SSZ Effective Stress-Energy Tensor
================================================================================

Test Configuration:
  Object: Sgr A* (supermassive black hole)
  Mass M = 8.544e+36 kg ≈ 4.30e+06 M☉
  Schwarzschild radius r_s = 1.269e+10 m

Energy Conditions:
  WEC (Weak):      ρ ≥ 0 and ρ + p_t ≥ 0
  DEC (Dominant):  ρ ≥ |p_r| and ρ ≥ |p_t|
  SEC (Strong):    ρ + p_r + 2p_t ≥ 0
  NEC (Null):      ρ + p_r = 0 (analytic for SSZ)

Effective Stress-Energy from Metric:
  8πρ   = (1-A)/r² - A'/r
  8πp_r = A'/r + (A-1)/r²  → p_r = -ρ
  8πp_t = A''/2 + A'/r

================================================================================
   r/r_s       ρ [kg/m³]        p_r [Pa]        p_t [Pa]    WEC    DEC    SEC
--------------------------------------------------------------------------------
    1.20      -5.957e-23       5.354e-06      -1.071e-05      ✗      ✗      ✗
    1.50      -1.464e-23       1.316e-06      -3.072e-06      ✗      ✗      ✗
    2.00      -1.544e-24       1.388e-07      -5.556e-07      ✗      ✗      ✗
    3.00       3.050e-25      -2.741e-08      -2.764e-08      ✗      ✗      ✗
    5.00       1.028e-25      -9.237e-09       4.916e-09      ✓      ✓      ✓
   10.00       9.388e-27      -8.438e-10       7.361e-10      ✓      ✓      ✓
--------------------------------------------------------------------------------

[SSZ] Energy Conditions output converted to SI units (p_r = -ρ * c², p_t = p_t * c²)

Physical Interpretation:
  • p_r = -ρc² (radial tension balances density)
  • WEC/DEC/SEC violations confined to r < 5r_s
  • For r ≥ 5r_s: All energy conditions satisfied
  • Strong-field deviations controlled and finite

================================================================================
✓ Energy conditions test PASSED (r ≥ 5r_s)
================================================================================

  [OK] Energy Conditions Tests (took 0.1s)
[RUNNING] C1 Segments Tests
  Command: python test_c1_segments.py

================================================================================
C1 CONTINUITY: Cubic Hermite Blend at Segment Joins
================================================================================

Test Configuration:
  Mass M = 1.988e+30 kg (1 M☉)
  r_s = 2.953e+03 m
  φ = 1.6180339887 (golden ratio)
  r_φ = (φ/2)·r_s = 2.389e+03 m

Segment Blending:
  Inner region (r < r_L): F₁(r) = 1/(1 + (r_φ/r)^p)
  Blend zone [r_L, r_R]: Cubic Hermite interpolation
  Outer region (r > r_R): F₂(r) = 1/(1 + (r_φ/r)^(p/2))

Join Points:
  r_L = 5906.68r_s - 0.20r_s = 1.80r_s
  r_R = 5906.68r_s + 0.20r_s = 2.20r_s

C1 Requirements:
  • A(r) continuous at r_L and r_R (value match)
  • A'(r) continuous at r_L and r_R (slope match)

================================================================================

Continuity Check at Join Points:
  At r_L = 1.80r_s:
    |ΔA(r_L)|  = 6.819e-10  (should be < 1e-9)
    |ΔA'(r_L)| = 3.994e-11  (should be < 1e-9)
  At r_R = 2.20r_s:
    |ΔA(r_R)|  = 4.418e-10  (should be < 1e-9)
    |ΔA'(r_R)| = 1.880e-11  (should be < 1e-9)

Physical Interpretation:
  • C1 continuity ensures smooth metric transition
  • No discontinuities in curvature tensor
  • φ-based blending preserves segment structure
  • Hermite interpolation maintains derivative continuity

================================================================================
✓ C1 continuity test PASSED
================================================================================

  [OK] C1 Segments Tests (took 0.1s)
[RUNNING] C2 Segments Strict Tests
  Command: python test_c2_segments_strict.py

================================================================================
C2 STRICT CONTINUITY: Quintic Hermite with Analytic Derivatives
================================================================================

Test Configuration:
  Mass M = 1.988e+30 kg (1 M☉)
  r_s = 2.953e+03 m
  Blend zone: [1.80r_s, 2.20r_s]

C2 Requirements:
  • A(r)   continuous (value)
  • A'(r)  continuous (first derivative)
  • A''(r) continuous (second derivative)
  All checked analytically (no finite differences)

Quintic Hermite Basis:
  Matches A, A', A'' at both boundaries
  Ensures C2 continuity across blend zone

================================================================================

Continuity Check (Analytic):
rL: |ΔA|=0.000e+00 |ΔA'|=1.355e-20 |ΔA''|=0.000e+00
rR: |ΔA|=0.000e+00 |ΔA'|=0.000e+00 |ΔA''|=0.000e+00

Physical Interpretation:
  • C2 continuity ensures smooth Ricci curvature
  • No δ-function singularities in stress-energy
  • Analytic matching (machine-precision accuracy)
  • Quintic Hermite provides optimal smoothness

================================================================================
✓ C2 strict (analytic) test PASSED
================================================================================

  [OK] C2 Segments Strict Tests (took 0.1s)
[RUNNING] C2 Curvature Proxy Tests
  Command: python test_c2_curvature_proxy.py

================================================================================
C2 + CURVATURE PROXY: Analytic Smoothness Verification
================================================================================

Test Configuration:
  Mass M = 1.988e+30 kg (1 M☉)
  Blend zone: [1.80r_s, 2.20r_s]

Curvature Proxy:
  K = (A'/r)² + ((1-A)/r²)²
  Measures combined metric gradient and deviation
  Should remain finite and smooth across joins

================================================================================

C2 Continuity Check:
rL: |ΔA|=0.000e+00 |ΔA'|=1.355e-20 |ΔA''|=0.000e+00
rR: |ΔA|=0.000e+00 |ΔA'|=0.000e+00 |ΔA''|=0.000e+00
C2 strict (analytic) -> PASS

Curvature Proxy Evaluation:
   r/r_s               A         K_proxy
----------------------------------------
   1.798    7.500755e-02    1.548931e-15
   1.802    7.623504e-02    1.534697e-15
   2.000    2.122227e-01    3.612622e-15
   2.198    3.348445e-01    3.828264e-16
   2.202    3.358167e-01    3.784081e-16
----------------------------------------

Physical Interpretation:
  • Curvature proxy remains finite across joins
  • K ≈ 10⁻¹⁵ – 10⁻¹⁶ (extremely smooth)
  • C2 continuity ensures smooth Ricci tensor
  • No numerical artifacts or discontinuities

================================================================================
✓ C2 + curvature proxy test PASSED
================================================================================

  [OK] C2 Curvature Proxy Tests (took 0.1s)
[RUNNING] UTF-8 Encoding Tests
  Command: python test_utf8_encoding.py
======================================================================
UTF-8 Encoding Test
======================================================================
Test characters: µ (micro), — (em-dash), ± (plus-minus), € (euro), ° (degree)

Testing subprocess.run with UTF-8 encoding...
✅ Subprocess output: µ (micro), — (em-dash), ± (plus-minus), € (euro), ° (degree)
✅ Return code: 0

======================================================================
Test complete!
======================================================================
  [OK] UTF-8 Encoding Tests (took 0.4s)

----------------------------------------------------------------------------------------------------
PHASE 2: SEGWAVE TESTS
----------------------------------------------------------------------------------------------------

[RUNNING] SegWave Core Math Tests
  Command: python -m pytest tests/test_segwave_core.py -s -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pyproject.toml
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
collecting ... collected 20 items

tests/test_segwave_core.py::TestQFactor::test_temperature_only_basic 
================================================================================
Q-FACTOR: Temperature Ratio (β=1)
================================================================================
Temperature:
  Current ring: T_curr = 80.0 K
  Previous ring: T_prev = 100.0 K
  β parameter: 1.0

Q-Factor Calculation:
  q_k = (T_curr/T_prev)^β = (80.0/100.0)^1.0 = 0.800000

Physical Interpretation:
  • q_k < 1 indicates cooling between rings
  • Energy ratio = 80.0% of previous ring
  • Velocity will scale as q_k^(-α/2)
================================================================================
PASSED
tests/test_segwave_core.py::TestQFactor::test_temperature_with_beta 
================================================================================
Q-FACTOR: Temperature with β=2 (Enhanced Sensitivity)
================================================================================
Configuration:
  T_curr = 80.0 K, T_prev = 100.0 K
  β = 2.0 (enhanced temperature sensitivity)

Calculation:
  q_k = (80.0/100.0)^2.0 = 0.640000
  Compare to β=1: 0.800000

Physical Interpretation:
  • β=2 amplifies temperature effect: 0.64 vs 0.80
  • Stronger cooling yields lower q_k
  • Results in more dramatic velocity changes
================================================================================
PASSED
tests/test_segwave_core.py::TestQFactor::test_temperature_and_density 
================================================================================
Q-FACTOR: Temperature AND Density Combined
================================================================================
Configuration:
  Temperature: 80.0 K → 100.0 K
  Density: 1.0e+05 → 2.0e+05 cm⁻³
  β = 1.0, η = 0.5

Calculation:
  q_T = (80.0/100.0)^1.0 = 0.800000
  q_n = (1e+05/2e+05)^0.5 = 0.707107
  q_k = q_T × q_n = 0.565685

Physical Interpretation:
  • Both cooling AND density drop reduce q_k
  • Combined effect: q_k = 0.566 < 0.8 (temperature only)
  • Density amplifies temperature effect
================================================================================
PASSED
tests/test_segwave_core.py::TestQFactor::test_invalid_temperature_raises PASSED
tests/test_segwave_core.py::TestQFactor::test_invalid_density_raises PASSED
tests/test_segwave_core.py::TestVelocityProfile::test_single_shell 
================================================================================
SINGLE RING: Initial Condition
================================================================================
Configuration:
  Ring 1: T = 100.0 K
  Initial velocity: v₀ = 10.0 km/s
  α parameter: 1.0

Calculation:
  q_1 = 1.0 (no prior ring, baseline)
  v_1 = v₀ × q_1^(-α/2) = 10.0 × 1.0 = 10.0 km/s

Predicted:
  q_k = 1.000000
  v_pred = 10.00 km/s

Physical Interpretation:
  • First ring sets baseline: v = v₀
  • No propagation yet (needs ≥2 rings)
  • This establishes initial conditions for chain
================================================================================
PASSED
tests/test_segwave_core.py::TestVelocityProfile::test_two_shells_alpha_one 
================================================================================
SSZ RING VELOCITY: Two-Shell Propagation
================================================================================
Configuration:
  Ring 1: T = 100.0 K, v = 10.0 km/s (initial)
  Ring 2: T = 80.0 K
  α parameter: 1.0

Velocity Propagation:
  q_2 = T_2/T_1 = 80.0/100.0 = 0.800000
  v_2 = v_1 × q_2^(-α/2)
  v_2 = 10.0 × 0.800000^(-0.5)
  v_2 = 11.1803 km/s

Predicted Velocity:
  v_pred(ring 2) = 11.1803 km/s

Physical Interpretation:
  • Cooler ring → Higher velocity (11.1803 > 10.0)
  • SSZ predicts velocity increase of 11.8%
  • Consistent with flat rotation curves
================================================================================
PASSED
tests/test_segwave_core.py::TestVelocityProfile::test_deterministic_chain 
================================================================================
5-RING CHAIN: Temperature Gradient
================================================================================
Ring Evolution:
  Ring 1: T = 100.0 K, q_k = 1.0000, v = 12.50 km/s
  Ring 2: T =  90.0 K, q_k = 0.9000, v = 13.18 km/s
  Ring 3: T =  80.0 K, q_k = 0.8889, v = 13.98 km/s
  Ring 4: T =  70.0 K, q_k = 0.8750, v = 14.94 km/s
  Ring 5: T =  60.0 K, q_k = 0.8571, v = 16.14 km/s

Velocity Evolution:
  v_initial = 12.50 km/s
  v_final = 16.14 km/s
  Total increase: 29.1%

Physical Interpretation:
  • Cooling trend: T drops 40 K over 5 rings
  • Velocity amplification: 29.1% increase
  • Monotonic rise consistent with flat rotation curves
================================================================================
PASSED
tests/test_segwave_core.py::TestVelocityProfile::test_alpha_zero_constant_velocity 
================================================================================
α=0 LIMIT: No Segmentation (Classical)
================================================================================
Configuration:
  α = 0.0 (no SSZ effect)
  Temperature varies: 100 → 60 K

Velocities:
  Ring 1: T = 100.0 K, v = 15.00 km/s
  Ring 2: T =  80.0 K, v = 15.00 km/s
  Ring 3: T =  60.0 K, v = 15.00 km/s

Physical Interpretation:
  • α=0 ⇒ No segment field contribution
  • All velocities = 15.0 km/s (constant)
  • Classical limit: temperature has no effect
  • This is what GR/Newtonian gravity predicts
================================================================================
PASSED
tests/test_segwave_core.py::TestVelocityProfile::test_with_density 
================================================================================
TEMPERATURE + DENSITY: Combined Effect
================================================================================
Configuration:
  β = 1.0 (temperature exponent)
  η = 0.3 (density exponent)
  α = 1.0

Ring Evolution:
  Ring 1: T = 100.0 K, n = 1.0e+05 cm⁻³, v = 10.00 km/s
  Ring 2: T =  90.0 K, n = 8.0e+04 cm⁻³, v = 10.90 km/s
  Ring 3: T =  80.0 K, n = 6.0e+04 cm⁻³, v = 12.07 km/s

Physical Interpretation:
  • Both T and n decrease across rings
  • Combined q_k = (T_k/T_prev)^β × (n_k/n_prev)^η
  • Density drop amplifies temperature effect
  • Results in stronger velocity increase
================================================================================
PASSED
tests/test_segwave_core.py::TestVelocityProfile::test_mismatched_lengths_raises PASSED
tests/test_segwave_core.py::TestFrequencyTrack::test_single_gamma 
================================================================================
FREQUENCY REDSHIFT: Single γ
================================================================================
Input: ν_in = 1.000e+12 Hz (1 THz)
Segment field: γ = 2.0

Redshift:
  ν_out = ν_in × γ^(-1/2)
  ν_out = 7.071e+11 Hz
  Redshift z = Δν/ν = 0.414

Physical Interpretation:
  • Photons lose energy in segment field
  • Observable as spectral line shift
  • Analogous to gravitational redshift
================================================================================
PASSED
tests/test_segwave_core.py::TestFrequencyTrack::test_frequency_decreases_with_gamma 
================================================================================
FREQUENCY EVOLUTION: γ Sequence
================================================================================
Input: ν_in = 1.000e+12 Hz

Frequency vs γ:
  γ = 1.0 → ν = 1.000e+12 Hz
  γ = 1.2 → ν = 9.129e+11 Hz
  γ = 1.5 → ν = 8.165e+11 Hz
  γ = 2.0 → ν = 7.071e+11 Hz

Monotonicity:
  All Δν < 0: True

Physical Interpretation:
  • Frequency decreases monotonically
  • Higher γ → More segment density → More redshift
================================================================================
PASSED
tests/test_segwave_core.py::TestFrequencyTrack::test_invalid_gamma_raises PASSED
tests/test_segwave_core.py::TestResiduals::test_perfect_match 
================================================================================
RESIDUALS: Perfect Match
================================================================================
Predicted: [10. 11. 12.]
Observed:  [10. 11. 12.]

Metrics:
  MAE (Mean Absolute Error): 0.000000
  RMSE (Root Mean Square Error): 0.000000
  Max |residual|: 0.000000

Physical Interpretation:
  • Perfect model fit: all errors = 0
  • SSZ theory exactly reproduces observations
================================================================================
PASSED
tests/test_segwave_core.py::TestResiduals::test_systematic_bias 
================================================================================
RESIDUALS: Systematic Bias
================================================================================
Predicted: [10. 11. 12.]
Observed:  [ 9. 10. 11.]
Bias: 1.0 km/s (constant)

Metrics:
  MAE: 1.000000
  RMSE: 1.000000
  Max |residual|: 1.000000

Physical Interpretation:
  • Consistent +1 km/s over-prediction
  • Could indicate calibration offset
  • Easily corrected by shifting v0
================================================================================
PASSED
tests/test_segwave_core.py::TestResiduals::test_mixed_residuals 
================================================================================
RESIDUALS: Mixed Over/Under Prediction
================================================================================
Predicted: [10.  11.5 12. ]
Observed:  [10.5 11.  12.5]
Residuals: [-0.5  0.5 -0.5]

Metrics:
  MAE: 0.500000
  RMSE: 0.500000
  Max |residual|: 0.500000

Physical Interpretation:
  • Alternating over/under predictions
  • No systematic bias (errors cancel)
  • RMS captures scatter: ±0.5 km/s
  • Random noise in measurements
================================================================================
PASSED
tests/test_segwave_core.py::TestCumulativeGamma::test_constant_q 
================================================================================
CUMULATIVE γ: Constant q = 1.5
================================================================================
q sequence: [1.  1.5 1.5 1.5]

Cumulative γ:
  γ_1 = 1.0000 (= 1.5^0)
  γ_2 = 1.5000 (= 1.5^1)
  γ_3 = 2.2500 (= 1.5^2)
  γ_4 = 3.3750 (= 1.5^3)

Physical Interpretation:
  • γ grows exponentially with constant q > 1
  • Each step multiplies by factor 1.5
  • Segment field accumulates over multiple rings
================================================================================
PASSED
tests/test_segwave_core.py::TestCumulativeGamma::test_all_ones 
================================================================================
CUMULATIVE γ: All q = 1 (No Change)
================================================================================
q sequence: [1. 1. 1. 1. 1.]
γ sequence: [1. 1. 1. 1. 1.]

Physical Interpretation:
  • q=1 everywhere → no temperature/density changes
  • γ=1 for all rings → no segment field accumulation
  • Isothermal, homogeneous medium
================================================================================
PASSED
tests/test_segwave_core.py::TestCumulativeGamma::test_increasing_sequence 
================================================================================
CUMULATIVE γ: Increasing Sequence
================================================================================
q sequence: [1.  1.2 1.1 1.3]

γ Evolution:
  Step 1: q = 1.0, γ_cum = 1.0000
  Step 2: q = 1.2, γ_cum = 1.2000
  Step 3: q = 1.1, γ_cum = 1.3200
  Step 4: q = 1.3, γ_cum = 1.7160

Monotonicity:
  All Δγ > 0: True

Physical Interpretation:
  • All q > 1 → energy/temperature rising
  • γ accumulates monotonically
  • Heating trend amplifies segment field
================================================================================
PASSED

============================= 20 passed in 1.99s ==============================
  [OK] SegWave Core Math Tests (took 5.7s)
[RUNNING] SegWave CLI & Dataset Tests
  Command: python -m pytest tests/test_segwave_cli.py -s -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pyproject.toml
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
collecting ... collected 16 items

tests/test_segwave_cli.py::TestCLIBasic::test_help_flag PASSED
tests/test_segwave_cli.py::TestCLIBasic::test_missing_required_args PASSED
tests/test_segwave_cli.py::TestCLIBasic::test_invalid_csv_path PASSED
tests/test_segwave_cli.py::TestCLIExecution::test_fixed_alpha_execution PASSED
tests/test_segwave_cli.py::TestCLIExecution::test_fit_alpha_execution PASSED
tests/test_segwave_cli.py::TestCLIExecution::test_frequency_tracking PASSED
tests/test_segwave_cli.py::TestCLIExecution::test_custom_exponents PASSED
tests/test_segwave_cli.py::TestCLIValidation::test_negative_v0 PASSED
tests/test_segwave_cli.py::TestCLIValidation::test_mutually_exclusive_alpha PASSED
tests/test_segwave_cli.py::TestBundledDatasets::test_g79_dataset_exists PASSED
tests/test_segwave_cli.py::TestBundledDatasets::test_cygx_dataset_exists PASSED
tests/test_segwave_cli.py::TestBundledDatasets::test_sources_json_exists PASSED
tests/test_segwave_cli.py::TestBundledDatasets::test_sources_config_yaml_exists PASSED
tests/test_segwave_cli.py::TestBundledDatasets::test_load_sources_config_function PASSED
tests/test_segwave_cli.py::TestBundledDatasets::test_g79_cli_smoke_run PASSED
tests/test_segwave_cli.py::TestBundledDatasets::test_cygx_cli_smoke_run PASSED

============================= 16 passed in 27.62s =============================
  [OK] SegWave CLI & Dataset Tests (took 31.5s)
[RUNNING] MD Print Tool Tests
  Command: python -m pytest tests/test_print_all_md.py -s -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pyproject.toml
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
collecting ... collected 6 items

tests/test_print_all_md.py::test_print_all_md_basic PASSED
tests/test_print_all_md.py::test_print_all_md_depth_order PASSED
tests/test_print_all_md.py::test_print_all_md_exclude_dirs PASSED
tests/test_print_all_md.py::test_print_all_md_size_limit PASSED
tests/test_print_all_md.py::test_print_all_md_no_files PASSED
tests/test_print_all_md.py::test_print_all_md_custom_includes PASSED

============================== 6 passed in 1.71s ==============================
  [OK] MD Print Tool Tests (took 5.5s)

----------------------------------------------------------------------------------------------------
PHASE 3: MULTI-RING VALIDATION TESTS
----------------------------------------------------------------------------------------------------

[RUNNING] Multi-Ring Dataset Validation Tests
  Command: python -m pytest tests\test_ring_datasets.py -s -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pyproject.toml
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
collecting ... collected 11 items

tests/test_ring_datasets.py::test_ring_dataset_completeness[data/observations/G79_29+0_46_CO_NH3_rings.csv-10-Star-forming Region] 
================================================================================
RING DATASET VALIDATION: G79_29+0_46_CO_NH3_rings
================================================================================
Category: Star-forming Region
File: data/observations/G79_29+0_46_CO_NH3_rings.csv

Dataset Properties:
  Rings found: 10
  Expected rings: 10
  Columns: ring, radius_pc, T, n, v_obs...

Physical Interpretation:
  ✅ Sufficient rings for inter-ring analysis
  ✅ Can validate growth statistics
  ✅ Can test temperature/velocity gradients
================================================================================
PASSED
tests/test_ring_datasets.py::test_ring_dataset_completeness[data/observations/CygnusX_DiamondRing_CII_rings.csv-3-Molecular Cloud] 
================================================================================
RING DATASET VALIDATION: CygnusX_DiamondRing_CII_rings
================================================================================
Category: Molecular Cloud
File: data/observations/CygnusX_DiamondRing_CII_rings.csv

Dataset Properties:
  Rings found: 3
  Expected rings: 3
  Columns: ring, radius_pc, T, n, v_obs...

Physical Interpretation:
  ✅ Sufficient rings for inter-ring analysis
  ✅ Can validate growth statistics
  ✅ Can test temperature/velocity gradients
================================================================================
PASSED
tests/test_ring_datasets.py::test_ring_growth_statistics[data/observations/G79_29+0_46_CO_NH3_rings.csv-10-Star-forming Region] 
================================================================================
RING GROWTH: G79_29+0_46_CO_NH3_rings
================================================================================
Category: Star-forming Region
Rings: 10

Radius Growth Statistics:
  Mean Δr: 0.178 pc
  Min Δr: 0.150 pc
  Max Δr: 0.200 pc
  All positive: True

Physical Interpretation:
  • Radius increases monotonically outward
  • Expanding shell/ring structure
  • No unphysical radius inversions
================================================================================
PASSED
tests/test_ring_datasets.py::test_ring_growth_statistics[data/observations/CygnusX_DiamondRing_CII_rings.csv-3-Molecular Cloud] 
================================================================================
RING GROWTH: CygnusX_DiamondRing_CII_rings
================================================================================
Category: Molecular Cloud
Rings: 3

Radius Growth Statistics:
  Mean Δr: 0.150 pc
  Min Δr: 0.150 pc
  Max Δr: 0.150 pc
  All positive: True

Physical Interpretation:
  • Radius increases monotonically outward
  • Expanding shell/ring structure
  • No unphysical radius inversions
================================================================================
PASSED
tests/test_ring_datasets.py::test_temperature_gradient[data/observations/G79_29+0_46_CO_NH3_rings.csv-10-Star-forming Region] 
================================================================================
TEMPERATURE GRADIENT: G79_29+0_46_CO_NH3_rings
================================================================================
Category: Star-forming Region
Rings: 10

Temperature Statistics:
  Inner ring: 78.0 K
  Outer ring: 20.0 K
  Total change: -58.0 K
  Mean gradient: -6.44 K/ring

Physical Interpretation:
  • Temperature decreases outward (cooling)
  • Consistent with expanding shell physics
  • Or shielding in molecular cloud
================================================================================
PASSED
tests/test_ring_datasets.py::test_temperature_gradient[data/observations/CygnusX_DiamondRing_CII_rings.csv-3-Molecular Cloud] 
================================================================================
TEMPERATURE GRADIENT: CygnusX_DiamondRing_CII_rings
================================================================================
Category: Molecular Cloud
Rings: 3

Temperature Statistics:
  Inner ring: 48.0 K
  Outer ring: 36.0 K
  Total change: -12.0 K
  Mean gradient: -6.00 K/ring

Physical Interpretation:
  • Temperature decreases outward (cooling)
  • Consistent with expanding shell physics
  • Or shielding in molecular cloud
================================================================================
PASSED
tests/test_ring_datasets.py::test_velocity_profile[data/observations/G79_29+0_46_CO_NH3_rings.csv-10-Star-forming Region] 
================================================================================
VELOCITY PROFILE: G79_29+0_46_CO_NH3_rings
================================================================================
Category: Star-forming Region
Rings: 10

Velocity Statistics:
  Inner ring: 14.50 km/s
  Outer ring: 1.00 km/s
  Mean velocity: 4.94 km/s
  Velocity range: 1.00 - 14.50 km/s

Velocity Profile:
  Type: Decreasing velocity
  Interpretation: Momentum-conserving expansion

Physical Interpretation:
  • Expansion dynamics validated
  • Velocity structure consistent with Star-forming Region
================================================================================
PASSED
tests/test_ring_datasets.py::test_velocity_profile[data/observations/CygnusX_DiamondRing_CII_rings.csv-3-Molecular Cloud] 
================================================================================
VELOCITY PROFILE: CygnusX_DiamondRing_CII_rings
================================================================================
Category: Molecular Cloud
Rings: 3

Velocity Statistics:
  Inner ring: 1.30 km/s
  Outer ring: 1.30 km/s
  Mean velocity: 1.30 km/s
  Velocity range: 1.30 - 1.30 km/s

Velocity Profile:
  Type: Constant expansion
  Interpretation: Pressure-driven expansion

Physical Interpretation:
  • Expansion dynamics validated
  • Velocity structure consistent with Molecular Cloud
================================================================================
PASSED
tests/test_ring_datasets.py::test_tracer_documentation[data/observations/G79_29+0_46_CO_NH3_rings.csv-10-Star-forming Region] 
================================================================================
TRACER DOCUMENTATION: G79_29+0_46_CO_NH3_rings
================================================================================
Category: Star-forming Region
Rings: 10

Molecular Tracers Used:
  • 1)
  • 2)
  • CO(1-0)
  • CO(2-1)
  • CO(3-2)
  • HI
  • NH3(1
  • NH3(2
  • [CII]158um

Physical Interpretation:
  ✅ Data provenance documented
  ✅ Multiple tracers provide robust constraints
  ✅ Can cross-check consistency
================================================================================
PASSED
tests/test_ring_datasets.py::test_tracer_documentation[data/observations/CygnusX_DiamondRing_CII_rings.csv-3-Molecular Cloud] 
================================================================================
TRACER DOCUMENTATION: CygnusX_DiamondRing_CII_rings
================================================================================
Category: Molecular Cloud
Rings: 3

Molecular Tracers Used:
  • CO(1-0)
  • [C II]158um

Physical Interpretation:
  ✅ Data provenance documented
  ✅ Multiple tracers provide robust constraints
  ✅ Can cross-check consistency
================================================================================
PASSED
tests/test_ring_datasets.py::test_multi_ring_catalog_exists 
================================================================================
MULTI-RING CATALOG DOCUMENTATION
================================================================================
Catalog file: data\observations\MULTI_RING_CATALOG.md
Size: 4154 bytes

Physical Interpretation:
  ✅ All multi-ring datasets documented
  ✅ Source papers referenced
  ✅ Quality assessment included
================================================================================
PASSED

============================= 11 passed in 1.18s ==============================
  [OK] Multi-Ring Dataset Validation Tests (took 5.0s)

====================================================================================================
SUMMARY REPORT
====================================================================================================

Total Phases: 8
Passed: 8
Failed: 0
Success Rate: 100.0%
Total Test Time: 11.4s
Total Suite Time: 48.9s

Detailed Results:
  [PASS] PPN Exact Tests                          (0.1s)
  [PASS] Dual Velocity Tests                      (0.2s)
  [PASS] Energy Conditions Tests                  (0.1s)
  [PASS] C1 Segments Tests                        (0.1s)
  [PASS] C2 Segments Strict Tests                 (0.1s)
  [PASS] C2 Curvature Proxy Tests                 (0.1s)
  [PASS] SegWave Core Math Tests                  (5.7s)
  [PASS] Multi-Ring Validation Tests              (5.0s)

Summary written to: reports\RUN_SUMMARY.md

====================================================================================================
ECHOING REPORTS & SUMMARIES
====================================================================================================

[RUNNING] Markdown Echo
  Directory: reports/
  Command: python -m tools.print_all_md --root reports --order path

```

---

## Summary Statistics

- **Total Duration:** 48.9s
- **Test Suites:** 8
- **Passed:** 8
- **Failed:** 0

---

**Copyright 2025**
Carmen Wrede und Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
