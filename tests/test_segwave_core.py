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
        """Test q_k with temperature only, β=1"""
        q = compute_q_factor(T_curr=80.0, T_prev=100.0, beta=1.0)
        assert q == pytest.approx(0.8, rel=1e-6)
    
    def test_temperature_with_beta(self):
        """Test q_k with custom β"""
        q = compute_q_factor(T_curr=80.0, T_prev=100.0, beta=2.0)
        assert q == pytest.approx(0.64, rel=1e-6)  # (80/100)^2
    
    def test_temperature_and_density(self):
        """Test q_k with both T and n"""
        q = compute_q_factor(
            T_curr=80.0, T_prev=100.0,
            n_curr=1e5, n_prev=2e5,
            beta=1.0, eta=0.5
        )
        expected = 0.8 * (1e5 / 2e5) ** 0.5  # 0.8 * sqrt(0.5)
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
        """Test with single shell (no propagation)"""
        rings = np.array([1])
        T = np.array([100.0])
        v0 = 10.0
        
        df = predict_velocity_profile(rings, T, v0, alpha=1.0)
        
        assert len(df) == 1
        assert df['v_pred'].iloc[0] == pytest.approx(v0, rel=1e-6)
        assert df['q_k'].iloc[0] == pytest.approx(1.0, rel=1e-6)
    
    def test_two_shells_alpha_one(self):
        """Test two shells with α=1"""
        rings = np.array([1, 2])
        T = np.array([100.0, 80.0])
        v0 = 10.0
        alpha = 1.0
        
        df = predict_velocity_profile(rings, T, v0, alpha=alpha)
        
        # q_2 = 80/100 = 0.8
        # v_2 = v_1 * q_2^(-0.5) = 10.0 * 0.8^(-0.5)
        expected_v2 = 10.0 * (0.8 ** (-0.5))
        
        assert df['q_k'].iloc[1] == pytest.approx(0.8, rel=1e-6)
        assert df['v_pred'].iloc[1] == pytest.approx(expected_v2, rel=1e-6)
    
    def test_deterministic_chain(self):
        """Test deterministic 5-shell sequence"""
        rings = np.array([1, 2, 3, 4, 5])
        T = np.array([100.0, 90.0, 80.0, 70.0, 60.0])
        v0 = 12.5
        alpha = 1.0
        
        df = predict_velocity_profile(rings, T, v0, alpha=alpha)
        
        # Check monotonic increase in velocity (T decreasing)
        velocities = df['v_pred'].values
        assert np.all(np.diff(velocities) > 0), "Velocity should increase as T decreases"
        
        # Check DataFrame structure
        assert list(df.columns) == ['ring', 'T', 'q_k', 'v_pred']
        assert len(df) == 5
    
    def test_alpha_zero_constant_velocity(self):
        """Test α=0 gives constant velocity (no segmentation)"""
        rings = np.array([1, 2, 3])
        T = np.array([100.0, 80.0, 60.0])
        v0 = 15.0
        
        df = predict_velocity_profile(rings, T, v0, alpha=0.0)
        
        # All velocities should equal v0 when α=0
        assert np.allclose(df['v_pred'].values, v0, rtol=1e-6)
    
    def test_with_density(self):
        """Test velocity profile with density included"""
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
        """Test frequency shift with single gamma"""
        nu_in = 1e12  # 1 THz
        gamma_series = np.array([2.0])
        
        nu_out = predict_frequency_track(nu_in, gamma_series)
        
        # ν_out = ν_in * γ^(-0.5)
        expected = nu_in * (2.0 ** (-0.5))
        assert nu_out.iloc[0] == pytest.approx(expected, rel=1e-6)
    
    def test_frequency_decreases_with_gamma(self):
        """Test that frequency decreases as gamma increases"""
        nu_in = 1e12
        gamma_series = np.array([1.0, 1.2, 1.5, 2.0])
        
        nu_out = predict_frequency_track(nu_in, gamma_series)
        
        # Frequency should monotonically decrease
        assert np.all(np.diff(nu_out.values) < 0)
    
    def test_invalid_gamma_raises(self):
        """Test that negative/zero gamma raises error"""
        with pytest.raises(ValueError):
            predict_frequency_track(1e12, np.array([1.0, -0.5, 2.0]))


class TestResiduals:
    """Tests for residual computation"""
    
    def test_perfect_match(self):
        """Test residuals with perfect prediction"""
        v_pred = np.array([10.0, 11.0, 12.0])
        v_obs = np.array([10.0, 11.0, 12.0])
        
        metrics = compute_residuals(v_pred, v_obs)
        
        assert metrics['mae'] == pytest.approx(0.0, abs=1e-10)
        assert metrics['rmse'] == pytest.approx(0.0, abs=1e-10)
        assert metrics['max_abs_residual'] == pytest.approx(0.0, abs=1e-10)
    
    def test_systematic_bias(self):
        """Test residuals with systematic offset"""
        v_pred = np.array([10.0, 11.0, 12.0])
        v_obs = np.array([9.0, 10.0, 11.0])  # Offset by -1.0
        
        metrics = compute_residuals(v_pred, v_obs)
        
        assert metrics['mae'] == pytest.approx(1.0, rel=1e-6)
        assert metrics['rmse'] == pytest.approx(1.0, rel=1e-6)
        assert metrics['max_abs_residual'] == pytest.approx(1.0, rel=1e-6)
    
    def test_mixed_residuals(self):
        """Test residuals with mixed over/under prediction"""
        v_pred = np.array([10.0, 11.5, 12.0])
        v_obs = np.array([10.5, 11.0, 12.5])
        # Residuals: [-0.5, +0.5, -0.5]
        
        metrics = compute_residuals(v_pred, v_obs)
        
        assert metrics['mae'] == pytest.approx(0.5, rel=1e-6)
        assert metrics['rmse'] == pytest.approx(0.5, rel=1e-6)
        assert metrics['max_abs_residual'] == pytest.approx(0.5, rel=1e-6)


class TestCumulativeGamma:
    """Tests for cumulative gamma computation"""
    
    def test_constant_q(self):
        """Test cumulative gamma with constant q"""
        q_series = np.array([1.0, 1.5, 1.5, 1.5])
        gamma = compute_cumulative_gamma(q_series)
        
        expected = np.array([1.0, 1.5, 2.25, 3.375])
        assert np.allclose(gamma, expected, rtol=1e-6)
    
    def test_all_ones(self):
        """Test cumulative gamma with all q=1"""
        q_series = np.ones(5)
        gamma = compute_cumulative_gamma(q_series)
        
        assert np.allclose(gamma, np.ones(5), rtol=1e-10)
    
    def test_increasing_sequence(self):
        """Test cumulative gamma increases with q>1"""
        q_series = np.array([1.0, 1.2, 1.1, 1.3])
        gamma = compute_cumulative_gamma(q_series)
        
        # Cumulative product should be monotonically increasing
        assert np.all(np.diff(gamma) > 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
