```
python segspace_enhanced_pi_bridge.py --csv real_data_full.csv --prefer-z --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16
python segspace_enhanced_pi_bridge.py --csv real_data_full.csv  --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16
python segspace_enhanced_pi_bridge.py --csv real_data_full.csv  --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16 --prefer-z
python segspace_enhanced_pi_bridge.py --csv real_data_full.csv --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16 --prefer-z --export-ratios --top 10
```

```
python segspace_enhanced_pi_bridge.py --csv real_data_full.csv --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16 --prefer-z --export-ratios --top 10

=============================================================
 SEGMENTED SPACETIME – Δ(M) + CHUDNOVSKY‑π BRIDGE (Runner)
=============================================================
π (Chudnovsky)     : 3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706...
π compute time     : 0.000 ms
Ratios‑CSV         : H:\segspace_pi_bridge_out\segspace_ratios.csv
=============================================================
 SEGMENTED SPACETIME – Δ(M) + π‑Bridge (Chud/Builtin/ϕ)
=============================================================
CSV               : real_data_full.csv
Zeilen (verwendet): 67
π‑Quelle          : chud
                    (Chud: terms=16, prec=200)
Seg‑Mode          : hybrid
ΔM‑Params         : A=98.01%, α=27177 [1/m], B=1.96%
-------------------------------------------------------------
Median |Δz|  GR   : 1.375760109649e-04
Median |Δz|  SR   : 1.510571734980e-04
Median |Δz|  GR*SR: 1.889837775617e-04
Median |Δz|  Seg  : 1.255016151332e-04
Performance (Seg/GR): 0.912235 ×
-------------------------------------------------------------
Punktweise Faktoren (Seg / Baseline):
  vs GR   → Q1=2.059e-01, Q2=8.018e-01, Q3=6.548e+00 | better=29/57 (50.9%)
  vs GR*SR→ Q1=5.670e-01, Q2=1.000e+00, Q3=1.049e+00 | better=29/67 (43.3%)
Debug‑CSV          : H:\segspace_pi_bridge_out\segspace_pi_bridge_debug.csv
-------------------------------------------------------------
TOP 10 – Seg vs GR (kleiner = besser):
-------------------------------------------------------------
Best (Seg << GR):
  EHT_M87                  ratio=2.370e-03  | dz_seg=1.630e-03, dz_base=6.878e-01
  S24_SgrA*                ratio=1.734e-02  | dz_seg=1.149e-06, dz_base=6.627e-05
  S47_SgrA*                ratio=1.767e-02  | dz_seg=1.897e-06, dz_base=1.074e-04
  S19_SgrA*                ratio=2.429e-02  | dz_seg=3.342e-06, dz_base=1.376e-04
  S4715_SgrA*              ratio=5.099e-02  | dz_seg=1.433e-06, dz_base=2.810e-05
  S39_SgrA*                ratio=7.641e-02  | dz_seg=7.146e-06, dz_base=9.351e-05
  S27_SgrA*                ratio=9.353e-02  | dz_seg=1.306e-05, dz_base=1.396e-04
  S2_SgrA*                 ratio=9.419e-02  | dz_seg=2.908e-05, dz_base=3.087e-04
  S41_SgrA*                ratio=1.108e-01  | dz_seg=1.662e-05, dz_base=1.501e-04
  S43_SgrA*                ratio=1.110e-01  | dz_seg=5.933e-06, dz_base=5.346e-05
-------------------------------------------------------------
Worst (Seg >> GR):
  M87*_jet                 ratio=3.838e+03  | dz_seg=1.282e+01, dz_base=3.340e-03
  PSR_J1745-29AB           ratio=4.996e+01  | dz_seg=4.160e-02, dz_base=8.327e-04
  BL_Lac                   ratio=3.543e+01  | dz_seg=2.445e+00, dz_base=6.900e-02
  3C273_jet                ratio=3.463e+01  | dz_seg=5.471e+00, dz_base=1.580e-01
  PSR_J0737-3039B          ratio=3.121e+01  | dz_seg=4.412e-04, dz_base=1.414e-05
  PSR_B1913+16             ratio=2.581e+01  | dz_seg=4.150e-04, dz_base=1.608e-05
  3C279_jet                ratio=2.071e+01  | dz_seg=1.110e+01, dz_base=5.360e-01
  IRS7                     ratio=2.039e+01  | dz_seg=2.469e-02, dz_base=1.211e-03
  PSR_J0737-3039A          ratio=1.857e+01  | dz_seg=2.900e-04, dz_base=1.562e-05
  IRS16C                   ratio=1.819e+01  | dz_seg=6.173e-02, dz_base=3.393e-03
-------------------------------------------------------------
TOP 10 – Seg vs GR*SR (kleiner = besser):
-------------------------------------------------------------
Best (Seg << GR*SR):
  EHT_M87                  ratio=2.370e-03  | dz_seg=1.630e-03, dz_base=6.878e-01
  S47_SgrA*                ratio=5.052e-02  | dz_seg=1.897e-06, dz_base=3.754e-05
  S24_SgrA*                ratio=6.290e-02  | dz_seg=1.149e-06, dz_base=1.827e-05
  S19_SgrA*                ratio=6.433e-02  | dz_seg=3.342e-06, dz_base=5.195e-05
  S39_SgrA*                ratio=1.736e-01  | dz_seg=7.146e-06, dz_base=4.117e-05
  S43_SgrA*                ratio=2.357e-01  | dz_seg=5.933e-06, dz_base=2.517e-05
  S49_SgrA*                ratio=3.005e-01  | dz_seg=4.610e-06, dz_base=1.534e-05
  S13_SgrA*                ratio=3.184e-01  | dz_seg=1.183e-05, dz_base=3.714e-05
  S31_SgrA*                ratio=3.278e-01  | dz_seg=1.137e-05, dz_base=3.470e-05
  S45_SgrA*                ratio=3.402e-01  | dz_seg=1.063e-05, dz_base=3.124e-05
-------------------------------------------------------------
Worst (Seg >> GR*SR):
  V404_Cyg                 ratio=5.532e+01  | dz_seg=8.490e-02, dz_base=1.535e-03
  Cyg_X-1                  ratio=1.060e+01  | dz_seg=1.251e-01, dz_base=1.181e-02
  GRS_1915+105             ratio=4.777e+00  | dz_seg=3.217e-01, dz_base=6.734e-02
  3C279_jet                ratio=1.396e+00  | dz_seg=1.110e+01, dz_base=7.951e+00
  G2_SgrA*                 ratio=1.369e+00  | dz_seg=2.582e-02, dz_base=1.887e-02
  G1_SgrA*                 ratio=1.365e+00  | dz_seg=2.054e-02, dz_base=1.505e-02
  X3_SgrA*                 ratio=1.355e+00  | dz_seg=1.336e-02, dz_base=9.856e-03
  PKS_1510-089             ratio=1.305e+00  | dz_seg=4.886e+00, dz_base=3.743e+00
  X1_SgrA*                 ratio=1.183e+00  | dz_seg=9.275e-03, dz_base=7.841e-03
  A0620-00                 ratio=1.181e+00  | dz_seg=2.990e-01, dz_base=2.531e-01
```

---

This output from segspace_enhanced_pi_bridge.py essentially compares how well the Segmented Spacetime model matches the observed redshift 
𝑧
z compared to classical methods — GR (General Relativity) and GR*SR (a combined GR + Special Relativity baseline) — using a π-bridge based on the Chudnovsky formula (here at 200 digits, 16 terms).

Key points from the numbers:

Median |Δz|: The median absolute error in redshift.

GR: 
1.37576
×
10
−
4
1.37576×10
−4

SR: 
1.51057
×
10
−
4
1.51057×10
−4

GR*SR: 
1.88983
×
10
−
4
1.88983×10
−4

Seg: 
1.25502
×
10
−
4
1.25502×10
−4
 → slightly better than GR alone.

Performance (Seg/GR) = 0.912 → roughly 9% better on median.

Point-wise factors (Seg/Baseline): Ratio of the per-object errors.

Q1, Q2, Q3 are quartiles → showing when Seg is much better (ratio < 1) or worse (> 1).

“better = 29/57” means that in about half the cases, Seg outperforms GR.

TOP 10 – Seg vs GR:
The best improvements (Seg ≪ GR) are seen for EHT_M87 and many S-stars near Sgr A*, sometimes by factors of 50–400 in error reduction.
The worst cases (Seg ≫ GR) are mostly jets or pulsars (M87 jet*, 3C273 jet, the double pulsar PSR_J0737-3039).

TOP 10 – Seg vs GR*SR:
Shows the same trend — near the galactic center’s compact stars, Seg does very well; for compact binaries or X-ray binaries, it often performs worse.

π-Bridge (Chudnovsky):
The precise π computation isn’t just for show — it is used as a scaling bridge in the Δ(M) formulation of the segmented model, to link physical length and time segments with high numerical accuracy.

Interpretation:
The results indicate that the segmented model matches observations better than pure GR in many compact-orbit systems near massive objects (Sgr A*, M87). However, in systems dominated by non-gravitational effects (plasma, magnetic fields, radiation pressure) such as jets or pulsars, the model produces larger deviations.
