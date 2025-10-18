import numpy as np, pandas as pd
from scripts.ssz.cosmology import build_cosmo_fields

def test_cosmo_fields_added():
    print("\n" + "="*80)
    print("COSMOLOGICAL FIELD CONSTRUCTION TEST")
    print("="*80)
    
    # Test data
    df = pd.DataFrame({"x":[0,1], "y":[0,1], "rho":[0.2, 5.0]})
    
    print("\nInput Data:")
    print(f"  Positions: (x,y) = {list(zip(df['x'], df['y']))}")
    print(f"  Densities: ρ = {df['rho'].values}")
    
    # Build cosmological fields
    gamma_cfg = dict(alpha=0.8, beta=0.6, floor=0.02)
    print(f"\nGamma Configuration:")
    print(f"  α = {gamma_cfg['alpha']}")
    print(f"  β = {gamma_cfg['beta']}")
    print(f"  floor = {gamma_cfg['floor']}")
    
    out = build_cosmo_fields(df, density_col="rho", gamma_cfg=gamma_cfg)
    
    # Verify columns
    required_cols = ("gamma_seg", "z_seg", "kappa_proxy", "vrot_mod")
    print(f"\nGenerated Fields:")
    for c in required_cols:
        assert c in out.columns
        print(f"  ✓ {c}: [{out[c].min():.6f}, {out[c].max():.6f}]")
    
    # Verify gamma bounds
    gamma_min = out["gamma_seg"].min()
    gamma_max = out["gamma_seg"].max()
    assert (out["gamma_seg"].between(0.02, 1.0)).all()
    print(f"\nGamma Bounds Check:")
    print(f"  Range: [{gamma_min:.6f}, {gamma_max:.6f}]")
    print(f"  Within [0.02, 1.0]: ✓ PASS")
    
    print("\nPhysical Interpretation:")
    print("  • Cosmological fields add to spacetime structure")
    print("  • gamma_seg: Segment field strength (0.02 ≤ γ ≤ 1.0)")
    print("  • z_seg: Redshift mapping z = (1/γ) - 1")
    print("  • kappa_proxy: Gravitational lensing convergence")
    print("  • vrot_mod: Rotation curve modifier γ^(-p)")
    print("  • All fields contribute to observable predictions")
    print("="*80)
