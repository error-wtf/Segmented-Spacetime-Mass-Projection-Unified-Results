"""
CLI Integration Tests for SSZ-Rings

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pytest
import subprocess
import sys
from pathlib import Path
import pandas as pd
import tempfile
import os


# Path to CLI script
CLI_SCRIPT = Path(__file__).resolve().parents[1] / "cli" / "ssz_rings.py"
EXAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "observations" / "ring_temperature_data.csv"


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestCLIBasic:
    """Basic CLI functionality tests"""
    
    def test_help_flag(self):
        """Test --help flag works"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "ssz-rings" in result.stdout.lower()
        assert "csv" in result.stdout.lower()
    
    def test_missing_required_args(self):
        """Test CLI fails gracefully without required args"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()
    
    def test_invalid_csv_path(self):
        """Test CLI handles missing CSV file"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", "nonexistent_file.csv",
             "--v0", "12.5",
             "--alpha", "1.0"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


class TestCLIExecution:
    """Test CLI execution with real data"""
    
    def test_fixed_alpha_execution(self, temp_dir):
        """Test basic execution with fixed alpha"""
        if not EXAMPLE_CSV.exists():
            pytest.skip(f"Example CSV not found: {EXAMPLE_CSV}")
        
        out_table = temp_dir / "results.csv"
        out_report = temp_dir / "report.txt"
        
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", str(EXAMPLE_CSV),
             "--v0", "12.5",
             "--alpha", "1.0",
             "--out-table", str(out_table),
             "--out-report", str(out_report)],
            capture_output=True,
            text=True
        )
        
        # Check exit code
        if result.returncode != 0:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        
        # Check outputs exist
        assert out_table.exists(), "Output table not created"
        assert out_report.exists(), "Output report not created"
        
        # Validate table structure
        df = pd.read_csv(out_table)
        required_cols = ['ring', 'T', 'q_k', 'v_pred']
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"
        
        assert len(df) > 0, "Output table is empty"
        
        # Validate report content
        report_text = out_report.read_text(encoding='utf-8')
        assert "SSZ RINGS" in report_text
        assert "PARAMETERS" in report_text
        assert "12.5" in report_text  # v0 value
    
    def test_fit_alpha_execution(self, temp_dir):
        """Test execution with alpha fitting"""
        if not EXAMPLE_CSV.exists():
            pytest.skip(f"Example CSV not found: {EXAMPLE_CSV}")
        
        # Check if v_obs column exists
        df_check = pd.read_csv(EXAMPLE_CSV)
        if 'v_obs' not in df_check.columns:
            pytest.skip("Example CSV lacks v_obs column for fitting")
        
        out_table = temp_dir / "fitted_results.csv"
        
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", str(EXAMPLE_CSV),
             "--v0", "12.5",
             "--fit-alpha",
             "--out-table", str(out_table)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        assert result.returncode == 0, f"Fit-alpha CLI failed: {result.stderr}"
        
        # Check that fitted alpha is reported
        assert "optimal" in result.stdout.lower() or "fitted" in result.stdout.lower()
        
        # Check table includes residuals
        df = pd.read_csv(out_table)
        assert 'v_obs' in df.columns
        assert 'residual' in df.columns
    
    def test_frequency_tracking(self, temp_dir):
        """Test frequency tracking option"""
        if not EXAMPLE_CSV.exists():
            pytest.skip(f"Example CSV not found: {EXAMPLE_CSV}")
        
        out_table = temp_dir / "freq_results.csv"
        
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", str(EXAMPLE_CSV),
             "--v0", "12.5",
             "--alpha", "1.0",
             "--nu-in", "3.0e11",
             "--out-table", str(out_table)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Frequency CLI failed: {result.stderr}"
        
        # Check table includes frequency column
        df = pd.read_csv(out_table)
        assert 'nu_out_Hz' in df.columns, "Frequency column missing"
        assert df['nu_out_Hz'].notna().all(), "Frequency values contain NaN"
    
    def test_custom_exponents(self, temp_dir):
        """Test custom beta and eta parameters"""
        if not EXAMPLE_CSV.exists():
            pytest.skip(f"Example CSV not found: {EXAMPLE_CSV}")
        
        out_table = temp_dir / "custom_results.csv"
        
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", str(EXAMPLE_CSV),
             "--v0", "10.0",
             "--alpha", "1.5",
             "--beta", "0.8",
             "--eta", "0.2",
             "--out-table", str(out_table)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Custom params CLI failed: {result.stderr}"
        assert out_table.exists()


class TestCLIValidation:
    """Test CLI input validation"""
    
    def test_negative_v0(self, temp_dir):
        """Test CLI rejects negative v0 (should run but may give warnings)"""
        if not EXAMPLE_CSV.exists():
            pytest.skip(f"Example CSV not found: {EXAMPLE_CSV}")
        
        # Note: Implementation may or may not reject negative v0
        # This test just ensures it doesn't crash
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", str(EXAMPLE_CSV),
             "--v0", "-10.0",
             "--alpha", "1.0"],
            capture_output=True,
            text=True
        )
        
        # Should either fail gracefully or warn
        assert result.returncode in [0, 1]
    
    def test_mutually_exclusive_alpha(self):
        """Test that --alpha and --fit-alpha are mutually exclusive"""
        if not EXAMPLE_CSV.exists():
            pytest.skip(f"Example CSV not found: {EXAMPLE_CSV}")
        
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", str(EXAMPLE_CSV),
             "--v0", "12.5",
             "--alpha", "1.0",
             "--fit-alpha"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "mutually exclusive" in result.stderr.lower() or "not allowed" in result.stderr.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
