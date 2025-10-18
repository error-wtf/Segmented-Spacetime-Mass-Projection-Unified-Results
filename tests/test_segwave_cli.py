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


class TestBundledDatasets:
    """Tests for bundled observational datasets"""
    
    def test_g79_dataset_exists(self):
        """Test G79.29+0.46 dataset exists and is loadable"""
        g79_csv = Path(__file__).resolve().parents[1] / "data" / "observations" / "G79_29+0_46_CO_NH3_rings.csv"
        
        if not g79_csv.exists():
            pytest.skip(f"G79.29+0.46 dataset not found: {g79_csv}")
        
        # Load and validate structure
        df = pd.read_csv(g79_csv)
        
        # Check required columns
        required_cols = ['ring', 'radius_pc', 'T', 'n', 'v_obs']
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"
        
        # Check data integrity
        assert len(df) == 10, "G79.29+0.46 should have 10 rings"
        assert df['T'].min() >= 20, "Temperature too low"
        assert df['T'].max() <= 80, "Temperature too high"
        assert df['v_obs'].min() >= 1.0, "Velocity too low"
        assert df['v_obs'].max() <= 16.0, "Velocity too high"
    
    def test_cygx_dataset_exists(self):
        """Test Cygnus X Diamond Ring dataset exists and is loadable"""
        cygx_csv = Path(__file__).resolve().parents[1] / "data" / "observations" / "CygnusX_DiamondRing_CII_rings.csv"
        
        if not cygx_csv.exists():
            pytest.skip(f"Cygnus X dataset not found: {cygx_csv}")
        
        # Load and validate structure
        df = pd.read_csv(cygx_csv)
        
        # Check required columns
        required_cols = ['ring', 'radius_pc', 'T', 'n', 'v_obs']
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"
        
        # Check data integrity
        assert len(df) == 3, "Cygnus X Diamond Ring should have 3 rings"
        assert df['v_obs'].std() < 0.1, "Velocity should be nearly constant"
        assert abs(df['v_obs'].mean() - 1.3) < 0.1, "Mean velocity should be ~1.3 km/s"
    
    def test_sources_json_exists(self):
        """Test sources manifest exists and contains required keys"""
        sources_json = Path(__file__).resolve().parents[1] / "data" / "observations" / "sources.json"
        
        if not sources_json.exists():
            pytest.skip(f"Sources manifest not found: {sources_json}")
        
        import json
        with open(sources_json, 'r', encoding='utf-8') as f:
            sources = json.load(f)
        
        # Check required object keys
        assert "G79.29+0.46" in sources, "Missing G79.29+0.46 in sources"
        assert "CygnusX_DiamondRing" in sources, "Missing CygnusX_DiamondRing in sources"
        
        # Check structure for G79
        g79 = sources["G79.29+0.46"]
        assert "papers_local" in g79, "Missing papers_local for G79"
        assert "tracers" in g79, "Missing tracers for G79"
        assert isinstance(g79["papers_local"], list), "papers_local should be list"
        assert len(g79["papers_local"]) > 0, "papers_local should not be empty"
    
    def test_sources_config_yaml_exists(self):
        """Test sources.yaml config exists and is loadable"""
        sources_yaml = Path(__file__).resolve().parents[1] / "config" / "sources.yaml"
        
        if not sources_yaml.exists():
            pytest.skip(f"Sources config not found: {sources_yaml}")
        
        import yaml
        with open(sources_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Check for any base_dir variant (new format supports multiple keys)
        has_base_dir = any(key.startswith('base_dir') for key in config.keys())
        assert has_base_dir, "Missing base_dir* keys in sources.yaml"
        
        # Check that at least one base_dir key has a valid path string
        base_dir_keys = [k for k in config.keys() if k.startswith('base_dir')]
        assert len(base_dir_keys) > 0, "No base_dir configuration found"
        
        # Verify at least one is a string path
        has_valid_path = any(isinstance(config[k], str) for k in base_dir_keys)
        assert has_valid_path, "At least one base_dir should be a string path"
    
    def test_load_sources_config_function(self):
        """Test load_sources_config function from io module"""
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        
        try:
            from ssz.segwave.io import load_sources_config
            
            # Test function call
            config = load_sources_config()
            
            # Validate structure
            assert 'base_dir' in config, "Missing base_dir in config"
            assert 'exists' in config, "Missing exists in config"
            assert 'source' in config, "Missing source in config"
            
            # Check types
            assert isinstance(config['base_dir'], str), "base_dir should be string"
            assert isinstance(config['exists'], bool), "exists should be boolean"
            assert isinstance(config['source'], str), "source should be string"
            
            # Warn if validation papers directory doesn't exist (non-fatal)
            if not config['exists']:
                print(f"\nWARNING: Validation papers directory not found: {config['base_dir']}")
                print(f"         Resolved from: {config['source']}")
                print("         This is non-fatal but affects paper validation features")
        
        except ImportError as e:
            pytest.skip(f"Cannot import load_sources_config: {e}")
    
    def test_g79_cli_smoke_run(self, temp_dir):
        """Smoke test: run CLI on G79.29+0.46 dataset"""
        g79_csv = Path(__file__).resolve().parents[1] / "data" / "observations" / "G79_29+0_46_CO_NH3_rings.csv"
        
        if not g79_csv.exists():
            pytest.skip(f"G79.29+0.46 dataset not found: {g79_csv}")
        
        out_table = temp_dir / "g79_test.csv"
        
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", str(g79_csv),
             "--v0", "12.5",
             "--alpha", "1.0",
             "--out-table", str(out_table)],
            capture_output=True,
            text=True
        )
        
        # Check success
        if result.returncode != 0:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        assert result.returncode == 0, f"G79 CLI run failed: {result.stderr}"
        
        # Check output exists
        assert out_table.exists(), "G79 output table not created"
        
        # Validate output
        df_out = pd.read_csv(out_table)
        assert len(df_out) == 10, "Output should have 10 rings"
        assert 'v_pred' in df_out.columns, "Missing v_pred column"
    
    def test_cygx_cli_smoke_run(self, temp_dir):
        """Smoke test: run CLI on Cygnus X Diamond Ring dataset"""
        cygx_csv = Path(__file__).resolve().parents[1] / "data" / "observations" / "CygnusX_DiamondRing_CII_rings.csv"
        
        if not cygx_csv.exists():
            pytest.skip(f"Cygnus X dataset not found: {cygx_csv}")
        
        out_table = temp_dir / "cygx_test.csv"
        
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT),
             "--csv", str(cygx_csv),
             "--v0", "1.3",
             "--alpha", "1.0",
             "--out-table", str(out_table)],
            capture_output=True,
            text=True
        )
        
        # Check success
        if result.returncode != 0:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        assert result.returncode == 0, f"Cygnus X CLI run failed: {result.stderr}"
        
        # Check output exists
        assert out_table.exists(), "Cygnus X output table not created"
        
        # Validate output
        df_out = pd.read_csv(out_table)
        assert len(df_out) == 3, "Output should have 3 rings"
        assert 'v_pred' in df_out.columns, "Missing v_pred column"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
