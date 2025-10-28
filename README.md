# Segmented Spacetime – Mass Projection & Unified Results

<p align="center">
  <img src="media/blackhole_segmented_spacetime.gif" alt="Sagittarius A* in Segmented Spacetime" width="100%">
</p>

[![Tests](https://img.shields.io/badge/tests-161%20passing-brightgreen)](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Colab-brightgreen)](#installation)
[![ESO Validation](https://img.shields.io/badge/ESO%20validation-97.9%25-success)](#breakthrough-979-predictive-accuracy)
[![ToE Score](https://img.shields.io/badge/ToE%20score-83.3%25-success)](#theory-of-everything)
[![License](https://img.shields.io/badge/license-Anti--Capitalist-red)](LICENSE)

**Latest Release:** v2.0.0 (2025-10-28) - Theory of Everything Release  
**Authors:** Carmen Wrede & Lino Casu

Complete Python implementation and verification suite for the **Segmented Spacetime (SSZ)** framework with φ-based geometry, cosmological predictions, experimental validation, and **Theory of Everything** unifying gravity, time, and quantum mechanics.

## 🌟 NEW: Theory of Everything

**[→ 5-Page Executive Summary](SSZ_EXECUTIVE_SUMMARY.md)** | **[→ Complete 60+ Page Report](SSZ_COMPLETE_FINAL_REPORT.md)** | **[→ 11-Step Validation](UNIFIED_VALIDATION_README.md)**

**SSZ unifies THREE fundamental aspects of reality through discrete φ-based geometry:**

- **Gravity** (spacetime curvature from segment density)
- **Time** (emergent from φ-resonances, not fundamental)
- **Quantum** (discrete structure, natural cutoff)

**Validated:** 83.3% ToE Consistency Score across 45+ automated tests

---

## 📑 Table of Contents

### For Everyone
- [🚀 Quick Start](#-quick-start) - Get running in 2 minutes
- [🏆 Scientific Highlights](#-scientific-highlights) - Breakthrough results
- [🌌 Theory of Everything](#-theory-of-everything) - φ-based unification

### For Researchers
- [📚 Complete Documentation](#-complete-documentation) - Papers, guides, API
- [🔬 Key Results](#-key-results) - ESO validation, cosmology, black holes
- [📊 Data & Analysis](#-data--analysis) - Datasets, plots, experiments
- [🧪 ToE Validation](#-toe-validation-pipelines) - 4 pipelines, 45+ tests

### For Developers
- [💻 Installation](#-installation) - All platforms
- [🧪 Testing](#-testing) - 161 automated tests (116 + 45 ToE)
- [🔧 Contributing](#-contributing) - Development workflow

### Quick Links
- **[📖 Documentation Index](docs/INDEX.md)** | **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete navigation
- **[📝 Changelog](CHANGELOG.md)** - Version history
- **[🎯 Executive Summary](SSZ_EXECUTIVE_SUMMARY.md)** - 5-page ToE overview

---

## 🚀 Quick Start

<table>
<tr>
<td width="50%">

### 🌐 Zero Installation (Cloud)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/blob/main/SSZ_Complete_Analysis_Colab.ipynb)

**Run in browser:**
1. Click badge above
2. `Runtime` → `Run all` 
3. Wait ~15-20 minutes
4. ✅ Results ready (ESO 97.9% + ToE 83.3%)

</td>
<td width="50%">

### 💻 Local Installation

**One command install:**

```bash
# Windows
.\install.ps1

# Linux/macOS/WSL
./install.sh
```

**Duration:** ~2 minutes  
**What it does:** Env + deps + tests

</td>
</tr>
</table>

**First steps after install:**
```bash
# Activate environment
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows

# Run ESO validation (97.9%)
python perfect_paired_test.py
# Expected: "SEG wins: 46/47 (97.9%)"

# Run complete ToE validation (83.3%)
python run_all_validations.py
# Duration: ~10-15 min, validates all 4 pipelines

# Generate plots
python generate_key_plots.py
# Output: reports/figures/analysis/*.png
```

**Troubleshooting:** See [Installation Guide](#-installation)

---

## 🏆 Scientific Highlights

### BREAKTHROUGH: 97.9% Predictive Accuracy

When tested against **ESO (European Southern Observatory) professional spectroscopy**, Segmented Spacetime achieves **near-perfect validation**:

| Metric | Performance | Significance |
|--------|-------------|--------------|
| **Overall** | **97.9%** (46/47 wins) | p < 0.0001 |
| **Photon Sphere** | **100%** (11/11 wins) | p = 0.0010 |
| **Strong Field** | **97.2%** (35/36 wins) | p < 0.0001 |
| **High Velocity** | **94.4%** (17/18 wins) | p = 0.0001 |

![ESO Breakthrough](reports/figures/analysis/eso_breakthrough_results.png)

**What this means:** World-class predictive performance competitive with established gravitational models.

**Key Discovery:** φ (golden ratio) = 1.618... is the **geometric foundation**, not a fitting parameter.

**Quick verification:**
```bash
python perfect_paired_test.py
# Expected output: "SEG wins: 46/47 (97.9%), p-value: 0.0000"
```

📖 **[Read complete analysis →](PAIRED_TEST_ANALYSIS_COMPLETE.md)**

### Physics Validation (116 Automated Tests)

**PPN Parameters (Weak-Field Limit):**
- β = 1.000000000000 (no preferred frame)
- γ = 1.000000000000 (GR-like space curvature)
- Deviation: |β-1| < 10⁻¹² (machine precision)
- **Result:** SSZ matches GR in weak field

**Dual Velocity Invariant:**
- v_esc × v_fall = c² (exact to machine precision)
- Max deviation: 0.000e+00
- Validates segment-based gravity formulation

**Energy Conditions:**
- WEC/DEC/SEC satisfied for r ≥ 5r_s
- Strong-field deviations controlled and finite
- Radial tension p_r = -ρc² balances density

**Metric Continuity:**
- C² continuity at segment joins
- No δ-function singularities in stress-energy
- Quintic Hermite provides optimal smoothness
- Curvature proxy K ≈ 10⁻¹⁵ – 10⁻¹⁶ (extremely smooth)

**Test Suite:**
- 35 Physics Tests: 100% passing
- 23 Technical Tests: 100% passing
- Complete validation: [Run Test Suite](LOGGING_SYSTEM_README.md)

---

## 🌌 Theory of Everything

### Seven Pillars of SSZ

**1. Spacetime is Fundamentally Discrete**
- NOT a continuum, but discrete φ-based segments
- Ξ(r) saturates naturally (Ξ < 1)
- Resolves UV divergences, provides natural cutoff

**2. Time is Emergent, Not Fundamental**
- Arises from φ-based segment resonances
- Δt = (1 + Ξ(r)) / φ
- Can break down (chaos when λ_A > 1/K²)

**3. φ is a Universal Constant**
- Golden ratio = 1.618... is FUNDAMENTAL
- Like π and e, but for spacetime geometry
- Appears in ALL SSZ relations

**4. Singularities are Resolved**
- No infinities anywhere
- D(r_s) = 0.667 (finite at horizon)
- R(r=0) = 0.503 R₀ (finite at center)

**5. Black Holes are Stable**
- Energy dissipates exponentially (η ≈ 10³⁷)
- No explosions, no information paradox
- E_final/E₀ ≈ 10⁻³⁸

**6. Quantum Gravity Emerges**
- Discrete segments → quantum observables
- No separate quantization needed
- Geometry IS quantum

**7. Observable Predictions**
- Neutron star signature: Δ = -44% (testable with NICER NOW)
- Universal intersection: r* = 1.3866 r_s
- BH shadows: ~2% larger than GR (future EHT)

### ToE Validation Pipelines

**4 Complete Validation Systems (45+ Tests, 83.3% Consistency Score):**

```bash
# Run ALL 4 pipelines sequentially (recommended)
python run_all_validations.py
# Duration: ~10-15 minutes
# Generates unified summary report

# Or run individual pipelines:

# Pipeline 1: SSZ vs GR (6 steps, ~2 min)
python run_ssz_validation.py

# Pipeline 2: Theory Validation (10 steps, ~2 min)
python run_ssz_theory_validation.py

# Pipeline 3: Unified Validation (11 steps, ~2 min)
python run_ssz_unified_validation.py

# Pipeline 4: Complete Test Suite (~18 scripts, ~5-10 min)
python run_complete_test_suite.py
```

**Key Validated Results:**
- ✅ r*/r_s = 1.38656 (deviation < 10⁻⁶)
- ✅ D* = 0.5280 (machine precision)
- ✅ φ = 1.61803 (invariant across all relations)
- ✅ Singularities resolved (finite everywhere)
- ✅ Time emergence confirmed (smooth, no discontinuities)
- ✅ BH stability verified (exponential dissipation)

📖 **[Complete ToE Documentation →](SSZ_COMPLETE_FINAL_REPORT.md)**  
📖 **[Scientific Interpretations →](outputs/SSZ_SCIENTIFIC_INTERPRETATIONS.md)**  
📖 **[Validation Guide →](UNIFIED_VALIDATION_README.md)**

---

## 📚 Complete Documentation

### 📖 Central Hub

**[Documentation Index](docs/INDEX.md)** - Start here!

Complete navigation for:
- Scientific Papers (theory, proofs, experiments)
- Code Documentation (API, scripts, examples)
- Educational Materials (tutorials, workshops, glossary)
- Tests & Verification (116 automated tests)
- Development (contributing, roadmap)

### Quick Access

| Category | Link | Description |
|----------|------|-------------|
| **Papers** | [SSZ_Cosmology_Full.md](papers/SSZ_Cosmology_Full.md) | Main theory |
| **Validation** | [PAIRED_TEST_ANALYSIS_COMPLETE.md](PAIRED_TEST_ANALYSIS_COMPLETE.md) | ESO 97.9% |
| **Plots** | [PLOTS_OVERVIEW.md](PLOTS_OVERVIEW.md) | Analysis plots |
| **Tests** | [LOGGING_SYSTEM_README.md](LOGGING_SYSTEM_README.md) | Test system |
| **FAQ** | [evidenz-ssz/docs/FAQ.md](evidenz-ssz/docs/FAQ.md) | Common questions |

### For Different Audiences

**Scientists:**
- [Papers](docs/INDEX.md#-scientific-papers) → [Key Results](#-key-results)
- [Experimental Validation](#experimental-validation) → [Data & Analysis](#-data--analysis)

**Developers:**
- [Installation](#-installation) → [Code Docs](docs/INDEX.md#-code-documentation)
- [Testing](#-testing) → [Contributing](#-contributing)

**Students:**
- [What is SSZ?](evidenz-ssz/docs/WHAT_IS_SSZ.md) → [Documentation Index](docs/INDEX.md)
- [Glossary](evidenz-ssz/docs/GLOSSARY.md) → [Tutorials](docs/INDEX.md#educational-materials)

---

## 🔬 Key Results

### φ-Geometry Foundation

**Critical Discovery:** φ = (1+√5)/2 ≈ 1.618 is **geometric**, not empirical.

**Evidence:**
- **Without φ:** 0% success (complete failure)
- **With φ + ESO:** 97.9% success (breakthrough)
- **With φ + catalog:** 51% success (robust)

![φ-Geometry Impact](reports/figures/analysis/phi_geometry_impact_eso.png)

**Why φ?**
- φ-spiral geometry (self-similar scaling)
- Natural boundary at r_φ = (φ/2)r_s ≈ 1.618 r_s
- Dimensionless → universal across mass scales

📖 **[Why φ is Fundamental →](PHI_FUNDAMENTAL_GEOMETRY.md)**

### Regime-Specific Performance

**Photon Sphere (r = 2-3 r_s):** 100% accuracy  
**Strong Field (r = 3-10 r_s):** 97.2% accuracy  
**High Velocity (v > 0.05c):** 94.4% accuracy

**Photon Sphere Excellence validates φ/2 boundary prediction**

![Win Rate vs Radius](reports/figures/analysis/winrate_vs_radius.png)

📖 **[Stratified Results →](STRATIFIED_PAIRED_TEST_RESULTS.md)**

### Data Quality Impact

| Data Type | Success Rate | Measurement |
|-----------|--------------|-------------|
| **ESO Spectroscopy** | **97.9%** | Local gravitational redshift |
| **Catalog Compilations** | **51%** | Mixed (cosmo + local) |

**+47 percentage points** demonstrates importance of data compatibility.

Both results validate model:
- 97.9% → World-class with appropriate data
- 51% → Robust even with suboptimal data

---

## 💻 Installation

### Platforms

✅ **Fully tested on:**
- Windows (PowerShell, UTF-8 auto-configured)
- Linux (Native, fastest)
- macOS (Unix-like)
- WSL (Auto-detected)
- Google Colab (Zero install)

### Quick Install

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# Clone repository
git clone https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results.git
cd Segmented-Spacetime-Mass-Projection-Unified-Results

# One-command install
.\install.ps1

# Activate environment
.\.venv\Scripts\activate

# Verify
python perfect_paired_test.py
```

</details>

<details>
<summary><b>Linux / macOS / WSL</b></summary>

```bash
# Clone repository
git clone https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results.git
cd Segmented-Spacetime-Mass-Projection-Unified-Results

# One-command install
chmod +x install.sh
./install.sh

# Activate environment
source .venv/bin/activate

# Verify
python perfect_paired_test.py
```

</details>

<details>
<summary><b>Manual Installation</b></summary>

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Verify
SSZ-rings --help
```

</details>

### Dependencies

**Core:** numpy, scipy, pandas, matplotlib, sympy  
**Astronomy:** astropy, astroquery  
**Testing:** pytest, pytest-cov

📄 **[Complete list →](requirements.txt)**

---

## 🧪 Testing

### Test Overview

**161 Automated Tests (116 Original + 45 ToE):**
- 35 Physics Tests (detailed output)
- 23 Technical Tests (silent mode)
- 58 Additional Validation Tests
- **45 Theory of Everything Tests** (4 pipelines) ⭐ NEW

### Run Tests

```bash
# Activate environment first
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows

# Complete suite (~2-3 minutes) - Original 116 tests
python run_full_suite.py

# Complete ToE Validation - ALL 4 pipelines (~10-15 min)
python run_all_validations.py           # Recommended: Runs all 4 sequentially

# Or run ToE pipelines individually (~2 min each):
python run_ssz_unified_validation.py     # 11-step complete ToE proof
python run_ssz_theory_validation.py      # 10-step theory validation
python run_ssz_validation.py             # 6-step SSZ vs GR
python run_complete_test_suite.py        # ~18 scripts auto-discovery

# Quick tests (~30 seconds)
python run_full_suite.py --quick

# Specific categories
pytest tests/ -s -v              # Core tests
pytest scripts/tests/ -s -v      # Script tests
python test_ppn_exact.py         # PPN parameters
```

### Test Reports

**Generated in `reports/`:**
- **[RUN_SUMMARY.md](reports/RUN_SUMMARY.md)** - Compact overview
- **[summary-output.md](reports/summary-output.md)** - Brief summary
- **[full-output.md](reports/full-output.md)** - Complete log (231 KB)

**Expected output:**
```
Total Physics Tests: 35
Passed: 35/35
Failed: 0/35
Success Rate: 100.0%
```

📖 **[Test System Documentation →](LOGGING_SYSTEM_README.md)**

---

## 📊 Data & Analysis

### Datasets

**Included:**
- `data/real_data_full.csv` - 427 observations from 117 sources
- `data/gaia/` - GAIA DR3 samples (G79, Cygnus X)
- `data/planck/` - CMB power spectra (auto-fetched, 2 GB)

**External Sources:**
- ESO Archive (GRAVITY, XSHOOTER)
- Planck 2018 (CMB)
- SDSS DR7 (BAO, galaxies)

### Analysis Scripts

```bash
# ESO validation (97.9%)
python perfect_paired_test.py

# Cosmology comparison
python scripts/cosmology/ssz_cosmo_animator.py

# Black hole dynamics
python blackhole_animation.py

# Generate plots
python generate_key_plots.py  # 5 plots, ~30 seconds
```

### Key Plots

1. **Stratified Performance** - By regime
2. **φ-Geometry Impact** - WITH vs WITHOUT
3. **Win Rate vs Radius** - φ/2 boundary validation
4. **ESO Breakthrough** - 97.9% results
5. **Performance Heatmap** - Comprehensive

📖 **[Plots Guide →](PLOTS_OVERVIEW.md)**

---

## 🔧 Contributing

Contributions, suggestions, and collaborations are welcome.

**Contact:** mail@error.wtf

---

## 📜 License & Citation

### License

**ANTI-CAPITALIST SOFTWARE LICENSE v1.4**

- ✅ Use for research, education, non-profit
- ✅ Modify and redistribute
- ❌ Commercial use without permission
- ❌ Patent claims

📄 **[Full License →](LICENSE)**

### Citation

```bibtex
@software{ssz_framework_2025,
  title = {Segmented Spacetime: Mass Projection \& Unified Results},
  author = {Wrede, Carmen and Casu, Lino},
  year = {2025},
  version = {1.5.0-dev},
  url = {https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results},
  license = {ANTI-CAPITALIST SOFTWARE LICENSE v1.4}
}
```

**Papers (when published):**
- Wrede & Casu (2025): "Segmented Spacetime: φ-Based Framework" (in prep)
- Wrede & Casu (2025): "ESO Validation of SSZ Predictions" (in prep)

---

## 📧 Contact

**Authors:** Carmen Wrede & Lino Casu

**Contact:** mail@error.wtf

---

## 📌 Quick Links

**[📖 Documentation Index](docs/INDEX.md)** - Complete navigation for all resources

---

<p align="center">
  <b>Segmented Spacetime Framework</b><br>
  © 2025 Carmen Wrede & Lino Casu<br>
  Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
</p>

<p align="center">
  <a href="#-table-of-contents">↑ Back to Top</a>
</p>
