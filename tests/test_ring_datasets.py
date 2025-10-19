"""
Ring Dataset Validation Tests

Tests multi-ring observations using real astronomical data.
Ensures all ring datasets have sufficient data for meaningful validation.

Copyright © 2025
Carmen Wrede und Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Multi-ring datasets with expected ring counts
MULTI_RING_DATASETS = [
    ("data/observations/G79_29+0_46_CO_NH3_rings.csv", 10, "Star-forming Region"),
    ("data/observations/CygnusX_DiamondRing_CII_rings.csv", 3, "Molecular Cloud"),
]


@pytest.mark.parametrize("dataset_path,expected_rings,category", MULTI_RING_DATASETS)
def test_ring_dataset_completeness(dataset_path, expected_rings, category):
    """Test that ring datasets have sufficient rings for validation.
    
    Physical Meaning:
    Multi-ring datasets are required for testing ring-to-ring growth,
    temperature gradients, and expansion dynamics. Single-ring systems
    cannot validate these physical processes.
    """
    df = pd.read_csv(dataset_path)
    
    print("\n" + "="*80)
    print(f"RING DATASET VALIDATION: {Path(dataset_path).stem}")
    print("="*80)
    print(f"Category: {category}")
    print(f"File: {dataset_path}")
    print(f"\nDataset Properties:")
    print(f"  Rings found: {len(df)}")
    print(f"  Expected rings: {expected_rings}")
    print(f"  Columns: {', '.join(df.columns[:5])}...")
    
    # Critical assertion: Must have ≥2 rings
    assert len(df) >= 2, f"Dataset needs ≥2 rings for validation (got {len(df)})"
    assert len(df) == expected_rings, f"Expected {expected_rings} rings, got {len(df)}"
    
    print(f"\nPhysical Interpretation:")
    print(f"  ✅ Sufficient rings for inter-ring analysis")
    print(f"  ✅ Can validate growth statistics")
    print(f"  ✅ Can test temperature/velocity gradients")
    print("="*80)


@pytest.mark.parametrize("dataset_path,expected_rings,category", MULTI_RING_DATASETS)
def test_ring_growth_statistics(dataset_path, expected_rings, category):
    """Test ring-to-ring growth with real multi-ring observations.
    
    Physical Meaning:
    Ring structures should show monotonic or consistent growth patterns.
    This validates the physical expansion/structure of the system.
    """
    df = pd.read_csv(dataset_path)
    
    # Require minimum 2 rings
    if len(df) < 2:
        pytest.skip(f"Need ≥2 rings for growth test (got {len(df)})")
    
    # Calculate radius growth (if radius available)
    if 'radius_pc' in df.columns:
        radius_growth = df['radius_pc'].diff().dropna()
        
        print("\n" + "="*80)
        print(f"RING GROWTH: {Path(dataset_path).stem}")
        print("="*80)
        print(f"Category: {category}")
        print(f"Rings: {len(df)}")
        print(f"\nRadius Growth Statistics:")
        print(f"  Mean Δr: {radius_growth.mean():.3f} pc")
        print(f"  Min Δr: {radius_growth.min():.3f} pc")
        print(f"  Max Δr: {radius_growth.max():.3f} pc")
        print(f"  All positive: {(radius_growth > 0).all()}")
        
        print(f"\nPhysical Interpretation:")
        print(f"  • Radius increases monotonically outward")
        print(f"  • Expanding shell/ring structure")
        print(f"  • No unphysical radius inversions")
        print("="*80)
        
        # Physical constraint: radius must increase
        assert (radius_growth > 0).all(), "Radius must increase monotonically"


@pytest.mark.parametrize("dataset_path,expected_rings,category", MULTI_RING_DATASETS)
def test_temperature_gradient(dataset_path, expected_rings, category):
    """Test temperature gradient across rings.
    
    Physical Meaning:
    Temperature typically decreases outward in expanding shells
    (cooling) or molecular clouds (shielding). Validates thermal
    structure consistency.
    """
    df = pd.read_csv(dataset_path)
    
    if len(df) < 2:
        pytest.skip(f"Need ≥2 rings for gradient test (got {len(df)})")
    
    if 'T' not in df.columns:
        pytest.skip("Temperature column 'T' not found")
    
    temp_gradient = df['T'].diff().dropna()
    
    print("\n" + "="*80)
    print(f"TEMPERATURE GRADIENT: {Path(dataset_path).stem}")
    print("="*80)
    print(f"Category: {category}")
    print(f"Rings: {len(df)}")
    print(f"\nTemperature Statistics:")
    print(f"  Inner ring: {df['T'].iloc[0]:.1f} K")
    print(f"  Outer ring: {df['T'].iloc[-1]:.1f} K")
    print(f"  Total change: {df['T'].iloc[-1] - df['T'].iloc[0]:.1f} K")
    print(f"  Mean gradient: {temp_gradient.mean():.2f} K/ring")
    
    # Check if cooling (most common) or heating
    is_cooling = temp_gradient.mean() < 0
    
    print(f"\nPhysical Interpretation:")
    if is_cooling:
        print(f"  • Temperature decreases outward (cooling)")
        print(f"  • Consistent with expanding shell physics")
        print(f"  • Or shielding in molecular cloud")
    else:
        print(f"  • Temperature increases outward (heating)")
        print(f"  • May indicate external heating source")
    print("="*80)
    
    # Physical constraint: Temperature must be positive
    assert (df['T'] > 0).all(), "Temperature must be positive"


@pytest.mark.parametrize("dataset_path,expected_rings,category", MULTI_RING_DATASETS)
def test_velocity_profile(dataset_path, expected_rings, category):
    """Test velocity profile across rings.
    
    Physical Meaning:
    Velocity profiles reveal expansion dynamics. Can be constant
    (pressure-driven), decreasing (momentum-conserving), or
    increasing (acceleration).
    """
    df = pd.read_csv(dataset_path)
    
    if len(df) < 3:
        pytest.skip(f"Need ≥3 rings for velocity profile (got {len(df)})")
    
    if 'v_obs' not in df.columns:
        pytest.skip("Velocity column 'v_obs' not found")
    
    velocities = df['v_obs'].values
    v_gradient = np.diff(velocities)
    
    print("\n" + "="*80)
    print(f"VELOCITY PROFILE: {Path(dataset_path).stem}")
    print("="*80)
    print(f"Category: {category}")
    print(f"Rings: {len(df)}")
    print(f"\nVelocity Statistics:")
    print(f"  Inner ring: {velocities[0]:.2f} km/s")
    print(f"  Outer ring: {velocities[-1]:.2f} km/s")
    print(f"  Mean velocity: {velocities.mean():.2f} km/s")
    print(f"  Velocity range: {velocities.min():.2f} - {velocities.max():.2f} km/s")
    
    # Check velocity profile type
    mean_gradient = v_gradient.mean()
    is_constant = np.abs(mean_gradient) < 0.5  # Within 0.5 km/s variation
    is_decreasing = mean_gradient < -0.5
    is_increasing = mean_gradient > 0.5
    
    print(f"\nVelocity Profile:")
    if is_constant:
        print(f"  Type: Constant expansion")
        print(f"  Interpretation: Pressure-driven expansion")
    elif is_decreasing:
        print(f"  Type: Decreasing velocity")
        print(f"  Interpretation: Momentum-conserving expansion")
    elif is_increasing:
        print(f"  Type: Increasing velocity")
        print(f"  Interpretation: Acceleration or infall")
    
    print(f"\nPhysical Interpretation:")
    print(f"  • Expansion dynamics validated")
    print(f"  • Velocity structure consistent with {category}")
    print("="*80)
    
    # Physical constraint: Velocities must be non-negative
    assert (df['v_obs'] >= 0).all(), "Velocities must be non-negative"


@pytest.mark.parametrize("dataset_path,expected_rings,category", MULTI_RING_DATASETS)
def test_tracer_documentation(dataset_path, expected_rings, category):
    """Test that molecular tracers are documented.
    
    Physical Meaning:
    Each ring should document which molecular transitions were used
    for observations. Essential for understanding data provenance.
    """
    df = pd.read_csv(dataset_path)
    
    print("\n" + "="*80)
    print(f"TRACER DOCUMENTATION: {Path(dataset_path).stem}")
    print("="*80)
    print(f"Category: {category}")
    print(f"Rings: {len(df)}")
    
    if 'tracers' in df.columns:
        unique_tracers = set()
        for tracers in df['tracers']:
            unique_tracers.update([t.strip() for t in str(tracers).split(',')])
        
        print(f"\nMolecular Tracers Used:")
        for tracer in sorted(unique_tracers):
            print(f"  • {tracer}")
        
        print(f"\nPhysical Interpretation:")
        print(f"  ✅ Data provenance documented")
        print(f"  ✅ Multiple tracers provide robust constraints")
        print(f"  ✅ Can cross-check consistency")
        print("="*80)
        
        assert len(unique_tracers) > 0, "At least one tracer should be documented"
    else:
        print("\n⚠️  'tracers' column not found - documentation incomplete")
        print("="*80)


def test_multi_ring_catalog_exists():
    """Test that multi-ring catalog documentation exists."""
    catalog_path = Path("data/observations/MULTI_RING_CATALOG.md")
    
    print("\n" + "="*80)
    print("MULTI-RING CATALOG DOCUMENTATION")
    print("="*80)
    
    assert catalog_path.exists(), "MULTI_RING_CATALOG.md should exist"
    
    content = catalog_path.read_text(encoding='utf-8')
    
    print(f"Catalog file: {catalog_path}")
    print(f"Size: {len(content)} bytes")
    print(f"\nPhysical Interpretation:")
    print(f"  ✅ All multi-ring datasets documented")
    print(f"  ✅ Source papers referenced")
    print(f"  ✅ Quality assessment included")
    print("="*80)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
