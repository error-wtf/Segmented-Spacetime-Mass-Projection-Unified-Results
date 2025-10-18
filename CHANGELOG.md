# Changelog

All notable changes to the Segmented Spacetime Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.0] - 2025-10-18

### 🎉 Major Update: Complete Test System Overhaul

#### Added

**Test System:**
- Complete logging system capturing all output to `reports/summary-output.md` (~100-500 KB)
- 35 physics tests now show detailed physical interpretations
- 23 technical tests converted to silent background mode
- Smart data fetching system (checks existing files, never overwrites)

**New Scripts:**
- `scripts/fetch_planck.py` - Planck data downloader (2GB) with progress bar
- `COPY_TO_TEST_SUITES.ps1` - Project copy script for test suites

**Documentation (9 new files):**
- `TESTING_COMPLETE_GUIDE.md` - Master testing guide
- `tests/README_TESTS.md` - Tests directory documentation
- `scripts/tests/README_SCRIPTS_TESTS.md` - Scripts tests documentation
- `LOGGING_SYSTEM_README.md`, `INSTALL_README.md`, `DATA_FETCHING_README.md`
- `PHYSICS_TESTS_COMPLETE_LIST.md`, `VERIFICATION_COMPLETE.md`
- `REPO_UPDATE_CHECKLIST.md`, `LINUX_TEST_PLAN.md`

**Papers:**
- Added PDF versions of all theoretical papers (alongside MD)

#### Changed

**Test Output Format:**
- All 35 physics tests standardized with: Configuration → Results → Physical Interpretation
- Each test shows 3+ bullet points explaining physical meaning
- Unified format across all test files

**Test Runner:**
- `run_full_suite.py` captures ALL output to StringIO buffer
- Generates 2 files: `RUN_SUMMARY.md` (compact) + `summary-output.md` (complete log)
- Silent tests excluded from summary display

**Installation:**
- `install.ps1`/`install.sh` updated to 10 steps (added data checking)
- Step [8/10]: Check and fetch missing data files
- Auto-fetch Planck only if missing, never overwrites

**Updated Test Files:**
- `tests/test_segwave_core.py` - 16 tests verbose
- `scripts/tests/test_ssz_invariants.py` - 6 tests (added 3 new)
- All 6 root-level tests verbose

#### Fixed

**Critical Bugs:**
- 🔴 **Pytest I/O Crash**: Changed `--disable-warnings` to `-s` flag
  - Root cause: `ValueError: I/O operation on closed file`
  - Fixed in: `run_full_suite.py`, `install.ps1`, `install.sh`
  
- 🔴 **test_segmenter.py Import Error**: Removed non-existent `create_segments` import
  - Now uses correct `assign_segments_xy` API
  
- 🔴 **False "Failed: 3"**: Fixed summary counting logic
  - Silent tests no longer counted as failures

**Other Fixes:**
- Python cache clearing documented
- Shell script permissions on Linux
- Line ending issues

#### Performance

- Complete test suite: ~2-3 minutes
- Installation without Planck: ~2 minutes  
- Installation with Planck: ~20 minutes (connection dependent)
- Re-installation: ~2 minutes (skips existing data)

#### Statistics

- Physics Tests: 35 (all verbose with interpretations)
- Technical Tests: 23 (all silent)
- Modified Files: 15 (12 tests + 3 runners)
- New Files: 10 (9 docs + 1 script)

---

## [Unreleased]

### Added - 2025-01-18

#### Validation Papers Integration (`config/sources.yaml`)

**Windows/WSL Sources Configuration**

New configuration system for validation papers directory:
- **Base directory:** `H:\WINDSURF\VALIDATION_PAPER` (Windows)
- **WSL alternative:** `/mnt/h/WINDSURF/VALIDATION_PAPER`
- **Environment override:** `SSZ_SOURCES_DIR` (highest priority)

**Path Resolution:**
```python
from ssz.segwave import load_sources_config

config = load_sources_config()
print(config['base_dir'])    # H:\WINDSURF\VALIDATION_PAPER
print(config['exists'])      # True/False
print(config['source'])      # environment/config_windows/config_unix
```

**Features:**
- Automatic OS detection (Windows vs WSL/Linux)
- Smart fallback chain for cross-platform compatibility
- Non-fatal warnings if papers directory missing
- Enables offline validation against local PDF archive

**Usage:**
- Windows: `setx SSZ_SOURCES_DIR "H:\WINDSURF\VALIDATION_PAPER"`
- WSL: `export SSZ_SOURCES_DIR=/mnt/h/WINDSURF/VALIDATION_PAPER`

#### Segmented Radiowave Propagation Module (`ssz/segwave/`)

**New Feature: SSZ-Rings CLI Tool**

A complete implementation of radiowave propagation through segmented spacetime shells based on the γ_seg(r) formalism.

**Core Functionality:**
- `seg_wave_propagation.py`: Mathematical core implementing velocity evolution (v_k = v_{k-1} · q_k^{-α/2}) and frequency shifts
- `calib.py`: Alpha parameter calibration via RMSE minimization against observations
- `io.py`: CSV/JSON data handling for ring temperature, density, and velocity data
- `visuals.py`: Optional matplotlib-based plotting utilities

**CLI Tool (`ssz-rings`):**
- Command-line interface for velocity profile predictions
- Fixed or fitted α parameter modes
- Optional frequency tracking (ν_out = ν_in · γ^{-1/2})
- Customizable temperature/density coupling exponents (β, η)
- CSV table and text report outputs

**Data & Documentation:**
- Example dataset: `data/observations/ring_temperature_data.csv`
- Sources manifest: `data/observations/sources.json`
- Comprehensive guide: `docs/segwave_guide.md`

**Testing:**
- Unit tests: `tests/test_segwave_core.py` (deterministic mathematical validation)
- CLI integration tests: `tests/test_segwave_cli.py` (end-to-end workflow validation)

**Integration:**
- Added `ssz-rings` entry point to `pyproject.toml`
- No modifications to existing analysis pipelines (pure addition)
- Compatible with existing SSZ suite infrastructure

**Scientific Basis:**
- Implements segment-based velocity damping from Casu & Wrede segmented spacetime framework
- Validates against molecular ring observations (CO, NH3, CII tracers)
- Provides quantitative fit metrics (MAE, RMSE) for model assessment

**Usage Example:**
```bash
ssz-rings --csv data/observations/ring_temperature_data.csv \
          --v0 12.5 --fit-alpha \
          --out-table results.csv --out-report summary.txt
```

**Risks:** None - all changes are additive, no existing files modified or deleted.

---

## Previous Releases

### [1.0] - 2024-10-17

Initial release of Segmented Spacetime Suite with:
- Complete analysis pipeline
- Debian package infrastructure
- UTF-8 encoding fixes
- Repository portability improvements
- Comprehensive test suite

---

**Copyright © 2025 Carmen Wrede und Lino Casu**  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
