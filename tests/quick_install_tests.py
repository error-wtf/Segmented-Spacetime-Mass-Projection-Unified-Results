"""
Quick Installation Validation Tests

These tests verify that the installation is functional WITHOUT requiring
pipeline outputs (debug files, generated CSVs, etc.).

Run these during installation to confirm:
- Core modules importable
- Essential data files present
- Basic physics calculations work

For comprehensive testing including pipeline outputs, run:
    python run_full_suite.py
"""

import pytest
from pathlib import Path


def test_core_imports():
    """Verify core SSZ modules can be imported."""
    import core.ssz
    import core.stats
    import core.transforms
    import core.segmenter
    assert True, "Core modules imported successfully"


def test_essential_data_files_exist():
    """Verify essential data files are present."""
    data_files = [
        "data/real_data_full.csv",
        "data/gaia/gaia_sample_small.csv",
    ]
    
    for file_path in data_files:
        path = Path(file_path)
        assert path.exists(), f"Missing essential data file: {file_path}"


def test_config_files_exist():
    """Verify configuration files exist."""
    config_files = [
        "sources.json",
        "pyproject.toml",
        "README.md",
    ]
    
    for file_path in config_files:
        path = Path(file_path)
        assert path.exists(), f"Missing config file: {file_path}"


def test_basic_ppn_calculation():
    """Test basic PPN parameter calculation."""
    from core.ssz import compute_ppn_params
    
    # Test with standard parameters
    beta, gamma = compute_ppn_params(M_sun=1.0, eps3=-4.8)
    
    # Should match GR in weak field
    assert abs(beta - 1.0) < 1e-10, f"β deviation too large: {abs(beta - 1.0)}"
    assert abs(gamma - 1.0) < 1e-10, f"γ deviation too large: {abs(gamma - 1.0)}"


def test_dual_velocity_invariant():
    """Test dual velocity invariant calculation."""
    from core.ssz import compute_dual_velocities
    import numpy as np
    
    # Test at r = 2 r_s
    M_kg = 1.989e30  # 1 solar mass
    r_s = 2 * 6.674e-11 * M_kg / (3e8)**2  # Schwarzschild radius
    r = 2.0 * r_s
    
    v_esc, v_fall = compute_dual_velocities(r, r_s)
    
    # Invariant: v_esc * v_fall = c²
    c_squared = (3e8)**2
    product = v_esc * v_fall
    rel_error = abs(product - c_squared) / c_squared
    
    assert rel_error < 1e-12, f"Dual velocity invariant failed: error = {rel_error}"


def test_segwave_imports():
    """Test SegWave module imports."""
    from segwave.core import calculate_q_factor, predict_velocities
    from segwave.cli import main as segwave_main
    assert True, "SegWave modules imported successfully"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
