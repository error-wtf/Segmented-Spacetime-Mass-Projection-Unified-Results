# Segmented Spacetime – Mass Projection & Unified Results

<p align="center">
  <img src="media/blackhole_segmented_spacetime.gif" alt="Sagittarius A* in Segmented Spacetime" width="100%">
</p>

[![Tests](https://img.shields.io/badge/tests-116%20passing-brightgreen)](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Colab-brightgreen)](#installation)
[![ESO Validation](https://img.shields.io/badge/ESO%20validation-97.9%25-success)](#breakthrough-979-predictive-accuracy)
[![License](https://img.shields.io/badge/license-Anti--Capitalist-red)](LICENSE)

**Latest Release:** v1.5.0-dev (2025-10-27) - Trilingual Video System + Visual Animations  
**Authors:** Carmen Wrede & Lino Casu

Complete Python implementation and verification suite for the **Segmented Spacetime (SSZ)** framework with φ-based geometry, cosmological predictions, and experimental validation.

---

## 📑 Table of Contents

### For Everyone
- [🚀 Quick Start](#-quick-start) - Get running in 2 minutes
- [🌀 Visual Gallery](#-visual-gallery) - Animations & Videos
- [🏆 Scientific Highlights](#-scientific-highlights) - Breakthrough results

### For Researchers
- [📚 Complete Documentation](#-complete-documentation) - Papers, guides, API
- [🔬 Key Results](#-key-results) - ESO validation, cosmology, black holes
- [📊 Data & Analysis](#-data--analysis) - Datasets, plots, experiments

### For Developers
- [💻 Installation](#-installation) - All platforms
- [🧪 Testing](#-testing) - 116 automated tests
- [🔧 Contributing](#-contributing) - Development workflow

### Quick Links
- **[📖 Documentation Index](docs/INDEX.md)** ← ⭐ **Complete navigation hub**
- **[✅ TODO List](TODO_DOCUMENTATION_UPLOAD.md)** ← Current session tasks
- **[📝 Changelog](CHANGELOG.md)** - Version history

---

## 🚀 Quick Start

<table>
<tr>
<td width="50%">

### 🌐 Zero Installation (Cloud)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/blob/main/SSZ_Full_Pipeline_Colab.ipynb)

**Run in browser:**
1. Click badge above
2. `Runtime` → `Run all`
3. Wait ~5-10 minutes
4. ✅ Results ready

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

# Run quick validation
python perfect_paired_test.py
# Expected: "SEG wins: 46/47 (97.9%)"

# Generate plots
python generate_key_plots.py
# Output: reports/figures/analysis/*.png
```

**Troubleshooting:** See [Installation Guide](#-installation)

---

## 🌀 Scientific Animations

**5 Key Visualizations** (GIFs available in repository)

### 1️⃣ Big Bang vs. Segmented Spacetime
No singularity, finite origin - comparison between classical ΛCDM model and SSZ framework.  
→ [📖 Read detailed explanation](docs/ssz_bigbang_vs_ssz_demo.md)

### 2️⃣ Mathematical Proof v6
C² continuity and stability analysis showing resonance-driven expansion.  
→ [📖 Read detailed explanation](docs/ssz_proof_anim_v6.md)

### 3️⃣ Cosmological Comparison
ΛCDM vs SSZ based on Hubble diagram, BAO, and large-scale structure data.  
→ [📖 Read detailed explanation](docs/ssz_cosmo_anim.md)

### 4️⃣ Black Holes – Segmented Spacetime
Sagittarius A* simulation showing no singularity, finite segment density.  
→ [📖 Read detailed explanation](docs/blackhole_segmented_spacetime.md)

### 5️⃣ Energy is Finite
Black Hole Bomb experiment validates segment damping mechanism.  
→ [📖 Read detailed explanation](docs/ssz_bomb_animation.md)

**Note:** All animations available in `assets/ssz_animations/` directory

### Videos (Trilingual Series)

**6-Part Educational Series** (DE 🇩🇪 | EN 🇬🇧 | IT 🇮🇹)

| Part | Topic | Duration | Audio Scripts |
|------|-------|----------|---------------|
| 1 | Big Bang vs Segmentation | 19s | [View](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md#teil-1) |
| 2 | Cosmological Observations | 19s | [View](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md#teil-2) |
| 3 | Mathematical Stability | 19s | [View](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md#teil-3) |
| 4 | Black Holes (No Singularity) | 20s | [View](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md#teil-4) |
| 5 | Stellar Nucleosynthesis | 21s | [View](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md#teil-5) |
| 6 | Energy is Finite | 18s | [View](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md#teil-6) |

**Total Duration:** ~2 minutes per language  
**Status:** 🔄 Production in progress  
**YouTube:** Coming soon

**Resources:**
- [Audio Scripts Archive](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md) - All texts (DE/EN/IT)
- [Video Production Guide](evidenz-ssz/videos/README.md) - Workflow

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

### Core Principles

<table>
<tr>
<td width="25%">

#### φ-Geometry
Golden ratio emerges as natural spacetime boundary

</td>
<td width="25%">

#### No Singularities
Segment density provides natural cut-off

</td>
<td width="25%">

#### Energy Finite
Segment damping prevents runaway growth

</td>
<td width="25%">

#### Testable
97.9% accuracy vs professional observations

</td>
</tr>
</table>

### Experimental Validation

**Black Hole Bomb (2024):**
- ✅ Braidotti et al. experiment validated
- ✅ SSZ stabilizes -2 unstable modes
- ✅ 96.6% theorem validation (348 configs)

**Cosmology:**
- ✅ Hubble diagram fit
- ✅ BAO compatible
- ✅ CMB (Planck 2018) consistent
- ✅ LSS: 2.3σ better than ΛCDM

**Black Holes:**
- ✅ Sagittarius A* (4.15×10⁶ M☉)
- ✅ Event Horizon Telescope compatible
- ✅ S-Stars orbital dynamics
- ✅ No information paradox

---

## 📚 Complete Documentation

### 📖 Central Hub

**[Documentation Index](docs/INDEX.md)** ← ⭐ **Start here!**

Complete navigation for:
- Visual Animations (6 detailed explanations)
- Scientific Papers (theory, proofs, experiments)
- Code Documentation (API, scripts, examples)
- Educational Materials (tutorials, workshops, glossary)
- Videos (production workflow, metadata)
- Tests & Verification (116 automated tests)
- Development (contributing, roadmap, TODO)

### Quick Access

| Category | Link | Description |
|----------|------|-------------|
| **Papers** | [SSZ_Cosmology_Full.md](papers/SSZ_Cosmology_Full.md) | Main theory |
| **Validation** | [PAIRED_TEST_ANALYSIS_COMPLETE.md](PAIRED_TEST_ANALYSIS_COMPLETE.md) | ESO 97.9% |
| **Videos** | [SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md) | All audio scripts |
| **Plots** | [PLOTS_OVERVIEW.md](PLOTS_OVERVIEW.md) | Visual guide |
| **Tests** | [LOGGING_SYSTEM_README.md](LOGGING_SYSTEM_README.md) | Test system |
| **FAQ** | [evidenz-ssz/docs/FAQ.md](evidenz-ssz/docs/FAQ.md) | Common questions |

### For Different Audiences

**Scientists:**
- [Visual Animations](#visual-gallery) → [Papers](docs/INDEX.md#-scientific-papers)
- [Key Results](#-key-results) → [Experimental Validation](#experimental-validation)

**Developers:**
- [Installation](#-installation) → [Code Docs](docs/INDEX.md#-code-documentation)
- [Testing](#-testing) → [Contributing](#-contributing)

**Students:**
- [What is SSZ?](evidenz-ssz/docs/WHAT_IS_SSZ.md) → [Visual Gallery](#visual-gallery)
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

**116 Automated Tests:**
- 35 Physics Tests (detailed output)
- 23 Technical Tests (silent mode)
- 58 Additional Validation Tests

### Run Tests

```bash
# Activate environment first
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows

# Complete suite (~2-3 minutes)
python run_full_suite.py

# Quick tests (~30 seconds)
python run_full_suite.py --quick

# Specific categories
pytest tests/ -s -v              # Core tests
pytest scripts/tests/ -s -v      # Script tests
python test_ppn_exact.py         # PPN parameters
```

### Test Reports

**Generated in `reports/`:**
- `RUN_SUMMARY.md` - Compact overview
- `summary-output.md` - Brief summary
- `full-output.md` - Complete log (231 KB)

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

### Current Tasks

**[📋 TODO List](TODO_DOCUMENTATION_UPLOAD.md)** ← **Current session priorities**

**High Priority:**
- [ ] Video scripts ins Repo kopieren
- [ ] Git LFS konfigurieren (große GIFs)
- [ ] FFmpeg installieren & Videos neu erstellen
- [ ] YouTube Upload vorbereiten

**Medium Priority:**
- [ ] Papers aktualisieren (Part 5 & 6)
- [ ] Tests für Video-Production
- [ ] Animation Creation Guide
- [ ] GitHub Release v1.5.0

### Development Workflow

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Segmented-Spacetime-Mass-Projection-Unified-Results.git
   ```

2. **Create Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make Changes**
   - Follow [Coding Standards](CODING_STANDARDS.md)
   - Add tests for new features
   - Update documentation

4. **Test**
   ```bash
   python run_full_suite.py
   pytest -s -v
   ```

5. **Submit PR**
   - Clear description
   - Link related issues
   - Pass all CI checks

### Guidelines

- **Code:** PEP 8, type hints, docstrings
- **Tests:** Coverage >80%, physics interpretations
- **Docs:** Markdown, cross-references, examples
- **Commits:** Conventional commits format

📖 **[Development Guide →](DEVELOPMENT_SETUP.md)**

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

## 📧 Contact & Support

**Authors:**
- **Carmen Wrede** - carmen.wrede@error-wtf.de
- **Lino Casu** - lino.casu@error-wtf.de

**Community:**
- **Issues:** [GitHub Issues](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/issues)
- **Discussions:** [GitHub Discussions](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/discussions)

**Collaboration:**
- Academic partnerships welcome
- Open source contributions encouraged
- Educational use permitted (with attribution)

---

## 📌 Quick Links

### Documentation
- [📖 Documentation Index](docs/INDEX.md) - Complete navigation
- [📋 TODO List](TODO_DOCUMENTATION_UPLOAD.md) - Current tasks
- [📝 Changelog](CHANGELOG.md) - Version history
- [❓ FAQ](evidenz-ssz/docs/FAQ.md) - Common questions

### Key Papers
- [SSZ Cosmology](papers/SSZ_Cosmology_Full.md) - Main theory
- [Black Holes](papers/SSZ_Black_Holes.md) - No singularities
- [Mathematical Proof](papers/SSZ_Mathematical_Proof.md) - C² continuity
- [ESO Validation](PAIRED_TEST_ANALYSIS_COMPLETE.md) - 97.9% accuracy

### Resources
- [Animation Explanations](docs/) - 6 detailed docs
- [Audio Scripts](docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md) - DE/EN/IT texts
- [Plots Guide](PLOTS_OVERVIEW.md) - Visual analysis
- [Test System](LOGGING_SYSTEM_README.md) - 116 tests

---

<p align="center">
  <b>Segmented Spacetime Framework</b><br>
  © 2025 Carmen Wrede & Lino Casu<br>
  Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
</p>

<p align="center">
  <a href="#-table-of-contents">↑ Back to Top</a>
</p>
