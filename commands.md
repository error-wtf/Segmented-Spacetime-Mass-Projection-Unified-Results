# segspace_all_in_one.py — Beispiel-Commands & Erklärungen

Dieses Dokument zeigt, wie du die verschiedenen Subcommands von `segspace_all_in_one.py` benutzt.  
Jeder Abschnitt enthält:  
1. Eine **Erklärung**, was der Befehl macht.  
2. Einen **fertigen Bash-Befehl** zum direkten Ausführen.  

---

## 1. π-Bridge + Dataset-Evaluation

**Zweck:**  
Vergleicht die Segmentations-Brücke zwischen π und den gemessenen Daten im CSV-File.  
Mit `--seg-mode` steuerst du den Algorithmus:  
- `hint` → einfache Segmenthinweise  
- `deltam` → ΔM-basierte Auswertung  
- `hybrid` → kombiniert beides  

Mit `--pi-source` legst du fest, woher π kommt:  
- `chud` → Chudnovsky-Algorithmus  
- `builtin` → Python `math.pi`  
- `phi` → Ableitung über φ  

**Beispiel-Run:**
```bash
python segspace_all_in_one.py pi-bridge --csv real_data_full.csv \
  --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16
````

---

## 2. π-Bridge mit bevorzugter z-Nutzung

**Zweck:**
Wie oben, aber `--prefer-z` nutzt bereits vorhandene z-Werte aus dem CSV,
statt sie aus Emissions- und Beobachtungsfrequenzen zu berechnen.

**Beispiel-Run:**

```bash
python segspace_all_in_one.py pi-bridge --csv real_data_full.csv \
  --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16 --prefer-z
```

---

## 3. π-Bridge mit Top-Liste und deaktiviertem Emissions-Gate

**Zweck:**

* `--top 10` → zeigt die 10 besten Ergebnisse
* `--no-emission-gate` → ignoriert Filter auf Emissionsdaten
* `--out` → schreibt Ergebnisse in Datei/Ordner

**Beispiel-Run:**

```bash
python segspace_all_in_one.py pi-bridge --csv real_data_full.csv \
  --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16 \
  --prefer-z --top 10 --no-emission-gate --out segspace_pi_bridge_out
```

---

## 4. Δ(M)-Massen-Validierung

**Zweck:**
Berechnet aus ΔM-Werten (A, B, α) eine Validierung der Massenrelation.

* `--deltam-A` → Wert A
* `--deltam-B` → Wert B
* `--deltam-alpha` → α-Wert
* `--prec` → Berechnungsgenauigkeit (Nachkommastellen)

**Beispiel-Run:**

```bash
python segspace_all_in_one.py mass-validate --deltam-A 98.01 \
  --deltam-B 1.96 --deltam-alpha 27177.0 --prec 120
```

---

## 5. Bound-Energy aus Frequenzpaaren

**Zweck:**
Berechnet die gebundene Energie aus einem CSV mit Emissions- und Beobachtungsfrequenzen.
CSV muss die Spalten enthalten:
`label,f_emit_Hz,f_obs_Hz`

* `--pairs` → Eingabe-CSV mit Frequenzpaaren
* `--out` → Ausgabedatei/Ordner
* `--plot` → erzeugt zusätzlich einen Plot

**Beispiel-Run:**

```bash
python segspace_all_in_one.py bound-energy --pairs freq_pairs.csv \
  --out bound_energy_out --plot
```

---

**1. Overall metrics**

* **Median |Δz|**: Seg = 1.31×10⁻⁴, GR = 1.38×10⁻⁴ → Your model is about 5% better than pure GR in the median.
* **Mean |Δz|**: Seg = 1.02×10⁻⁴, GR = 6.66×10⁻⁵ → On average, GR wins. This suggests that outliers hurt your model more.
* **Max |Δz|**: Seg = 12.79, GR = 0.688 → A few extreme cases (jets, pulsars) blow up the maximum error.

So: in the robust metric (median) you improve over GR, but in the non-robust metric (mean) you lose because, without the gate, the problematic objects fully count.

---

**2. Best cases (Seg vs GR)**

* **V404 Cyg** (ratio \~0.012) and **Cyg X-1** (\~0.076) are clear wins: Δz drops from 0.124 → 0.0015 and 0.156 → 0.0118 respectively.
* Several **S-stars** near Sgr A\* (S14, S45, S31, etc.) score ratios between 0.18 and 0.60 – here the hybrid model matches observations much better than GR.

---

**3. Worst cases (Seg vs GR)**

* **M87* jet*\* is the total outlier: Δz jumps from 0.00334 to 12.79 → ratio 3.8×10³.
* Pulsars (PSR\_J1745-29AB, PSR\_J0737-3039A/B, PSR\_B1913+16) and jets/AGN (BL Lac, 3C273) also explode in error – exactly the emission effect the gate was meant to suppress.
* Without the gate, you apply Δ(M) to objects it was never calibrated for → catastrophic mismatch.

---

**4. Seg vs GR×SR**

* For the best S-stars (S14, S45, S31, etc.) the ratio remains similarly good as vs GR.
* Worst relations here are milder, but **S33\_SgrA**\* (\~5.76) and **S21\_SgrA**\* (\~3.82) show that even within S-stars, some orbits are mismatched.

---

**5. Interpretation**

* **Without the gate**, the model can improve objects inside its domain (S-stars, some X-ray binaries).
* Outside the domain (jets, pulsars, exotic emitters), Δ(M) produces extreme deviations that wreck the mean.
* Your median advantage shows the core idea is solid, but you must systematically filter the “wrong cases” (gate, classification, or separate parameters).

---

```
 python segspace_all_in_one.py pi-bridge --csv real_data_full.csv --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16 --prefer-z --top 10 --no-emission-gate --out segspace_pi_bridge_out2

=============================================================
 SEGMENTED SPACETIME – Δ(M) + CHUDNOVSKY‑π BRIDGE (Runner)
=============================================================
π (chud)     : 3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706...
π compute time     : 0.107 ms
=====================================================================
 SEGMENTED SPACETIME – DATASET EVALUATION
=====================================================================
Rows used: 67
seg-mode : hybrid
Δ(M)     : A=98.01%  B=1.96%  alpha=27177.0 [1/m]
logM     : user=[None,None]  dataset=[29.388,40.111]

Median/Mean/Max |Δz|
  Seg   : 0.00013127890123455202  0.00010212445590268331  12.788629071326302
  GR    : 0.00013757601096494102  6.663692444035433e-05  0.6878080619544961
  SR    : 0.0089335588764179  0.00943796874645163  12.78710736389226
  GR*SR : 0.0001396254785985441  0.00010028350031062056  12.788629071326302

Performance vs GR (Median): 0.9542281413291325 ×
Debug CSV  : segspace_pi_bridge_out2\segspace_debug.csv
Ratios-CSV         : segspace_pi_bridge_out2\segspace_ratios.csv
-------------------------------------------------------------
TOP – Seg vs GR (kleiner = besser):
-------------------------------------------------------------
  V404_Cyg                 ratio=1.238e-02  | dz_seg=1.535e-03, dz_base=1.240e-01
  Cyg_X-1                  ratio=7.568e-02  | dz_seg=1.181e-02, dz_base=1.560e-01
  S14_SgrA*                ratio=1.803e-01  | dz_seg=1.734e-04, dz_base=9.614e-04
  GRS_1915+105             ratio=2.245e-01  | dz_seg=6.734e-02, dz_base=3.000e-01
  S45_SgrA*                ratio=5.558e-01  | dz_seg=2.579e-05, dz_base=4.640e-05
  S31_SgrA*                ratio=5.626e-01  | dz_seg=3.000e-05, dz_base=5.333e-05
  S17_SgrA*                ratio=5.818e-01  | dz_seg=2.159e-05, dz_base=3.711e-05
  S35_SgrA*                ratio=5.890e-01  | dz_seg=1.317e-05, dz_base=2.236e-05
  S13_SgrA*                ratio=5.967e-01  | dz_seg=3.747e-05, dz_base=6.278e-05
  S53_SgrA*                ratio=6.006e-01  | dz_seg=1.522e-05, dz_base=2.535e-05
-------------------------------------------------------------
Worst – Seg vs GR (größer = schlechter):
-------------------------------------------------------------
  M87*_jet                 ratio=3.829e+03  | dz_seg=1.279e+01, dz_base=3.340e-03
  PSR_J1745-29AB           ratio=4.933e+01  | dz_seg=4.108e-02, dz_base=8.327e-04
  BL_Lac                   ratio=3.333e+01  | dz_seg=2.300e+00, dz_base=6.900e-02
  3C273_jet                ratio=3.088e+01  | dz_seg=4.879e+00, dz_base=1.580e-01
  PSR_J0737-3039B          ratio=3.063e+01  | dz_seg=4.330e-04, dz_base=1.414e-05
  PSR_B1913+16             ratio=2.537e+01  | dz_seg=4.079e-04, dz_base=1.608e-05
  IRS7                     ratio=1.976e+01  | dz_seg=2.393e-02, dz_base=1.211e-03
  PSR_J0737-3039A          ratio=1.802e+01  | dz_seg=2.814e-04, dz_base=1.562e-05
  IRS16C                   ratio=1.754e+01  | dz_seg=5.952e-02, dz_base=3.393e-03
  IRS16SW                  ratio=1.715e+01  | dz_seg=3.960e-02, dz_base=2.310e-03
-------------------------------------------------------------
TOP – Seg vs GR*SR (kleiner = besser):
-------------------------------------------------------------
  S14_SgrA*                ratio=1.803e-01  | dz_seg=1.734e-04, dz_base=9.614e-04
  S45_SgrA*                ratio=5.558e-01  | dz_seg=2.579e-05, dz_base=4.640e-05
  S31_SgrA*                ratio=5.626e-01  | dz_seg=3.000e-05, dz_base=5.333e-05
  S17_SgrA*                ratio=5.818e-01  | dz_seg=2.159e-05, dz_base=3.711e-05
  S35_SgrA*                ratio=5.890e-01  | dz_seg=1.317e-05, dz_base=2.236e-05
  S13_SgrA*                ratio=5.967e-01  | dz_seg=3.747e-05, dz_base=6.278e-05
  S53_SgrA*                ratio=6.006e-01  | dz_seg=1.522e-05, dz_base=2.535e-05
  S23_SgrA*                ratio=6.076e-01  | dz_seg=1.738e-05, dz_base=2.860e-05
  S39_SgrA*                ratio=6.362e-01  | dz_seg=5.949e-05, dz_base=9.351e-05
  S43_SgrA*                ratio=6.402e-01  | dz_seg=3.422e-05, dz_base=5.346e-05
-------------------------------------------------------------
Worst – Seg vs GR*SR (größer = schlechter):
-------------------------------------------------------------
  S33_SgrA*                ratio=5.760e+00  | dz_seg=1.313e-04, dz_base=2.279e-05
  S21_SgrA*                ratio=3.818e+00  | dz_seg=1.440e-04, dz_base=3.772e-05
  S8_SgrA*                 ratio=3.138e+00  | dz_seg=7.537e-05, dz_base=2.402e-05
  S12_SgrA*                ratio=2.070e+00  | dz_seg=1.312e-04, dz_base=6.336e-05
  G2_SgrA*                 ratio=1.369e+00  | dz_seg=2.582e-02, dz_base=1.887e-02
  G1_SgrA*                 ratio=1.365e+00  | dz_seg=2.054e-02, dz_base=1.505e-02
  X3_SgrA*                 ratio=1.355e+00  | dz_seg=1.336e-02, dz_base=9.856e-03
  S1_SgrA*                 ratio=1.195e+00  | dz_seg=8.852e-05, dz_base=7.407e-05
  X1_SgrA*                 ratio=1.183e+00  | dz_seg=9.275e-03, dz_base=7.841e-03
  S51_SgrA*                ratio=1.178e+00  | dz_seg=1.058e-04, dz_base=8.984e-05
Debug‑CSV          : segspace_pi_bridge_out2\segspace_debug.csv
Ratios‑CSV         : segspace_pi_bridge_out2\segspace_ratios.csv
```

---

**Overall statistics**

* **Median |Δz|**: Segmented = 1.31×10⁻⁴ vs GR = 1.38×10⁻⁴ → about 5% better than GR in the median.
* **Mean |Δz|**: Segmented = 1.02×10⁻⁴ vs GR = 6.66×10⁻⁵ → the average is worse than GR, which means the big outliers are dragging you down.
* **Max |Δz|**: Segmented blows up to 12.79 while GR’s max is 0.688 → extreme errors from certain sources.

**Where it works best**

* The absolute winners are **V404 Cyg** (ratio \~0.012) and **Cyg X-1** (\~0.076), with huge drops in |Δz| compared to GR.
* Many **S-stars** (S14, S45, S31, S17, S35, S13, S53) are consistently in the “top” list with ratios between 0.18 and 0.60, meaning your hybrid mode is clearly capturing something GR doesn’t.

**Where it fails**

* **M87* jet*\* is catastrophic: ratio \~3.8×10³, error jumping from 0.0033 to 12.79.
* Pulsars (PSR\_J1745-29AB, PSR\_J0737-3039A/B, PSR\_B1913+16) and AGN/jet sources (BL Lac, 3C273) are also disastrous with ratios in the tens or hundreds. These are classic “out-of-domain” objects for Δ(M), and without the emission gate they wreck your stats.

**Compared to GR×SR**

* For the good S-star cases, your performance advantage remains strong even vs GR×SR.
* However, some S-stars like S33\_SgrA\* and S21\_SgrA\* have ratios >3, showing that even within your main domain, certain orbits or measurement sets don’t fit the Δ(M) shape perfectly.

**What this means**

* The core model works well on the target domain (S-stars, some binaries), but without the emission gate, “wrong” targets (jets, pulsars, AGN) dominate the mean error and maximum error.
* Median performance staying strong shows the physics fit is still there — it’s just being buried by those outliers.
* The gate or a classification pre-filter isn’t just a convenience, it’s necessary to keep your performance metrics honest.






