# Quick Start - Paper Export Tools

**Fertig zum Testen!** Alle Tools sind implementiert.

---

## 🚀 **Sofort-Test (5 Minuten)**

### **1. Demo ausführen**

```bash
python demo_paper_exports.py
```

**Was passiert:**
- ✅ Erstellt Test-Figures in `reports/figures/demo/`
- ✅ Zeigt Caption-System
- ✅ Erstellt Manifest mit SHA256
- ✅ Testet kompletten Orchestrator

**Erwartete Ausgabe:**
```
================================================================================
SSZ Paper Export Tools - DEMO
================================================================================

================================================================================
DEMO 1: Basis-Plots
================================================================================

[1/3] Erstelle Line-Plot...
✓ Erstellt: ['reports/figures/demo/fig_demo_line.png', ...]

[2/3] Erstelle Scatter-Plot...
✓ Erstellt: ['reports/figures/demo/fig_demo_scatter.png', ...]

[3/3] Erstelle Heatmap...
✓ Erstellt: ['reports/figures/demo/fig_demo_heatmap.png']

✅ Demo 1 complete!

...

✅ ALLE DEMOS ERFOLGREICH!
```

---

## 📁 **Nach dem Test prüfen**

```bash
# Windows PowerShell
tree reports /F

# Linux
tree reports
```

**Erwartete Struktur:**
```
reports/
├── figures/
│   ├── demo/
│   │   ├── fig_demo_line.png
│   │   ├── fig_demo_line.svg
│   │   ├── fig_demo_scatter.png
│   │   ├── fig_demo_scatter.svg
│   │   └── fig_demo_heatmap.png
│   ├── DemoObject/
│   │   ├── fig_DemoObject_ringchain_v_vs_k.png
│   │   ├── fig_DemoObject_ringchain_v_vs_k.svg
│   │   └── ...
│   └── FIGURE_INDEX.md
├── DEMO_MANIFEST.json
└── PAPER_EXPORTS_MANIFEST.json
```

---

## 🧪 **Einzelne Komponenten testen**

### **Test 1: Plot-Helpers**

```python
from tools.plot_helpers import line, scatter, heatmap
import numpy as np

# Line-Plot
x = [1, 2, 3, 4, 5]
y = [10, 12, 14, 16, 18]
paths = line(x, y, "x", "y", "Test", "reports/test_line")
print(paths)
```

### **Test 2: Captions**

```python
from tools.figure_catalog import get_caption, list_all_figures

# Alle verfügbaren Figures
print(list_all_figures())

# Caption holen
caption = get_caption("ringchain_v_vs_k", "G79")
print(caption)
```

### **Test 3: I/O-Utils**

```python
from tools.io_utils import sha256_file, update_manifest

# Hash berechnen
hash = sha256_file("reports/figures/demo/fig_demo_line.png")
print(f"SHA256: {hash}")

# Manifest updaten
update_manifest("reports/TEST_MANIFEST.json", {
    "test": True,
    "artifacts": [{"path": "test.png", "sha256": hash}]
})
```

### **Test 4: Orchestrator**

```python
from tools.figure_orchestrator import finalize_figures
import numpy as np

class Args:
    fig = True
    fig_formats = "png,svg"
    fig_dpi = 600
    fig_width_mm = 160
    fig_out = "reports/figures"

args = Args()

datasets = {
    "k": np.arange(1, 6),
    "v": [12, 13, 14, 15, 16],
    "log_gamma": np.log([1.0, 1.1, 1.2, 1.3, 1.4]),
    "gamma": [1.0, 1.1, 1.2, 1.3, 1.4],
    "nu_out": [1e12, 9e11, 8e11, 7e11, 6e11]
}

finalize_figures(args, "TestObject", datasets)
```

---

## 🎯 **Integration in echte Pipeline**

### **Schritt 1: CLI-Flags hinzufügen**

In `cli/ssz_rings.py`:

```python
# Copy-Paste aus CLI_FIGURE_FLAGS.md
parser.add_argument("--fig", action="store_true")
parser.add_argument("--fig-formats", default="png,svg")
parser.add_argument("--fig-dpi", type=int, default=600)
parser.add_argument("--fig-width-mm", type=float, default=160.0)
parser.add_argument("--fig-out", default="reports/figures")
```

### **Schritt 2: Am Ende aufrufen**

```python
if args.fig:
    from tools.figure_orchestrator import finalize_figures
    import numpy as np
    
    datasets = {
        "k": ring_indices,
        "v": velocities,
        "log_gamma": np.log(gamma),
        "gamma": gamma,
        "nu_out": nu_out
    }
    
    finalize_figures(args, "G79", datasets)
```

### **Schritt 3: Testen**

```bash
python -m cli.ssz_rings --csv data/observations/G79.csv --v0 12.5 --fig
```

---

## 📊 **Was Carmen bekommt**

Nach dem Run:

1. **Figures:** `reports/figures/G79/*.png|svg`
2. **Index:** `reports/figures/FIGURE_INDEX.md`
3. **Manifest:** `reports/PAPER_EXPORTS_MANIFEST.json`

**Ins Paper einfügen:**

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.8\textwidth]{figures/G79/fig_G79_ringchain_v_vs_k.pdf}
  \caption{Ring-Ketten-Propagation im SSZ-Feld. Die Umlaufgeschwindigkeit 
           v_k steigt trotz fallender Temperatur über k und reproduziert 
           die 14–16 km s⁻¹.}
  \label{fig:g79_velocity}
\end{figure}
```

---

## 🐛 **Troubleshooting**

### **Problem: Import-Fehler**

```
ModuleNotFoundError: No module named 'tools'
```

**Lösung:** Von Root-Verzeichnis ausführen:
```bash
cd h:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00
python demo_paper_exports.py
```

### **Problem: Matplotlib-Fehler**

```
ModuleNotFoundError: No module named 'matplotlib'
```

**Lösung:**
```bash
pip install matplotlib numpy
```

### **Problem: Permission-Denied**

```
PermissionError: [Errno 13] Permission denied: 'reports/...'
```

**Lösung:** Ordner existiert nicht oder keine Schreibrechte:
```bash
mkdir -p reports/figures
```

---

## ✅ **Checkliste**

- [ ] `demo_paper_exports.py` erfolgreich ausgeführt
- [ ] Figures in `reports/figures/demo/` vorhanden
- [ ] `FIGURE_INDEX.md` erstellt
- [ ] Manifeste haben SHA256-Hashes
- [ ] Einzelne Komponenten getestet
- [ ] Bereit für CLI-Integration

---

**Alles funktioniert? Dann bist du ready für die echte Pipeline-Integration!** 🚀

© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
