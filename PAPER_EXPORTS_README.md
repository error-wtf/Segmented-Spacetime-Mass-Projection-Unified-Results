# SSZ Suite - Paper Export Pipeline

**Status:** ✅ **FOUNDATION COMPLETE** - Ready for physics implementation  
**Date:** 2025-10-18

---

## 🎯 Zielbild

**Vollständige Paper-Export-Pipeline mit:**
- ✅ I/O-Sicherheit (`tools/io_utils.py`)
- ✅ Statistische Metriken (`tools/metrics.py`)
- ✅ Plot-System (`tools/plots.py`, `tools/figure_captions.py`, `tools/figure_index.py`)
- ⏳ Core-Module (Stubs mit TODOs)
- ⏳ CLI-Integration
- ⏳ Tests

---

## 📁 Struktur

```
Segmented-Spacetime-../
├─ core/                          # ⏳ NEU - Paper-Export-Module
│  ├─ __init__.py                 # ✅ DONE
│  ├─ inference.py                # TODO: α,β,η Bootstrap/MCMC
│  ├─ uncertainty.py              # TODO: Monte-Carlo Propagation
│  ├─ compare.py                  # TODO: AIC/BIC/WAIC Vergleich
│  ├─ predict.py                  # TODO: Linien-Ratios & Radio
│  ├─ sweep.py                    # TODO: Parameter-Grid-Sweeps
│  ├─ lensing.py                  # TODO: Deflection-Proxy
│  ├─ stability.py                # TODO: Stabilitätskriterien
│  └─ xval.py                     # TODO: Cross-Validation
│
├─ tools/                         # ✅ COMPLETE
│  ├─ io_utils.py                 # ✅ DONE - Safe I/O + Manifest
│  ├─ metrics.py                  # ✅ DONE - RMSE/AIC/BIC/Cliff's δ
│  ├─ plots.py                    # ✅ DONE - PNG/SVG Export
│  ├─ figure_captions.py          # ✅ DONE - Caption-Katalog
│  └─ figure_index.py             # ✅ DONE - Index-Generator
│
├─ reports/                       # ✅ Output-Verzeichnis
│  ├─ figures/                    # Figure-Output
│  │  ├─ G79/
│  │  ├─ CygnusX/
│  │  ├─ shared/
│  │  └─ FIGURE_INDEX.md
│  ├─ fits/                       # Posterior-Fits
│  └─ PAPER_EXPORTS_MANIFEST.json # Master-Manifest
│
└─ agent_out/                     # ✅ Laufzeit-Output
   ├─ reports/
   ├─ figures/
   └─ logs/
```

---

## ✅ Bereits implementiert

### 1. **tools/io_utils.py** - I/O-Sicherheit
```python
from tools.io_utils import safe_path, sha256_file, update_manifest

# Sicherer Dateizugriff (nur agent_out/ und reports/)
path = safe_path("reports/test.csv")  # ✅ OK
# safe_path("/tmp/test.csv")           # ❌ RuntimeError!

# SHA256 für Reproduzierbarkeit
hash = sha256_file("data/observations/G79.csv")

# Manifest-Tracking
update_manifest("reports/MANIFEST.json", {
    "artifacts": [{"role": "figure", "path": "fig.png", "sha256": hash}]
})
```

**Features:**
- ✅ Write-Scope auf `agent_out/` und `reports/` begrenzt
- ✅ SHA256-Checksums für alle Artefakte
- ✅ Manifest mit Metadaten (Git-Commit, Python-Version, Seeds)

### 2. **tools/metrics.py** - Statistische Metriken
```python
from tools.metrics import rmse, mae, aic, bic, cliffs_delta

# Goodness of fit
error = rmse([1, 2, 3], [1.1, 2.0, 2.9])  # RMSE
error = mae([1, 2, 3], [1.1, 2.0, 2.9])   # MAE

# Information criteria
aic_val = aic(log_likelihood=-50, k=3)
bic_val = bic(log_likelihood=-50, k=3, n=100)

# Effect size
delta = cliffs_delta([1, 2, 3], [2, 3, 4])  # Non-parametric
```

**Verfügbare Metriken:**
- ✅ RMSE, MAE, MAPE, R²
- ✅ AIC, AICc, BIC, WAIC
- ✅ Cliff's δ, Cohen's d
- ✅ Log-Likelihood (Gaussian)

### 3. **tools/plots.py** - Plot-System
```python
from tools.plots import plot_line, plot_scatter, plot_heatmap

# Linienplot mit PNG + SVG Export
paths = plot_line(
    x=[1, 2, 3, 4],
    y=[10, 12, 14, 16],
    xlabel="Ring index k",
    ylabel="Velocity v_k [km/s]",
    title="G79: Ring-chain velocity",
    basepath="reports/figures/G79/fig_G79_velocity",
    formats=("png", "svg"),
    dpi=600,
    width_mm=160
)
# → ["reports/figures/G79/fig_G79_velocity.png",
#    "reports/figures/G79/fig_G79_velocity.svg"]
```

**Features:**
- ✅ PNG (600 DPI) + SVG (Vektor) Export
- ✅ Paper-Breiten (160mm 2-Spalte, 84mm 1-Spalte)
- ✅ Fehlerbalken, Unsicherheitsbänder
- ✅ Heatmaps, Corner-Plots
- ✅ Residual-Plots

### 4. **tools/figure_captions.py** - Caption-Katalog
```python
from tools.figure_captions import get_caption

caption = get_caption("ringchain_v_vs_k", object_name="G79")
# → "Ring-Ketten-Propagation im SSZ-Feld. Die Umlaufgeschwindigkeit..."
```

**Paper-ready Captions:**
- ✅ 8 Objekt-spezifische Plots
- ✅ 4 Shared/Comparison Plots
- ✅ LaTeX- und Markdown-Formatierung

### 5. **tools/figure_index.py** - Index-Generator
```python
from tools.figure_index import write_figure_index, scan_figure_directory

# Automatisch alle Figures scannen
entries = scan_figure_directory("reports/figures")

# Index mit Captions erstellen
write_figure_index(entries, "reports/figures/FIGURE_INDEX.md")
```

**Output:** `FIGURE_INDEX.md`
```markdown
# SSZ Suite - Figure Index

## G79
### Ringchain V Vs K
**Caption:** Ring-Ketten-Propagation im SSZ-Feld...
**Files:**
- **PNG**: `G79/fig_G79_ringchain_v_vs_k.png`
  - SHA256: `a1b2c3d4...`
- **SVG**: `G79/fig_G79_ringchain_v_vs_k.svg`
```

---

## ⏳ TODO - Core-Module (Stubs für Physik)

Die folgenden Module müssen noch mit der echten SSZ-Physik gefüllt werden:

### 1. **core/inference.py** - Parameter-Inferenz
```python
# TODO: Implementiere Bootstrap oder MCMC
def infer_params_bootstrap(T, n, v_obs, v0, samples=20000, seed=42):
    """
    Infer α, β, η parameters via Bootstrap
    
    TODO:
    - Grid-Search über Parameter-Space
    - Bootstrap-Resampling für CI
    - Posterior-Export als JSON
    """
    pass  # STUB - Physik einfügen
```

### 2. **core/uncertainty.py** - Fehlerfortpflanzung
```python
# TODO: Implementiere Monte-Carlo Propagation
def propagate(T, n, v0, sigmaT, sigman, sigmav0, N=5000, rng=None):
    """
    Propagate measurement errors through SSZ model
    
    TODO:
    - Sample (T, n, v0) mit Gaussian Noise
    - Compute (v_k, γ_k) für jede Iteration
    - Return Medians + CI (68%, 95%)
    """
    pass  # STUB - Physik einfügen
```

### 3. **core/compare.py** - Modellvergleich
```python
# TODO: Implementiere Baseline-Vergleiche
def compare_models(y_obs, models_dict):
    """
    Compare SSZ vs. Shock/PDR/GR
    
    TODO:
    - Compute AIC, BIC, WAIC für jedes Modell
    - RMSE, MAE, Cliff's δ
    - Export Comparison-Table
    """
    pass  # STUB - Physik einfügen
```

### 4. **core/predict.py** - Observable-Vorhersagen
```python
# TODO: Implementiere Linien-Ratios & Radio-Slope
def predict_line_ratios(gamma, lines=["co21", "co32"]):
    """
    Predict line intensity ratios from γ-field
    
    TODO:
    - Map γ → excitation conditions
    - Compute line ratios
    - Compare to observations
    """
    pass  # STUB - Physik einfügen
```

### 5-8. Weitere Module (sweep, lensing, stability, xval)
- Analog: Stubs mit TODOs für echte Implementierung

---

## 🔧 CLI-Integration (TODO)

**Neue Flags für `run_all_ssz_terminal.py`:**

```bash
python run_all_ssz_terminal.py \
  --csv data/observations/G79.csv \
  --v0 12.5 \
  --infer "alpha~U(0,1.5),beta~U(0.5,2),eta~U(0,1)" \
  --samples 20000 \
  --seed 42 \
  --propagate 5000 \
  --sigmaT 0.1 --sigman 0.2 --sigmav0 0.05 \
  --compare shock,pdr,gr0 \
  --metrics aic,bic,waic,rmse \
  --predict-lines co21,co32,nh3_11 \
  --predict-radio \
  --sweep "alpha=0:1.5:0.1,beta=0.5:2:0.25" \
  --lensing \
  --stability \
  --xval "train=G79,test=CygnusX" \
  --fig --fig-dpi 600 --fig-formats png,svg \
  --export-rings BOTH \
  --manifest reports/PAPER_EXPORTS_MANIFEST.json
```

---

## 📊 Manifest-Format

`reports/PAPER_EXPORTS_MANIFEST.json`:
```json
{
  "meta": {
    "created_utc": "2025-10-18T15:20:00Z",
    "git_commit": "abc123",
    "python": "3.10.11",
    "seed": 42
  },
  "params": {
    "infer": "alpha~U(0,1.5),...",
    "samples": 20000
  },
  "artifacts": [
    {
      "role": "figure",
      "path": "figures/G79/fig_G79_velocity.png",
      "sha256": "a1b2c3...",
      "format": "png"
    }
  ],
  "status": "success"
}
```

---

## 🧪 Tests (TODO)

**Für jedes core-Modul:**
```python
# tests/test_inference.py
def test_inference_returns_ci():
    result = infer_params_bootstrap(T, n, v_obs, v0, samples=100)
    assert "alpha" in result
    assert "ci68" in result["alpha"]

def test_inference_deterministic():
    r1 = infer_params_bootstrap(..., seed=42)
    r2 = infer_params_bootstrap(..., seed=42)
    assert r1 == r2  # Same seed → same result
```

---

## 🚀 Nächste Schritte

### Phase 1: Foundation ✅ COMPLETE
- [x] `tools/io_utils.py`
- [x] `tools/metrics.py`
- [x] `tools/plots.py`
- [x] `tools/figure_captions.py`
- [x] `tools/figure_index.py`

### Phase 2: Core-Stubs (NEXT)
- [ ] Create stub files for all core modules
- [ ] Add docstrings with TODOs
- [ ] Define function signatures

### Phase 3: CLI-Integration
- [ ] Add argparse flags to `run_all_ssz_terminal.py`
- [ ] Orchestrate core modules
- [ ] Generate manifest

### Phase 4: Tests
- [ ] Smoke-tests for each module
- [ ] Determinism tests (fixed seed)
- [ ] Golden file tests

### Phase 5: Documentation
- [ ] README section "Paper Exports"
- [ ] Usage examples
- [ ] CI/CD setup

---

## 📖 Verwendung für Carmen (Paper)

**1. Pipeline laufen lassen:**
```bash
python run_all_ssz_terminal.py --csv data/observations/G79.csv --fig
```

**2. Figures finden:**
```
reports/figures/
├─ G79/                    # Alle G79-Plots
├─ shared/                 # Comparison-Plots
└─ FIGURE_INDEX.md         # ← Übersicht mit Captions
```

**3. Ins Paper einfügen:**
- **LaTeX:** Kopiere PNG/SVG aus `reports/figures/`
- **Captions:** Aus `FIGURE_INDEX.md`
- **Checksums:** Aus `PAPER_EXPORTS_MANIFEST.json`

**4. Methods-Section:**
- Parameter-Inferenz: `reports/fits/posterior.json`
- Model-Comparison: `reports/compare/scores.csv`
- Predictions: `reports/pred/line_ratios.csv`

---

## ⚠️ Sicherheits-Regeln

**NIEMALS:**
- ❌ Schreiben außerhalb `agent_out/` oder `reports/`
- ❌ `rm -rf` oder Lösch-Routinen ohne Zustimmung
- ❌ Seeds ändern (Reproduzierbarkeit!)

**IMMER:**
- ✅ `safe_path()` für alle Writes
- ✅ SHA256 für alle Artefakte
- ✅ Manifest-Updates nach jedem Export
- ✅ UTF-8 encoding für alle Files

---

## 📞 Support

**Dokumentation:**
- `PAPER_EXPORTS_README.md` (diese Datei)
- `tools/io_utils.py` (Docstrings)
- `tools/metrics.py` (Docstrings)

**Bei Fragen:**
© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
