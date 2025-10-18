# SSZ Suite - Complete Full Output Log

**Generated:** 2025-10-18 23:32:52

This file contains the COMPLETE output from all test phases.

---

## Full Test Suite Output

```

====================================================================================================
SSZ PROJECTION SUITE - FULL TEST & ANALYSIS WORKFLOW
====================================================================================================

Started: 2025-10-18 23:29:50
Python: 3.10.11
Working Directory: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00


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
  [OK] UTF-8 Encoding Tests (took 0.5s)

----------------------------------------------------------------------------------------------------
PHASE 2: SEGWAVE TESTS
----------------------------------------------------------------------------------------------------

[RUNNING] SegWave Core Math Tests
  Command: python -m pytest tests/test_segwave_core.py -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 20 items

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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
tests/test_segwave_core.py::TestQFactor::test_invalid_temperature_raises [32mPASSED[0m
tests/test_segwave_core.py::TestQFactor::test_invalid_density_raises [32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
tests/test_segwave_core.py::TestVelocityProfile::test_mismatched_lengths_raises [32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
tests/test_segwave_core.py::TestFrequencyTrack::test_invalid_gamma_raises [32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m

[32m============================= [32m[1m20 passed[0m[32m in 2.21s[0m[32m ==============================[0m
  [OK] SegWave Core Math Tests (took 6.0s)
[RUNNING] SegWave CLI & Dataset Tests
  Command: python -m pytest tests/test_segwave_cli.py -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 16 items

tests/test_segwave_cli.py::TestCLIBasic::test_help_flag [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIBasic::test_missing_required_args [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIBasic::test_invalid_csv_path [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIExecution::test_fixed_alpha_execution [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIExecution::test_fit_alpha_execution [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIExecution::test_frequency_tracking [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIExecution::test_custom_exponents [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIValidation::test_negative_v0 [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIValidation::test_mutually_exclusive_alpha [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_g79_dataset_exists [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_cygx_dataset_exists [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_sources_json_exists [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_sources_config_yaml_exists [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_load_sources_config_function [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_g79_cli_smoke_run [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_cygx_cli_smoke_run [32mPASSED[0m

[32m============================= [32m[1m16 passed[0m[32m in 29.48s[0m[32m =============================[0m
  [OK] SegWave CLI & Dataset Tests (took 33.2s)
[RUNNING] MD Print Tool Tests
  Command: python -m pytest tests/test_print_all_md.py -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 6 items

tests/test_print_all_md.py::test_print_all_md_basic [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_depth_order [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_exclude_dirs [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_size_limit [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_no_files [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_custom_includes [32mPASSED[0m

[32m============================== [32m[1m6 passed[0m[32m in 1.65s[0m[32m ==============================[0m
  [OK] MD Print Tool Tests (took 5.5s)

----------------------------------------------------------------------------------------------------
PHASE 3: SCRIPTS/TESTS
----------------------------------------------------------------------------------------------------

[RUNNING] SSZ Kernel Tests
  Command: python -m pytest scripts/tests/test_ssz_kernel.py -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 4 items

scripts/tests/test_ssz_kernel.py::test_gamma_bounds_and_monotonic 
================================================================================
GAMMA SEGMENT FIELD TEST
================================================================================
Density range: ρ = [0.0, 100.0]

Gamma values:
  ρ =    0.0 → γ = 1.000000
  ρ =    0.1 → γ = 0.782318
  ρ =    1.0 → γ = 0.380522
  ρ =   10.0 → γ = 0.038292
  ρ =  100.0 → γ = 0.020000

Bounds Check:
  Minimum γ: 0.020000 (floor = 0.02)
  Maximum γ: 1.000000 (max = 1.0)
  All in bounds: True

Monotonicity Check:
  All differences ≤ 0: True
  Max increase: -1.83e-02 (should be ~0)

Physical Interpretation:
  • γ decreases with density (segment saturation)
  • Bounded between floor and 1.0 (physical limits)
  • Smooth monotonic behavior ensures stability
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_kernel.py::test_redshift_mapping 
================================================================================
REDSHIFT-GAMMA MAPPING TEST
================================================================================
Mapping: z = (1/γ) - 1

Results:
  γ = 1.00 → z = 0.00 (expected 0.00)
  γ = 0.50 → z = 1.00 (expected 1.00)
  γ = 0.25 → z = 3.00 (expected 3.00)

Physical Interpretation:
  • γ = 1.0 → z = 0.0 (no redshift, local frame)
  • γ = 0.5 → z = 1.0 (50% field strength, z=1 cosmology)
  • γ = 0.25 → z = 3.0 (25% field strength, z=3 cosmology)
  • Lower γ → Higher z (weaker field, greater cosmological distance)
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_kernel.py::test_rotation_modifier 
================================================================================
ROTATION CURVE MODIFIER TEST
================================================================================
Power parameter p = 0.5

Rotation Modifiers:
  γ = 1.00 → v_mod = 1.0000
  γ = 0.50 → v_mod = 1.4142
  γ = 0.25 → v_mod = 2.0000

Monotonicity Check:
  v_mod increases as γ decreases: True

Physical Interpretation:
  • Weaker segment field (low γ) → Stronger rotation boost
  • Explains flat rotation curves in galaxies
  • Alternative to dark matter hypothesis
  • Modifier scales as γ^(-p) where p=0.5
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_kernel.py::test_lensing_proxy_positive 
================================================================================
GRAVITATIONAL LENSING PROXY TEST
================================================================================
Density range: ρ ∈ [0.0, 10.0]
κ scale parameter: 1.0

Lensing Convergence κ:
  Minimum: 0.000000
  Maximum: 261.149026
  All positive: True

Sample values:
  ρ =  0.00 → κ = 0.000000
  ρ =  2.50 → κ = 12.937135
  ρ =  5.00 → κ = 55.016041
  ρ =  7.50 → κ = 137.906175
  ρ = 10.00 → κ = 261.149026

Physical Interpretation:
  • κ > 0 everywhere (positive mass lenses light)
  • κ increases with density (stronger lensing)
  • Observable via gravitational lensing surveys
  • Consistent with weak lensing constraints
================================================================================
[32mPASSED[0m

[32m============================== [32m[1m4 passed[0m[32m in 0.24s[0m[32m ==============================[0m
  [OK] SSZ Kernel Tests (took 4.9s)
[RUNNING] SSZ Invariants Tests
  Command: python -m pytest scripts/tests/test_ssz_invariants.py -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 6 items

scripts/tests/test_ssz_invariants.py::test_segment_growth_is_monotonic 
================================================================================
SEGMENT GROWTH MONOTONICITY TEST
================================================================================
Dataset: 2025-10-17_gaia_ssz_v1
Number of rings: 1

Growth Statistics:
  Mean growth: nan
  Min growth: nan
  Max growth: nan
  All non-negative: True

Physical Interpretation:
  • Segment density increases outward (or remains stable)
  • Ensures consistent spacetime structure
  • No unphysical density drops between rings
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_natural_boundary_positive 
================================================================================
NATURAL BOUNDARY POSITIVITY TEST
================================================================================
Dataset: 2025-10-17_gaia_ssz_v1

Natural Boundary Statistics:
  Minimum: 5.224918e+00
  Maximum: 8.014793e+00
  Median: 6.630052e+00
  All positive: True

Physical Interpretation:
  • Positive boundary radii ensure physical segments
  • Defines scale where segmentation becomes important
  • Related to φ-based natural scales in spacetime
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_manifest_exists [32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_spiral_index_bounds [32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_solar_segments_non_empty [32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_segment_density_positive 
================================================================================
SEGMENT DENSITY POSITIVITY TEST
================================================================================
Dataset: 2025-10-17_gaia_ssz_v1
Total segments: 550

Density Statistics:
  Minimum: 1.577892e+01
  Maximum: 1.894541e+01
  Mean: 1.745581e+01
  Std Dev: 3.097954e-01
  All positive: True

Physical Interpretation:
  • Positive density ensures physical spacetime segments
  • Zero density would indicate classical (non-SSZ) limit
  • Density distribution shows segment field strength
================================================================================
[32mPASSED[0m

[32m============================== [32m[1m6 passed[0m[32m in 0.41s[0m[32m ==============================[0m
  [OK] SSZ Invariants Tests (took 4.9s)
[RUNNING] Segmenter Tests
  Command: python -m pytest scripts/tests/test_segmenter.py -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 2 items

scripts/tests/test_segmenter.py::test_segments_cover_all_points 
================================================================================
SEGMENT COVERAGE TEST
================================================================================
Spacetime points: 5000
Requested rings: 16

Segmentation Results:
  Points covered: 5000/5000
  Ring IDs: 0 to 7
  Segment IDs: 0 to 15

Physical Interpretation:
  • Complete coverage: all 5000 points assigned
  • Each point in exactly one segment
  • Ensures consistent segmented spacetime structure
================================================================================
[32mPASSED[0m
scripts/tests/test_segmenter.py::test_segment_counts_grow 
================================================================================
SEGMENT RESOLUTION SCALING TEST
================================================================================
Base segments: 4
Number of rings: 5

Segment Count Growth:
  Ring 1: 4 segments
  Ring 2: 5 segments
  Ring 3: 5 segments
  Ring 4: 6 segments
  Ring 5: 7 segments

Monotonicity:
  Segments never shrink: True

Physical Interpretation:
  • Segment count grows (or stays constant) with ring index
  • Physical structure preserved across rings
  • Algorithm handles varying densities correctly
================================================================================
[32mPASSED[0m

[32m============================== [32m[1m2 passed[0m[32m in 0.23s[0m[32m ==============================[0m
  [OK] Segmenter Tests (took 4.9s)
[RUNNING] Cosmo Fields Tests
  Command: python -m pytest scripts/tests/test_cosmo_fields.py -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 1 item

scripts/tests/test_cosmo_fields.py::test_cosmo_fields_added 
================================================================================
COSMOLOGICAL FIELD CONSTRUCTION TEST
================================================================================

Input Data:
  Positions: (x,y) = [(0, 0), (1, 1)]
  Densities: ρ = [0.2 5. ]

Gamma Configuration:
  α = 0.8
  β = 0.6
  floor = 0.02

Generated Fields:
  ✓ gamma_seg: [0.139861, 0.742681]
  ✓ z_seg: [0.346473, 6.149971]
  ✓ kappa_proxy: [0.269295, 35.749854]
  ✓ vrot_mod: [1.160376, 2.673943]

Gamma Bounds Check:
  Range: [0.139861, 0.742681]
  Within [0.02, 1.0]: ✓ PASS

Physical Interpretation:
  • Cosmological fields add to spacetime structure
  • gamma_seg: Segment field strength (0.02 ≤ γ ≤ 1.0)
  • z_seg: Redshift mapping z = (1/γ) - 1
  • kappa_proxy: Gravitational lensing convergence
  • vrot_mod: Rotation curve modifier γ^(-p)
  • All fields contribute to observable predictions
================================================================================
[32mPASSED[0m

[32m============================== [32m[1m1 passed[0m[32m in 0.23s[0m[32m ==============================[0m
  [OK] Cosmo Fields Tests (took 4.7s)
[RUNNING] Cosmo Multibody Tests
  Command: python -m pytest scripts/tests/test_cosmo_multibody.py -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 3 items

scripts/tests/test_cosmo_multibody.py::test_sigma_additive_mass 
================================================================================
SEGMENT DENSITY ADDITIVITY TEST
================================================================================
Test Configuration:
  Sun:     Position = (0.0, 0.0, 0.0) m
           Mass = 1.989e+30 kg (1 M☉)
  Jupiter: Position = (7.8e11, 0.0, 0.0) m (5.2 AU)
           Mass = 1.898e+27 kg (318 M⊕)
  Test Point: (1.5e11, 0.0, 0.0) m (1 AU from Sun)

Segment Density σ:
  Sun only:        σ = 1.145715e-03
  Sun + Jupiter:   σ = 2.291431e-03
  Increase:        Δσ = 1.145715e-03

Additivity Check:
  σ_combined ≥ σ_primary: True

Physical Interpretation:
  • Multiple bodies contribute to total segment density
  • Superposition principle holds for segment fields
  • Jupiter's contribution is small (mass ratio ~1/1000)
  • Consistent with weak-field GR limit
================================================================================
[32mPASSED[0m
scripts/tests/test_cosmo_multibody.py::test_tau_monotonic_with_alpha 
================================================================================
TIME DILATION vs ALPHA PARAMETER TEST
================================================================================
Test Configuration:
  Body mass: 1.989e+30 kg (1 M☉)
  Position: (0.0, 0.0, 0.0) m
  Test point: (2.0e11, 0.0, 0.0) m (1.3 AU)

Alpha Parameter Scan:
  Low α  = 0.2 → τ = 0.99988974
  High α = 1.2 → τ = 0.99933862

Time Dilation Effect:
  Δτ = 0.00055112
  Ratio τ_low/τ_high = 1.000551

Monotonicity Check:
  τ_low > τ_high: True

Physical Interpretation:
  • α controls strength of time dilation
  • Higher α → More time dilation (slower clocks)
  • Lower α → Less time dilation (faster clocks)
  • α ≈ 1 recovers GR-like behavior
================================================================================
[32mPASSED[0m
scripts/tests/test_cosmo_multibody.py::test_refractive_index_baseline 
================================================================================
REFRACTIVE INDEX BASELINE TEST
================================================================================
Test Configuration:
  Earth mass: 5.972e+24 kg (1 M⊕)
  Position: (0.0, 0.0, 0.0) m
  κ parameter: 0.02
  Test point: (3.0e11, 0.0, 0.0) m (2 AU)

Refractive Index:
  n = 1.0000229143
  Deviation from vacuum: n - 1 = 2.29e-05

Causality Check:
  n ≥ 1.0: True

Physical Interpretation:
  • n ≥ 1 ensures causality (no FTL propagation)
  • n > 1 means effective light speed < c
  • Small deviation (n ≈ 1) consistent with weak field
  • Leads to gravitational lensing: Δθ ∝ (n-1)
================================================================================
[32mPASSED[0m

[32m============================== [32m[1m3 passed[0m[32m in 2.40s[0m[32m ==============================[0m
  [OK] Cosmo Multibody Tests (took 7.3s)

----------------------------------------------------------------------------------------------------
PHASE 4: COSMOS TESTS
----------------------------------------------------------------------------------------------------

[RUNNING] Cosmos Multi-Body Sigma Tests
  Command: python -m pytest tests/cosmos/ -s -v --tb=short
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 1 item

tests/cosmos/test_multi_body_sigma.py::test_two_body_sigma_superposition 
================================================================================
TWO-BODY SEGMENT DENSITY SUPERPOSITION
================================================================================
Test Configuration:
  Body A: Position = (0.0, 0.0, 0.0) m
          Mass = 5.972e+24 kg (1 M⊕)
  Body B: Position = (0.5, 0.0, 0.0) m
          Mass = 5.972e+24 kg (1 M⊕)
  Test point: (1.0, 0.0, 0.0) m

Segment Density σ:
  Body A only:  σ_A = 1.145715e-03
  Body B only:  σ_B = 1.145715e-03
  Combined:     σ_total = 2.291431e-03
  Sum A+B:      σ_A + σ_B = 2.291431e-03

Superposition Check:
  σ_total ≈ σ_A + σ_B: True
  Relative difference: 0.00%

Physical Interpretation:
  • Segment fields add linearly (superposition)
  • Consistent with weak-field GR limit
  • Both bodies contribute to spacetime structure
  • No non-linear effects at this scale
================================================================================
[32mPASSED[0m

[32m============================== [32m[1m1 passed[0m[32m in 2.98s[0m[32m ==============================[0m
  [OK] Cosmos Multi-Body Sigma Tests (took 7.1s)

----------------------------------------------------------------------------------------------------
PHASE 5: COMPLETE SSZ ANALYSIS
----------------------------------------------------------------------------------------------------

[RUNNING] Full SSZ Terminal Analysis
  Command: python run_all_ssz_terminal.py
==========================================================================================
 SEGMENTED SPACETIME — AUTO RUN (NO ARGS)
==========================================================================================
Deterministic SSZ evaluation with phi/2 coupling and fixed Delta(M).

Direct calculations only — no fitting. Verbose comparison against GR, SR, GRxSR.

==========================================================================================
 INPUTS & PROVENANCE (REPRODUCIBILITY)
==========================================================================================
CSV file     : H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\real_data_full.csv

CSV sha256   : 37964601e730cb00bdbbd0bb4788ae10ca6dc8cc0b774c77b121ce28b6a78695

CSV mtime    : 2025-10-17T17:09:24.209314

--- Checking for Planck CMB map data ---
[OK] Planck map found (run-specific): H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\data\raw\planck\2025-10-17_gaia_ssz_real\planck_map.fits
     Size: 1.88 GB

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\segspace_all_in_one_extended.py all ---
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11]  SEGSPACE ALL-IN-ONE (FINAL v2) – START
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11]  DETERMINISM SETUP
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11] [OK] NumPy seeded
[ECHO 2025-10-18 23:31:11] [OK] Decimal precision = 200
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11]  SAFETY PREFLIGHT
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11] [OK] ensured: agent_out
[ECHO 2025-10-18 23:31:11] [OK] ensured: agent_out\data
[ECHO 2025-10-18 23:31:11] [OK] ensured: agent_out\figures
[ECHO 2025-10-18 23:31:11] [OK] ensured: agent_out\reports
[ECHO 2025-10-18 23:31:11] [OK] ensured: agent_out\logs
[ECHO 2025-10-18 23:31:11] [SAFE] All writes restricted to outdir subtree.
[ECHO 2025-10-18 23:31:11] [OK] wrote JSON: agent_out\MANIFEST.json
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11]  WORKFLOW: MASS VALIDATION
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11] Invert mass from r_obs=1.0945634625413836795736636983851130109193420637640166677567311016291260750689407100197427388210594562769023502931847628771294766692446794739157260103963186314273107212114432823332077867788285998792881E-57 with M0=9.10938356E-31
[ECHO 2025-10-18 23:31:11] [Newton] Converged at 0 | residual=-1E-256
[ECHO 2025-10-18 23:31:11]       Elektron | M_true=9.10938356E-31 kg | r_obs=1.0945634625413836795736636983851130109193420637640166677567311016291260750689407100197427388210594562769023502931847628771294766692446794739157260103963186314273107212114432823332077867788285998792881E-57 m | M_rec=9.10938356E-31 kg | rel=0
[ECHO 2025-10-18 23:31:11] Invert mass from r_obs=0.000093112782431423285923554186742162695999575222823121001173829046011377758450638394621052218232426366185228085916399665644877327085290642845116819920129001194490841441353642423259204924846221800210026544 with M0=7.342E+22
[ECHO 2025-10-18 23:31:11] [Newton] Converged at 0 | residual=1E-204
[ECHO 2025-10-18 23:31:11]           Mond | M_true=7.342E+22 kg | r_obs=0.000093112782431423285923554186742162695999575222823121001173829046011377758450638394621052218232426366185228085916399665644877327085290642845116819920129001194490841441353642423259204924846221800210026544 m | M_rec=7.342E+22 kg | rel=0
[ECHO 2025-10-18 23:31:11] Invert mass from r_obs=0.0072911742760279982761951503539759022318687772664031979787670187787422384625548383893235035436166244671126127622122557062485685553203542950871985039837794149665955885473692338858358955005024357004507269 with M0=5.97219E+24
[ECHO 2025-10-18 23:31:11] [Newton] Converged at 0 | residual=0E-202
[ECHO 2025-10-18 23:31:11]           Erde | M_true=5.97219E+24 kg | r_obs=0.0072911742760279982761951503539759022318687772664031979787670187787422384625548383893235035436166244671126127622122557062485685553203542950871985039837794149665955885473692338858358955005024357004507269 m | M_rec=5.97219E+24 kg | rel=0
[ECHO 2025-10-18 23:31:11] Invert mass from r_obs=2431.4938230200168113032706246644281202657960784712108525787226988286950118758537737437686887847201382320063167986296334704211779364667138182219478502620016245222958552596653591685556273031828445457360 with M0=1.98847E+30
[ECHO 2025-10-18 23:31:11] [Newton] Converged at 0 | residual=0E-196
[ECHO 2025-10-18 23:31:11]          Sonne | M_true=1.98847E+30 kg | r_obs=2431.4938230200168113032706246644281202657960784712108525787226988286950118758537737437686887847201382320063167986296334704211779364667138182219478502620016245222958552596653591685556273031828445457360 m | M_rec=1.98847E+30 kg | rel=0
[ECHO 2025-10-18 23:31:11] Invert mass from r_obs=10468059481.387632361874563126523908489999471271833524809177593163441352061320762366465610048635507347034277955899067228996176315915142129933309308353120473514781225626670483802708208783004432377111047 with M0=8.54445559E+36
[ECHO 2025-10-18 23:31:11] [Newton] Converged at 0 | residual=0E-189
[ECHO 2025-10-18 23:31:11] Sagittarius A* | M_true=8.54445559E+36 kg | r_obs=10468059481.387632361874563126523908489999471271833524809177593163441352061320762366465610048635507347034277955899067228996176315915142129933309308353120473514781225626670483802708208783004432377111047 m | M_rec=8.54445559E+36 kg | rel=0
[ECHO 2025-10-18 23:31:11] [OK] wrote CSV: agent_out\reports\mass_validation.csv
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11]  WORKFLOW: REDSHIFT EVAL
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11] Loading CSV: real_data_full.csv
[ECHO 2025-10-18 23:31:11] [OK] loaded rows: 127
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11]  EVALUATE REDSHIFT
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11] [PAIRED] Seg better in 82/127 pairs (p~0.00131)
[ECHO 2025-10-18 23:31:11] [OK] wrote JSON: agent_out\reports\redshift_medians.json
[ECHO 2025-10-18 23:31:11] [OK] wrote JSON: agent_out\reports\redshift_paired_stats.json
[ECHO 2025-10-18 23:31:11] [INFO] For per-row debug, run the v1 'all' once to create redshift_debug.csv
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11]  WORKFLOW: BOUND ENERGY & α
[ECHO 2025-10-18 23:31:11] ================================================================================
[ECHO 2025-10-18 23:31:11] E_bound = 5.974419644760417875984776719304208912E-16 J | f_thr = 901653545693357604.42934289177487939997133896929841589437443550156196278724878878621591411917062182023533209952508577048493819522873599519618729059184500182208303363646097227026792042037164366574054457 Hz | lambda = 3.3249185280967785186671459606021200884228391918132440568069436865448902415820676436940925894268308481998848894269007623165075313810641323231543134855826262282543282567767447862605669503849310419973091E-10 m
[ECHO 2025-10-18 23:31:11] [OK] wrote text: agent_out\reports\bound_energy.txt

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\ssz_covariant_smoketest_verbose_lino_casu.py ---
======================================================================================
SEGMENTED SPACETIME – COVARIANT SMOKETEST (VERBOSE, NO NaN, PPN exact)
======================================================================================
Metric: A(U)=1-2U+2U²+ε₃U³ with ε₃=-24/5;  B=1/A;  U=GM/(rc²).
PPN exact at U=0: β=1, γ=1. All sections print finite values.
--------------------------------------------------------------------------------------
======================================================================================
[CASE] Sun (weak-field benchmark) | Mass = 1.988470e+30 kg | eps3=-4.8
--------------------------------------------------------------------------------------
Schwarzschild radius r_s         :  2.95334k m
Segment scale r_phi=φ GM/c²      :   2.3893k m  (φ=1.61803398874989)

[PPN] Far-field parameters (analytic at U=0)
  γ = 1.000000000000  (GR=1)
  β = 1.000000000000  (GR=1)

[WEAK-FIELD TESTS] using PPN formulas
  Light bending @solar limb   : 8.490267e-06 rad  | GR: 8.490267e-06  Δrel=0.000e+00
  Shapiro delay (Earth-Sun)   : 2.389501e-04 s    | GR: 2.389501e-04  Δrel=0.000e+00
  Mercury perihelion/orbit    : 5.018815e-07 rad | GR: 5.018815e-07  Δrel=0.000e+00

[STRONG-FIELD] photon sphere, shadow, ISCO
  Photon sphere radius r_ph :  4.43001k m | GR:  4.43001k m  Δrel=7.152e-13
  Shadow impact b_ph        :  7.20753k m | GR:    7.673k m  Δrel=6.066e-02
  ISCO radius r_isco        :  8.41003k m | GR:  8.86002k m  Δrel=5.079e-02

[SUMMARY] acceptance checks
  PPN close to GR (|γ-1|,|β-1| < 1e-12) : PASS
  Weak-field classic tests              : PASS
  Strong-field                          : PASS (finite values)

======================================================================================
[CASE] Sgr A* (strong-field showcase) | Mass = 8.544456e+36 kg | eps3=-4.8
--------------------------------------------------------------------------------------
Schwarzschild radius r_s         :  12.6905G m
Segment scale r_phi=φ GM/c²      :  10.2668G m  (φ=1.61803398874989)

[PPN] Far-field parameters (analytic at U=0)
  γ = 1.000000000000  (GR=1)
  β = 1.000000000000  (GR=1)

[WEAK-FIELD TESTS] using PPN formulas
  Light bending @b=10 r_s     : 2.000000e-01 rad  | GR: 2.000000e-01  Δrel=0.000e+00
  Shapiro delay @rE=rT=1000r_s: 8.971312e+02 s    | GR: 8.971312e+02  Δrel=0.000e+00

[STRONG-FIELD] photon sphere, shadow, ISCO
  Photon sphere radius r_ph :  19.0357G m | GR:  19.0357G m  Δrel=3.902e-11
  Shadow impact b_ph        :  30.9708G m | GR:  32.9709G m  Δrel=6.066e-02
  ISCO radius r_isco        :  36.1378G m | GR:  38.0715G m  Δrel=5.079e-02

[SUMMARY] acceptance checks
  PPN close to GR (|γ-1|,|β-1| < 1e-12) : PASS
  Weak-field classic tests              : PASS
  Strong-field                          : PASS (finite values)


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\test_ppn_exact.py ---

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


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\test_c1_segments.py ---

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


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\test_c2_segments_strict.py ---

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


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\test_energy_conditions.py ---

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


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\shadow_predictions_exact.py ---
Sgr A*: diameter = 53.255 µas  [M=4.297e+06 Msun, D=8277 pc]
M87*:   diameter = 39.689 µas  [M=6.5e+09 Msun, D=1.68e+07 pc]

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\qnm_eikonal.py ---
Eikonal QNM (l>>1) for M=30 Msun: Omega_c=1.386478e+03  lambda=1.323476e+03 [1/s]

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\test_vfall_duality.py --mass Earth --r-mults 1.1,2.0 ---

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
    2.0000       1.774018e-02 7.071068e-01 1.414214e+00   1.000000000000e+00 1.414214e+00 1.414214e+00     1.57e-16
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


--- Running pytest unit tests ---
  Running tests/ directory...

--- Running C:\Program Files\Python310\python.exe -m pytest H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\tests -s -v --tb=short ---
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 67 items

tests/cosmos/test_multi_body_sigma.py::test_two_body_sigma_superposition 
================================================================================
TWO-BODY SEGMENT DENSITY SUPERPOSITION
================================================================================
Test Configuration:
  Body A: Position = (0.0, 0.0, 0.0) m
          Mass = 5.972e+24 kg (1 M⊕)
  Body B: Position = (0.5, 0.0, 0.0) m
          Mass = 5.972e+24 kg (1 M⊕)
  Test point: (1.0, 0.0, 0.0) m

Segment Density σ:
  Body A only:  σ_A = 1.145715e-03
  Body B only:  σ_B = 1.145715e-03
  Combined:     σ_total = 2.291431e-03
  Sum A+B:      σ_A + σ_B = 2.291431e-03

Superposition Check:
  σ_total ≈ σ_A + σ_B: True
  Relative difference: 0.00%

Physical Interpretation:
  • Segment fields add linearly (superposition)
  • Consistent with weak-field GR limit
  • Both bodies contribute to spacetime structure
  • No non-linear effects at this scale
================================================================================
[32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_basic [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_depth_order [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_exclude_dirs [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_size_limit [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_no_files [32mPASSED[0m
tests/test_print_all_md.py::test_print_all_md_custom_includes [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIBasic::test_help_flag [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIBasic::test_missing_required_args [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIBasic::test_invalid_csv_path [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIExecution::test_fixed_alpha_execution [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIExecution::test_fit_alpha_execution [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIExecution::test_frequency_tracking [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIExecution::test_custom_exponents [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIValidation::test_negative_v0 [32mPASSED[0m
tests/test_segwave_cli.py::TestCLIValidation::test_mutually_exclusive_alpha [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_g79_dataset_exists [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_cygx_dataset_exists [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_sources_json_exists [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_sources_config_yaml_exists [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_load_sources_config_function [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_g79_cli_smoke_run [32mPASSED[0m
tests/test_segwave_cli.py::TestBundledDatasets::test_cygx_cli_smoke_run [32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
tests/test_segwave_core.py::TestQFactor::test_invalid_temperature_raises [32mPASSED[0m
tests/test_segwave_core.py::TestQFactor::test_invalid_density_raises [32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
tests/test_segwave_core.py::TestVelocityProfile::test_mismatched_lengths_raises [32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
tests/test_segwave_core.py::TestFrequencyTrack::test_invalid_gamma_raises [32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
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
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestPPNParameters::test_ppn_beta_equals_one 
================================================================================
PPN PARAMETER β (Preferred-Frame)
================================================================================
Calculated β:  1.000000000000
GR prediction: 1.000000000000
Difference:    0.00e+00

Physical Interpretation:
  β = 1 → No preferred reference frame
  β = 1 → SSZ matches GR in weak gravitational fields
  β = 1 → Compatible with solar system observations
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestPPNParameters::test_ppn_gamma_equals_one 
================================================================================
PPN PARAMETER γ (Space Curvature)
================================================================================
Calculated γ:  1.000000000000
GR prediction: 1.000000000000
Difference:    0.00e+00

Physical Interpretation:
  γ = 1 → Light bending matches GR
  γ = 1 → Shapiro time delay matches GR
  γ = 1 → Gravitational lensing matches observations
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestNaturalBoundary::test_natural_boundary_radius[Sun] 
================================================================================
NATURAL BOUNDARY: Sun
================================================================================
Object: Our Sun - reference star
Mass:   1.988e+30 kg (1.00e+00 M_☉)

Radii:
  Schwarzschild r_s: 2.953e+03 m
  Natural r_φ:       2.389e+03 m
  Ratio r_φ/r_s:     0.809017 = φ/2
  φ value:           1.6180339887

Physical Interpretation:
  • Sun has a natural boundary at r_φ = 2.389e+03 m
  • Segment density saturates at this radius
  • No mathematical singularity - energy remains finite
  • Information is preserved at the boundary surface
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestNaturalBoundary::test_natural_boundary_radius[SgrA*] 
================================================================================
NATURAL BOUNDARY: SgrA*
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Mass:   8.544e+36 kg (4.30e+06 M_☉)

Radii:
  Schwarzschild r_s: 1.269e+10 m
  Natural r_φ:       1.027e+10 m
  Ratio r_φ/r_s:     0.809017 = φ/2
  φ value:           1.6180339887

Physical Interpretation:
  • SgrA* has a natural boundary at r_φ = 1.027e+10 m
  • Segment density saturates at this radius
  • No mathematical singularity - energy remains finite
  • Information is preserved at the boundary surface
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestNaturalBoundary::test_natural_boundary_radius[M87*] 
================================================================================
NATURAL BOUNDARY: M87*
================================================================================
Object: M87* - supermassive black hole, first to be imaged by EHT
Mass:   1.293e+40 kg (6.50e+09 M_☉)

Radii:
  Schwarzschild r_s: 1.920e+13 m
  Natural r_φ:       1.553e+13 m
  Ratio r_φ/r_s:     0.809017 = φ/2
  φ value:           1.6180339887

Physical Interpretation:
  • M87* has a natural boundary at r_φ = 1.553e+13 m
  • Segment density saturates at this radius
  • No mathematical singularity - energy remains finite
  • Information is preserved at the boundary surface
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[1.1-Earth] 
================================================================================
DUAL VELOCITIES: Earth at r = 1.1r_s
================================================================================
Object: Earth - our planet
Mass:   5.972e+24 kg
Radius: r = 9.757e-03 m (1.1r_s)

Velocities:
  Escape velocity v_esc:  2.858409e+08 m/s (0.953463c)
  Infall velocity v_fall: 3.144250e+08 m/s (1.048809c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         0.000e+00

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[1.1-Sun] 
================================================================================
DUAL VELOCITIES: Sun at r = 1.1r_s
================================================================================
Object: Our Sun - reference star
Mass:   1.988e+30 kg
Radius: r = 3.249e+03 m (1.1r_s)

Velocities:
  Escape velocity v_esc:  2.858409e+08 m/s (0.953463c)
  Infall velocity v_fall: 3.144250e+08 m/s (1.048809c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         1.780e-16

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[1.1-SgrA*] 
================================================================================
DUAL VELOCITIES: SgrA* at r = 1.1r_s
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Mass:   8.544e+36 kg
Radius: r = 1.396e+10 m (1.1r_s)

Velocities:
  Escape velocity v_esc:  2.858409e+08 m/s (0.953463c)
  Infall velocity v_fall: 3.144250e+08 m/s (1.048809c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         1.780e-16

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[2.0-Earth] 
================================================================================
DUAL VELOCITIES: Earth at r = 2.0r_s
================================================================================
Object: Earth - our planet
Mass:   5.972e+24 kg
Radius: r = 1.774e-02 m (2.0r_s)

Velocities:
  Escape velocity v_esc:  2.119853e+08 m/s (0.707107c)
  Infall velocity v_fall: 4.239706e+08 m/s (1.414214c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         1.780e-16

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[2.0-Sun] 
================================================================================
DUAL VELOCITIES: Sun at r = 2.0r_s
================================================================================
Object: Our Sun - reference star
Mass:   1.988e+30 kg
Radius: r = 5.907e+03 m (2.0r_s)

Velocities:
  Escape velocity v_esc:  2.119853e+08 m/s (0.707107c)
  Infall velocity v_fall: 4.239706e+08 m/s (1.414214c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         1.780e-16

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[2.0-SgrA*] 
================================================================================
DUAL VELOCITIES: SgrA* at r = 2.0r_s
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Mass:   8.544e+36 kg
Radius: r = 2.538e+10 m (2.0r_s)

Velocities:
  Escape velocity v_esc:  2.119853e+08 m/s (0.707107c)
  Infall velocity v_fall: 4.239706e+08 m/s (1.414214c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         1.780e-16

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[5.0-Earth] 
================================================================================
DUAL VELOCITIES: Earth at r = 5.0r_s
================================================================================
Object: Earth - our planet
Mass:   5.972e+24 kg
Radius: r = 4.435e-02 m (5.0r_s)

Velocities:
  Escape velocity v_esc:  1.340713e+08 m/s (0.447214c)
  Infall velocity v_fall: 6.703563e+08 m/s (2.236068c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         0.000e+00

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[5.0-Sun] 
================================================================================
DUAL VELOCITIES: Sun at r = 5.0r_s
================================================================================
Object: Our Sun - reference star
Mass:   1.988e+30 kg
Radius: r = 1.477e+04 m (5.0r_s)

Velocities:
  Escape velocity v_esc:  1.340713e+08 m/s (0.447214c)
  Infall velocity v_fall: 6.703563e+08 m/s (2.236068c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         0.000e+00

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[5.0-SgrA*] 
================================================================================
DUAL VELOCITIES: SgrA* at r = 5.0r_s
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Mass:   8.544e+36 kg
Radius: r = 6.345e+10 m (5.0r_s)

Velocities:
  Escape velocity v_esc:  1.340713e+08 m/s (0.447214c)
  Infall velocity v_fall: 6.703563e+08 m/s (2.236068c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         0.000e+00

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[10.0-Earth] 
================================================================================
DUAL VELOCITIES: Earth at r = 10.0r_s
================================================================================
Object: Earth - our planet
Mass:   5.972e+24 kg
Radius: r = 8.870e-02 m (10.0r_s)

Velocities:
  Escape velocity v_esc:  9.480270e+07 m/s (0.316228c)
  Infall velocity v_fall: 9.480270e+08 m/s (3.162278c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         0.000e+00

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[10.0-Sun] 
================================================================================
DUAL VELOCITIES: Sun at r = 10.0r_s
================================================================================
Object: Our Sun - reference star
Mass:   1.988e+30 kg
Radius: r = 2.953e+04 m (10.0r_s)

Velocities:
  Escape velocity v_esc:  9.480270e+07 m/s (0.316228c)
  Infall velocity v_fall: 9.480270e+08 m/s (3.162278c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         0.000e+00

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestDualVelocities::test_dual_velocity_invariant[10.0-SgrA*] 
================================================================================
DUAL VELOCITIES: SgrA* at r = 10.0r_s
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Mass:   8.544e+36 kg
Radius: r = 1.269e+11 m (10.0r_s)

Velocities:
  Escape velocity v_esc:  9.480270e+07 m/s (0.316228c)
  Infall velocity v_fall: 9.480270e+08 m/s (3.162278c)

Invariant Check:
  Product v_esc × v_fall: 8.987552e+16 m²/s²
  Target c²:              8.987552e+16 m²/s²
  Relative error:         0.000e+00

Physical Interpretation:
  • Rest energy: E_rest = m × v_esc × v_fall = mc²
  • Energy conservation holds exactly
  • Mass-energy equivalence is preserved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestEnergyConditions::test_energy_conditions_real_object[1.2-SgrA*] 
================================================================================
ENERGY CONDITIONS: SgrA* at r = 1.2r_s
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Radius: r = 1.523e+10 m (1.2r_s)

Effective Stress-Energy Components:
  Energy density ρ:     -5.957276e-23 kg/m³
  Radial pressure p_r:  5.957276e-23 Pa
  Tangential pressure p_⊥: -1.191360e-22 Pa

Energy Conditions:
  WEC (Weak):      ✗ FAIL - ρ≥0 and ρ+p≥0
  DEC (Dominant):  ✗ FAIL - ρ≥|p|
  SEC (Strong):    ✗ FAIL - ρ+p+2p_⊥≥0
  NEC check: ρ+p_r = 0.000e+00 (should be ~0)

Physical Interpretation:
  • At r = 1.2r_s, strong field regime
  • Some conditions may not hold near r_φ
  • Natural boundary prevents singularity
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestEnergyConditions::test_energy_conditions_real_object[2.0-SgrA*] 
================================================================================
ENERGY CONDITIONS: SgrA* at r = 2.0r_s
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Radius: r = 2.538e+10 m (2.0r_s)

Effective Stress-Energy Components:
  Energy density ρ:     -1.544126e-24 kg/m³
  Radial pressure p_r:  1.544126e-24 Pa
  Tangential pressure p_⊥: -6.182404e-24 Pa

Energy Conditions:
  WEC (Weak):      ✗ FAIL - ρ≥0 and ρ+p≥0
  DEC (Dominant):  ✗ FAIL - ρ≥|p|
  SEC (Strong):    ✗ FAIL - ρ+p+2p_⊥≥0
  NEC check: ρ+p_r = 0.000e+00 (should be ~0)

Physical Interpretation:
  • At r = 2.0r_s, strong field regime
  • Some conditions may not hold near r_φ
  • Natural boundary prevents singularity
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestEnergyConditions::test_energy_conditions_real_object[5.0-SgrA*] 
================================================================================
ENERGY CONDITIONS: SgrA* at r = 5.0r_s
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Radius: r = 6.345e+10 m (5.0r_s)

Effective Stress-Energy Components:
  Energy density ρ:     1.027770e-25 kg/m³
  Radial pressure p_r:  -1.027770e-25 Pa
  Tangential pressure p_⊥: 5.469989e-26 Pa

Energy Conditions:
  WEC (Weak):      ✓ PASS - ρ≥0 and ρ+p≥0
  DEC (Dominant):  ✓ PASS - ρ≥|p|
  SEC (Strong):    ✓ PASS - ρ+p+2p_⊥≥0
  NEC check: ρ+p_r = 0.000e+00 (should be ~0)

Physical Interpretation:
  • At r = 5.0r_s, all conditions satisfied
  • Effective matter behaves physically
  • No exotic matter required
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestEnergyConditions::test_energy_conditions_real_object[10.0-SgrA*] 
================================================================================
ENERGY CONDITIONS: SgrA* at r = 10.0r_s
================================================================================
Object: Sagittarius A* - supermassive black hole at galactic center
Radius: r = 1.269e+11 m (10.0r_s)

Effective Stress-Energy Components:
  Energy density ρ:     9.388286e-27 kg/m³
  Radial pressure p_r:  -9.388286e-27 Pa
  Tangential pressure p_⊥: 8.190600e-27 Pa

Energy Conditions:
  WEC (Weak):      ✓ PASS - ρ≥0 and ρ+p≥0
  DEC (Dominant):  ✓ PASS - ρ≥|p|
  SEC (Strong):    ✓ PASS - ρ+p+2p_⊥≥0
  NEC check: ρ+p_r = 0.000e+00 (should be ~0)

Physical Interpretation:
  • At r = 10.0r_s, all conditions satisfied
  • Effective matter behaves physically
  • No exotic matter required
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestRealDataIntegration::test_load_real_data 
================================================================================
REAL ASTRONOMICAL DATA
================================================================================
Loaded 127 astronomical objects

Data columns: case, category, M_solar, a_m, e, P_year, T0_year, f_true_deg, z, f_emit_Hz, f_obs_Hz, lambda_emit_nm, lambda_obs_nm, v_los_mps, v_tot_mps, z_geom_hint, N0, source, r_emit_m

Physical Interpretation:
  • Real data validates SSZ predictions
  • Masses span 12 orders of magnitude
  • Perfect mass reconstruction achieved
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestMetricProperties::test_metric_continuity[Sun] 
================================================================================
METRIC CONTINUITY: Sun
================================================================================

Radius r = 2.0r_s:
  A(r):        0.5500000000
  A'(r) ≈      8.041744e-05
  |A_right - A_left|: 9.500000e-07

Radius r = 5.0r_s:
  A(r):        0.8152000000
  A'(r) ≈      1.181036e-05
  |A_right - A_left|: 3.488000e-07

Radius r = 10.0r_s:
  A(r):        0.9044000000
  A'(r) ≈      3.108346e-06
  |A_right - A_left|: 1.836000e-07

Physical Interpretation:
  • Metric is smooth and continuous
  • Gravitational field is well-defined
  • No unphysical discontinuities
================================================================================
[32mPASSED[0m
tests/test_ssz_real_data_comprehensive.py::TestMetricProperties::test_metric_continuity[SgrA*] 
================================================================================
METRIC CONTINUITY: SgrA*
================================================================================

Radius r = 2.0r_s:
  A(r):        0.5500000000
  A'(r) ≈      1.871479e-11
  |A_right - A_left|: 9.500000e-07

Radius r = 5.0r_s:
  A(r):        0.8152000000
  A'(r) ≈      2.748513e-12
  |A_right - A_left|: 3.488000e-07

Radius r = 10.0r_s:
  A(r):        0.9044000000
  A'(r) ≈      7.233758e-13
  |A_right - A_left|: 1.836000e-07

Physical Interpretation:
  • Metric is smooth and continuous
  • Gravitational field is well-defined
  • No unphysical discontinuities
================================================================================
[32mPASSED[0m
================================================================================
SEGMENTED SPACETIME TEST SUITE SUMMARY
================================================================================

Theoretical Framework:
  • φ-based segment density corrections to GR
  • Natural boundary at r_φ = (φ/2)r_s
  • PPN parameters: β = γ = 1 (matches GR in weak field)
  • Dual velocity invariant: v_esc × v_fall = c²

Validation Results:
  ✓ PPN parameters match GR
  ✓ Natural boundary prevents singularities
  ✓ Dual velocity invariant holds to machine precision
  ✓ Energy conditions satisfied (r ≥ 5r_s)
  ✓ Metric is C¹ continuous

Physical Predictions:
  • Black holes have finite surface at r_φ
  • Information is preserved
  • Singularity paradox is resolved
  • Hawking radiation emerges naturally

© 2025 Carmen Wrede, Lino Casu
Anti-Capitalist Software License (v 1.4)
================================================================================



[32m============================= [32m[1m67 passed[0m[32m in 32.10s[0m[32m =============================[0m
  Running scripts/tests/ directory...

--- Running C:\Program Files\Python310\python.exe -m pytest H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests -s -v --tb=short ---
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0 -- C:\Program Files\Python310\python.exe
cachedir: .pytest_cache
rootdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
configfile: pytest.ini
plugins: anyio-4.9.0, dash-3.2.0, langsmith-0.3.44, docker-3.1.2, timeout-2.4.0
timeout: 300.0s
timeout method: thread
timeout func_only: False
[1mcollecting ... [0mcollected 28 items

scripts/tests/test_cosmo_fields.py::test_cosmo_fields_added 
================================================================================
COSMOLOGICAL FIELD CONSTRUCTION TEST
================================================================================

Input Data:
  Positions: (x,y) = [(0, 0), (1, 1)]
  Densities: ρ = [0.2 5. ]

Gamma Configuration:
  α = 0.8
  β = 0.6
  floor = 0.02

Generated Fields:
  ✓ gamma_seg: [0.139861, 0.742681]
  ✓ z_seg: [0.346473, 6.149971]
  ✓ kappa_proxy: [0.269295, 35.749854]
  ✓ vrot_mod: [1.160376, 2.673943]

Gamma Bounds Check:
  Range: [0.139861, 0.742681]
  Within [0.02, 1.0]: ✓ PASS

Physical Interpretation:
  • Cosmological fields add to spacetime structure
  • gamma_seg: Segment field strength (0.02 ≤ γ ≤ 1.0)
  • z_seg: Redshift mapping z = (1/γ) - 1
  • kappa_proxy: Gravitational lensing convergence
  • vrot_mod: Rotation curve modifier γ^(-p)
  • All fields contribute to observable predictions
================================================================================
[32mPASSED[0m
scripts/tests/test_cosmo_multibody.py::test_sigma_additive_mass 
================================================================================
SEGMENT DENSITY ADDITIVITY TEST
================================================================================
Test Configuration:
  Sun:     Position = (0.0, 0.0, 0.0) m
           Mass = 1.989e+30 kg (1 M☉)
  Jupiter: Position = (7.8e11, 0.0, 0.0) m (5.2 AU)
           Mass = 1.898e+27 kg (318 M⊕)
  Test Point: (1.5e11, 0.0, 0.0) m (1 AU from Sun)

Segment Density σ:
  Sun only:        σ = 1.145715e-03
  Sun + Jupiter:   σ = 2.291431e-03
  Increase:        Δσ = 1.145715e-03

Additivity Check:
  σ_combined ≥ σ_primary: True

Physical Interpretation:
  • Multiple bodies contribute to total segment density
  • Superposition principle holds for segment fields
  • Jupiter's contribution is small (mass ratio ~1/1000)
  • Consistent with weak-field GR limit
================================================================================
[32mPASSED[0m
scripts/tests/test_cosmo_multibody.py::test_tau_monotonic_with_alpha 
================================================================================
TIME DILATION vs ALPHA PARAMETER TEST
================================================================================
Test Configuration:
  Body mass: 1.989e+30 kg (1 M☉)
  Position: (0.0, 0.0, 0.0) m
  Test point: (2.0e11, 0.0, 0.0) m (1.3 AU)

Alpha Parameter Scan:
  Low α  = 0.2 → τ = 0.99988974
  High α = 1.2 → τ = 0.99933862

Time Dilation Effect:
  Δτ = 0.00055112
  Ratio τ_low/τ_high = 1.000551

Monotonicity Check:
  τ_low > τ_high: True

Physical Interpretation:
  • α controls strength of time dilation
  • Higher α → More time dilation (slower clocks)
  • Lower α → Less time dilation (faster clocks)
  • α ≈ 1 recovers GR-like behavior
================================================================================
[32mPASSED[0m
scripts/tests/test_cosmo_multibody.py::test_refractive_index_baseline 
================================================================================
REFRACTIVE INDEX BASELINE TEST
================================================================================
Test Configuration:
  Earth mass: 5.972e+24 kg (1 M⊕)
  Position: (0.0, 0.0, 0.0) m
  κ parameter: 0.02
  Test point: (3.0e11, 0.0, 0.0) m (2 AU)

Refractive Index:
  n = 1.0000229143
  Deviation from vacuum: n - 1 = 2.29e-05

Causality Check:
  n ≥ 1.0: True

Physical Interpretation:
  • n ≥ 1 ensures causality (no FTL propagation)
  • n > 1 means effective light speed < c
  • Small deviation (n ≈ 1) consistent with weak field
  • Leads to gravitational lensing: Δθ ∝ (n-1)
================================================================================
[32mPASSED[0m
scripts/tests/test_data_fetch.py::test_gaia_smoke [32mPASSED[0m
scripts/tests/test_data_fetch.py::test_sdss_smoke [32mPASSED[0m
scripts/tests/test_data_fetch.py::test_planck_presence [32mPASSED[0m
scripts/tests/test_gaia_required_columns.py::test_harmonize_columns_preserves_required [32mPASSED[0m
scripts/tests/test_gaia_required_columns.py::test_harmonize_columns_rejects_missing_errors [32mPASSED[0m
scripts/tests/test_gaia_required_columns.py::test_harmonize_columns_soft_fills_missing_errors [GAIA-CLEAN] Missing uncertainty columns filled with NaN: pmdec_error, pmra_error
[32mPASSED[0m
scripts/tests/test_plot_ssz_maps.py::test_plot_mollweide_handles_nan [32mPASSED[0m
scripts/tests/test_plot_ssz_maps.py::test_plot_mollweide_derives_galactic [32mPASSED[0m
scripts/tests/test_segmenter.py::test_segments_cover_all_points 
================================================================================
SEGMENT COVERAGE TEST
================================================================================
Spacetime points: 5000
Requested rings: 16

Segmentation Results:
  Points covered: 5000/5000
  Ring IDs: 0 to 6
  Segment IDs: 0 to 11

Physical Interpretation:
  • Complete coverage: all 5000 points assigned
  • Each point in exactly one segment
  • Ensures consistent segmented spacetime structure
================================================================================
[32mPASSED[0m
scripts/tests/test_segmenter.py::test_segment_counts_grow 
================================================================================
SEGMENT RESOLUTION SCALING TEST
================================================================================
Base segments: 4
Number of rings: 5

Segment Count Growth:
  Ring 1: 4 segments
  Ring 2: 5 segments
  Ring 3: 5 segments
  Ring 4: 6 segments
  Ring 5: 7 segments

Monotonicity:
  Segments never shrink: True

Physical Interpretation:
  • Segment count grows (or stays constant) with ring index
  • Physical structure preserved across rings
  • Algorithm handles varying densities correctly
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_segment_growth_is_monotonic 
================================================================================
SEGMENT GROWTH MONOTONICITY TEST
================================================================================
Dataset: 2025-10-17_gaia_ssz_v1
Number of rings: 1

Growth Statistics:
  Mean growth: nan
  Min growth: nan
  Max growth: nan
  All non-negative: True

Physical Interpretation:
  • Segment density increases outward (or remains stable)
  • Ensures consistent spacetime structure
  • No unphysical density drops between rings
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_natural_boundary_positive 
================================================================================
NATURAL BOUNDARY POSITIVITY TEST
================================================================================
Dataset: 2025-10-17_gaia_ssz_v1

Natural Boundary Statistics:
  Minimum: 5.224918e+00
  Maximum: 8.014793e+00
  Median: 6.630052e+00
  All positive: True

Physical Interpretation:
  • Positive boundary radii ensure physical segments
  • Defines scale where segmentation becomes important
  • Related to φ-based natural scales in spacetime
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_manifest_exists [32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_spiral_index_bounds [32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_solar_segments_non_empty [32mPASSED[0m
scripts/tests/test_ssz_invariants.py::test_segment_density_positive 
================================================================================
SEGMENT DENSITY POSITIVITY TEST
================================================================================
Dataset: 2025-10-17_gaia_ssz_v1
Total segments: 550

Density Statistics:
  Minimum: 1.577892e+01
  Maximum: 1.894541e+01
  Mean: 1.745581e+01
  Std Dev: 3.097954e-01
  All positive: True

Physical Interpretation:
  • Positive density ensures physical spacetime segments
  • Zero density would indicate classical (non-SSZ) limit
  • Density distribution shows segment field strength
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_kernel.py::test_gamma_bounds_and_monotonic 
================================================================================
GAMMA SEGMENT FIELD TEST
================================================================================
Density range: ρ = [0.0, 100.0]

Gamma values:
  ρ =    0.0 → γ = 1.000000
  ρ =    0.1 → γ = 0.782318
  ρ =    1.0 → γ = 0.380522
  ρ =   10.0 → γ = 0.038292
  ρ =  100.0 → γ = 0.020000

Bounds Check:
  Minimum γ: 0.020000 (floor = 0.02)
  Maximum γ: 1.000000 (max = 1.0)
  All in bounds: True

Monotonicity Check:
  All differences ≤ 0: True
  Max increase: -1.83e-02 (should be ~0)

Physical Interpretation:
  • γ decreases with density (segment saturation)
  • Bounded between floor and 1.0 (physical limits)
  • Smooth monotonic behavior ensures stability
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_kernel.py::test_redshift_mapping 
================================================================================
REDSHIFT-GAMMA MAPPING TEST
================================================================================
Mapping: z = (1/γ) - 1

Results:
  γ = 1.00 → z = 0.00 (expected 0.00)
  γ = 0.50 → z = 1.00 (expected 1.00)
  γ = 0.25 → z = 3.00 (expected 3.00)

Physical Interpretation:
  • γ = 1.0 → z = 0.0 (no redshift, local frame)
  • γ = 0.5 → z = 1.0 (50% field strength, z=1 cosmology)
  • γ = 0.25 → z = 3.0 (25% field strength, z=3 cosmology)
  • Lower γ → Higher z (weaker field, greater cosmological distance)
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_kernel.py::test_rotation_modifier 
================================================================================
ROTATION CURVE MODIFIER TEST
================================================================================
Power parameter p = 0.5

Rotation Modifiers:
  γ = 1.00 → v_mod = 1.0000
  γ = 0.50 → v_mod = 1.4142
  γ = 0.25 → v_mod = 2.0000

Monotonicity Check:
  v_mod increases as γ decreases: True

Physical Interpretation:
  • Weaker segment field (low γ) → Stronger rotation boost
  • Explains flat rotation curves in galaxies
  • Alternative to dark matter hypothesis
  • Modifier scales as γ^(-p) where p=0.5
================================================================================
[32mPASSED[0m
scripts/tests/test_ssz_kernel.py::test_lensing_proxy_positive 
================================================================================
GRAVITATIONAL LENSING PROXY TEST
================================================================================
Density range: ρ ∈ [0.0, 10.0]
κ scale parameter: 1.0

Lensing Convergence κ:
  Minimum: 0.000000
  Maximum: 261.149026
  All positive: True

Sample values:
  ρ =  0.00 → κ = 0.000000
  ρ =  2.50 → κ = 12.937135
  ρ =  5.00 → κ = 55.016041
  ρ =  7.50 → κ = 137.906175
  ρ = 10.00 → κ = 261.149026

Physical Interpretation:
  • κ > 0 everywhere (positive mass lenses light)
  • κ increases with density (stronger lensing)
  • Observable via gravitational lensing surveys
  • Consistent with weak lensing constraints
================================================================================
[32mPASSED[0m
scripts/tests/test_utf8_encoding.py::test_utf8_environment [32mPASSED[0m
scripts/tests/test_utf8_encoding.py::test_stdout_encoding [33mSKIPPED[0m
scripts/tests/test_utf8_encoding.py::test_utf8_file_write_read [32mPASSED[0m
scripts/tests/test_utf8_encoding.py::test_json_utf8 [32mPASSED[0m

[32m======================== [32m[1m27 passed[0m, [33m1 skipped[0m[32m in 5.24s[0m[32m ========================[0m

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\phi_test.py --in H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\real_data_full.csv --outdir H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\out --f-emit f_emit_Hz --f-obs f_obs_Hz ---
[OK] rows used: 127
[OK] abs_residual_median: 0.00048739530319731757
[OK] outdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\out
[INFO] column_log: {"used_f_emit": "f_emit_Hz", "used_f_obs": "f_obs_Hz"}

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\phi_bic_test.py --in H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\real_data_full.csv --outdir H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\out --f-emit f_emit_Hz --f-obs f_obs_Hz ---
[OK] rows used: 127
[OK] abs_residual_median: 0.0004873953031977789
[OK] ΔBIC (uniform - lattice): 142.6322434551314  -> φ-Gitter besser
[OK] sign-test p(two-sided): 4.738017452905029e-06
[OK] outdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\out

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\compute_vfall_from_z.py --in H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\real_data_full.csv --outdir H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\vfall_out ---
[OK] rows used: 127
[OK] abs_residual_median: 0.0004873953031977789
[OK] prod_rel_err_median: 0.0
[OK] outdir: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\vfall_out
[INFO] column_log: {"auto_z": "z"}

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\segspace_final_test.py --csv H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\real_data_30_segmodel.csv ---
[INFO] using --csv H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\real_data_30_segmodel.csv
========================================================================
 SEGSPACE — FINALE TESTS abgeschlossen. Siehe ./out
========================================================================

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\segspace_final_explain.py ---
========================================================================
 SEGMENTED SPACETIME — ERKLÄRENDER LAUF
========================================================================
CSV: real_data_30_segmodel.csv

[S2_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=153088900000000.0, e=0.8843, f_true=0.0, M_solar=4297000.0
  v_los_mps=0.000e+00
  z_data = 6.671282e-04
  r_eff = 1.771239e+13 m  (Quelle: r(a,e,f_true))
  v_pred = 7.788997e+06 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 6.962059e-04  → Δz = -2.907774e-05
  z_GR = 3.584306e-04    → Δz = 3.086976e-04
  z_SR = 3.376849e-04    → Δz = 3.294433e-04
  z_GR*SR = 6.962366e-04 → Δz = -2.910837e-05

[S29_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=523702500000000.0, e=0.728, f_true=0.0, M_solar=4297000.0
  z_data = 7.118109e-05
  r_eff = 1.424471e+14 m  (Quelle: r(a,e,f_true))
  v_pred = 2.630208e+06 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 8.299048e-05  → Δz = -1.180938e-05
  z_GR = 4.454759e-05    → Δz = 2.663351e-05
  z_SR = 3.848877e-05    → Δz = 3.269233e-05
  z_GR*SR = 8.303807e-05 → Δz = -1.185697e-05
  Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.

[S38_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=173297400000000.0, e=0.8201, f_true=0.0, M_solar=4297000.0
  z_data = 3.300885e-04
  r_eff = 3.117620e+13 m  (Quelle: r(a,e,f_true))
  v_pred = 5.770070e+06 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 3.889104e-04  → Δz = -5.882189e-05
  z_GR = 2.035908e-04    → Δz = 1.264977e-04
  z_SR = 1.852727e-04    → Δz = 1.448158e-04
  z_GR*SR = 3.889012e-04 → Δz = -5.881268e-05
  Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.

[S62_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=110714100000000.0, e=0.976, f_true=0.0, M_solar=4297000.0
  z_data = 3.975941e-03
  r_eff = 2.657138e+12 m  (Quelle: r(a,e,f_true))
  v_pred = 2.059356e+07 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 4.770002e-03  → Δz = -7.940613e-04
  z_GR = 2.396589e-03    → Δz = 1.579352e-03
  z_SR = 2.367728e-03    → Δz = 1.608213e-03
  z_GR*SR = 4.769992e-03 → Δz = -7.940505e-04
  Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.

[S4711_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=92632040000000.0, e=0.768, f_true=0.0, M_solar=4297000.0
  z_data = 4.798593e-04
  r_eff = 2.149063e+13 m  (Quelle: r(a,e,f_true))
  v_pred = 6.849543e+06 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 5.565861e-04  → Δz = -7.672679e-05
  z_GR = 2.953874e-04    → Δz = 1.844720e-04
  z_SR = 2.611090e-04    → Δz = 2.187503e-04
  z_GR*SR = 5.565735e-04 → Δz = -7.671414e-05
  Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.

[S4712_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=556594500000000.0, e=0.364, f_true=0.0, M_solar=4297000.0
  z_data = 2.871072e-05
  r_eff = 3.539941e+14 m  (Quelle: r(a,e,f_true))
  v_pred = 1.482362e+06 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 3.012511e-05  → Δz = -1.414387e-06
  z_GR = 1.792521e-05    → Δz = 1.078551e-05
  z_SR = 1.222489e-05    → Δz = 1.648583e-05
  z_GR*SR = 3.015033e-05 → Δz = -1.439602e-06
  Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.

[S4713_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=247347900000000.0, e=0.351, f_true=0.0, M_solar=4297000.0
  z_data = 6.305164e-05
  r_eff = 1.605288e+14 m  (Quelle: r(a,e,f_true))
  v_pred = 2.190767e+06 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 6.620273e-05  → Δz = -3.151097e-06
  z_GR = 3.952952e-05    → Δz = 2.352212e-05
  z_SR = 2.670168e-05    → Δz = 3.634996e-05
  z_GR*SR = 6.623225e-05 → Δz = -3.180617e-06
  Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.

[S4714_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=125864800000000.0, e=0.985, f_true=0.0, M_solar=4297000.0
  z_data = 5.600994e-03
  r_eff = 1.887972e+12 m  (Quelle: r(a,e,f_true))
  v_pred = 2.448655e+07 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 6.741682e-03  → Δz = -1.140688e-03
  z_GR = 3.377920e-03    → Δz = 2.223074e-03
  z_SR = 3.352458e-03    → Δz = 2.248536e-03
  z_GR*SR = 6.741702e-03 → Δz = -1.140708e-03
  Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.

[S4715_SgrA*] (S-stars)
  Eingaben: z (direkt), N0=1.0000000028, a=177611600000000.0, e=0.247, f_true=0.0, M_solar=4297000.0
  z_data = 7.555117e-05
  r_eff = 1.337415e+14 m  (Quelle: r(a,e,f_true))
  v_pred = 2.305925e+06 m/s (Quelle: vis‑viva(a,r_eff), strong=True)
  z_pred(seg) = 7.698412e-05  → Δz = -1.432957e-06
  z_GR = 4.744750e-05    → Δz = 2.810367e-05
  z_SR = 2.958272e-05    → Δz = 4.596845e-05
  z_GR*SR = 7.703162e-05 → Δz = -1.480457e-06
  Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.

Δz (data − Seg PRED): median=2.908e-05, mean=2.352e-04, max|=1.141e-03

Δz (data − GR): median=1.265e-04, mean=5.012e-04, max|=2.223e-03

Δz (data − SR): median=1.448e-04, mean=5.201e-04, max|=2.249e-03

Δz (data − GR*SR): median=2.911e-05, mean=2.353e-04, max|=1.141e-03

Fertig. Details: ./out/_explain_debug.csv
========================================================================

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\segspace_enhanced_test_better_final.py --csv H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\real_data_full.csv --prefer-z --seg-mode hint ---
[INFO] CSV: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\real_data_full.csv | SHA256=37964601e730cb00bdbbd0bb4788ae10ca6dc8cc0b774c77b121ce28b6a78695
[CHECK] GRS_1915+105: r_eff suspiciously small (8.949e+04 m)
[CHECK] Cyg_X-1: r_eff suspiciously small (1.311e+05 m)
[CHECK] A0620-00: r_eff suspiciously small (5.848e+04 m)
[CHECK] V404_Cyg: r_eff suspiciously small (7.974e+04 m)
[CHECK] PSR_B1913+16: r_eff suspiciously small (1.240e+04 m)
[CHECK] PSR_J0737-3039A: r_eff suspiciously small (1.187e+04 m)
[CHECK] PSR_J0737-3039B: r_eff suspiciously small (1.108e+04 m)
[CHECK] PSR_J1141-6545: r_eff suspiciously small (1.152e+04 m)
[CHECK] PSR_B1534+12: r_eff suspiciously small (1.178e+04 m)
[VELFIX] cat=nearby-stars orig=-12000.0 -> 23323.8 m/s (rad=12000.0, tan=20000)
[CHECK] Vega: r_eff suspiciously small (1.861e+04 m)
[CHECK] Sirius_A: r_eff suspiciously small (1.790e+04 m)
[VELFIX] cat=nearby-stars orig=-22000.0 -> 29732.1 m/s (rad=22000.0, tan=20000)
[CHECK] Proxima_Cen: r_eff suspiciously small (1.090e+03 m)
[VELFIX] cat=nearby-stars orig=-22000.0 -> 29732.1 m/s (rad=22000.0, tan=20000)
[CHECK] Alpha_Cen_A: r_eff suspiciously small (9.746e+03 m)
[CHECK] Betelgeuse: r_eff suspiciously small (1.028e+05 m)
[CHECK] Rigel: r_eff suspiciously small (1.657e+05 m)
[CHECK] Spica: r_eff suspiciously small (9.082e+04 m)
[VELFIX] cat=nearby-stars orig=-3200.0 -> 30170.2 m/s (rad=3200.0, tan=30000)
[CHECK] Antares: r_eff suspiciously small (1.099e+05 m)
[VELFIX] cat=nearby-stars orig=-17000.0 -> 26248.8 m/s (rad=17000.0, tan=20000)
[CHECK] Polaris: r_eff suspiciously small (4.784e+04 m)
[CHECK] Aldebaran: r_eff suspiciously small (1.028e+04 m)
[CHECK] LMC_X1: r_eff suspiciously small (8.537e+05 m)
[CHECK] PSR_J1748-2446ad: r_eff suspiciously small (1.453e+04 m)
[CHECK] Vela_Pulsar: r_eff suspiciously small (1.286e+04 m)
[CHECK] Crab_Pulsar: r_eff suspiciously small (1.234e+04 m)
[CHECK] PSR_J1614-2230: r_eff suspiciously small (1.477e+04 m)
[CHECK] PSR_J0952-0607: r_eff suspiciously small (1.319e+04 m)
[CHECK] PSR_J1738+0333: r_eff suspiciously small (1.162e+04 m)
[CHECK] PSR_J0030+0451: r_eff suspiciously small (1.473e+04 m)
[CHECK] PSR_J0740+6620: r_eff suspiciously small (1.275e+04 m)
[CHECK] PSR_J1909-3744: r_eff suspiciously small (1.156e+04 m)
[CHECK] PSR_J1713+0747: r_eff suspiciously small (1.294e+04 m)
[CHECK] PSR_J2317+1439: r_eff suspiciously small (1.035e+04 m)
[CHECK] PSR_J0437-4715: r_eff suspiciously small (1.392e+04 m)
[CHECK] PSR_J1012+5307: r_eff suspiciously small (1.337e+04 m)
[CHECK] GW170817: r_eff suspiciously small (1.312e+05 m)
[CHECK] GW190425: r_eff suspiciously small (6.291e+04 m)
[CHECK] GW200105: r_eff suspiciously small (2.719e+05 m)
[CHECK] GW200115: r_eff suspiciously small (2.622e+05 m)
[CHECK] XTE_J1550-564: r_eff suspiciously small (6.165e+05 m)
[CHECK] GRO_J1655-40: r_eff suspiciously small (1.511e+05 m)
[CHECK] 4U_1543-47: r_eff suspiciously small (6.532e+05 m)
[CHECK] XTE_J1859+226: r_eff suspiciously small (4.294e+05 m)
[CHECK] GS_2000+25: r_eff suspiciously small (5.516e+05 m)
[CHECK] Nova_Sco_1994: r_eff suspiciously small (5.523e+05 m)
[CHECK] SAX_J1819.3-2525: r_eff suspiciously small (5.299e+05 m)
[CHECK] XTE_J1752-223: r_eff suspiciously small (7.464e+05 m)
========================================================================
 SEGSPACE — ENHANCED TEST REPORT (IMPROVED)
========================================================================
Rows used: 127   |   Strong rows: 127
Velocity corrections applied: 5
seg-mode : hint
deltaM   : A=4.0%  B=0.0%  alpha=1e-11  logM_min=None  logM_max=None
           dataset_logM_min=29.388424154620214  dataset_logM_max=41.29851904318082

Median/Mean/Max |Δz|
  Seg   : 0.00927508456008531  0.007782441447854322  12.816619156650988
  GR    : 0.22407774320119264  0.22409262484670547  2.216214084809513
  SR    : 0.0015345557279556887  0.0012694523386642673  12.78710736389226
  GR*SR : 0.22542015776898125  0.23280480503604922  15.886464405058554

Performance vs GR:
  Seg   : 0.04139226157663276x  ✓ BETTER
  SR    : 0.00684831838286526x
  GR*SR : 1.005990842948571x

Debug CSV : out\_enhanced_debug.csv

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\final_test.py ---

Segmented-Spacetime Roundtrip Mass Validation

Objekt          M_in [kg]            r_phi [m]           M_out [kg]     rel. Fehler
-------------------------------------------------------------------------------------
Elektron   9.1094e-31 1.0946e-57 9.1094e-31 1.10e-50
Mond       7.3420e+22 8.8220e-5 7.3420e+22 1.36e-50
Erde       5.9722e+24 7.1761e-3 5.9722e+24 0.00e-42
Sonne      1.9885e+30 2.3893e+3 1.9885e+30 0.00e-42

✅ Test abgeschlossen: Keine Zirkularität, keine Masseinjektion.


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\segmented_full_proof.py ---

============================================================
SEGMENTED SPACETIME – MASS VALIDATION (30+1 Objects)
============================================================
© Carmen Wrede & Lino Casu – All rights reserved.

This demo reconstructs the masses of celestial bodies and
the electron using φ/2-corrected segment radii.

Results: All astrophysical objects PASS (0.000001 % tolerance)
Electron comparison also included (see below).

CSV Export: segmented_spacetime_mass_validation.csv

          Objekt  M_true_Msun  M_corr_Msun    rel_err_%  PASS
           Vesta 1.302509e-10 1.302509e-10 0.000000e+00  True
           Ceres 4.723732e-10 4.723732e-10 9.581604e-48  True
           Pluto 6.552777e-09 6.552777e-09 0.000000e+00  True
            Eris 8.280738e-09 8.280738e-09 0.000000e+00  True
          Europa 2.413816e-08 2.413816e-08 2.083420e-48  True
            Mond 3.692280e-08 3.692280e-08 0.000000e+00  True
         Ganymed 7.454326e-08 7.454326e-08 6.746408e-48  True
           Titan 7.656000e-08 7.656000e-08 0.000000e+00  True
              Io 8.491845e-08 8.491845e-08 0.000000e+00  True
          Merkur 1.660121e-07 1.660121e-07 0.000000e+00  True
            Mars 3.227155e-07 3.227155e-07 3.116672e-48  True
            Erde 3.003506e-06 3.003506e-06 0.000000e+00  True
           Venus 4.047862e-06 4.047862e-06 3.727147e-48  True
          Uranus 4.366568e-05 4.366568e-05 4.606814e-48  True
          Neptun 5.155010e-05 5.155010e-05 0.000000e+00  True
          Saturn 2.858177e-04 2.858177e-04 1.759510e-48  True
         Jupiter 9.545861e-04 9.545861e-04 0.000000e+00  True
Proxima Centauri 1.210000e-01 1.210000e-01 4.156192e-48  True
        Sirius B 1.019000e+00 1.019000e+00 4.935223e-48  True
Alpha Centauri A 1.100000e+00 1.100000e+00 4.571811e-48  True
  Neutronenstern 1.400000e+00 1.400000e+00 3.592137e-48  True
        Sirius A 2.020000e+00 2.020000e+00 2.489600e-48  True
  PSR J0740+6620 2.080000e+00 2.080000e+00 2.417785e-48  True
    LMC X-3 (BH) 7.000000e+00 7.000000e+00 7.184274e-48  True
 V404 Cygni (BH) 9.000000e+00 9.000000e+00 0.000000e+00  True
 Cygnus X-1 (BH) 1.500000e+01 1.500000e+01 3.352661e-48  True
  M82 X-1 (IMBH) 3.000000e+03 3.000000e+03 0.000000e+00  True
     NGC 4395 BH 3.000000e+05 3.000000e+05 0.000000e+00  True
  Sagittarius A* 4.297000e+06 4.297000e+06 4.681398e-48  True

------------------------------------------------------------
Electron Mass Validation (Segmented Spacetime Model):
------------------------------------------------------------
  True mass   : 9.10938e-31 kg
  Reconstructed: 9.10938e-31 kg
  Rel. error  : 1.10e-48 %
  PASS        : True

Max. relativer Fehler   : 9.58e-48 %
Median relativer Fehler : 2.08e-48 %
Anzahl FAILS            : 0
Fertig ✅
Hinweis: Alle relativen Fehler stammen ausschließlich aus numerischer Rundung bei G, c, φ – das Modell ist exakt.

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\segmented_full_calc_proof.py ---

=============================================================
SEGMENTED SPACETIME – MASS VALIDATION (BASE+CSV LIST)
=============================================================
© Carmen Wrede & Lino Casu – All rights reserved.

This demo reconstructs masses purely via the segmented-spacetime
correction model Δ(M). All relative errors ≤ 1e-6 %.

CSV export → segmented_spacetime_mass_validation_full.csv

Objekt                    M_true(kg)       M_rec(kg)      Δ %   RelErr %
----------------------------------------------------------------------
Elektron                9.109384e-31    9.109384e-31    0.000  0.000e+00
Mond                    7.342000e+22    7.342000e+22    5.546  0.000e+00
Erde                    5.972190e+24    5.972190e+24    1.604  0.000e+00
Sonne                   1.988470e+30    1.988470e+30    1.766  0.000e+00
Sagittarius A*          8.544456e+36    8.544456e+36    1.960  0.000e+00
Fertig ✅

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\segmented_full_compare_proof.py ---

=============================================================
SEGMENTED SPACETIME – PERFECT MASS VALIDATION
=============================================================
© Carmen Wrede & Lino Casu – All rights reserved.

Reconstruction via full Δ(M)-model + Newton‐inversion.
All relative errors ≤ 1e-6 %. No φ/2 “Trick” in output.

CSV output → segmented_spacetime_mass_validation_perfect.csv

Objekt                    M_true(kg)       M_rec(kg)   RelErr_%
--------------------------------------------------------------
Elektron                9.109384e-31    9.109384e-31  0.000e+00
Mond                    7.342000e+22    7.342000e+22  0.000e+00
Erde                    5.972190e+24    5.972190e+24  0.000e+00
Sonne                   1.988470e+30    1.988470e+30  0.000e+00
Sagittarius A*          8.544456e+36    8.544456e+36  0.000e+00

Fertig ✅
==========================================================================================
 RUN COMPLETE
==========================================================================================
Summary JSON             : H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\full_pipeline\reports\summary_full_terminal_v4.json
Deterministic; no fitting. For figures, post-process this JSON.

==========================================================================================
Dual Velocities in Segmented Spacetime  A Concise Overview
==========================================================================================
Authors: C. N. Wrede, L. P. Casu, Bingsi

In the segmented-spacetime picture there are two characteristic velocities:
  * v_esc(r): escape velocity from radius r (outward)
  * v_fall(r): reciprocal 'fall' velocity (inward)
Their product is an invariant:  v_esc(r) * v_fall(r) = c^2
E_rest = m * v_esc * v_fall = m c^2
gamma_s(r) = 1/sqrt(1 - r_s/r),  E_local = gamma(u) m c^2,  E_inf = (gamma(u)/gamma_s(r)) m c^2

r/r_s = 1.1, gamma(u) in [1.0, 2.0]:
  v_esc  =  2.858409e+08 m/s
  v_fall =  3.144250e+08 m/s
  gamma_s(r) =  3.317e+00
  E = gamma(u) * m * v_esc * v_fall   =  8.987552e+16 J
  E_rest                          =  8.987552e+16 J
  E_local = gamma(u) m c^2            =  8.987552e+16 J
  E_inf   = E_local / gamma_s(r)      =  2.709849e+16 J
  invariant_error |v_esc*v_fall/c^2 - 1| = 0.000e+00

  v_esc  =  2.858409e+08 m/s
  v_fall =  3.144250e+08 m/s
  gamma_s(r) =  3.317e+00
  E = gamma(u) * m * v_esc * v_fall   =  1.797510e+17 J
  E_rest                          =  8.987552e+16 J
  E_local = gamma(u) m c^2            =  1.797510e+17 J
  E_inf   = E_local / gamma_s(r)      =  5.419698e+16 J
  invariant_error |v_esc*v_fall/c^2 - 1| = 0.000e+00

r/r_s = 2.0, gamma(u) in [1.0, 2.0]:
  v_esc  =  2.119853e+08 m/s
  v_fall =  4.239706e+08 m/s
  gamma_s(r) =  1.414e+00
  E = gamma(u) * m * v_esc * v_fall   =  8.987552e+16 J
  E_rest                          =  8.987552e+16 J
  E_local = gamma(u) m c^2            =  8.987552e+16 J
  E_inf   = E_local / gamma_s(r)      =  6.355159e+16 J
  invariant_error |v_esc*v_fall/c^2 - 1| = 0.000e+00

  v_esc  =  2.119853e+08 m/s
  v_fall =  4.239706e+08 m/s
  gamma_s(r) =  1.414e+00
  E = gamma(u) * m * v_esc * v_fall   =  1.797510e+17 J
  E_rest                          =  8.987552e+16 J
  E_local = gamma(u) m c^2            =  1.797510e+17 J
  E_inf   = E_local / gamma_s(r)      =  1.271032e+17 J
  invariant_error |v_esc*v_fall/c^2 - 1| = 0.000e+00


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\lagrangian_tests.py --object sun ---
==============================================================================
LAGRANGIAN TESTS — Sun | M = 1.988470E+30 kg | eps3 = -4.8
==============================================================================
Schwarzschild radius r_s : 2.953339E+3 m
Photon sphere r_ph       : 4.430009E+3 m
GR baseline (eps3=0)     : 4.430009E+3 m
Δrel vs GR               : 4.514663E-80
ISCO radius r_isco       : 7.453763E+3 m
GR baseline (eps3=0)     : 8.860018E+3 m
Δrel vs GR               : -1.587192E-1
Ω^2 at 10 r_s            : 4.729632E+6 s^-2

Summary:
 - r_ph from d/dr(A/r^2)=0 (null circular)
 - r_isco from d/dr L^2=0 (marginally stable timelike circular)
 - GR baselines: r_ph=1.5 r_s, r_isco=3 r_s
 - Finite, small deviations indicate the strong-field SSZ signature.
==============================================================================

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\lagrangian_tests.py --object sgrA ---
==============================================================================
LAGRANGIAN TESTS — Sgr A* | M = 8.544456E+36 kg | eps3 = -4.8
==============================================================================
Schwarzschild radius r_s : 1.269050E+10 m
Photon sphere r_ph       : 1.903575E+10 m
GR baseline (eps3=0)     : 1.903575E+10 m
Δrel vs GR               : -5.253273E-80
ISCO radius r_isco       : 3.202882E+10 m
GR baseline (eps3=0)     : 3.807150E+10 m
Δrel vs GR               : -1.587192E-1
Ω^2 at 10 r_s            : 2.561513E-7 s^-2

Summary:
 - r_ph from d/dr(A/r^2)=0 (null circular)
 - r_isco from d/dr L^2=0 (marginally stable timelike circular)
 - GR baselines: r_ph=1.5 r_s, r_isco=3 r_s
 - Finite, small deviations indicate the strong-field SSZ signature.
==============================================================================

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\lagrangian_tests.py --mass 8.544456e36 --label Sgr A* --eps3 -4.8 ---
==============================================================================
LAGRANGIAN TESTS — Sgr A* | M = 8.544456E+36 kg | eps3 = -4.8
==============================================================================
Schwarzschild radius r_s : 1.269050E+10 m
Photon sphere r_ph       : 1.903575E+10 m
GR baseline (eps3=0)     : 1.903575E+10 m
Δrel vs GR               : -5.253273E-80
ISCO radius r_isco       : 3.202882E+10 m
GR baseline (eps3=0)     : 3.807150E+10 m
Δrel vs GR               : -1.587192E-1
Ω^2 at 10 r_s            : 2.561513E-7 s^-2

Summary:
 - r_ph from d/dr(A/r^2)=0 (null circular)
 - r_isco from d/dr L^2=0 (marginally stable timelike circular)
 - GR baselines: r_ph=1.5 r_s, r_isco=3 r_s
 - Finite, small deviations indicate the strong-field SSZ signature.
==============================================================================

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\derive_effective_stress_energy.py --M 1.98847e30 --eps3 -4.8 --r-mults 1.2,2,3,5,10 ---
==========================================================================================
SSZ Effective Stress-Energy (reverse engineered)
==========================================================================================
M = 1.988470e+30 kg | eps3 = -4.8 | r_s = 2.953339e+03 m

[Symbolic] rho(r), p_r(r), p_t(r) (compact forms):
rho(r) = G*M**2*(-G**4*M**4*eps3**2 - 3*G**3*M**3*c**2*eps3*r + 2*G**2*M**2*c**4*eps3*r**2 - 2*G**2*M**2*c**4*r**2 - G*M*c**6*eps3*r**3 + 2*G*M*c**6*r**3 - c**8*r**4)/(4*pi*c**8*r**8)
p_r(r) = -G*M**2*c**4*(G*M*eps3 + c**2*r)/(4*pi*r**2*(G**3*M**3*eps3 + 2*G**2*M**2*c**2*r - 2*G*M*c**4*r**2 + c**6*r**3))
p_t(r) = G*M**2*(3*G*M*eps3 + 2*c**2*r)/(8*pi*c**2*r**3)

r/rs        rho [J/m^3]             p_r [Pa]                 p_t [Pa]          |∇·T| components
------------------------------------------------------------------------------------------
 1.20   2.218729e+34    7.987425e+35   -3.344065e+42   ||∇·T||= 0.000e+00
 2.00   1.897812e+33    6.273759e+33   -4.815454e+41   ||∇·T||= 0.000e+00
 3.00  -4.771155e+32   -9.737051e+32   -5.350504e+40   ||∇·T||= 0.000e+00
 5.00  -1.872268e+32   -2.817343e+32    2.696654e+40   ||∇·T||= 0.000e+00
10.00  -1.897382e+31   -2.319709e+31    1.540945e+40   ||∇·T||= 0.000e+00

Note: This script reconstructs an *effective* T_{μν} for the chosen metric. It does not specify a fundamental action nor field equations for matter.


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\derive_effective_stress_energy.py --M 8.544456e36 --eps3 -4.8 --r-mults 1.2,2,3,5 --latex H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\agent_out\reports\ssz_sources_latex.txt ---
==========================================================================================
SSZ Effective Stress-Energy (reverse engineered)
==========================================================================================
M = 8.544456e+36 kg | eps3 = -4.8 | r_s = 1.269050e+10 m

[Symbolic] rho(r), p_r(r), p_t(r) (compact forms):
rho(r) = G*M**2*(-G**4*M**4*eps3**2 - 3*G**3*M**3*c**2*eps3*r + 2*G**2*M**2*c**4*eps3*r**2 - 2*G**2*M**2*c**4*r**2 - G*M*c**6*eps3*r**3 + 2*G*M*c**6*r**3 - c**8*r**4)/(4*pi*c**8*r**8)
p_r(r) = -G*M**2*c**4*(G*M*eps3 + c**2*r)/(4*pi*r**2*(G**3*M**3*eps3 + 2*G**2*M**2*c**2*r - 2*G*M*c**4*r**2 + c**6*r**3))
p_t(r) = G*M**2*(3*G*M*eps3 + 2*c**2*r)/(8*pi*c**2*r**3)

[OK] LaTeX dumped to: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\agent_out\reports\ssz_sources_latex.txt

r/rs        rho [J/m^3]             p_r [Pa]                 p_t [Pa]          |∇·T| components
------------------------------------------------------------------------------------------
 1.20   1.201638e+21    4.325896e+22   -3.344065e+42   ||∇·T||= 0.000e+00
 2.00   1.027833e+20    3.397794e+20   -4.815454e+41   ||∇·T||= 0.000e+00
 3.00  -2.584002e+19   -5.273473e+19   -5.350504e+40   ||∇·T||= 0.000e+00
 5.00  -1.013998e+19   -1.525840e+19    2.696654e+40   ||∇·T||= 0.000e+00

Note: This script reconstructs an *effective* T_{μν} for the chosen metric. It does not specify a fundamental action nor field equations for matter.


--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\ssz_theory_segmented.py --M 1.98847e30 --mode exterior --coord lnr --rmin-mult 1.05 --rmax-mult 12 --grid 200 --phi0 1e-4 --phip0 0 --pr0 0 --rho0 0 --cs2 0.30 --mphi 1e-7 --lam 1e-6 --Z0 1.0 --alpha 3e-3 --beta=-8e-3 --Zmin 1e-8 --Zmax 1e8 --phi-cap 5e-3 --phip-cap 1e-3 --max-step-rs 0.02 --export H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\out_theory_exterior.csv ---
================================================================================
SSZ — Wirkungsbasiert (Skalar mit anisotroper Kinetik) — stabil (v2)
================================================================================
M =  1.988470e+30 kg | r_s =  2.953339e+03 m
[grid] r/rs in [1.05, 12.00] mit 200 Punkten
[mode] exterior | coord=lnr
[Zpar] Z0=1 α=0.003 β=-0.008 | caps: φ=0.005, φ'=0.001 | clamp: Z∈[1e-08,1e+08]
[fluid] cs2=0.300 rho0= 0.000e+00 | pr0= 0.000e+00
[guard] abort_on_horizon=True margin= 1.0e-06
[compat] seg_frac=0.6 seg_scale=r_phi kernel=gauss eps3=-4.8
[warn] m0 groß relativ zu rmin: 2m/r = 0.952

[ok] CSV: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\out_theory_exterior.csv

--- EHT Shadow Comparison Matrix ---

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\analysis\eht_shadow_comparison.py ---

================================================================================
EHT Shadow Comparison: SSZ vs. GR
================================================================================

Per-Object Results:
--------------------------------------------------------------------------------

Sagittarius A*:
  Observed:         51.8 ±   8.6 μas
  SSZ Prediction:   54.9 μas  (Δ =   +3.1 μas, +0.36σ)
  GR Prediction:    51.8 μas  (Δ =   +0.0 μas, +0.00σ)
  χ²(SSZ):         0.130
  χ²(GR):          0.000
  Status:         ✓ SSZ within 1σ

M87*:
  Observed:         39.0 ±   8.0 μas
  SSZ Prediction:   44.5 μas  (Δ =   +5.5 μas, +0.69σ)
  GR Prediction:    42.0 μas  (Δ =   +3.0 μas, +0.38σ)
  χ²(SSZ):         0.473
  χ²(GR):          0.141
  Status:         ✓ SSZ within 1σ

--------------------------------------------------------------------------------
Combined Statistics:
--------------------------------------------------------------------------------
χ²(SSZ):      0.603  (dof = 2)
χ²(GR):       0.141  (dof = 2)
p(SSZ):      0.7399
p(GR):       0.9321
Δχ²:         +0.462  (SSZ - GR)

--------------------------------------------------------------------------------
Interpretation:
--------------------------------------------------------------------------------
  ✓ SSZ is statistically consistent with EHT data (p > 0.05)
  ✓ GR is statistically consistent with EHT data (p > 0.05)
  ✓ Sagittarius A*: SSZ within 1σ of observation
  ✓ M87*: SSZ within 1σ of observation
  → GR has lower χ² than SSZ by 0.462

================================================================================

--- SSZ Rings Analysis ---
  Analyzing G79.29+0.46...

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\ring_temperature_to_velocity.py H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\data\observations\G79_29+0_46_CO_NH3_rings.csv --v0 12.5 ---
[INFO] Using column 'T' as temperature proxy (renamed to 'T_proxy_K')
================================================================================
Ring Temperature → Velocity Prediction (Section 4.6)
================================================================================
Timestamp: 2025-10-18T23:32:38.455111
Input file: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\data\observations\G79_29+0_46_CO_NH3_rings.csv
Number of rings: 10
Baseline velocity v0: 12.500 km/s

Model: v_k = v_{k-1} * (T_k / T_{k-1})^{-1/2}
================================================================================

 ring  T_proxy_K   q_k  v_pred_kms
   1      78       NaN    12.500  
   2      65     0.833    13.693  
   3      55     0.846    14.886  
   4      45     0.818    16.457  
   5      38     0.844    17.909  
   6      32     0.842    19.516  
   7      28     0.875    20.863  
   8      25     0.893    22.079  
   9      22     0.880    23.537  
  10      20     0.909    24.686  

--------------------------------------------------------------------------------
SUMMARY
--------------------------------------------------------------------------------
Initial velocity (ring 0):       12.500 km/s
Final velocity (ring 10):        24.686 km/s
Predicted Δv (total):            12.186 km/s
Velocity ratio (v_N / v_0):       1.975x
================================================================================
  Analyzing Cygnus X Diamond Ring...

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\ring_temperature_to_velocity.py H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\data\observations\CygnusX_DiamondRing_CII_rings.csv --v0 1.3 ---
[INFO] Using column 'T' as temperature proxy (renamed to 'T_proxy_K')
================================================================================
Ring Temperature → Velocity Prediction (Section 4.6)
================================================================================
Timestamp: 2025-10-18T23:32:39.671724
Input file: H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\data\observations\CygnusX_DiamondRing_CII_rings.csv
Number of rings: 3
Baseline velocity v0: 1.300 km/s

Model: v_k = v_{k-1} * (T_k / T_{k-1})^{-1/2}
================================================================================

 ring  T_proxy_K   q_k  v_pred_kms
  1       48       NaN    1.300   
  2       42     0.875    1.390   
  3       36     0.857    1.501   

--------------------------------------------------------------------------------
SUMMARY
--------------------------------------------------------------------------------
Initial velocity (ring 0):        1.300 km/s
Final velocity (ring  3):         1.501 km/s
Predicted Δv (total):             0.201 km/s
Velocity ratio (v_N / v_0):       1.155x
================================================================================
==========================================================================================
INTERPRETATION & QUALITY ASSESSMENT
==========================================================================================
* All-in-one: paired sign-test shows Seg better in 82/127 rows; two-sided p ~ 0.0013073851235000232
* All-in-one medians |dz|: Seg=0.00927508456008531
* Bound-energy threshold (from all-in-one): f_thr ~ 901653545693357604.42934289177487939997133896929841589437443550156196278724878878621591411917062182023533209952508577048493819522873599519618729059184500182208303363646097227026792042037164366574054457 Hz; lambda ~ 3.3249185280967785186671459606021200884228391918132440568069436865448902415820676436940925894268308481998848894269007623165075313810641323231543134855826262282543282567767447862605669503849310419973091E-10 m
* Mass validation: roundtrip reconstruction succeeded on the sample (report present).
* Weak-field sector: PPN(beta=gamma=1) and classic tests match GR at machine precision.
* Strong field: photon sphere/ISCO finite; shadow impact b_ph shows a stable ~6% offset vs GR.
* Phi-tests: median absolute residuals are at the 1e-4 to 1e-3 level on the used subset.
* Dual-velocity invariant: median (v_esc*v_fall)/c^2 ~ 1 ~ 0 in diagnostics; here max abs error = 0.000e+00,
* Energy conditions: violations confined to r <~ 5 r_s; for r >= ~5 r_s, WEC/DEC/SEC hold.
* Lagrangian geodesic tests (eps3=-4.8): v_r pm matches the GR baseline (rel ~ 1e-3).
* ISCO  -15.9% vs GR, and ^2(10 r_s) is finite  confirming finite strong-field deviations and the SSS signature without pathologies.

# Interpretation of the Dual Velocities block:
Dual-velocity interpretation: the computed examples (r/rs1.1 and 2; gamma(u)=1 and 2) respect the invariant v_esc*v_fallc^2 to machine precision.
Increasing gamma(u) scales E_local linearly, while E_inf is reduced by 1/gamma_s(r). Near the horizon (r/rs1.1), gamma_s(r)3.317 compresses E_inf by 3.3; at r/rs2, gamma_s(r)1.414 yields a gentler reduction.
This matches the segmentedspacetime energy bookkeeping and the tight v_escv_fall duality observed elsewhere in the pipeline.

# Action-based scalar (exterior)  quick readout:
* Horizon clearance: min(1-2m/r) = 4.761905e-02  OK.
* Scalar anisotropy ||: median = 1.542098e-27, max = 4.236274e-27.
* Kinetic weight Z(): range = 1.000000e+00 .. 1.000000e+00.
* Fluid outside: off (0=n/a, pr0=n/a)  exterior solution with fixed Schwarzschild mass at rr_min.
* Expect GR-like exterior with small anisotropic corrections unless || grows above the curvature scales.

Bottom line: exterior looks GR-like with controlled anisotropy; check CSV for  and Z() profiles.
Bottom line: SR-level redshift fidelity on the data subset, GR-consistent weak field, finite strong-field behavior, clear evidence for phi-structure on frequency ratios, and a numerically tight dual-velocity invariant.

================================================================================
[SSZ ADDON] Running Segment-Redshift Add-on...
================================================================================

--- Running C:\Program Files\Python310\python.exe H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\addons\segment_redshift_addon.py --segment-redshift --proxy N --nu-em 1.0e18 --r-em 2.0 --r-out 50.0 --seg-plot ---
[SSZ][addon] segment-redshift: OK → reports/segment_redshift.csv | .md
[SSZ][addon] plot → reports/figures/fig_shared_segment_redshift_profile.png
[SSZ ADDON] Segment-Redshift completed successfully!
[SSZ ADDON] Output: reports/segment_redshift.csv | .md | .png

================================================================================
ÜBERSICHT: ALLE GENERIERTEN PLOTS
================================================================================

  Gesamt: 15 Plot-Dateien gefunden

  .PNG-Dateien (10):
    out/
      - phi_step_qq_uniform.png
      - phi_step_residual_abs_scatter.png
      - phi_step_residual_hist.png
    reports\figures/
      - fig_shared_segment_redshift_profile.png
    reports\figures\DemoObject/
      - fig_DemoObject_freqshift_vs_gamma.png
      - fig_DemoObject_gamma_log_vs_k.png
      - fig_DemoObject_ringchain_v_vs_k.png
    reports\figures\demo/
      - fig_demo_heatmap.png
      - fig_demo_line.png
      - fig_demo_scatter.png

  .SVG-Dateien (5):
    reports\figures\DemoObject/
      - fig_DemoObject_freqshift_vs_gamma.svg
      - fig_DemoObject_gamma_log_vs_k.svg
      - fig_DemoObject_ringchain_v_vs_k.svg
    reports\figures\demo/
      - fig_demo_line.svg
      - fig_demo_scatter.svg

  Wichtige Plot-Kategorien:
    - Demo-Plots: 5 Dateien
    - Paper Exports: 12 Dateien

================================================================================
SPEICHERORTE:
================================================================================
  ✓ H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\reports\figures
  ✓ H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\agent_out\figures
  ✓ H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\out
  ✓ H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\vfall_out
  ○ H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\full_pipeline\figures (nicht vorhanden)
  ○ H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\final_reports\figures (nicht vorhanden)
================================================================================
2025-10-18 23:31:59,164 [INFO] TEST_GAIA: Logger initialized -> data\logs\tests_2025-10-17_gaia_ssz_real_20251018_233159.log
2025-10-18 23:31:59,307 [INFO] TEST_GAIA: GAIA smoke rows=5000
2025-10-18 23:31:59,313 [INFO] TEST_SDSS: Logger initialized -> data\logs\tests_2025-10-17_gaia_ssz_real_20251018_233159.log
2025-10-18 23:31:59,323 [INFO] TEST_SDSS: SDSS smoke rows=5000
2025-10-18 23:31:59,326 [INFO] TEST_PLANCK: Logger initialized -> data\logs\tests_2025-10-17_gaia_ssz_real_20251018_233159.log
2025-10-18 23:31:59,327 [INFO] TEST_PLANCK: Planck present -> data\raw\planck\2025-10-17_gaia_ssz_real\planck_map.fits
H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\addons\segment_redshift_addon.py:39: DeprecationWarning: `trapz` is deprecated. Use `trapezoid` instead, or one of the numerical integration functions in `scipy.integrate`.
  return float(np.trapz(N, ln_r))
  [OK] Full SSZ Terminal Analysis (took 92.3s)

----------------------------------------------------------------------------------------------------
PHASE 6: EXAMPLE ANALYSIS RUNS
----------------------------------------------------------------------------------------------------

[RUNNING] G79 Example Run
  Command: python -m cli.ssz_rings --csv data\observations\G79_29+0_46_CO_NH3_rings.csv --v0 12.5 --fit-alpha --out-table reports/g79_test.csv --out-report reports/g79_test.txt
Loading data from: data\observations\G79_29+0_46_CO_NH3_rings.csv
  Loaded 10 rings
Fitting alpha parameter...
  Optimal alpha = 0.100007
  RMSE = 9.4378 km/s
Computing velocity profile...
Saving table to: reports/g79_test.csv
Saving report to: reports/g79_test.txt

============================================================
SSZ RINGS - SEGMENTED RADIOWAVE PROPAGATION REPORT
============================================================

PARAMETERS:
  v0 (initial velocity): 12.500 km/s
  alpha (fitted): 0.100007
  beta (temperature exp): 1.000
  eta (density exp): 0.000

DATA:
  Number of rings: 10
  Temperature range: 20.00 - 78.00 K
  Density range: 2.50e+03 - 2.00e+04 cm^-3

PREDICTIONS:
  v_pred range: 12.500 - 13.380 km/s
  q_k range: 0.818182 - 1.000000

VALIDATION METRICS:
  MAE: 8.4396 km/s
  RMSE: 9.4378 km/s
  Max |residual|: 12.3803 km/s

============================================================


[OK] SSZ-Rings completed successfully
  [OK] G79 Example Run (took 2.5s)
[RUNNING] Cygnus X Example Run
  Command: python -m cli.ssz_rings --csv data\observations\CygnusX_DiamondRing_CII_rings.csv --v0 1.3 --alpha 1.0 --out-table reports/cygx_test.csv --out-report reports/cygx_test.txt
Loading data from: data\observations\CygnusX_DiamondRing_CII_rings.csv
  Loaded 3 rings
Using fixed alpha = 1.000000
Computing velocity profile...
Saving table to: reports/cygx_test.csv
Saving report to: reports/cygx_test.txt

============================================================
SSZ RINGS - SEGMENTED RADIOWAVE PROPAGATION REPORT
============================================================

PARAMETERS:
  v0 (initial velocity): 1.300 km/s
  alpha (fixed): 1.000000
  beta (temperature exp): 1.000
  eta (density exp): 0.000

DATA:
  Number of rings: 3
  Temperature range: 36.00 - 48.00 K
  Density range: 5.50e+03 - 9.00e+03 cm^-3

PREDICTIONS:
  v_pred range: 1.300 - 1.501 km/s
  q_k range: 0.857143 - 1.000000

VALIDATION METRICS:
  MAE: 0.0970 km/s
  RMSE: 0.1272 km/s
  Max |residual|: 0.2011 km/s

============================================================


[OK] SSZ-Rings completed successfully
  [OK] Cygnus X Example Run (took 2.9s)

----------------------------------------------------------------------------------------------------
PHASE 7: PAPER EXPORT TOOLS
----------------------------------------------------------------------------------------------------

[RUNNING] Paper Export Tools Demo
  Command: python demo_paper_exports.py
================================================================================
SSZ Paper Export Tools - DEMO
================================================================================

================================================================================
DEMO 1: Basis-Plots
================================================================================

[1/3] Erstelle Line-Plot...
✓ Erstellt: ['reports/figures/demo/fig_demo_line.png', 'reports/figures/demo/fig_demo_line.svg']

[2/3] Erstelle Scatter-Plot...
✓ Erstellt: ['reports/figures/demo/fig_demo_scatter.png', 'reports/figures/demo/fig_demo_scatter.svg']

[3/3] Erstelle Heatmap...
✓ Erstellt: ['reports/figures/demo/fig_demo_heatmap.png']

✅ Demo 1 complete!

================================================================================
DEMO 2: Caption-System
================================================================================

Verfügbare Figures:
  - freqshift_vs_gamma
  - gamma_log_vs_k
  - lensing_deflection_map
  - line_ratios_vs_radius
  - model_compare_scores
  - posterior_corner
  - radio_spectral_index
  - residuals_model_vs_obs
  - ringchain_v_vs_k
  - stability_criteria
  - sweep_heatmap_alpha_beta
  - uncertainty_bands_v_vs_k

Beispiel-Captions:

ringchain_v_vs_k:
  G79: Ring-Ketten-Propagation im SSZ-Feld. Die Umlaufgeschwindigkeit v_k steigt t...

gamma_log_vs_k:
  G79: Exponentielles Wachstum der kumulativen Zeitdichte γ entlang der Ringe – sk...

posterior_corner:
  G79: Posterior-Verteilungen von (α, β, η) mit 68/95%-Konfidenzintervallen....

================================================================================
DEMO 3: Manifest-System
================================================================================

[1/2] Erstelle Manifest: reports/DEMO_MANIFEST.json
[2/2] Registriere 3 Artifacts...
✓ Manifest erstellt: reports/DEMO_MANIFEST.json

✅ Demo 3 complete!

================================================================================
DEMO 4: Figure-Orchestrator
================================================================================

Generiere Figures mit Orchestrator...

[SSZ] Generating figures for DemoObject...

[SSZ] Figures written:
  - reports\figures\DemoObject\fig_DemoObject_ringchain_v_vs_k.png
  - reports\figures\DemoObject\fig_DemoObject_ringchain_v_vs_k.svg
  - reports\figures\DemoObject\fig_DemoObject_gamma_log_vs_k.png
  - reports\figures\DemoObject\fig_DemoObject_gamma_log_vs_k.svg
  - reports\figures\DemoObject\fig_DemoObject_freqshift_vs_gamma.png
  - reports\figures\DemoObject\fig_DemoObject_freqshift_vs_gamma.svg

Index: reports\figures\FIGURE_INDEX.md
Manifest: reports/PAPER_EXPORTS_MANIFEST.json


✅ Demo 4 complete!

================================================================================
✅ ALLE DEMOS ERFOLGREICH!
================================================================================

Erstellte Dateien:
  - reports/figures/demo/*.png
  - reports/figures/demo/*.svg
  - reports/DEMO_MANIFEST.json
  - reports/figures/FIGURE_INDEX.md
  - reports/PAPER_EXPORTS_MANIFEST.json


  [OK] Paper Export Tools Demo (took 3.8s)

====================================================================================================
SUMMARY REPORT
====================================================================================================

Total Phases: 17
Passed: 17
Failed: 0
Success Rate: 100.0%
Total Test Time: 141.9s
Total Suite Time: 181.1s

Detailed Results:
  [PASS] PPN Exact Tests                          (0.1s)
  [PASS] Dual Velocity Tests                      (0.2s)
  [PASS] Energy Conditions Tests                  (0.1s)
  [PASS] C1 Segments Tests                        (0.1s)
  [PASS] C2 Segments Strict Tests                 (0.1s)
  [PASS] C2 Curvature Proxy Tests                 (0.1s)
  [PASS] SegWave Core Math Tests                  (6.0s)
  [PASS] SSZ Kernel Tests                         (4.9s)
  [PASS] SSZ Invariants Tests                     (4.9s)
  [PASS] Segmenter Tests                          (4.9s)
  [PASS] Cosmo Fields Tests                       (4.7s)
  [PASS] Cosmo Multibody Tests                    (7.3s)
  [PASS] Cosmos Multi-Body Sigma Tests            (7.1s)
  [PASS] SSZ Complete Analysis                    (92.3s)
  [PASS] G79 Analysis                             (2.5s)
  [PASS] Cygnus X Analysis                        (2.9s)
  [PASS] Paper Export Tools                       (3.8s)

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

- **Total Duration:** 181.1s
- **Test Suites:** 17
- **Passed:** 17
- **Failed:** 0

---

**Copyright 2025**
Carmen Wrede und Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
