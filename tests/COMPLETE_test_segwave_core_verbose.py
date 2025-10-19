# DIESE DATEI ENTHÄLT BEISPIEL-ERGÄNZUNGEN FÜR DIE RESTLICHEN TESTS
# Kopieren Sie die gewünschten Abschnitte in test_segwave_core.py

# ===== TestFrequencyTrack =====

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


# ===== TestResiduals =====

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


# ===== TestCumulativeGamma =====

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
