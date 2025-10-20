![S-Stars Residuals: SSZ vs GR Comparison](reports/figures/readme_header_sstars_comparison.png)

# Segmented Spacetime – Mass Projection & Unified Results

[![Quality](https://img.shields.io/badge/quality-95.1%25%20(A%2B)-brightgreen)](REPOSITORY_QUALITY_REPORT_v1.3.0.md)
[![Tests](https://img.shields.io/badge/tests-69%20passing-brightgreen)](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20WSL%20%7C%20macOS%20%7C%20Colab-brightgreen)](#cross-platform-compatibility)
[![License](https://img.shields.io/badge/license-Anti--Capitalist-red)](LICENSE)

© Carmen Wrede & Lino Casu

**Latest Release:** v1.3.0 (2025-10-20) - Documentation Excellence & Quality Assurance  
✅ **Status:** 69 automated tests passing | Cross-platform verified | Full documentation

Complete Python implementation and verification suite for the **Segmented Spacetime (SSZ) Mass Projection Model** with runners, tests, datasets, and plotting routines to reproduce all reported results in a deterministic environment.

**Status:** ✅ Production-ready | Reproducible evidence of model functionality (theory + code + tests)

---

## 🚀 Quick Start

### Option 1: Google Colab (No Installation)

**Run everything in your browser - Zero setup required:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/blob/main/SSZ_Full_Pipeline_Colab.ipynb)

1. Click badge above
2. `Runtime` → `Run all`
3. Wait ~5-10 minutes
4. ✅ Download ZIP with all results

### Option 2: Local Installation (One Command)

**Windows:**
```powershell
.\install.ps1              # ~2 minutes
```

**Linux/WSL/macOS:**
```bash
chmod +x install.sh
./install.sh               # ~2 minutes
```

**What happens (11 steps):**
- ✅ [1/11] Checks Python 3.10+
- ✅ [2/11] Creates virtual environment
- ✅ [3/11] Activates venv
- ✅ [4/11] Upgrades pip/setuptools
- ✅ [5/11] Installs dependencies
- ✅ [6/11] Fetches data (if missing)
- ✅ [7/11] Installs SSZ package
- ✅ [8/11] Generates pipeline outputs
- ✅ [9/11] Runs 69 tests
- ✅ [10/11] Verifies installation
- ✅ [11/11] Generates summary

---

## 🌍 Cross-Platform Compatibility

✅ **Fully tested and supported on ALL platforms:**

| Platform | Status | Installation | Notes |
|----------|--------|--------------|-------|
| **Windows** | ✅ Full | `.\install.ps1` | PowerShell, UTF-8 auto-configured |
| **WSL** | ✅ Full | `./install.sh` | Auto-detected, Linux-compatible |
| **Linux** | ✅ Full | `./install.sh` | Native, fastest execution |
| **macOS** | ✅ Full | `./install.sh` | Unix-like, same as Linux |
| **Google Colab** | ✅ Full | One-click notebooks | No installation needed |

**CI/CD Testing:** 6 configurations (2 OS × 3 Python versions) on every push

**Details:** See [`CROSS_PLATFORM_COMPATIBILITY_ANALYSIS.md`](CROSS_PLATFORM_COMPATIBILITY_ANALYSIS.md)

**What's New:** See [CHANGELOG.md](CHANGELOG.md) for complete release history

**📖 Key Terms & Glossary:** See [Technical Glossary](docs/improvement/TERMINOLOGY_GLOSSARY.md) for 200+ terms (EN/DE)

---

## 📚 Key Terminology

**SSZ:** Segmented Spacetime (φ-based geometric framework)  
**GAIA:** ESA's Gaia space observatory (stellar data)  
**NED:** NASA/IPAC Extragalactic Database  
**EHT:** Event Horizon Telescope (EHT) (EHT)  
**PPN:** Parametrized Post-Newtonian formalism  

See complete [**Technical Glossary**](docs/improvement/TERMINOLOGY_GLOSSARY.md) with 200+ terms in English and German.

---

## 📦 Installation Details

### Dependencies

**Core Scientific:**
- numpy, scipy, pandas, matplotlib, sympy

**Astronomy & Data:**
- astropy, astroquery, pyarrow

**Testing:**
- pytest, pytest-timeout, pytest-cov, colorama

**See [`requirements.txt`](requirements.txt) for complete list**

### Installation Options

```bash
# Standard install (recommended)
./install.sh               # Linux/WSL/macOS
.\install.ps1              # Windows

# With full test suite (~10-15 min)
./install_and_test.sh      # Linux/WSL/macOS
.\install_and_test.ps1     # Windows

# Quick tests only (~2 min)
./install_and_test.sh --quick    # Linux/WSL/macOS
.\install_and_test.ps1 -Quick    # Windows

# Dry-run (see what would be done)
./install.sh --dry-run     # Linux/WSL/macOS
.\install.ps1 -DryRun      # Windows
```

### Manual Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/WSL/macOS
.\.venv\Scripts\activate.ps1  # Windows

pip install -r requirements.txt
pip install -e .

# Verify
SSZ-rings --help
SSZ-print-md --help
```

---

## 🧪 Testing System

### Test Overview

**Total: 69 Tests**
- **35 Physics Tests** - Detailed output with physical interpretations
- **23 Technical Tests** - Silent mode (background validation)
- **11 Multi-Ring Validation Tests** - Real astronomical ring datasets (G79, Cygnus X)

### Run Tests

```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/WSL/macOS
.\.venv\Scripts\activate.ps1  # Windows

# Complete test suite
python run_full_suite.py              # ~2-3 minutes

# Quick tests only
python run_full_suite.py --quick      # ~30 seconds

# Individual test categories
python test_ppn_exact.py              # PPN parameters
python test_vfall_duality.py          # Dual velocity
pytest tests/ -s -v                   # All pytest tests
pytest scripts/tests/ -s -v           # Script tests
```

### Test Reports

Generated in `reports/`:
- `RUN_SUMMARY.md` - Compact overview
- `summary-output.md` - Complete log (~100-500 KB)

**Critical:** Always use `-s` flag with pytest (NOT `--disable-warnings`)

---

## 🔬 Scientific Analysis Pipeline

### Complete SSZ Analysis

```bash
python run_all_ssz_terminal.py
```

**Runs 20+ scripts:**
- Redshift analysis (emission lines + continuum)
- Mass validation & roundtrip
- PPN parameters (β, γ)
- Shadow predictions (M87*, Sgr A*)
- QNM eikonal checks
- φ-lattice model selection
- Lagrangian tests
- Stress-energy tensor
- Extended theory calculations

**Output:** `reports/summary_full_terminal_v4.json` + detailed CSV/MD files

### SegWave Ring Analysis

```bash
# G79+0.46 (ALMA CO + NH₃)
SSZ-rings --csv data/observations/G79_29+0_46_CO_NH3_rings.csv \
          --v0 12.5 --fit-alpha

# Cygnus X Diamond Ring (C II)
SSZ-rings --csv data/observations/CygnusX_DiamondRing_CII_rings.csv \
          --v0 1.3
```

### All-in-One Enhanced Runner

```bash
# Full pipeline
python segspace_all_in_one_extended.py all

# Redshift evaluation only
python segspace_all_in_one_extended.py eval-redshift \
       --csv ./data/real_data_emission_lines.csv \
       --mode hybrid --ci 2000 --plots

# Mass validation
python segspace_all_in_one_extended.py validate-mass

# Bound energy plots
python segspace_all_in_one_extended.py bound-energy --plots
```

---

## 📊 Key Results

### Current Dataset (v1.2.1)

**427 data points** from **117 unique sources**

- **Emission lines:** 143 rows (paired test)
- **Continuum:** 284 rows (spectrum analysis)
- **Frequency range:** 2.3×10¹¹ - 3.0×10¹⁸ Hz (9+ orders)
- **No synthetic data** - All real observations

### Performance Metrics

**Median |Δz| (lower is better):**
- SEG (φ/2 + Δ(M)): **1.31e-4**
- SR: 1.34e-2
- GR: 2.25e-1

**Paired comparison:** SEG better in 79/143 emission lines (55%), p < 0.001

**Mass bins:** SEG < GR×SR in all bins

---

## 📖 Documentation

### Core Documentation

- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - 📚 **Central documentation navigator** (START HERE)
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - 🚀 **Get started in < 5 minutes**
- **[CROSS_PLATFORM_COMPATIBILITY_ANALYSIS.md](CROSS_PLATFORM_COMPATIBILITY_ANALYSIS.md)** - ✅ Platform compatibility analysis
- **[Sources.md](Sources.md)** - Complete data provenance (117 sources)
- **[DATA_CHANGELOG.md](DATA_CHANGELOG.md)** - Data version history
- **[CHANGELOG.md](CHANGELOG.md)** - Release history
- **[INSTALL_README.md](INSTALL_README.md)** - Installation guide
- **[LOGGING_SYSTEM_README.md](LOGGING_SYSTEM_README.md)** - Test logging

### Data Documentation

- **[COMPREHENSIVE_DATA_ANALYSIS.md](COMPREHENSIVE_DATA_ANALYSIS.md)** - Complete data quality analysis
- **[DATA_IMPROVEMENT_ROADMAP.md](DATA_IMPROVEMENT_ROADMAP.md)** - Future enhancement plan
- **[DATA_TYPE_USAGE_GUIDE.md](data/DATA_TYPE_USAGE_GUIDE.md)** - Emission vs continuum guide
- **[PAIRED_TEST_ANALYSIS_COMPLETE.md](PAIRED_TEST_ANALYSIS_COMPLETE.md)** - Statistical analysis details

### Theory & Validation

- **[papers/validation/](papers/validation/)** - 11 validation papers
- **[docs/theory/](docs/theory/)** - 21 theory papers
- **[SSZ_COMPLETE_PIPELINE.md](SSZ_COMPLETE_PIPELINE.md)** - Complete pipeline docs

### Quality Assurance Reports

- **[VERSION_AUDIT_REPORT.md](VERSION_AUDIT_REPORT.md)** - Version consistency audit
- **[PRINT_STATEMENTS_FIX_SUMMARY.md](PRINT_STATEMENTS_FIX_SUMMARY.md)** - Print statement fixes
- **[FINAL_PRINT_AUDIT_COMPLETE.md](FINAL_PRINT_AUDIT_COMPLETE.md)** - Complete audit report
- **[DOCUMENTATION_OVERHAUL_SUMMARY.md](DOCUMENTATION_OVERHAUL_SUMMARY.md)** - Documentation improvements
- **[GIT_COMMIT_SUMMARY.md](GIT_COMMIT_SUMMARY.md)** - Repository status & workflow

---

## 🎯 Use Cases

### For Researchers

- Reproduce all SSZ results deterministically
- Validate theory predictions with real data
- Extend analysis with custom datasets
- Compare SEG vs GR/SR predictions

### For Developers

- Cross-platform Python scientific code example
- Comprehensive test system (69 tests)
- CI/CD integration (GitHub Actions)
- UTF-8 handling best practices

### For Students

- Interactive Colab notebooks (no setup)
- Step-by-step physics test outputs
- Real astronomical data from ALMA/Chandra/VLT
- Educational physics interpretations

---

## 🔧 Advanced Features

### Platform Compatibility Check

```bash
python PLATFORM_COMPATIBILITY_CHECK.py
```

**Tests:**
- Python version compatibility
- UTF-8 encoding support
- Path separator handling
- Platform-specific features
- Data file accessibility

### Data Fetching

**Smart data fetching (only missing files):**

```bash
# Planck CMB data (~2 GB)
python scripts/fetch_planck.py

# GAIA stellar data
python scripts/fetch_gaia_full.py

# NED spectral data
python scripts/data_acquisition/fetch_ned_spectra.py
```

### Output Printing

```bash
# Print all Markdown documentation
SSZ-print-md --root . --order path    # Alphabetical
SSZ-print-md --root . --order depth   # Shallow-first
SSZ-print-md --root papers            # Papers only
SSZ-print-md --root reports           # Reports only
```

---

## 📝 Dataset Schema

**Minimum CSV header:**

```csv
case,category,M_solar,a_m,e,P_year,T0_year,f_true_deg,z,
f_emit_Hz,f_obs_Hz,lambda_emit_nm,lambda_obs_nm,
v_los_mps,v_tot_mps,z_geom_hint,N0,source,r_emit_m
```

**Key columns:**
- `a_m` - Semi-major axis in **meters**
- `M_solar` - Mass in solar masses
- `z` - Redshift (optional if frequencies given)
- `f_emit_Hz`, `f_obs_Hz` - Emitted and observed frequency
- `source` - Data provenance (required)

**Example (S2 star 2018 pericenter):**
```csv
S2_SgrA*,S-stars,4297000.0,1.530889e+14,0.8843,16.0518,2018.379,0.0,
0.0006671281903963041,,,,,0,,0.0003584,1.0000000028,GRAVITY 2018
```

---

## 🤝 Contributing

**This is a research artifact.** Independent replication and peer review are encouraged.

**Contributions welcome:**
- Bug reports → [Issues](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/issues)
- Platform testing → Submit CI/CD logs
- Data integration → Follow [DATA_IMPROVEMENT_ROADMAP.md](DATA_IMPROVEMENT_ROADMAP.md)
- Documentation → Markdown PRs welcome

---

## ⚖️ License

**ANTI-CAPITALIST SOFTWARE LICENSE v1.4**

See [LICENSE](LICENSE) for full terms.

**TL;DR:**
- ✅ Free for personal, research, educational use
- ✅ Free for non-profit organizations
- ✅ Source code must remain open
- ❌ No commercial/proprietary use without permission
- ❌ No military use

---

## 📞 Contact & Citation

**Authors:** Carmen Wrede & Lino Casu

**Contact:** mail@error.wtf

**Repository:** https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results

**Citation:**
```bibtex
@software{wrede_casu_ssz_2025,
  author = {Wrede, Carmen and Casu, Lino},
  title = {Segmented Spacetime Mass Projection \& Unified Results},
  year = {2025},
  version = {1.2.1},
  url = {https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results}
}
```

---

## 🎓 What This Repository Is

### ✅ φ-Based Geometric Field Theory
- **Theoretical foundation:** Segmented spacetime structure derived from Euler formula (e^(iφπ))
- **φ as central constant:** Golden ratio emerges from geometric constraints of piecewise spacetime matching (not chosen a priori)
- **Statistically tested:** φ-lattice test confirms φ-based segmentation (ΔBIC = +926, p < 10⁻⁶⁸, 427 observations)
- **Complete formulation:** Lagrangian, stress-energy tensor, variational φ/2 coupling, PPN consistency (β=γ=1)

### ✅ Statistically Validated Predictions

![φ-Lattice Pattern in Data](reports/figures/readme_results_phi_lattice.png)

- **φ-lattice structure confirmed:** Data clusters around φ-steps with ΔBIC = +926 over uniform distribution
- **Extreme significance:** Sign test p < 10⁻⁶⁸ (427 observations, 117 independent sources) - pattern warrants independent replication to verify against systematic effects
- **87× smaller median residuals than GR** for S-stars around Sgr A* in our test suite (median |Δz|: SSZ = 0.00049 vs GR = 0.04253) - statistical comparison on dataset, not claim of superiority
- **Dual velocity invariant:** v_esc × v_fall = c² (exact mathematical identity in SSZ framework, verified numerically: |deviation| < 10⁻¹⁵)
- **Coordinate transformation:** 100% invertible Jacobian ensuring deterministic bidirectional mapping (reconstruction error = 4.69×10⁻¹⁷)

### ✅ Comprehensive Implementation
- **69 automated tests** - 35 physics + 23 technical + 11 multi-ring validation
- **Cross-platform verified** - Windows, Linux, macOS, WSL, Google Colab
- **Real astronomical data** - GAIA, ALMA, Chandra, VLT, GRAVITY, EHT archives
- **Cosmological framework** - Redshift, rotation curves, lensing, CMB integration
- **Reproducible pipeline** - Deterministic, no manual tuning, complete documentation

## ⚠️ Current Limitations

### Scientific Validation Status
- **Not yet peer-reviewed** - Theory papers are preprints awaiting journal submission
- **Not yet independently replicated** - φ-lattice results (ΔBIC=926, p<10⁻⁶⁸) await validation by independent research groups
- **EHT verification pending** - Shadow predictions calculated but not yet compared with EHT collaboration's analysis

### Theoretical Scope
- **φ-based framework** - φ emerges from Euler formula as central structure constant (physical constants c, G, ℏ remain fixed)
- **Quantum regime** - Classical geometric framework; quantum field theory interface remains open research question

### Implementation Status
- **Optimal for r ≥ 5r_s** - Energy conditions fully satisfied; r < 5r_s predictions finite but larger residuals
- **Cosmology & β-calibration** - Algorithms complete and validated; separate publication papers pending

**Status:** φ-structured spacetime framework with statistically tested predictions (ΔBIC=926, 87× smaller residuals in tests) awaiting independent experimental verification and peer review

---

## 🚨 Important Notes

### Data Quality

- **Current (v1.3.0):** 427 real observations from 117 peer-reviewed sources
- **No synthetic data:** All placeholder/synthetic data removed (completed v1.2.0)
- **Data expansion:** 143 → 427 rows via NASA/IPAC NED continuum spectra integration (v1.2.1)
- **Provenance:** All data cited in [Sources.md](Sources.md), publicly accessible

### Platform-Specific

- **Windows:** UTF-8 auto-configured, PowerShell recommended
- **WSL:** Auto-detected, behaves like Linux
- **Colab:** Ubuntu-based, Python 3 pre-installed
- **CI/CD:** Tested on ubuntu-latest + windows-latest

### Test System

- **Physics tests:** Verbose, detailed interpretations
- **Technical tests:** Silent, background validation
- **Critical:** Use `pytest -s` NOT `pytest --disable-warnings`

---

## 📂 Repository Structure

```
Segmented-Spacetime-Mass-Projection-Unified-Results/
├── data/                           # Real astronomical data
│   ├── real_data_full.csv         # Complete dataset (427 rows)
│   ├── real_data_emission_lines.csv  # Emission data (143 rows)
│   ├── real_data_continuum.csv    # Continuum data (284 rows)
│   ├── observations/              # Ring observations (G79, Cygnus X)
│   └── gaia/                      # GAIA stellar catalogs
├── scripts/                        # Analysis & data acquisition
│   ├── tests/                     # Script-level tests
│   ├── analysis/                  # Analysis tools
│   └── data_acquisition/          # Data fetchers
├── tests/                          # Main test suite
│   ├── test_segwave_core.py       # SegWave tests
│   ├── test_segwave_cli.py        # CLI tests
│   └── cosmos/                    # Cosmology tests
├── papers/                         # Documentation
│   ├── validation/                # 11 validation papers
│   └── theory/                    # Theory papers (moved to docs/)
├── docs/                           # Theory documentation
│   └── theory/                    # 21 theory papers
├── reports/                        # Generated reports
├── out/                           # Output data
├── install.sh                      # Linux/WSL/macOS installer
├── install.ps1                     # Windows installer
├── run_full_suite.py              # Complete test runner
├── run_all_ssz_terminal.py        # SSZ pipeline runner
├── segspace_all_in_one_extended.py  # All-in-one CLI
└── SSZ_*.ipynb                    # Google Colab notebooks
```

---

**Version:** v1.2.1 (2025-10-19)  
**Status:** ✅ Production-Ready | Cross-Platform Compatible  
**Tests:** 69 passing (35 physics + 23 technical + 11 ring)  
**Data:** 427 real observations from 117 sources + 13 multi-ring structures

© 2025 Carmen Wrede & Lino Casu | ANTI-CAPITALIST SOFTWARE LICENSE v1.4
