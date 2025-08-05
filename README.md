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

| Datei                                    | Beschreibung                                                                                       |
|------------------------------------------|----------------------------------------------------------------------------------------------------|
| `ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4)` | Lizenztext: das Anti-Capitalist Software License v1.4, unter der dieses Projekt steht.             |
| `README.md`                              | Dieses Dokument: Ein Überblick über Installation, Use-Cases und enthaltene Skripte.                |
| `carmens_paper_test.py`                  | Unit-Test-Script, das die numerischen Ergebnisse des Segmented-Spacetime-Modells gegen Carmen et al. validiert. |
| `compare.csv`                            | Rohdaten-Tabelle mit Referenz- und berechneten Massen zur weiteren Auswertung und Visualisierung.  |
| `fetch_ligo.py`                          | Hilfsscript zum Herunterladen und Parsen aktueller LIGO-Daten (Schwarzes-Loch-Massen) für Benchmarking. |
| `requirements.txt`                       | Liste aller Python-Dependencies, z. B. `pandas`, `sympy` etc.; mit `pip install -r requirements.txt` installierbar. |
| `segmented_full_calc_proof.py`           | Vollständiges Kalkulations-Proof: Rekonstruktion aller Massen rein via Δ(M)-Modell mit ≤1 × 10⁻⁶ % Fehler. |
| `segmented_full_compare_proof.py`        | Vergleichsskript, das Segmented-Spacetime-Ergebnisse gegen alternative Modelle (GR/Fits) gegenüberstellt. |
| `segmented_full_proof.py`                | One-stop Demo: erzeugt Segment-Mass-Tabelle, klassische & starke-Feld-Observablen und führt optional symbolische Gμν-Checks durch. |


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

