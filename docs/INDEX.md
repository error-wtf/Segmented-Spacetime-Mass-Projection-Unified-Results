# 📚 SSZ Documentation Index

**Segmented Spacetime (SSZ) - Complete Documentation Navigator**

© 2025 Carmen Wrede & Lino Casu | [Anti-Capitalist Software License v1.4](../LICENSE)

---

## 🚀 Quick Start

| For... | Start here |
|--------|------------|
| **Scientists** | [Visual Animations](#-visual-animations) → [Papers](#-scientific-papers) |
| **Developers** | [Code Documentation](#-code-documentation) → [Tests](#-tests--verification) |
| **Students** | [Educational Materials](#-educational-materials) → [Videos](#-videos) |
| **Contributors** | [TODO List](../TODO_DOCUMENTATION_UPLOAD.md) → [Development](#-development) |

---

## 📖 Table of Contents

### Core Documentation
1. [Visual Animations](#-visual-animations)
2. [Scientific Papers](#-scientific-papers)
3. [Code Documentation](#-code-documentation)
4. [Educational Materials](#-educational-materials)
5. [Videos](#-videos)
6. [Tests & Verification](#-tests--verification)
7. [Development](#-development)
8. [Data & Results](#-data--results)

---

## 🌀 Visual Animations

**Location:** `assets/ssz_animations/` & `docs/`

### Interactive Explanations

| Animation | Topic | Explanation |
|-----------|-------|-------------|
| 🌌 **Big Bang vs SSZ** | Cosmological Origin | [ssz_bigbang_vs_ssz_demo.md](ssz_bigbang_vs_ssz_demo.md) |
| 📐 **Proof v6** | Mathematical Stability | [ssz_proof_anim_v6.md](ssz_proof_anim_v6.md) |
| 🌍 **Cosmology** | ΛCDM vs SSZ Comparison | [ssz_cosmo_anim.md](ssz_cosmo_anim.md) |
| ⚫ **Black Hole** | Sagittarius A* (No Singularity) | [blackhole_segmented_spacetime.md](blackhole_segmented_spacetime.md) |
| 💥 **Energy Finite** | Black Hole Bomb Test | [ssz_bomb_animation.md](ssz_bomb_animation.md) |

**Additional (Video Production Only):**
- ⭐ **Stellar Nucleosynthesis** - [ssz_matter_creation_final.md](ssz_matter_creation_final.md) (for video part 5)

**See also:** [Animation Creation Guide](#animation-creation-guide)

---

## 📄 Scientific Papers

**Location:** `papers/`

### Published / Preprint

- **Main Theory:** [SSZ_Cosmology_Full.md](../papers/SSZ_Cosmology_Full.md)
  - Segmented Spacetime Framework
  - φ-Based Geometry
  - Cosmological Predictions
  
- **Black Holes:** [SSZ_Black_Holes.md](../papers/SSZ_Black_Holes.md)
  - No Singularities
  - Sagittarius A* Analysis
  - Information Preservation

- **Mathematical Proof:** [SSZ_Mathematical_Proof.md](../papers/SSZ_Mathematical_Proof.md)
  - C² Continuity
  - Stability Analysis
  - Resonance Control

- **Experimental Validation:** [SSZ_Black_Hole_Bomb.md](../papers/SSZ_Black_Hole_Bomb.md)
  - 2024 Braidotti Experiment
  - Energy Finiteness
  - Segment Damping

### Comparisons

- [SSZ_vs_LCDM_Comparison.md](../papers/SSZ_vs_LCDM_Comparison.md) - Cosmological Models
- [SSZ_vs_GR_Comparison.md](../papers/SSZ_vs_GR_Comparison.md) - General Relativity

---

## 💻 Code Documentation

**Location:** `scripts/`, `core/`, `tests/`

### Core Modules

**Physics Engine:**
- `core/segments.py` - Segmented spacetime field calculations
- `core/coords.py` - Coordinate transformations
- `core/stats.py` - Extended statistical metrics

**Simulations:**
- `scripts/black_hole_bomb/` - Black Hole Bomb experiment
- `scripts/proof_systems/v6/` - Mathematical proof verification
- `scripts/cosmology/` - Cosmological models

### Animation Scripts

**Location:** `evidenz-ssz/scripts/animations/`

- `ssz_stellar_nucleosynthesis_animator.py` - Matter creation GIF
- `blackhole_segmented_spacetime_animator.py` - Sgr A* visualization
- `ssz_cosmo_animator.py` - ΛCDM vs SSZ comparison

**Guide:** [Animation Creation Guide](#animation-creation-guide)

### Video Production

**Location:** `evidenz-ssz/scripts/video_production/`

- `ssz_video_scripts_part6_final.py` - 6-part audio scripts
- `ssz_6parts_final_producer.py` - Automated video generation
- `ssz_extended_video_producer_5parts.py` - Legacy 5-part system

**Guide:** [Video Production Workflow](#video-production-workflow)

---

## 🎓 Educational Materials

### Guides & Tutorials

**Beginner:**
- [What is SSZ?](../evidenz-ssz/docs/WHAT_IS_SSZ.md) - Gentle introduction
- [FAQ](../evidenz-ssz/docs/FAQ.md) - Common questions
- [Glossary](../evidenz-ssz/docs/GLOSSARY.md) - Term definitions

**Intermediate:**
- [SSZ Physics Primer](../evidenz-ssz/docs/PHYSICS_PRIMER.md) - Core concepts
- [Computational Guide](../COMPUTATIONAL_GUIDE.md) - Running simulations
- [Data Analysis Tutorial](../DATA_ANALYSIS_TUTORIAL.md) - Working with results

**Advanced:**
- [Mathematical Foundations](../MATH_FOUNDATIONS.md) - Rigorous derivations
- [Numerical Methods](../NUMERICAL_METHODS.md) - Implementation details
- [Research Directions](../RESEARCH_DIRECTIONS.md) - Open problems

### Workshops & Presentations

**Location:** `workshops/`

- Slide decks (PDF + PowerPoint)
- Jupyter notebooks
- Demo scripts

---

## 📺 Videos

### Trilingual Series (DE/EN/IT)

**6-Part Educational Series:**

1. **Big Bang vs Segmentation** (19s)
   - Classical singularity problem
   - SSZ ordered origin
   
2. **Cosmological Observations** (19s)
   - Hubble, BAO, SNe data
   - SSZ compatibility
   
3. **Mathematical Stability** (19s)
   - C² metric proof
   - Stability range
   
4. **Black Holes** (20s)
   - No singularity
   - Sagittarius A*
   
5. **Stellar Nucleosynthesis** (21s)
   - CNO cycle
   - Life prerequisites
   
6. **Energy is Finite** (18s)
   - Black Hole Bomb
   - Segment damping

**Total Duration:** ~2 minutes per language

**Resources:**
- [Audio Scripts Archive](../docs/SSZ_VIDEO_AUDIOTEXTE_ALLE_TEILE.md) - All texts
- [Video Production Workflow](#video-production-workflow) - Creation guide
- [YouTube Metadata](../evidenz-ssz/videos/YOUTUBE_METADATA.md) - Upload info

---

## ✅ Tests & Verification

**Location:** `tests/`, `scripts/tests/`

### Test Categories

**Physics Tests (35):**
- PPN parameters (β, γ)
- Velocity duality (v_esc × v_fall = c²)
- Energy conditions (WEC/DEC/SEC)
- C¹/C² continuity
- Segment stability

**Technical Tests (23):**
- UTF-8 encoding
- CLI arguments
- Markdown printing
- Cross-platform compatibility

**Run All Tests:**
```bash
python run_full_suite.py
# Expected: 35/35 physics tests passing
```

**Documentation:**
- [Test System Overview](../LOGGING_SYSTEM_README.md)
- [Physics Tests List](../PHYSICS_TESTS_COMPLETE_LIST.md)
- [Verification Status](../VERIFICATION_COMPLETE.md)

---

## 🔧 Development

### For Contributors

**Getting Started:**
1. [Installation Guide](../INSTALL_README.md)
2. [Development Setup](../DEVELOPMENT_SETUP.md)
3. [Coding Standards](../CODING_STANDARDS.md)

**Current Tasks:**
- [TODO List](../TODO_DOCUMENTATION_UPLOAD.md) - ⭐ **Current session tasks**
- [Roadmap](../ROADMAP.md) - Future plans
- [Known Issues](../KNOWN_ISSUES.md) - Bug tracker

**Workflows:**
- [Animation Creation Guide](#animation-creation-guide)
- [Video Production Workflow](#video-production-workflow)
- [Paper Writing Guide](../PAPER_WRITING_GUIDE.md)

### Git & Repository

**Best Practices:**
- [Git LFS Setup](../GIT_LFS_SETUP.md) - Large files
- [Commit Guidelines](../COMMIT_GUIDELINES.md)
- [Release Process](../RELEASE_PROCESS.md)

**Platforms:**
- GitHub (Code & Issues)
- YouTube (Videos)
- ResearchGate (Papers)
- Zenodo (Data Archive)

---

## 📊 Data & Results

**Location:** `evidenz-ssz/results/`, `data/`

### Experimental Results

**Black Hole Bomb (v6):**
- [Full Results](../evidenz-ssz/results/README.md)
- 348 configurations tested
- 96.6% theorem validation
- -2 unstable modes (stabilization)

**ESO Validation:**
- [S-Stars Analysis](../reports/ESO_VALIDATION.md)
- 97.9% predictive accuracy
- 46/47 wins vs GR

**Cosmology:**
- [Planck 2018 Fit](../reports/PLANCK_FIT.md)
- [SDSS BAO Comparison](../reports/BAO_COMPARISON.md)
- [SNe Ia Hubble Diagram](../reports/SNE_HUBBLE.md)

### Datasets

**Included:**
- `data/real_data_full.csv` - Compiled observations
- `data/gaia/` - GAIA DR3 samples
- `data/planck/` - CMB power spectra (auto-fetched)

**External:**
- ESO Archive (GRAVITY, XSHOOTER)
- SDSS DR7 (galaxies)
- Planck 2018 (CMB)

---

## 📐 Appendices

### Animation Creation Guide

**File:** `evidenz-ssz/animations/CREATION_GUIDE.md`

**Topics:**
- Matplotlib setup & SSZ theme
- Color maps & scientific visualization
- GIF export settings
- Frame rate optimization
- File size management

**Example Scripts:**
- Stellar nucleosynthesis (4 panels, 600 frames)
- Black hole dynamics (6 panels, live math)
- Cosmological comparison (4 datasets)

### Video Production Workflow

**File:** `evidenz-ssz/videos/README.md`

**Workflow:**
1. **Script Writing** - Audio texts (DE/EN/IT)
2. **Audio Generation** - Edge-TTS or manual recording
3. **GIF Creation** - Animation scripts
4. **Video Assembly** - FFmpeg or editor
5. **Upload** - YouTube with metadata

**Tools:**
- Edge-TTS (Text-to-Speech)
- FFmpeg (Video processing)
- DaVinci Resolve / Premiere (Manual editing)

**Quality Checks:**
- Audio clarity
- Timing synchronization
- Subtitle accuracy
- Thumbnail design

---

## 🔗 External Resources

### Official Links

- **GitHub Repository:** https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results
- **YouTube Channel:** [SSZ Cosmology](https://youtube.com/@sszcosmology) (TBD)
- **ResearchGate:** [Carmen Wrede](https://researchgate.net/profile/Carmen-Wrede) (TBD)
- **License:** [ANTI-CAPITALIST SOFTWARE LICENSE v1.4](../LICENSE)

### Related Work

- Braidotti et al. (2024) - Black Hole Bomb Experiment
- Planck Collaboration (2018) - CMB Data
- GRAVITY Collaboration (2020) - S-Stars
- SDSS (2021) - Large Scale Structure

---

## 📧 Contact & Support

**Authors:**
- Carmen Wrede - carmen.wrede@error-wtf.de
- Lino Casu - lino.casu@error-wtf.de

**Issues & Questions:**
- GitHub Issues: [Open Issue](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/issues)
- Discussions: [GitHub Discussions](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/discussions)

**Collaboration:**
- Academic partnerships welcome
- Open source contributions encouraged
- Educational use permitted (with attribution)

---

## 📝 Document Version

**Last Updated:** 2025-10-27  
**Version:** 1.5.0-dev  
**Status:** Active Development

**Changelog:**
- 2025-10-27: Added Visual Animations section
- 2025-10-27: Integrated Video Production docs
- 2025-10-27: Restructured for logical navigation
- 2025-10-26: Part 5 & 6 added
- 2025-10-21: v1.4.0 ESO Breakthrough

---

**Navigate:** [↑ Top](#-ssz-documentation-index) | [README](../README.md) | [TODO](../TODO_DOCUMENTATION_UPLOAD.md)

© 2025 Carmen Wrede & Lino Casu | Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
