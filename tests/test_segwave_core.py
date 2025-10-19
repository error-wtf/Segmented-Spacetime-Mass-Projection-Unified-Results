"""
Unit Tests for Segwave Core Module

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ssz.segwave import (
    compute_q_factor,
    predict_velocity_profile,
    predict_frequency_track,
    compute_residuals,
    compute_cumulative_gamma
)


class TestQFactor:
    """Tests for q_k computation"""
    
    def test_temperature_only_basic(self):
        """Test q_k with temperature only, β=1
        
        Physical Meaning:
        q_k = (T_curr/T_prev)^β quantifies the energy ratio between successive rings.
        For β=1, this is simply the temperature ratio.
        """
        T_curr, T_prev, beta = 80.0, 100.0, 1.0
        q = compute_q_factor(T_curr=T_curr, T_prev=T_prev, beta=beta)
        
        print("\n" + "="*80)
        print("Q-FACTOR: Temperature Ratio (β=1)")
        print("="*80)
        print(f"Temperature:")
        print(f"  Current ring: T_curr = {T_curr:.1f} K")
        print(f"  Previous ring: T_prev = {T_prev:.1f} K")
        print(f"  β parameter: {beta:.1f}")
        print(f"\nQ-Factor Calculation:")
        print(f"  q_k = (T_curr/T_prev)^β = ({T_curr}/{T_prev})^{beta} = {q:.6f}")
        print(f"\nPhysical Interpretation:")
        print(f"  • q_k < 1 indicates cooling between rings")
        print(f"  • Energy ratio = {q:.1%} of previous ring")
        print(f"  • Velocity will scale as q_k^(-α/2)")
        print("="*80)
        
        assert q == pytest.approx(0.8, rel=1e-6)
    
    def test_temperature_with_beta(self):
        """Test q_k with custom β
        
        Physical Meaning:
        β parameter controls the temperature sensitivity.
        β > 1: Stronger temperature dependence (more sensitive)
        β < 1: Weaker temperature dependence (less sensitive)
        """
        T_curr, T_prev, beta = 80.0, 100.0, 2.0
        q = compute_q_factor(T_curr=T_curr, T_prev=T_prev, beta=beta)
        
        print("\n" + "="*80)
        print("Q-FACTOR: Temperature with β=2 (Enhanced Sensitivity)")
        print("="*80)
        print(f"Configuration:")
        print(f"  T_curr = {T_curr:.1f} K, T_prev = {T_prev:.1f} K")
        print(f"  β = {beta:.1f} (enhanced temperature sensitivity)")
        print(f"\nCalculation:")
        print(f"  q_k = ({T_curr}/{T_prev})^{beta} = {q:.6f}")
        print(f"  Compare to β=1: {0.8:.6f}")
        print(f"\nPhysical Interpretation:")
        print(f"  • β=2 amplifies temperature effect: {q:.2f} vs 0.80")
        print(f"  • Stronger cooling yields lower q_k")
        print(f"  • Results in more dramatic velocity changes")
        print("="*80)
        
        assert q == pytest.approx(0.64, rel=1e-6)  # (80/100)^2
    
    def test_temperature_and_density(self):
        """Test q_k with both T and n
        
        Physical Meaning:
        Combines temperature AND density effects:
        q_k = (T_curr/T_prev)^β × (n_curr/n_prev)^η
        
        Both temperature and density affect segment field strength.
        """
        T_curr, T_prev = 80.0, 100.0
        n_curr, n_prev = 1e5, 2e5
        beta, eta = 1.0, 0.5
        
        q = compute_q_factor(
            T_curr=T_curr, T_prev=T_prev,
            n_curr=n_curr, n_prev=n_prev,
            beta=beta, eta=eta
        )
        expected = 0.8 * (1e5 / 2e5) ** 0.5  # 0.8 * sqrt(0.5)
        
        print("\n" + "="*80)
        print("Q-FACTOR: Temperature AND Density Combined")
        print("="*80)
        print(f"Configuration:")
        print(f"  Temperature: {T_curr:.1f} K → {T_prev:.1f} K")
        print(f"  Density: {n_curr:.1e} → {n_prev:.1e} cm⁻³")
        print(f"  β = {beta:.1f}, η = {eta:.1f}")
        print(f"\nCalculation:")
        print(f"  q_T = ({T_curr}/{T_prev})^{beta} = {0.8:.6f}")
        print(f"  q_n = ({n_curr:.0e}/{n_prev:.0e})^{eta} = {(0.5)**0.5:.6f}")
        print(f"  q_k = q_T × q_n = {q:.6f}")
        print(f"\nPhysical Interpretation:")
        print(f"  • Both cooling AND density drop reduce q_k")
        print(f"  • Combined effect: q_k = {q:.3f} < 0.8 (temperature only)")
        print(f"  • Density amplifies temperature effect")
        print("="*80)
        
        assert q == pytest.approx(expected, rel=1e-6)
    
    def test_invalid_temperature_raises(self):
        """Test that negative/zero temperature raises error"""
        with pytest.raises(ValueError):
            compute_q_factor(T_curr=-10.0, T_prev=100.0)
        
        with pytest.raises(ValueError):
            compute_q_factor(T_curr=80.0, T_prev=0.0)
    
    def test_invalid_density_raises(self):
        """Test that negative/zero density raises error"""
        with pytest.raises(ValueError):
            compute_q_factor(
                T_curr=80.0, T_prev=100.0,
                n_curr=-1e5, n_prev=1e5,
                eta=0.5
            )


class TestVelocityProfile:
    """Tests for velocity profile prediction"""
    
    def test_single_shell(self):
        """Test with single shell (no propagation)
        
        Physical Meaning:
        Single ring has no predecessor → q_k = 1.0 (baseline)
        v_k = v0 (initial velocity, no change)
        This establishes the initial condition for the ring chain.
        """
        rings = np.array([1])
        T = np.array([100.0])
        v0 = 10.0
        
        df = predict_velocity_profile(rings, T, v0, alpha=1.0)
        
        print("\n" + "="*80)
        print("SINGLE RING: Initial Condition")
        print("="*80)
        print(f"Configuration:")
        print(f"  Ring 1: T = {T[0]:.1f} K")
        print(f"  Initial velocity: v₀ = {v0:.1f} km/s")
        print(f"  α parameter: 1.0")
        print(f"\nCalculation:")
        print(f"  q_1 = 1.0 (no prior ring, baseline)")
        print(f"  v_1 = v₀ × q_1^(-α/2) = {v0:.1f} × 1.0 = {v0:.1f} km/s")
        print(f"\nPredicted:")
        print(f"  q_k = {df['q_k'].iloc[0]:.6f}")
        print(f"  v_pred = {df['v_pred'].iloc[0]:.2f} km/s")
        print(f"\nPhysical Interpretation:")
        print(f"  • First ring sets baseline: v = v₀")
        print(f"  • No propagation yet (needs ≥2 rings)")
        print(f"  • This establishes initial conditions for chain")
        print("="*80)
        
        assert len(df) == 1
        assert df['v_pred'].iloc[0] == pytest.approx(v0, rel=1e-6)
        assert df['q_k'].iloc[0] == pytest.approx(1.0, rel=1e-6)
    
    def test_two_shells_alpha_one(self):
        """Test two shells with α=1
        
        Physical Meaning:
        Velocity propagates between rings via v_k = v_{k-1} × q_k^(-α/2).
        This is the core SSZ ring velocity prediction formula.
        """
        rings = np.array([1, 2])
        T = np.array([100.0, 80.0])
        v0 = 10.0
        alpha = 1.0
        
        df = predict_velocity_profile(rings, T, v0, alpha=alpha)
        
        # q_2 = 80/100 = 0.8
        # v_2 = v_1 * q_2^(-0.5) = 10.0 * 0.8^(-0.5)
        q_2 = 0.8
        expected_v2 = 10.0 * (q_2 ** (-0.5))
        
        print("\n" + "="*80)
        print("SSZ RING VELOCITY: Two-Shell Propagation")
        print("="*80)
        print(f"Configuration:")
        print(f"  Ring 1: T = {T[0]:.1f} K, v = {v0:.1f} km/s (initial)")
        print(f"  Ring 2: T = {T[1]:.1f} K")
        print(f"  α parameter: {alpha:.1f}")
        print(f"\nVelocity Propagation:")
        print(f"  q_2 = T_2/T_1 = {T[1]}/{T[0]} = {q_2:.6f}")
        print(f"  v_2 = v_1 × q_2^(-α/2)")
        print(f"  v_2 = {v0:.1f} × {q_2:.6f}^(-{alpha/2:.1f})")
        print(f"  v_2 = {expected_v2:.4f} km/s")
        print(f"\nPredicted Velocity:")
        print(f"  v_pred(ring 2) = {df['v_pred'].iloc[1]:.4f} km/s")
        print(f"\nPhysical Interpretation:")
        print(f"  • Cooler ring → Higher velocity ({expected_v2:.4f} > {v0:.1f})")
        print(f"  • SSZ predicts velocity increase of {(expected_v2/v0 - 1)*100:.1f}%")
        print(f"  • Consistent with flat rotation curves")
        print("="*80)
        
        assert df['q_k'].iloc[1] == pytest.approx(0.8, rel=1e-6)
        assert df['v_pred'].iloc[1] == pytest.approx(expected_v2, rel=1e-6)
    
    def test_deterministic_chain(self):
        """Test deterministic 5-shell sequence
        
        Physical Meaning:
        Velocity propagates through 5 rings with decreasing temperature.
        Each ring amplifies velocity: v_k+1 = v_k × q_k^(-α/2)
        """
        rings = np.array([1, 2, 3, 4, 5])
        T = np.array([100.0, 90.0, 80.0, 70.0, 60.0])
        v0 = 12.5
        alpha = 1.0
        
        df = predict_velocity_profile(rings, T, v0, alpha=alpha)
        
        print("\n" + "="*80)
        print("5-RING CHAIN: Temperature Gradient")
        print("="*80)
        print(f"Ring Evolution:")
        for i in range(5):
            print(f"  Ring {i+1}: T = {df['T'].iloc[i]:5.1f} K, q_k = {df['q_k'].iloc[i]:.4f}, v = {df['v_pred'].iloc[i]:.2f} km/s")
        
        velocities = df['v_pred'].values
        v_increase = (velocities[-1] / velocities[0] - 1) * 100
        
        print(f"\nVelocity Evolution:")
        print(f"  v_initial = {velocities[0]:.2f} km/s")
        print(f"  v_final = {velocities[-1]:.2f} km/s")
        print(f"  Total increase: {v_increase:.1f}%")
        print(f"\nPhysical Interpretation:")
        print(f"  • Cooling trend: T drops {T[0]-T[-1]:.0f} K over 5 rings")
        print(f"  • Velocity amplification: {v_increase:.1f}% increase")
        print(f"  • Monotonic rise consistent with flat rotation curves")
        print("="*80)
        
        # Check monotonic increase in velocity (T decreasing)
        assert np.all(np.diff(velocities) > 0), "Velocity should increase as T decreases"
        
        # Check DataFrame structure
        assert list(df.columns) == ['ring', 'T', 'q_k', 'v_pred']
        assert len(df) == 5
    
    def test_alpha_zero_constant_velocity(self):
        """Test α=0 gives constant velocity (no segmentation)
        
        Physical Meaning:
        α=0 means NO segment field effect.
        v_k = v0 for all k (velocity doesn't propagate)
        This is the classical (non-SSZ) limit.
        """
        rings = np.array([1, 2, 3])
        T = np.array([100.0, 80.0, 60.0])
        v0 = 15.0
        
        df = predict_velocity_profile(rings, T, v0, alpha=0.0)
        
        print("\n" + "="*80)
        print("α=0 LIMIT: No Segmentation (Classical)")
        print("="*80)
        print(f"Configuration:")
        print(f"  α = 0.0 (no SSZ effect)")
        print(f"  Temperature varies: {T[0]:.0f} → {T[-1]:.0f} K")
        print(f"\nVelocities:")
        for i in range(3):
            print(f"  Ring {i+1}: T = {T[i]:5.1f} K, v = {df['v_pred'].iloc[i]:.2f} km/s")
        print(f"\nPhysical Interpretation:")
        print(f"  • α=0 ⇒ No segment field contribution")
        print(f"  • All velocities = {v0:.1f} km/s (constant)")
        print(f"  • Classical limit: temperature has no effect")
        print(f"  • This is what GR/Newtonian gravity predicts")
        print("="*80)
        
        # All velocities should equal v0 when α=0
        assert np.allclose(df['v_pred'].values, v0, rtol=1e-6)
    
    def test_with_density(self):
        """Test velocity profile with density included
        
        Physical Meaning:
        Both temperature AND density affect q_k.
        q_k = (T_k/T_{k-1})^β × (n_k/n_{k-1})^η
        Combined effect amplifies velocity changes.
        """
        rings = np.array([1, 2, 3])
        T = np.array([100.0, 90.0, 80.0])
        n = np.array([1e5, 8e4, 6e4])
        v0 = 10.0
        
        df = predict_velocity_profile(
            rings, T, v0,
            alpha=1.0,
            n=n,
            beta=1.0,
            eta=0.3
        )
        
        print("\n" + "="*80)
        print("TEMPERATURE + DENSITY: Combined Effect")
        print("="*80)
        print(f"Configuration:")
        print(f"  β = 1.0 (temperature exponent)")
        print(f"  η = 0.3 (density exponent)")
        print(f"  α = 1.0")
        print(f"\nRing Evolution:")
        for i in range(3):
            print(f"  Ring {i+1}: T = {df['T'].iloc[i]:5.1f} K, n = {df['n'].iloc[i]:.1e} cm⁻³, v = {df['v_pred'].iloc[i]:.2f} km/s")
        print(f"\nPhysical Interpretation:")
        print(f"  • Both T and n decrease across rings")
        print(f"  • Combined q_k = (T_k/T_prev)^β × (n_k/n_prev)^η")
        print(f"  • Density drop amplifies temperature effect")
        print(f"  • Results in stronger velocity increase")
        print("="*80)
        
        assert 'n' in df.columns
        assert len(df) == 3
    
    def test_mismatched_lengths_raises(self):
        """Test that mismatched array lengths raise error"""
        rings = np.array([1, 2, 3])
        T = np.array([100.0, 80.0])  # Wrong length
        
        with pytest.raises(ValueError):
            predict_velocity_profile(rings, T, 10.0)


class TestFrequencyTrack:
    """Tests for frequency tracking"""
    
    def test_single_gamma(self):
        """Test frequency shift with single gamma
        
        Physical Meaning:
        Photon frequency redshifts when passing through segment fields:
        ν_out = ν_in × γ^(-1/2)
        Higher γ → Lower frequency (redshift)
        """
        nu_in = 1e12  # 1 THz
        gamma_series = np.array([2.0])
        
        nu_out = predict_frequency_track(nu_in, gamma_series)
        expected = nu_in * (2.0 ** (-0.5))
        
        print("\n" + "="*80)
        print("FREQUENCY REDSHIFT: Single γ")
        print("="*80)
        print(f"Input: ν_in = {nu_in:.3e} Hz (1 THz)")
        print(f"Segment field: γ = 2.0")
        print(f"\nRedshift:")
        print(f"  ν_out = ν_in × γ^(-1/2)")
        print(f"  ν_out = {nu_out.iloc[0]:.3e} Hz")
        print(f"  Redshift z = Δν/ν = {(nu_in-nu_out.iloc[0])/nu_out.iloc[0]:.3f}")
        print(f"\nPhysical Interpretation:")
        print(f"  • Photons lose energy in segment field")
        print(f"  • Observable as spectral line shift")
        print(f"  • Analogous to gravitational redshift")
        print("="*80)
        
        assert nu_out.iloc[0] == pytest.approx(expected, rel=1e-6)
    
    def test_frequency_decreases_with_gamma(self):
        """Test that frequency decreases as gamma increases
        
        Physical Meaning:
        Stronger segment fields (higher γ) cause more redshift.
        ν_out ∝ γ^(-1/2), so increasing γ → decreasing ν
        """
        nu_in = 1e12
        gamma_series = np.array([1.0, 1.2, 1.5, 2.0])
        
        nu_out = predict_frequency_track(nu_in, gamma_series)
        
        print("\n" + "="*80)
        print("FREQUENCY EVOLUTION: γ Sequence")
        print("="*80)
        print(f"Input: ν_in = {nu_in:.3e} Hz")
        print(f"\nFrequency vs γ:")
        for i, g in enumerate(gamma_series):
            print(f"  γ = {g:.1f} → ν = {nu_out.iloc[i]:.3e} Hz")
        print(f"\nMonotonicity:")
        print(f"  All Δν < 0: {np.all(np.diff(nu_out.values) < 0)}")
        print(f"\nPhysical Interpretation:")
        print(f"  • Frequency decreases monotonically")
        print(f"  • Higher γ → More segment density → More redshift")
        print("="*80)
        
        # Frequency should monotonically decrease
        assert np.all(np.diff(nu_out.values) < 0)
    
    def test_invalid_gamma_raises(self):
        """Test that negative/zero gamma raises error"""
        with pytest.raises(ValueError):
            predict_frequency_track(1e12, np.array([1.0, -0.5, 2.0]))


class TestResiduals:
    """Tests for residual computation"""
    
    def test_perfect_match(self):
        """Test residuals with perfect prediction
        
        Physical Meaning:
        Perfect model prediction: v_pred = v_obs exactly.
        All residual metrics should be zero.
        """
        v_pred = np.array([10.0, 11.0, 12.0])
        v_obs = np.array([10.0, 11.0, 12.0])
        
        metrics = compute_residuals(v_pred, v_obs)
        
        print("\n" + "="*80)
        print("RESIDUALS: Perfect Match")
        print("="*80)
        print(f"Predicted: {v_pred}")
        print(f"Observed:  {v_obs}")
        print(f"\nMetrics:")
        print(f"  MAE (Mean Absolute Error): {metrics['mae']:.6f}")
        print(f"  RMSE (Root Mean Square Error): {metrics['rmse']:.6f}")
        print(f"  Max |residual|: {metrics['max_abs_residual']:.6f}")
        print(f"\nPhysical Interpretation:")
        print(f"  • Perfect model fit: all errors = 0")
        print(f"  • SSZ theory exactly reproduces observations")
        print("="*80)
        
        assert metrics['mae'] == pytest.approx(0.0, abs=1e-10)
        assert metrics['rmse'] == pytest.approx(0.0, abs=1e-10)
        assert metrics['max_abs_residual'] == pytest.approx(0.0, abs=1e-10)
    
    def test_systematic_bias(self):
        """Test residuals with systematic offset
        
        Physical Meaning:
        Systematic bias: model consistently over/under-predicts.
        MAE, RMSE, and max residual all equal the bias.
        """
        v_pred = np.array([10.0, 11.0, 12.0])
        v_obs = np.array([9.0, 10.0, 11.0])  # Offset by -1.0
        
        metrics = compute_residuals(v_pred, v_obs)
        
        print("\n" + "="*80)
        print("RESIDUALS: Systematic Bias")
        print("="*80)
        print(f"Predicted: {v_pred}")
        print(f"Observed:  {v_obs}")
        print(f"Bias: {v_pred[0] - v_obs[0]:.1f} km/s (constant)")
        print(f"\nMetrics:")
        print(f"  MAE: {metrics['mae']:.6f}")
        print(f"  RMSE: {metrics['rmse']:.6f}")
        print(f"  Max |residual|: {metrics['max_abs_residual']:.6f}")
        print(f"\nPhysical Interpretation:")
        print(f"  • Consistent +1 km/s over-prediction")
        print(f"  • Could indicate calibration offset")
        print(f"  • Easily corrected by shifting v0")
        print("="*80)
        
        assert metrics['mae'] == pytest.approx(1.0, rel=1e-6)
        assert metrics['rmse'] == pytest.approx(1.0, rel=1e-6)
        assert metrics['max_abs_residual'] == pytest.approx(1.0, rel=1e-6)
    
    def test_mixed_residuals(self):
        """Test residuals with mixed over/under prediction
        
        Physical Meaning:
        Model alternates between over- and under-prediction.
        Residuals cancel out partially, but RMS captures variance.
        """
        v_pred = np.array([10.0, 11.5, 12.0])
        v_obs = np.array([10.5, 11.0, 12.5])
        # Residuals: [-0.5, +0.5, -0.5]
        
        metrics = compute_residuals(v_pred, v_obs)
        
        print("\n" + "="*80)
        print("RESIDUALS: Mixed Over/Under Prediction")
        print("="*80)
        print(f"Predicted: {v_pred}")
        print(f"Observed:  {v_obs}")
        print(f"Residuals: {v_pred - v_obs}")
        print(f"\nMetrics:")
        print(f"  MAE: {metrics['mae']:.6f}")
        print(f"  RMSE: {metrics['rmse']:.6f}")
        print(f"  Max |residual|: {metrics['max_abs_residual']:.6f}")
        print(f"\nPhysical Interpretation:")
        print(f"  • Alternating over/under predictions")
        print(f"  • No systematic bias (errors cancel)")
        print(f"  • RMS captures scatter: ±0.5 km/s")
        print(f"  • Random noise in measurements")
        print("="*80)
        
        assert metrics['mae'] == pytest.approx(0.5, rel=1e-6)
        assert metrics['rmse'] == pytest.approx(0.5, rel=1e-6)
        assert metrics['max_abs_residual'] == pytest.approx(0.5, rel=1e-6)


class TestCumulativeGamma:
    """Tests for cumulative gamma computation"""
    
    def test_constant_q(self):
        """Test cumulative gamma with constant q
        
        Physical Meaning:
        Cumulative γ = ∏ q_k (product of all q factors).
        With constant q, γ_k = q^k (exponential growth).
        """
        q_series = np.array([1.0, 1.5, 1.5, 1.5])
        gamma = compute_cumulative_gamma(q_series)
        
        expected = np.array([1.0, 1.5, 2.25, 3.375])
        
        print("\n" + "="*80)
        print("CUMULATIVE γ: Constant q = 1.5")
        print("="*80)
        print(f"q sequence: {q_series}")
        print(f"\nCumulative γ:")
        for i, g in enumerate(gamma):
            print(f"  γ_{i+1} = {g:.4f} (= 1.5^{i})")
        print(f"\nPhysical Interpretation:")
        print(f"  • γ grows exponentially with constant q > 1")
        print(f"  • Each step multiplies by factor 1.5")
        print(f"  • Segment field accumulates over multiple rings")
        print("="*80)
        
        assert np.allclose(gamma, expected, rtol=1e-6)
    
    def test_all_ones(self):
        """Test cumulative gamma with all q=1
        
        Physical Meaning:
        q=1 everywhere means no change between rings.
        γ_k = 1 for all k (no segment field accumulation).
        """
        q_series = np.ones(5)
        gamma = compute_cumulative_gamma(q_series)
        
        print("\n" + "="*80)
        print("CUMULATIVE γ: All q = 1 (No Change)")
        print("="*80)
        print(f"q sequence: {q_series}")
        print(f"γ sequence: {gamma}")
        print(f"\nPhysical Interpretation:")
        print(f"  • q=1 everywhere → no temperature/density changes")
        print(f"  • γ=1 for all rings → no segment field accumulation")
        print(f"  • Isothermal, homogeneous medium")
        print("="*80)
        
        assert np.allclose(gamma, np.ones(5), rtol=1e-10)
    
    def test_increasing_sequence(self):
        """Test cumulative gamma increases with q>1
        
        Physical Meaning:
        q > 1 means energy increases between rings.
        Cumulative γ grows monotonically.
        """
        q_series = np.array([1.0, 1.2, 1.1, 1.3])
        gamma = compute_cumulative_gamma(q_series)
        
        print("\n" + "="*80)
        print("CUMULATIVE γ: Increasing Sequence")
        print("="*80)
        print(f"q sequence: {q_series}")
        print(f"\nγ Evolution:")
        for i, (q, g) in enumerate(zip(q_series, gamma)):
            print(f"  Step {i+1}: q = {q:.1f}, γ_cum = {g:.4f}")
        print(f"\nMonotonicity:")
        print(f"  All Δγ > 0: {np.all(np.diff(gamma) > 0)}")
        print(f"\nPhysical Interpretation:")
        print(f"  • All q > 1 → energy/temperature rising")
        print(f"  • γ accumulates monotonically")
        print(f"  • Heating trend amplifies segment field")
        print("="*80)
        
        # Cumulative product should be monotonically increasing
        assert np.all(np.diff(gamma) > 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
