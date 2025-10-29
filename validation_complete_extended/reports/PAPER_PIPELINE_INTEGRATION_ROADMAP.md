# SSZ Paper Pipeline - Complete Integration Roadmap

**Status:** Foundation complete, ready for full integration  
**Date:** 2025-10-18  
**Goal:** Vollständige Paper-Export-Pipeline mit Tests, CI, und Reproduzierbarkeit

---

## 📊 **Status-Übersicht**

```
Phase 1: Foundation Tools       ✅ COMPLETE
Phase 2: Core Module Stubs      ✅ COMPLETE
Phase 3: CLI Integration        ⏳ NEXT (this document)
Phase 4: Tests                  ⏳ TODO
Phase 5: CI/CD                  ⏳ TODO
```

---

## ✅ **Was bereits implementiert ist**

### **Foundation (aus Linos erstem Snippet):**

| Komponente | Status | Datei |
|------------|--------|-------|
| I/O-Sicherheit | ✅ | `tools/io_utils.py` |
| Metriken | ✅ | `tools/metrics.py` |
| Plot-System | ✅ | `tools/plots.py` (vorher vorhanden) |
| Figure-Captions | ✅ | `tools/figure_catalog.py` |
| Plot-Helpers | ✅ | `tools/plot_helpers.py` |
| Figure-Orchestrierung | ✅ | `tools/figure_orchestrator.py` |

### **Core Module (Stubs mit TODOs):**

| Modul | Status | Datei |
|-------|--------|-------|
| Parameter-Inferenz | ✅ Stub | `core/inference.py` |
| Fehlerfortpflanzung | ✅ Stub | `core/uncertainty.py` |
| Modellvergleich | ✅ Stub | `core/compare.py` |
| Observable-Vorhersagen | ✅ Stub | `core/predict.py` |
| Parameter-Sweeps | ✅ Stub | `core/sweep.py` |
| Lensing-Proxy | ✅ Stub | `core/lensing.py` |
| Stabilitätskriterien | ✅ Stub | `core/stability.py` |
| Cross-Validation | ✅ Stub | `core/xval.py` |

---

## ⏳ **Was noch zu tun ist (aus Linos zweitem Blueprint)**

### **Phase 3: CLI-Integration**

#### **3.1 Neue CLI-Flags hinzufügen**

In `cli/ssz_rings.py` und `run_all_ssz_terminal.py`:

```python
# Parameter Inference
parser.add_argument("--infer", metavar="PARAMS",
                    help="Infer parameters: 'alpha~U(0,1.5),beta~U(0.5,2),eta~U(0,1)'")
parser.add_argument("--samples", "-S", type=int, default=20000,
                    help="Number of inference samples (default: 20000)")

# Uncertainty Propagation
parser.add_argument("--propagate", "-P", type=int, default=0,
                    help="Number of Monte Carlo samples for error propagation")
parser.add_argument("--sigmaT", type=float, default=0.1,
                    help="Temperature uncertainty [K]")
parser.add_argument("--sigman", type=float, default=0.2,
                    help="Density uncertainty [cm^-3]")
parser.add_argument("--sigmav0", type=float, default=0.05,
                    help="Initial velocity uncertainty [km/s]")

# Model Comparison
parser.add_argument("--compare", "-C", metavar="MODELS",
                    help="Compare models: 'shock,pdr,gr0'")
parser.add_argument("--metrics", "-M", metavar="LIST",
                    help="Metrics to compute: 'aic,bic,waic,rmse,cliffs'")

# Predictions
parser.add_argument("--predict-lines", metavar="LIST",
                    help="Predict line ratios: 'co21,co32,nh3_11,nh3_22'")
parser.add_argument("--predict-radio", action="store_true",
                    help="Predict radio spectral index")

# Parameter Sweeps
parser.add_argument("--sweep", metavar="RANGES",
                    help="Parameter grid: 'alpha=0:1.5:0.1,beta=0.5:2:0.25'")

# Additional Analysis
parser.add_argument("--lensing", action="store_true",
                    help="Compute lensing deflection proxy")
parser.add_argument("--stability", action="store_true",
                    help="Compute stability criteria")
parser.add_argument("--entropy-proxy", action="store_true",
                    help="Include entropy proxy in stability")

# Cross-Validation
parser.add_argument("--xval", metavar="SPEC",
                    help="Cross-validation: 'train=G79,test=CygnusX'")

# Export Options
parser.add_argument("--export-rings", choices=["CSV", "JSON", "BOTH"],
                    default="CSV", help="Ring export format")
parser.add_argument("--manifest", default="reports/PAPER_EXPORTS_MANIFEST.json",
                    help="Manifest file path")
parser.add_argument("--seed", type=int, default=42,
                    help="Random seed for reproducibility")
parser.add_argument("--outdir", default="reports",
                    help="Output directory")
```

#### **3.2 Orchestrierung in run_all_ssz_terminal.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Paper Pipeline - Complete Orchestrator

Runs full analysis pipeline with reproducibility guarantees.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import argparse
import numpy as np
from datetime import datetime

# UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Imports (add as needed)
from tools.io_utils import create_manifest, finalize_manifest, register_artifact
from tools.figure_orchestrator import finalize_figures


def main():
    parser = argparse.ArgumentParser(description="SSZ Paper Pipeline")
    
    # ... (add all CLI flags from above)
    
    args = parser.parse_args()
    
    # ===== PHASE 0: Determinism & Safety =====
    print("[SSZ] Determinism & Safety Setup...")
    np.random.seed(args.seed)
    # ... (set decimal precision)
    
    # Create manifest
    manifest_path = args.manifest
    create_manifest(manifest_path, meta={
        "seed": args.seed,
        "python": sys.version,
        "created_utc": datetime.utcnow().isoformat() + "Z"
    })
    
    try:
        # ===== PHASE 1: Load Data & Run Base Model =====
        print("[SSZ] Loading data...")
        # ... (existing SSZ analysis)
        
        # ===== PHASE 2: Rings Export =====
        if args.export_rings:
            print("[SSZ] Exporting rings...")
            # ... (export logic)
        
        # ===== PHASE 3: Parameter Inference =====
        if args.infer:
            print("[SSZ] Running parameter inference...")
            from core.inference import infer_params_bootstrap
            posterior = infer_params_bootstrap(T, n, v_obs, v0,
                                              samples=args.samples,
                                              seed=args.seed,
                                              manifest_path=manifest_path)
        
        # ===== PHASE 4: Uncertainty Propagation =====
        if args.propagate > 0:
            print("[SSZ] Propagating uncertainties...")
            from core.uncertainty import propagate_uncertainties
            uncertainty = propagate_uncertainties(T, n, v0,
                                                 args.sigmaT, args.sigman, args.sigmav0,
                                                 n_samples=args.propagate,
                                                 seed=args.seed,
                                                 manifest_path=manifest_path)
        
        # ===== PHASE 5: Model Comparison =====
        if args.compare:
            print("[SSZ] Comparing models...")
            from core.compare import run_full_comparison
            comparison = run_full_comparison(T, n, v_obs, v0, v_ssz,
                                            metrics=args.metrics.split(","),
                                            manifest_path=manifest_path)
        
        # ===== PHASE 6: Predictions =====
        if args.predict_lines:
            print("[SSZ] Predicting line ratios...")
            from core.predict import predict_line_ratios
            line_ratios = predict_line_ratios(gamma, radius,
                                             lines=args.predict_lines.split(","),
                                             manifest_path=manifest_path)
        
        if args.predict_radio:
            print("[SSZ] Predicting radio spectral index...")
            from core.predict import predict_radio_spectral_index
            radio = predict_radio_spectral_index(gamma,
                                                manifest_path=manifest_path)
        
        # ===== PHASE 7: Parameter Sweep =====
        if args.sweep:
            print("[SSZ] Running parameter sweep...")
            from core.sweep import parameter_sweep
            sweep_results = parameter_sweep(T, n, v_obs, v0,
                                           # ... (parse args.sweep)
                                           manifest_path=manifest_path)
        
        # ===== PHASE 8: Lensing =====
        if args.lensing:
            print("[SSZ] Computing lensing proxy...")
            from core.lensing import compute_deflection_angle
            lensing = compute_deflection_angle(gamma, radius,
                                              manifest_path=manifest_path)
        
        # ===== PHASE 9: Stability =====
        if args.stability:
            print("[SSZ] Computing stability criteria...")
            from core.stability import compute_stability_criteria
            stability = compute_stability_criteria(v, gamma, radius,
                                                  manifest_path=manifest_path)
        
        # ===== PHASE 10: Cross-Validation =====
        if args.xval:
            print("[SSZ] Running cross-validation...")
            from core.xval import cross_validate
            xval_results = cross_validate(train_data, test_data,
                                         manifest_path=manifest_path)
        
        # ===== PHASE 11: Figures =====
        if args.fig:
            print("[SSZ] Generating figures...")
            datasets = {
                "k": ring_indices,
                "v": velocities,
                "log_gamma": np.log(gamma),
                "gamma": gamma,
                "nu_out": nu_out
            }
            finalize_figures(args, obj_name, datasets)
        
        # ===== PHASE 12: Finalize =====
        finalize_manifest(manifest_path, status="success")
        print(f"\n[SSZ] Pipeline complete! Manifest: {manifest_path}")
        
    except Exception as e:
        finalize_manifest(manifest_path, status="failed", error=str(e))
        print(f"\n[ERROR] Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

### **Phase 4: Tests**

Erstelle für jedes Core-Modul einen Smoke-Test:

```python
# tests/test_inference.py
def test_inference_returns_ci():
    from core.inference import infer_params_bootstrap
    import numpy as np
    
    T = np.array([100, 90, 80])
    n = np.array([1e5, 1e5, 1e5])
    v_obs = np.array([12.5, 13.0, 13.5])
    
    result = infer_params_bootstrap(T, n, v_obs, v0=12.5, samples=100, seed=42)
    
    assert "alpha" in result
    assert "ci68" in result["alpha"]
    assert len(result["alpha"]["ci68"]) == 2


def test_inference_deterministic():
    # Same seed → same result
    from core.inference import infer_params_bootstrap
    import numpy as np
    
    T = np.array([100, 90, 80])
    n = np.array([1e5, 1e5, 1e5])
    v_obs = np.array([12.5, 13.0, 13.5])
    
    r1 = infer_params_bootstrap(T, n, v_obs, v0=12.5, samples=100, seed=42)
    r2 = infer_params_bootstrap(T, n, v_obs, v0=12.5, samples=100, seed=42)
    
    assert r1 == r2
```

---

### **Phase 5: CI/CD**

#### **5.1 GitHub Actions**

Erstelle `.github/workflows/paper-pipeline.yml`:

```yaml
name: SSZ Paper Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e .[test]
      - name: Run tests
        run: |
          pytest tests/ -v --tb=short
  
  paper-exports:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - name: Install dependencies
        run: pip install -e .
      - name: Run paper export pipeline
        run: |
          python run_all_ssz_terminal.py \
            --csv data/observations/G79.csv --v0 12.5 \
            --infer "alpha~U(0,1.5),beta~U(0.5,2),eta~U(0,1)" \
            --samples 5000 --seed 42 \
            --propagate 1000 --sigmaT 0.1 --sigman 0.2 --sigmav0 0.05 \
            --compare shock,pdr,gr0 --metrics aic,bic,rmse \
            --predict-lines co21,co32,nh3_11,nh3_22 --predict-radio \
            --fig --export-rings BOTH \
            --manifest reports/PAPER_EXPORTS_MANIFEST.json
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: paper-exports
          path: |
            reports/**
            agent_out/**
```

#### **5.2 Lokaler Runner (PowerShell)**

Erstelle `scripts/paper_exports.ps1`:

```powershell
# SSZ Paper Export Pipeline - Local Runner
# © 2025 Carmen Wrede, Lino Casu

Write-Host "SSZ Paper Export Pipeline" -ForegroundColor Green

python run_all_ssz_terminal.py `
  --csv data/observations/G79.csv --v0 12.5 `
  --infer "alpha~U(0,1.5),beta~U(0.5,2),eta~U(0,1)" `
  --samples 20000 --seed 42 `
  --propagate 5000 --sigmaT 0.1 --sigman 0.2 --sigmav0 0.05 `
  --compare shock,pdr,gr0 --metrics aic,bic,waic,rmse,cliffs `
  --predict-lines co21,co32,nh3_11,nh3_22 --predict-radio `
  --sweep "alpha=0:1.5:0.1,beta=0.5:2:0.25,eta=0:1:0.1" `
  --lensing --stability `
  --fig --fig-dpi 600 `
  --export-rings BOTH `
  --manifest reports/PAPER_EXPORTS_MANIFEST.json `
  --outdir reports

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Pipeline complete!" -ForegroundColor Green
    Write-Host "Manifest: reports/PAPER_EXPORTS_MANIFEST.json"
} else {
    Write-Host "`n❌ Pipeline failed!" -ForegroundColor Red
    exit 1
}
```

---

## 🎯 **Integration Checkliste**

### **Phase 3: CLI Integration**
- [ ] CLI-Flags in `cli/ssz_rings.py` einfügen
- [ ] Orchestrierung in `run_all_ssz_terminal.py` implementieren
- [ ] Manifest-Creation/Finalization einbauen
- [ ] Alle Core-Module aufrufen (wenn Flags gesetzt)
- [ ] Figure-Generation integrieren

### **Phase 4: Tests**
- [ ] `tests/test_inference.py` - Smoke + Determinismus
- [ ] `tests/test_uncertainty.py` - CSV-Output + Shapes
- [ ] `tests/test_compare.py` - Metrics vorhanden
- [ ] `tests/test_predict.py` - Line-Ratios Shape
- [ ] `tests/test_sweep.py` - Grid-Scores existieren
- [ ] `tests/test_lensing.py` - Positive Deflection
- [ ] `tests/test_stability.py` - Monotonie
- [ ] `tests/test_xval.py` - Transfer-Performance

### **Phase 5: CI/CD**
- [ ] `.github/workflows/paper-pipeline.yml` erstellen
- [ ] `scripts/paper_exports.ps1` erstellen
- [ ] `Makefile` (Linux) erstellen
- [ ] README-Abschnitt "Paper Exports" hinzufügen

---

## 📖 **Verwendung nach Integration**

```bash
# Full pipeline mit allen Features
python run_all_ssz_terminal.py \
  --csv data/observations/G79.csv --v0 12.5 \
  --infer "alpha~U(0,1.5),beta~U(0.5,2),eta~U(0,1)" --samples 20000 --seed 42 \
  --propagate 5000 --sigmaT 0.1 --sigman 0.2 --sigmav0 0.05 \
  --compare shock,pdr,gr0 --metrics aic,bic,waic,rmse,cliffs \
  --predict-lines co21,co32,nh3_11,nh3_22 --predict-radio \
  --sweep "alpha=0:1.5:0.1,beta=0.5:2:0.25,eta=0:1:0.1" \
  --lensing --stability --xval "train=G79,test=CygnusX" \
  --fig --fig-dpi 600 \
  --export-rings BOTH --manifest reports/PAPER_EXPORTS_MANIFEST.json

# Minimal (nur Figures)
python run_all_ssz_terminal.py \
  --csv data/observations/G79.csv --v0 12.5 \
  --fig --export-rings CSV
```

---

## ✅ **Status-Check**

```
✅ Foundation Tools implementiert (Phase 1)
✅ Core Stubs implementiert (Phase 2)
⏳ CLI-Integration TODO (Phase 3) ← NEXT
⏳ Tests TODO (Phase 4)
⏳ CI/CD TODO (Phase 5)
```

**Nächster Schritt:** CLI-Flags einfügen und Orchestrierung implementieren!

---

© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
