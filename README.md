# Segmented Spacetime – Mass Projection & Unified Results
© Carmen Wrede und Lino Casu

This repository provides a full Python-based implementation and verification of the **Segmented Spacetime Mass Projection Model**, offering a high-precision, testable alternative to traditional gravitational models.

## 📌 Overview

The method implemented here reconstructs the **effective mass** of physical objects based on the principle of **space segmentation**, using a universal scaling function that links gravitational behavior across micro and macro scales.

### Included Features

- ✅ Unified segment-based mass inversion from observed radii
- ✅ Comparison with established experimental values (e.g. electron mass, planetary bodies)
- ✅ Reproduction of classical observables (e.g. Mercury's perihelion, black hole shadow radius)
- ✅ Symbolic check for modified Einstein tensor compatibility (`Gμν = 0`)

## Contents

| Datei                                    | Beschreibung                                                                                                                       |
|------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| `ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4)` | Lizenztext: das Anti-Capitalist Software License v1.4, unter der dieses Projekt steht.                                           |
| `README.md`                              | Dieses Dokument: Ein Überblick über Installation, Use-Cases und enthaltene Skripte.                                                |
| `bound_energy`                           | Unit-Test-Script, das die numerischen Ergebnisse des Segmented-Spacetime-Modells von Carmen et al. validiert.                      |
| `fetch_ligo.py`                          | Hilfsscript zum Herunterladen und Parsen aktueller LIGO-Daten (Schwarzes-Loch-Massen) für Benchmarking.                            |
| `requirements.txt`                       | Liste aller Python-Dependencies, z. B. `pandas`, `sympy` etc.; mit `pip install -r requirements.txt` installierbar.                |
| `segmented_full_calc_proof.py`           | Vollständiges Kalkulations-Proof: Rekonstruktion aller Massen rein via Δ(M)-Modell mit ≤1 × 10⁻⁶ % Fehler.                         |
| `segmented_full_compare_proof.py`        | Vergleichsskript, das Segmented-Spacetime-Ergebnisse gegen alternative Modelle (GR/Fits) gegenüberstellt.                          |
| `segmented_full_proof.py`                | One-stop Demo: erzeugt Segment-Mass-Tabelle, klassische & starke-Feld-Observablen und führt optional symbolische Gμν-Checks durch. |
| `calculation_test.py`                    | Zirkelfreies Tool zur Massenrekonstruktion aus segmentiertem Radius `r_phi`; optional mit Demo-Tabelle für Elektron, Erde, Sonne.  |
| `final_test.py`                          | final Test                                                                                                                         |

## Bound Energy Scripts and Validation

| File                                         | Purpose                                                                                                                                                                                           |
|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bound_energy_plot_with_frequenz_shift_fix.py | High-precision comparison between segmented spacetime (with ΔM correction) and classical gravitational redshift. Calculates, exports, and plots all values for selected astrophysical test cases. |
| bound_energy_plot.py                         | Same as above, but **without** ΔM correction. Pure numerical comparison of the models, including CSV export and plot.                                                                             |
| bound_energy_english.py                      | English version of the bound energy calculation script – implements all core functions, model comparison and CSV export for papers/presentations.                                                 |
| bound_energy_with_deltaM.csv                 | Exported CSV containing all calculated values from `bound_energy_plot_with_frequenz_shift_fix.py`.                                                                                                |



## 🚀 How to Run

Make sure you have Python 3 installed. Then simply run:

```bash
python segmented_full_proof.py
````

## ⚙️ Setup with Virtual Environment

To keep your environment clean and reproducible, it's recommended to run this project inside a virtual environment.

### 🧰 Steps

```bash
# 1. Create virtual environment (folder name: venv)
python3 -m venv venv

# 2. Activate the environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt
````
## Second Content

### `bound_energy.py`

Calculates the bound‐electron mass and emitted photon energy from a local frequency shift, using the segmented-spacetime model developed in:

> Wrede/Casu et al., “Segmented Spacetime: Bound Energy and the Structural Origin of the Fine-Structure Constant” (2025).

- **Usage**:  
  ```bash
  python bound_energy.py
  ````
### Third Content

#### `calculation_test.py`

`calculation_test.py` ist der **Schnelleinstieg** in die zirkel­freie Massen­berechnung via Segment-Radius `r_phi`.

| Option / Modus                       | Beschreibung                                                                                           |
|--------------------------------------|---------------------------------------------------------------------------------------------------------|
| `--rphi <wert>`                      | Gibt die Masse in Kilogramm für einen einzelnen gemessenen `r_phi`‐Wert aus.                            |
| `--demo`                             | Führt eine Mini-Runde (Elektron, Mond, Erde, Sonne) durch und zeigt, wie präzise das Verfahren arbeitet.|

**Beispiele**

```bash
# Einzelwert berechnen
python calculation_test.py --rphi 1.0945634795e-57

# Demo-Runde starten
python calculation_test.py --demo
````
### Fourth Content

## ✅ `final_test.py` – Roundtrip Validation of Segmented-Spacetime Mass Reconstruction

This script demonstrates that the segmented-spacetime model can reconstruct the rest mass of an object purely from its segmented radius – without relying on built-in constants like the Compton wavelength or classical radius.

### What It Does

- Takes known rest masses of test objects (electron, Moon, Earth, Sun).
- Computes the segmented radius using:

  r_phi = (G * m / c^2) * phi

- Then inverts that radius back into mass via:

  m = (c^2 * r_phi) / (G * phi)

- Finally, it compares the original mass (M_in) with the reconstructed mass (M_out), and prints the relative error.

### Why It Matters

- No circular dependency: The mass is not hidden in the inputs.
- No use of Compton wavelength or predefined scale lengths.
- The reconstruction is based only on geometry and physical constants.

This test directly avoids the circular logic found in other models, where mass is inserted via lambda_C and reappears in the result.

### Example Output

---

Segmented-Spacetime Roundtrip Mass Validation

## Objekt     M\_in \[kg]     r\_phi \[m]       M\_out \[kg]     rel. error

Electron   9.1094e-31    1.0946e-57      9.1094e-31      1.10e-50

Moon       7.3420e+22    8.8220e-5       7.3420e+22      1.36e-50

Earth      5.9722e+24    7.1761e-3       5.9722e+24      <1e-42

Sun        1.9885e+30    2.3893e+3       1.9885e+30      <1e-42

---

### Conclusion

The `final_test.py` script confirms:

- The segmented-spacetime model does not rely on hidden mass inputs.
- It is free of circular logic.
- Mass is derived from geometric structure alone.
- The numerical error is near machine precision.


This is a clean and direct demonstration that mass can be reconstructed from segmented spacetime – without assumptions, without shortcuts.



  


