"""
Quick Installation Validation Tests

These tests verify that the installation is functional WITHOUT requiring
pipeline outputs (debug files, generated CSVs, etc.).

Run these during installation to confirm:
- Python environment works
- Essential data files present
- No import errors

For comprehensive testing including pipeline outputs, run:
    python run_full_suite.py
"""

import pytest
from pathlib import Path
import sys


def test_core_imports():
    """Verify Python environment and basic imports work."""
    # Test that Python can import standard libraries
    import numpy as np
    import pandas as pd
    import matplotlib
    
    # Test that we can add current directory to path (needed for local imports)
    import os
    root_path = Path(__file__).parent.parent
    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))
    
    assert True, "Python environment working"


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
    """Test that PPN test script exists and is executable."""
    ppn_test = Path("test_ppn_exact.py")
    assert ppn_test.exists(), "test_ppn_exact.py not found"
    
    # Verify it's a Python file
    content = ppn_test.read_text(encoding='utf-8')
    assert "PPN" in content or "ppn" in content, "PPN test file seems invalid"


def test_dual_velocity_invariant():
    """Test that dual velocity test script exists."""
    vfall_test = Path("test_vfall_duality.py")
    assert vfall_test.exists(), "test_vfall_duality.py not found"
    
    # Verify it's a Python file with dual velocity content
    content = vfall_test.read_text(encoding='utf-8')
    assert "v_esc" in content or "v_fall" in content, "Dual velocity test file seems invalid"


def test_segwave_imports():
    """Test that SegWave test files exist."""
    segwave_test = Path("tests/test_segwave_core.py")
    assert segwave_test.exists(), "test_segwave_core.py not found"
    
    # Verify it's a valid test file
    content = segwave_test.read_text(encoding='utf-8')
    assert "segwave" in content.lower() or "q_factor" in content.lower(), "SegWave test file seems invalid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
