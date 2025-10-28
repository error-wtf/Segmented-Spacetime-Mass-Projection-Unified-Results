# 🎯 SSZ Black Hole Stability - Quick Reference

## 📊 Alle Abbildungen auf einen Blick

### Figure 1: Segmentation & Krümmung
```
Ξ(r) = 0.99 × (1 - exp(-φ(r+ε)))    [Segmentdichte]
R_proxy(r) = 1 / (1 + Ξ(r))         [Krümmungsindikator]
```
**Result:** R(r→0) ≈ 0.5 R_0 (endlich!) vs. GR: R(r→0) → ∞

### Figure 2: Stabilitätskarte
```
Stabilitätskriterium: λ_A < 1/K²
```
**Examples:** (K=32, λ=0.0006) ✅ Stabil | (K=16, λ=0.02) ❌ Instabil

### Figure 3: Energie-Evolution
```
Stable:   E_final = 2.62 E_0       (saturiert bei φ² ≈ 2.618)
Unstable: E_final = 1.3×10³⁸ E_0    (exponentiell)
Dämpfung: η = 4.9×10³⁷
```

---

## 🎬 Schnellstart

### Alle Plots generieren
```bash
python ssz_stability_three_figures.py  # ~5 Sekunden
```

### Animation erstellen
```bash
python ssz_stability_animation.py      # ~30 Sekunden
```

### Output prüfen
```bash
ls -lh results/
# ssz_formal_fig_Xi_Rproxy.png      1.2M ✓
# ssz_formal_fig_stability_map.png  0.9M ✓
# ssz_formal_fig_energy_series.png  1.5M ✓
# ssz_bomb_evolution.gif            2.3M ✓
```

---

## 📝 LaTeX Copy-Paste

```latex
% Figure 1
\begin{figure}[htbp]
\includegraphics[width=\textwidth]{ssz_formal_fig_Xi_Rproxy.png}
\caption{Segmentdichte Ξ(r) und Krümmungsindikator R_proxy(r)}
\label{fig:ssz_xi}
\end{figure}

% Figure 2
\begin{figure}[htbp]
\includegraphics[width=0.8\textwidth]{ssz_formal_fig_stability_map.png}
\caption{SSZ Stabilitätskarte: λ_A < 1/K²}
\label{fig:ssz_stability}
\end{figure}

% Figure 3
\begin{figure}[htbp]
\includegraphics[width=\textwidth]{ssz_formal_fig_energy_series.png}
\caption{Black Hole Bomb: Stabil vs. Instabil}
\label{fig:ssz_bomb}
\end{figure}
```

---

## 🔑 Key Numbers

| Parameter | Value | Bedeutung |
|-----------|-------|-----------|
| φ | 1.618034 | Goldener Schnitt |
| φ² | 2.618034 | Sättigungsgrenze |
| Ξ_max | 0.99 | Max. Segmentdichte |
| λ_crit(K=32) | 0.000977 | Kritische Kopplung |
| η_damp | 4.9×10³⁷ | Dämpfungsfaktor |

---

## 📍 File Locations

```
results/
├── ssz_formal_fig_Xi_Rproxy.png      ← Figure 1
├── ssz_formal_fig_stability_map.png  ← Figure 2
├── ssz_formal_fig_energy_series.png  ← Figure 3
├── ssz_bomb_evolution.gif            ← Animation
└── README_FIGURES.md                 ← Integration guide

Scripts:
├── ssz_stability_three_figures.py    ← Generates 1-3
└── ssz_stability_animation.py        ← Generates GIF

Documentation:
├── SSZ_BLACK_HOLE_STABILITY_ANALYSIS.md  ← Full analysis
└── SSZ_STABILITY_COMPLETE_SUMMARY.md     ← Summary
```

---

## ✅ Status: COMPLETE

**All deliverables ready for paper integration!**
