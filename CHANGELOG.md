# Changelog

All notable changes to the Segmented Spacetime Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
