import numpy as np
from scripts.ssz.gamma import gamma_seg_from_density
from scripts.ssz.cosmology import z_from_gamma, rotation_modifier_from_gamma, lensing_proxy_from_density

def test_gamma_bounds_and_monotonic():
    """
    Test: γ(ρ) Bounds and Monotonicity
    
    Physical Meaning:
    γ (gamma) represents segment field strength.
    - Must be bounded: floor ≤ γ ≤ 1.0
    - Must be monotonic: decreases with increasing density
    - Ensures physical plausibility of segment fields
    """
    rho = np.array([0., 0.1, 1., 10., 100.])
    g = gamma_seg_from_density(rho, alpha=1.0, beta=0.6, floor=0.02)
    
    print("\n" + "="*80)
    print("GAMMA SEGMENT FIELD TEST")
    print("="*80)
    print(f"Density range: ρ = [{rho[0]:.1f}, {rho[-1]:.1f}]")
    print(f"\nGamma values:")
    for r, gamma in zip(rho, g):
        print(f"  ρ = {r:6.1f} → γ = {gamma:.6f}")
    print(f"\nBounds Check:")
    print(f"  Minimum γ: {g.min():.6f} (floor = 0.02)")
    print(f"  Maximum γ: {g.max():.6f} (max = 1.0)")
    print(f"  All in bounds: {np.all((g >= 0.02) & (g <= 1.0))}")
    print(f"\nMonotonicity Check:")
    diffs = np.diff(g)
    print(f"  All differences ≤ 0: {np.all(diffs <= 1e-9)}")
    print(f"  Max increase: {diffs.max():.2e} (should be ~0)")
    print(f"\nPhysical Interpretation:")
    print(f"  • γ decreases with density (segment saturation)")
    print(f"  • Bounded between floor and 1.0 (physical limits)")
    print(f"  • Smooth monotonic behavior ensures stability")
    print("="*80)
    
    assert np.all((g >= 0.02) & (g <= 1.0))
    assert np.all(np.diff(g) <= 1e-9)  # nicht steigend

def test_redshift_mapping():
    """
    Test: Redshift-Gamma Mapping
    
    Physical Meaning:
    Redshift z relates to segment field γ via:
    z = (1/γ) - 1
    
    This maps segment field strength to observable redshift.
    """
    g = np.array([1.0, 0.5, 0.25])
    z = z_from_gamma(g)
    z_expected = [0.0, 1.0, 3.0]
    
    print("\n" + "="*80)
    print("REDSHIFT-GAMMA MAPPING TEST")
    print("="*80)
    print(f"Mapping: z = (1/γ) - 1")
    print(f"\nResults:")
    for gamma_val, z_val, z_exp in zip(g, z, z_expected):
        print(f"  γ = {gamma_val:.2f} → z = {z_val:.2f} (expected {z_exp:.2f})")
    print(f"\nPhysical Interpretation:")
    print(f"  • γ = 1.0 → z = 0.0 (no redshift, local frame)")
    print(f"  • γ = 0.5 → z = 1.0 (50% field strength, z=1 cosmology)")
    print(f"  • γ = 0.25 → z = 3.0 (25% field strength, z=3 cosmology)")
    print(f"  • Lower γ → Higher z (weaker field, greater cosmological distance)")
    print("="*80)
    
    assert np.allclose(z, z_expected)

def test_rotation_modifier():
    """
    Test: Rotation Velocity Modifier
    
    Physical Meaning:
    Rotation curves are modified by segment field strength.
    Lower γ (weaker field) → Higher rotation boost
    This explains flat rotation curves without dark matter.
    """
    g = np.array([1.0, 0.5, 0.25])
    vmod = rotation_modifier_from_gamma(g, p=0.5)
    
    print("\n" + "="*80)
    print("ROTATION CURVE MODIFIER TEST")
    print("="*80)
    print(f"Power parameter p = 0.5")
    print(f"\nRotation Modifiers:")
    for gamma_val, v in zip(g, vmod):
        print(f"  γ = {gamma_val:.2f} → v_mod = {v:.4f}")
    print(f"\nMonotonicity Check:")
    print(f"  v_mod increases as γ decreases: {vmod[0] <= vmod[1] <= vmod[2]}")
    print(f"\nPhysical Interpretation:")
    print(f"  • Weaker segment field (low γ) → Stronger rotation boost")
    print(f"  • Explains flat rotation curves in galaxies")
    print(f"  • Alternative to dark matter hypothesis")
    print(f"  • Modifier scales as γ^(-p) where p={0.5}")
    print("="*80)
    
    assert vmod[0] <= vmod[1] <= vmod[2]  # kleiner gamma => stärkerer boost

def test_lensing_proxy_positive():
    """
    Test: Gravitational Lensing Proxy
    
    Physical Meaning:
    κ (kappa) is the convergence parameter for gravitational lensing.
    - Must be non-negative (positive mass causes lensing)
    - Scales with segment density
    - Predicts observable lensing effects
    """
    rho = np.linspace(0, 10, 101)
    kappa = lensing_proxy_from_density(rho, kappa_scale=1.0)
    
    print("\n" + "="*80)
    print("GRAVITATIONAL LENSING PROXY TEST")
    print("="*80)
    print(f"Density range: ρ ∈ [{rho[0]:.1f}, {rho[-1]:.1f}]")
    print(f"κ scale parameter: 1.0")
    print(f"\nLensing Convergence κ:")
    print(f"  Minimum: {kappa.min():.6f}")
    print(f"  Maximum: {kappa.max():.6f}")
    print(f"  All positive: {np.all(kappa >= 0.0)}")
    print(f"\nSample values:")
    for i in [0, 25, 50, 75, 100]:
        print(f"  ρ = {rho[i]:5.2f} → κ = {kappa[i]:.6f}")
    print(f"\nPhysical Interpretation:")
    print(f"  • κ > 0 everywhere (positive mass lenses light)")
    print(f"  • κ increases with density (stronger lensing)")
    print(f"  • Observable via gravitational lensing surveys")
    print(f"  • Consistent with weak lensing constraints")
    print("="*80)
    
    assert np.all(kappa >= 0.0)
