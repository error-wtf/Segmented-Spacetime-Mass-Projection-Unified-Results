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





