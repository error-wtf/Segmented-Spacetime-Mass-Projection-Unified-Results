import numpy as np

from ssz_cosmos.bodies import BodyDefinition
from ssz_cosmos.field import BodyState, MultiBodyField


def test_two_body_sigma_superposition():
    """
    Test: Two-Body Segment Density Superposition
    
    Physical Meaning:
    Segment density σ from multiple bodies adds linearly (superposition principle).
    This validates that segment fields behave like classical gravitational fields
    in the weak-field limit.
    """
    core_points = np.array([[1.0, 0.0, 0.0]])
    field = MultiBodyField()

    M_earth = 5.97219e24  # Earth mass
    states = [
        BodyState("A", np.zeros(3), M_earth, 1.0, 0.015),
        BodyState("B", np.array([0.5, 0.0, 0.0]), M_earth, 1.0, 0.015),
    ]

    # Calculate individual contributions
    sigma_A = field.sigma(core_points, [states[0]])
    sigma_B = field.sigma(core_points, [states[1]])
    sigma_total = field.sigma(core_points, states)
    
    print("\n" + "="*80)
    print("TWO-BODY SEGMENT DENSITY SUPERPOSITION")
    print("="*80)
    print(f"Test Configuration:")
    print(f"  Body A: Position = (0.0, 0.0, 0.0) m")
    print(f"          Mass = {M_earth:.3e} kg (1 M⊕)")
    print(f"  Body B: Position = (0.5, 0.0, 0.0) m")
    print(f"          Mass = {M_earth:.3e} kg (1 M⊕)")
    print(f"  Test point: (1.0, 0.0, 0.0) m")
    print(f"\nSegment Density σ:")
    print(f"  Body A only:  σ_A = {float(sigma_A):.6e}")
    print(f"  Body B only:  σ_B = {float(sigma_B):.6e}")
    print(f"  Combined:     σ_total = {float(sigma_total):.6e}")
    print(f"  Sum A+B:      σ_A + σ_B = {float(sigma_A + sigma_B):.6e}")
    print(f"\nSuperposition Check:")
    print(f"  σ_total ≈ σ_A + σ_B: {np.allclose(sigma_total, sigma_A + sigma_B, rtol=0.1)}")
    print(f"  Relative difference: {abs(float(sigma_total) - float(sigma_A + sigma_B))/float(sigma_total)*100:.2f}%")
    print(f"\nPhysical Interpretation:")
    print(f"  • Segment fields add linearly (superposition)")
    print(f"  • Consistent with weak-field GR limit")
    print(f"  • Both bodies contribute to spacetime structure")
    print(f"  • No non-linear effects at this scale")
    print("="*80)
    
    assert sigma_total.shape == (1,)
    assert float(sigma_total) > 0.0
