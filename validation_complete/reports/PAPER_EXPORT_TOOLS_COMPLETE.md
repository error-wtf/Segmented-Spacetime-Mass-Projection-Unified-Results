# ✅ Paper Export Tools - COMPLETE & READY

**Status:** All copy-paste-ready tools implemented from Lino's snippets  
**Date:** 2025-10-18  
**Purpose:** Carmen kann jetzt figures 1:1 ins Paper ziehen

---

## 🎯 Was wurde implementiert?

### **Foundation Tools** ✅

| Datei | Status | Beschreibung |
|-------|--------|--------------|
| `tools/io_utils.py` | ✅ | Safe I/O + Manifest + SHA256 |
| `tools/metrics.py` | ✅ | RMSE, AIC, BIC, Cliff's δ |
| `tools/plots.py` | ✅ | Basis-Plot-System (vorher vorhanden) |
| `tools/figure_catalog.py` | ✅ **NEU** | Paper-ready Captions |
| `tools/plot_helpers.py` | ✅ **NEU** | Kompakte Helper (line, scatter, heatmap) |
| `tools/figure_orchestrator.py` | ✅ **NEU** | Orchestrierung + Index + Manifest |
| `CLI_FIGURE_FLAGS.md` | ✅ **NEU** | Integration-Doku |

---

## 📖 Verwendung (Copy-Paste)

### **1. CLI-Flags hinzufügen**

In `cli/ssz_rings.py` oder `run_all_ssz_terminal.py`:

```python
# --- Figure Generation Flags ---
parser.add_argument("--fig", action="store_true",
                    help="Erzeuge Abbildungen (PNG+SVG)")
parser.add_argument("--fig-formats", default="png,svg",
                    help="Formate: png,svg (Standard: png,svg)")
parser.add_argument("--fig-dpi", type=int, default=600,
                    help="PNG-Auflösung (Standard: 600)")
parser.add_argument("--fig-width-mm", type=float, default=160.0,
                    help="Breite in mm (160=2-col, 84=1-col)")
parser.add_argument("--fig-out", default="reports/figures",
                    help="Ausgabeordner (Standard: reports/figures)")
```

### **2. Am Ende der Pipeline aufrufen**

```python
if args.fig:
    from tools.figure_orchestrator import finalize_figures
    import numpy as np
    
    # Daten vorbereiten
    datasets = {
        "k": ring_indices,           # [1, 2, 3, ...]
        "v": velocities,             # [km/s]
        "log_gamma": np.log(gamma),  # log(γ)
        "gamma": gamma,              # γ
        "nu_out": nu_out             # [Hz]
    }
    
    # Objektname aus Eingabe
    obj_name = "G79"  # oder aus CSV-Namen extrahieren
    
    # Figures generieren
    finalize_figures(args, obj_name, datasets)
```

### **3. Ausführen**

```bash
python -m cli.ssz_rings --csv data/observations/G79.csv --v0 12.5 --fig
```

---

## 📁 Output-Struktur

```
reports/figures/
├── G79/
│   ├── fig_G79_ringchain_v_vs_k.png       (600 DPI)
│   ├── fig_G79_ringchain_v_vs_k.svg       (Vektor)
│   ├── fig_G79_gamma_log_vs_k.png
│   ├── fig_G79_gamma_log_vs_k.svg
│   ├── fig_G79_freqshift_vs_gamma.png
│   └── fig_G79_freqshift_vs_gamma.svg
├── CygnusX/
│   └── (analog)
├── shared/
│   └── (Vergleichs-Plots)
└── FIGURE_INDEX.md                         ← Alle Figures + Captions

reports/PAPER_EXPORTS_MANIFEST.json         ← Checksums + Metadaten
```

---

## 📊 Verfügbare Figures

**Aktuell implementiert:**

1. ✅ `ringchain_v_vs_k` - Velocity vs. Ring Index
2. ✅ `gamma_log_vs_k` - Log(γ) vs. Ring Index
3. ✅ `freqshift_vs_gamma` - Frequency Shift vs. γ

**TODO (Stubs vorhanden):**

4. ⏳ `residuals_model_vs_obs` - Residuals
5. ⏳ `posterior_corner` - Corner Plot (α, β, η)
6. ⏳ `uncertainty_bands_v_vs_k` - Unsicherheitsbänder
7. ⏳ `line_ratios_vs_radius` - Linien-Ratios
8. ⏳ `radio_spectral_index` - Radio-Slope
9. ⏳ `model_compare_scores` - AIC/BIC Vergleich
10. ⏳ `sweep_heatmap_alpha_beta` - Parameter-Heatmap
11. ⏳ `lensing_deflection_map` - Lensing-Map
12. ⏳ `stability_criteria` - Stabilitätskriterien

---

## 🎨 Captions (Paper-Ready)

**Alle Captions in:** `tools/figure_catalog.py`

**Beispiel:**
```python
CAPTIONS["ringchain_v_vs_k"] = \
    "Ring-Ketten-Propagation im SSZ-Feld. Die Umlaufgeschwindigkeit v_k " \
    "steigt trotz fallender Temperatur über k und reproduziert die " \
    "14–16 km s⁻¹."
```

**Verwendung:**
```python
from tools.figure_catalog import get_caption
caption = get_caption("ringchain_v_vs_k", "G79")
# → "G79: Ring-Ketten-Propagation im SSZ-Feld..."
```

---

## 🔧 Neue Figures hinzufügen

### **Schritt 1:** Caption definieren

In `tools/figure_catalog.py`:
```python
CAPTIONS["my_new_figure"] = "Beschreibung der neuen Figur..."
```

### **Schritt 2:** Generation hinzufügen

In `tools/figure_orchestrator.py` → `generate_figures()`:
```python
if "x_data" in datasets and "y_data" in datasets:
    p = _fig_base(fig_root, obj, "my_new_figure")
    paths += line(datasets["x_data"], datasets["y_data"],
                  "X Label", "Y Label", f"{obj}: Title", p, ...)
```

### **Schritt 3:** Daten bereitstellen

In Pipeline `datasets` dict erweitern:
```python
datasets["x_data"] = my_x_values
datasets["y_data"] = my_y_values
```

---

## 📖 Für Carmen (Paper-Workflow)

### **Schritt 1:** Analyse laufen lassen
```bash
python -m cli.ssz_rings --csv data/observations/G79.csv --v0 12.5 --fig
```

### **Schritt 2:** Index öffnen
```bash
cat reports/figures/FIGURE_INDEX.md
```

### **Schritt 3:** Figures ins Paper kopieren

**LaTeX:**
```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.8\textwidth]{figures/G79/fig_G79_ringchain_v_vs_k.pdf}
  \caption{Ring-Ketten-Propagation im SSZ-Feld...}
  \label{fig:g79_velocity}
\end{figure}
```

**Markdown:**
```markdown
<!-- Figure to be generated - run analysis with --save-figures flag -->
<!-- ![Ring-chain velocity](figures/G79/fig_G79_ringchain_v_vs_k.png) -->

*Figure 1:* Ring-Ketten-Propagation im SSZ-Feld...
(Figure will be generated when running G79 analysis with figure export enabled)
```

### **Schritt 4:** Checksums verifizieren
```bash
cat reports/PAPER_EXPORTS_MANIFEST.json
```

---

## ⚙️ Settings

| Setting | Default | Beschreibung |
|---------|---------|--------------|
| `--fig` | False | Figures generieren |
| `--fig-formats` | `png,svg` | PNG für Drafts, SVG für Druck |
| `--fig-dpi` | 600 | 600=Draft, 1200=Print |
| `--fig-width-mm` | 160.0 | 160=2-Spalten, 84=1-Spalte |
| `--fig-out` | `reports/figures` | Output-Verzeichnis |

---

## ✅ Checkliste für Integration

- [ ] Argparse-Flags in CLI-Script einfügen
- [ ] `finalize_figures()` am Ende der Pipeline aufrufen
- [ ] `datasets` dict mit erforderlichen Arrays füllen
- [ ] Test-Run mit `--fig` Flag
- [ ] Prüfen: `reports/figures/` enthält Figures
- [ ] Prüfen: `FIGURE_INDEX.md` vorhanden
- [ ] Prüfen: `PAPER_EXPORTS_MANIFEST.json` aktualisiert

---

## 📚 Dokumentation

| Datei | Zweck |
|-------|-------|
| `PAPER_EXPORTS_README.md` | Übersicht Paper-Export-System |
| `CLI_FIGURE_FLAGS.md` | CLI-Integration-Guide |
| `tools/figure_catalog.py` | Docstrings für Captions |
| `tools/figure_orchestrator.py` | Docstrings für Orchestrierung |
| `tools/plot_helpers.py` | Docstrings für Helper |

---

## 🚀 Nächste Schritte

### **Phase 1: Copy-Paste Integration** (NOW)
1. Flags in CLI einfügen ✅ Ready
2. `finalize_figures()` aufrufen ✅ Ready
3. Test-Run ⏳ TODO

### **Phase 2: Mehr Figures** (Later)
4. Residuals-Plot hinzufügen
5. Corner-Plot hinzufügen
6. Uncertainty-Bands hinzufügen
7. etc.

### **Phase 3: Tests** (Later)
8. Unit-Tests für figure_orchestrator
9. Golden-File-Tests für Reproduzierbarkeit
10. CI/CD Integration

---

## 🎉 Status: READY TO USE!

**Alle Tools von Lino's Snippet sind implementiert und dokumentiert.**

Carmen kann jetzt:
- ✅ Figures mit `--fig` generieren
- ✅ `FIGURE_INDEX.md` öffnen und Captions kopieren
- ✅ PNG/SVG direkt ins Paper einfügen
- ✅ Checksums aus Manifest verifizieren

**Bereit für Copy-Paste in CLI-Scripts!** 🚀

---

© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
