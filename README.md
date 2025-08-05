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

- **Fine‐structure constant** (`α_fs`): pulled from SciPy’s CODATA value and reconfirmed by the paper’s derivation.
- **Segmentation density** (`α_seg`): computed as the relative frequency shift `(1 – f_obs / f_emit)`, representing the local change in segment density.
- **Bound mass** (`m_bound`):  
  \[ m_bound = \frac{h · f_emit}{α_seg · c²} \]  
  the mass that a free electron must “lose” to become bound, per the model.
- **Photon energy** (`E_gamma`):  
  \[ E_γ = α_seg · m_bound · c² \]  
  the energy of the photon emitted when the electron transitions to its bound state.
- **Usage**:  
  ```bash
  python bound_energy.py


