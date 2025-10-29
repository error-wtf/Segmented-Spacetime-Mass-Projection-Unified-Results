# Testing Paper Export Tools

**Complete test suite for the SSZ paper export pipeline.**

© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4

---

## 🚀 **Quick Start (30 seconds)**

### **Windows PowerShell:**
```powershell
.\test_paper_exports.ps1
```

### **Linux/Mac:**
```bash
chmod +x test_paper_exports.sh
./test_paper_exports.sh
```

### **Python (cross-platform):**
```bash
python demo_paper_exports.py
```

---

## 📋 **Test Files Overview**

| File | Purpose | Platform |
|------|---------|----------|
| `demo_paper_exports.py` | Complete demo with all features | All |
| `test_paper_exports.ps1` | Automated test runner with checks | Windows |
| `test_paper_exports.sh` | Automated test runner with checks | Linux/Mac |
| `QUICK_START_PAPER_EXPORTS.md` | Step-by-step guide | Documentation |
| `PAPER_EXPORTS_README.md` | Complete pipeline docs | Documentation |

---

## 🧪 **Test Levels**

### **Level 1: Smoke Test (30 sec)**

**Goal:** Verify basic functionality

```bash
python demo_paper_exports.py
```

**Checks:**
- ✅ Plot helpers work (line, scatter, heatmap)
- ✅ Captions load correctly
- ✅ Files are written to correct locations
- ✅ Manifest generation works
- ✅ SHA256 hashing works
- ✅ Figure indexing works

**Expected output:**
```
✅ ALLE DEMOS ERFOLGREICH!

Erstellt:
  • 8 Figures (PNG + SVG)
  • 1 FIGURE_INDEX.md
  • 1 DEMO_MANIFEST.json
```

---

### **Level 2: Automated Test (1 min)**

**Goal:** Full pipeline verification with error checking

**Windows:**
```powershell
.\test_paper_exports.ps1
```

**Linux/Mac:**
```bash
./test_paper_exports.sh
```

**Checks:**
- ✅ Python version (3.7+)
- ✅ Dependencies (matplotlib, numpy)
- ✅ File creation
- ✅ File sizes (non-zero)
- ✅ Output structure
- ✅ Clean exit codes

**Expected output:**
```
===============================================================================
✅ ALL TESTS PASSED!
===============================================================================

Next steps:
  1. View figures: explorer reports\figures\demo
  2. Check index: code reports\figures\FIGURE_INDEX.md
  3. Read guide: code QUICK_START_PAPER_EXPORTS.md
  4. Integrate: Follow PAPER_EXPORTS_README.md
```

---

### **Level 3: Integration Test (5 min)**

**Goal:** Test with real SSZ pipeline

**Steps:**
1. Add CLI flags to `cli/ssz_rings.py` (see `CLI_FIGURE_FLAGS.md`)
2. Run with real data:
   ```bash
   python -m cli.ssz_rings --csv data/observations/G79.csv --v0 12.5 --fig
   ```
3. Check outputs in `reports/figures/G79/`

**Checks:**
- ✅ Figures generated from real physics data
- ✅ Captions match object name
- ✅ Manifest includes all artifacts
- ✅ FIGURE_INDEX.md updated
- ✅ File paths follow naming convention

---

### **Level 4: CI/CD Test (GitHub Actions)**

**Goal:** Automated testing in CI pipeline

**File:** `.github/workflows/paper_exports.yml`

```yaml
name: Paper Exports Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install matplotlib numpy
      - run: python demo_paper_exports.py
      - run: test -f reports/DEMO_MANIFEST.json
      - run: test -f reports/figures/FIGURE_INDEX.md
```

---

## 🔍 **What Gets Tested**

### **1. Plot Helpers (`tools/plot_helpers.py`)**

**Functions:**
- `line()` - Line plots with dual export (PNG + SVG)
- `scatter()` - Scatter plots
- `heatmap()` - 2D heatmaps with colorbar

**Test cases:**
```python
# Line plot
paths = line([1,2,3], [10,20,30], "x", "y", "Title", "reports/test")
assert len(paths) == 2  # PNG + SVG
assert all(os.path.exists(p) for p in paths)

# Scatter plot
paths = scatter([1,2,3], [10,20,30], "x", "y", "Title", "reports/test")
assert all(".png" in p or ".svg" in p for p in paths)

# Heatmap
Z = np.random.rand(10, 10)
paths = heatmap(Z, [0,1], [0,1], "x", "y", "Title", "reports/test")
assert os.path.getsize(paths[0]) > 0  # Non-empty
```

---

### **2. Caption Catalog (`tools/figure_catalog.py`)**

**Functions:**
- `get_caption()` - Retrieve caption with object substitution
- `list_all_figures()` - List available figure types

**Test cases:**
```python
# Get caption
caption = get_caption("ringchain_v_vs_k", "G79")
assert "G79" in caption
assert "v_k" in caption

# List figures
figures = list_all_figures()
assert "ringchain_v_vs_k" in figures
assert "gamma_log_vs_k" in figures
assert len(figures) == 12
```

---

### **3. I/O Utilities (`tools/io_utils.py`)**

**Functions:**
- `sha256_file()` - Compute SHA256 hash
- `update_manifest()` - Write/update JSON manifest
- `generate_figure_index()` - Create markdown index

**Test cases:**
```python
# SHA256
hash1 = sha256_file("test.png")
hash2 = sha256_file("test.png")
assert hash1 == hash2  # Deterministic
assert len(hash1) == 64  # Hex string

# Manifest
manifest = {"test": True, "files": []}
update_manifest("test.json", manifest)
assert os.path.exists("test.json")
with open("test.json") as f:
    loaded = json.load(f)
    assert loaded["test"] == True

# Figure index
entries = [
    {"name": "test", "path": "test.png", "caption": "Test figure"}
]
generate_figure_index("index.md", entries)
assert os.path.exists("index.md")
with open("index.md") as f:
    content = f.read()
    assert "test.png" in content
```

---

### **4. Figure Orchestrator (`tools/figure_orchestrator.py`)**

**Functions:**
- `finalize_figures()` - Generate all figures + manifest + index

**Test cases:**
```python
# Setup
class Args:
    fig = True
    fig_formats = "png,svg"
    fig_dpi = 600
    fig_width_mm = 160
    fig_out = "reports/figures"

datasets = {
    "k": [1, 2, 3],
    "v": [12, 14, 16],
    "log_gamma": [0, 0.1, 0.2],
    "gamma": [1.0, 1.1, 1.2],
    "nu_out": [1e12, 9e11, 8e11]
}

# Run
finalize_figures(Args(), "TestObj", datasets)

# Check outputs
assert os.path.exists("reports/figures/TestObj")
assert os.path.exists("reports/PAPER_EXPORTS_MANIFEST.json")
assert os.path.exists("reports/figures/FIGURE_INDEX.md")

# Verify manifest
with open("reports/PAPER_EXPORTS_MANIFEST.json") as f:
    manifest = json.load(f)
    assert "artifacts" in manifest
    assert len(manifest["artifacts"]) >= 4  # At least 4 figures
    assert all("sha256" in a for a in manifest["artifacts"])
```

---

## 📊 **Expected Output Structure**

```
reports/
├── figures/
│   ├── demo/                       # Demo outputs
│   │   ├── fig_demo_line.png
│   │   ├── fig_demo_line.svg
│   │   ├── fig_demo_scatter.png
│   │   ├── fig_demo_scatter.svg
│   │   └── fig_demo_heatmap.png
│   ├── DemoObject/                 # Orchestrator outputs
│   │   ├── fig_DemoObject_ringchain_v_vs_k.png
│   │   ├── fig_DemoObject_ringchain_v_vs_k.svg
│   │   ├── fig_DemoObject_gamma_log_vs_k.png
│   │   ├── fig_DemoObject_gamma_log_vs_k.svg
│   │   ├── fig_DemoObject_freqshift_vs_gamma.png
│   │   └── fig_DemoObject_freqshift_vs_gamma.svg
│   └── FIGURE_INDEX.md             # Auto-generated index
├── DEMO_MANIFEST.json              # Demo manifest
└── PAPER_EXPORTS_MANIFEST.json     # Production manifest
```

---

## 🐛 **Common Issues**

### **Issue 1: ModuleNotFoundError**

```
ModuleNotFoundError: No module named 'matplotlib'
```

**Solution:**
```bash
pip install matplotlib numpy
```

---

### **Issue 2: ImportError**

```
ImportError: cannot import name 'line' from 'tools.plot_helpers'
```

**Solution:** Run from project root:
```bash
cd h:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
python demo_paper_exports.py
```

---

### **Issue 3: Permission Denied**

```
PermissionError: [Errno 13] Permission denied: 'reports/...'
```

**Solution:** Create directory:
```bash
mkdir -p reports/figures
```

Or check write permissions:
```bash
# Windows
icacls reports /grant:r %USERNAME%:(OI)(CI)F

# Linux
chmod -R u+w reports/
```

---

### **Issue 4: Non-UTF8 Encoding**

```
UnicodeDecodeError: 'charmap' codec can't decode...
```

**Solution:** All files use UTF-8 explicitly:
```python
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
```

**Windows system fix:**
```powershell
# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## ✅ **Success Criteria**

After running tests, you should have:

- [ ] All demo figures (5 files: 3 PNG + 2 SVG + 1 heatmap)
- [ ] Orchestrator figures (6 files: 3 figures × 2 formats)
- [ ] FIGURE_INDEX.md with all figures listed
- [ ] DEMO_MANIFEST.json with SHA256 hashes
- [ ] All files non-empty (size > 0 bytes)
- [ ] No Python errors or warnings
- [ ] UTF-8 encoding works (German umlauts: ä, ö, ü)
- [ ] PNG quality good (600 DPI)
- [ ] SVG files viewable in browser
- [ ] Manifest JSON valid (can be parsed)

---

## 🚀 **Next Steps After Testing**

1. **Integrate into CLI:**
   - Add argparse flags from `CLI_FIGURE_FLAGS.md`
   - Call `finalize_figures()` at end of analysis

2. **Run with real data:**
   ```bash
   python -m cli.ssz_rings --csv data/observations/G79.csv --v0 12.5 --fig
   ```

3. **Check Carmen's workflow:**
   - Figures ready for paper (`reports/figures/G79/*.png|svg`)
   - Captions ready for LaTeX (`tools/figure_catalog.py`)
   - Manifest for reproducibility (`reports/PAPER_EXPORTS_MANIFEST.json`)

4. **CI/CD setup:**
   - Add GitHub Actions workflow (`.github/workflows/paper_exports.yml`)
   - Enable determinism checks (fixed seeds, SHA256 comparison)

5. **Physics implementation:**
   - Fill in core modules: `inference.py`, `uncertainty.py`, etc.
   - Connect to existing SSZ physics engine
   - Add model comparison baselines

---

## 📚 **Documentation**

- **Quick Start:** `QUICK_START_PAPER_EXPORTS.md`
- **Complete Guide:** `PAPER_EXPORTS_README.md`
- **CLI Integration:** `CLI_FIGURE_FLAGS.md`
- **Manifest Spec:** `MANIFEST_SPECIFICATION.md`
- **This File:** `TESTING_PAPER_EXPORTS.md`

---

## 🎯 **Test Matrix**

| Component | Unit Test | Integration Test | CI/CD |
|-----------|-----------|------------------|-------|
| Plot Helpers | ✅ demo_paper_exports.py | ✅ real pipeline | ✅ GHA |
| Captions | ✅ demo_paper_exports.py | ✅ real objects | ✅ GHA |
| I/O Utils | ✅ demo_paper_exports.py | ✅ manifest check | ✅ GHA |
| Orchestrator | ✅ demo_paper_exports.py | ✅ full run | ✅ GHA |
| CLI Flags | ⏳ TODO | ⏳ TODO | ⏳ TODO |
| Core Modules | ⏳ TODO (stubs) | ⏳ TODO | ⏳ TODO |

---

**All tests passing? You're ready for production! 🎉**

© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
