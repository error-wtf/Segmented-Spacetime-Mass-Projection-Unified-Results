import numpy as np
from ssz_cosmos.field import MultiBodyField, BodyState

def make_state(name: str, position, mass, alpha=1.0, kappa=0.015):
    return BodyState(name=name, position=np.array(position, dtype=float), mass_kg=mass, alpha=alpha, kappa=kappa)

def test_sigma_additive_mass():
    """
    Test: Segment Density Additivity
    
    Physical Meaning:
    Segment density σ from multiple bodies should be additive.
    σ_total ≥ σ_individual
    This ensures superposition principle for segment fields.
    """
    field = MultiBodyField()
    point = np.array([[1.5e11, 0.0, 0.0]])  # 1 AU from Sun
    
    state_primary = make_state("sun", [0.0, 0.0, 0.0], 1.989e30)
    sigma_primary = field.sigma(point, [state_primary])[0]
    
    state_secondary = make_state("jupiter", [7.8e11, 0.0, 0.0], 1.898e27)
    sigma_combined = field.sigma(point, [state_primary, state_secondary])[0]
    
    print("\n" + "="*80)
    print("SEGMENT DENSITY ADDITIVITY TEST")
    print("="*80)
    print(f"Test Configuration:")
    print(f"  Sun:     Position = (0.0, 0.0, 0.0) m")
    print(f"           Mass = {1.989e30:.3e} kg (1 M☉)")
    print(f"  Jupiter: Position = (7.8e11, 0.0, 0.0) m (5.2 AU)")
    print(f"           Mass = {1.898e27:.3e} kg (318 M⊕)")
    print(f"  Test Point: (1.5e11, 0.0, 0.0) m (1 AU from Sun)")
    print(f"\nSegment Density σ:")
    print(f"  Sun only:        σ = {sigma_primary:.6e}")
    print(f"  Sun + Jupiter:   σ = {sigma_combined:.6e}")
    print(f"  Increase:        Δσ = {sigma_combined - sigma_primary:.6e}")
    print(f"\nAdditivity Check:")
    print(f"  σ_combined ≥ σ_primary: {sigma_combined >= sigma_primary}")
    print(f"\nPhysical Interpretation:")
    print(f"  • Multiple bodies contribute to total segment density")
    print(f"  • Superposition principle holds for segment fields")
    print(f"  • Jupiter's contribution is small (mass ratio ~1/1000)")
    print(f"  • Consistent with weak-field GR limit")
    print("="*80)
    
    assert sigma_combined >= sigma_primary

def test_tau_monotonic_with_alpha():
    """
    Test: Time Dilation Monotonicity with α
    
    Physical Meaning:
    Time dilation τ scales with α parameter:
    - Higher α → Stronger time dilation effect
    - Lower α → Weaker time dilation effect
    τ_low_α > τ_high_α (less dilated > more dilated)
    """
    field = MultiBodyField()
    point = np.array([[2.0e11, 0.0, 0.0]])  # ~1.3 AU
    
    M_sun = 1.989e30
    state_low_alpha = make_state("low", [0.0, 0.0, 0.0], M_sun, alpha=0.2)
    state_high_alpha = make_state("high", [0.0, 0.0, 0.0], M_sun, alpha=1.2)
    
    tau_low = field.tau(point, [state_low_alpha])[0]
    tau_high = field.tau(point, [state_high_alpha])[0]
    
    print("\n" + "="*80)
    print("TIME DILATION vs ALPHA PARAMETER TEST")
    print("="*80)
    print(f"Test Configuration:")
    print(f"  Body mass: {M_sun:.3e} kg (1 M☉)")
    print(f"  Position: (0.0, 0.0, 0.0) m")
    print(f"  Test point: (2.0e11, 0.0, 0.0) m (1.3 AU)")
    print(f"\nAlpha Parameter Scan:")
    print(f"  Low α  = 0.2 → τ = {tau_low:.8f}")
    print(f"  High α = 1.2 → τ = {tau_high:.8f}")
    print(f"\nTime Dilation Effect:")
    print(f"  Δτ = {tau_low - tau_high:.8f}")
    print(f"  Ratio τ_low/τ_high = {tau_low/tau_high:.6f}")
    print(f"\nMonotonicity Check:")
    print(f"  τ_low > τ_high: {tau_low > tau_high}")
    print(f"\nPhysical Interpretation:")
    print(f"  • α controls strength of time dilation")
    print(f"  • Higher α → More time dilation (slower clocks)")
    print(f"  • Lower α → Less time dilation (faster clocks)")
    print(f"  • α ≈ 1 recovers GR-like behavior")
    print("="*80)
    
    assert tau_low > tau_high

def test_refractive_index_baseline():
    """
    Test: Refractive Index ≥ 1
    
    Physical Meaning:
    Refractive index n of spacetime due to segment fields.
    - Must satisfy n ≥ 1.0 (causality constraint)
    - n > 1 means light travels slower than c_vacuum
    - Leads to gravitational lensing and light deflection
    """
    field = MultiBodyField()
    point = np.array([[3.0e11, 0.0, 0.0]])  # ~2 AU
    
    M_earth = 5.972e24
    state = make_state("earth", [0.0, 0.0, 0.0], M_earth, kappa=0.02)
    n = field.refractive_index(point, [state])[0]
    
    print("\n" + "="*80)
    print("REFRACTIVE INDEX BASELINE TEST")
    print("="*80)
    print(f"Test Configuration:")
    print(f"  Earth mass: {M_earth:.3e} kg (1 M⊕)")
    print(f"  Position: (0.0, 0.0, 0.0) m")
    print(f"  κ parameter: 0.02")
    print(f"  Test point: (3.0e11, 0.0, 0.0) m (2 AU)")
    print(f"\nRefractive Index:")
    print(f"  n = {n:.10f}")
    print(f"  Deviation from vacuum: n - 1 = {n - 1:.2e}")
    print(f"\nCausality Check:")
    print(f"  n ≥ 1.0: {n >= 1.0}")
    print(f"\nPhysical Interpretation:")
    print(f"  • n ≥ 1 ensures causality (no FTL propagation)")
    print(f"  • n > 1 means effective light speed < c")
    print(f"  • Small deviation (n ≈ 1) consistent with weak field")
    print(f"  • Leads to gravitational lensing: Δθ ∝ (n-1)")
    print("="*80)
    
    assert n >= 1.0
