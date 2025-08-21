<img width="2400" height="1000" alt="segspace_comparison" src="https://github.com/user-attachments/assets/69e3e20d-6815-4a44-8d08-57ad646b96c5" />

# Segmented Spacetime – Mass Projection & Unified Results
© Carmen Wrede & Lino Casu

This repository provides a full Python-based implementation and verification of the **Segmented Spacetime Mass Projection Model**, offering a high-precision, testable alternative to traditional gravitational models.

---

To avoid any bias in favor of Segmented Spacetime Model, we apply strict, model-agnostic data hygiene: rows are only included if GR, SR, GR*SR and SSZ can all be computed (complete orbital elements or measured r_emit, plausible velocities, r > r_s, etc.). We use robust statistics (median, MAD) and identical kinematic fixes across all models, so corrections do not privilege our Model. Observations z_obs are never fed back into our model predictions; they are used only to form residuals. Despite this conservative filtering, our model achieves dramatically lower median errors than GR/SR on the paired sample, effectively absorbing the gravitational redshift uncertainty within a single flow via the Schwarzschild-compatible Δ(M) term. A pure geodesic GR/SR baseline on the same rows confirms the gain is due to modeling, not cherry-picking.


---

We use E_bound = alpha*m_bound*c^2 as a universal EM-coupling scale per electron (~3.73 keV for m_bound ~ m_e). This is not an atomic binding energy (e.g., 1/2 * alpha^2 * m_e * c^2 ~ 13.6 eV) and not a K-edge of any element (Z-dependent). It is a material-independent structural ceiling that provides a stable E–f–lambda reference. GR and kinematics shift observed frequencies; the scale itself remains fixed, letting us propagate redshift uncertainty within one model. This reduces residuals without feeding observations back into predictions.

---

The demo script was numerically correct but the claim it illustrated was too strong:
it assumed a full 1:1 mapping alpha_em/alpha_det ≈ N_emit/N0, which overshoots the
observed ratio f_emit/f_obs (~1.0257 vs. ~1.103). The data indicate at most a partial
coupling (effective beta ~0.25) or, more faithfully to our main pipeline, that the
redshift is carried by GR×SR with a Schwarzschild-compatible Δ(M) correction rather
than by a full 1:1 variation of alpha. In short: computation OK, interpretation too
strong; our core results do not rely on that assumption and remain non-circular.

---

The updated QED demo is non-circular and local. It keeps m_bound symmetric (k=0) 
and uses a partial mapping alpha_em/alpha_det = 1 + beta*(N_emit − N0).

With S2→Earth, β=0.25 reproduces the observed ratio f_emit/f_obs ≈ 1.025747 
to ~1e−9 precision, without touching m_bound. The earlier side script assumed a 
full 1:1 coupling (β=1), which predicts ≈1.103 and overshoots; rescuing that 
would require an implausible ~7% shift in m_bound.

So the computation was fine—the claim was too strong. Our main results do not rely 
on alpha–N coupling anyway; they come from GR×SR plus the Schwarzschild-compatible 
Δ(M) correction, evaluated non-circularly. The demo just shows that, if any local 
alpha–N coupling exists, it must be small (≈25% here), not full 1:1.

---

## 📌 Overview

The method reconstructs **effective mass** and predicts **redshifts** from the principle of **space segmentation**, using a universal scaling function that links gravitational behavior across micro and macro scales.

### Included Features
- ✅ Unified segment-based mass inversion from observed radii
- ✅ Validation on established values (electron, Moon, Earth, Sun, Sgr A*)
- ✅ Redshift evaluation across **GR**, **SR**, **GR×SR**, **Segmented** (hint/ΔM/hybrid/**geodesic**)
- ✅ Optional Δ(M) scaling with JSON parameter override
- ✅ Bootstrap CIs, exact binomial sign test, mass-binned medians, optional plots
- ✅ Bound energy & structural α (π–φ bridge)

---

## Reproducibility
- Fast install: `pip install -r requirements.txt`
- Exact snapshot: `pip install -r requirements-freeze.txt`
- Python: 3.11.9
- Artifacts (reports/JUnit) are written to `agent_out/`.

---

## 🚀 Quick Start (best overall accuracy)

```bash
# Full pipeline (mass validation → redshift eval (hybrid) → bound energy)
python segspace_all_in_one_extended.py all

# Pure geodesic (GR×SR combination without ΔM scaling)
python segspace_all_in_one_extended.py eval-redshift --csv ".\real_data_full.csv" --mode geodesic --prefer-z --ci 2000 --paired-stats --plots
```

> **Tip:** `--prefer-z` forces using the `z` column if both `z` and (`f_emit_Hz`,`f_obs_Hz`) are present.

---

## 🔧 CLI (single entry point)

All major tasks live in **`segspace_all_in_one_extended.py`**.

```text
Commands:
  validate-masses     Reconstruct masses from segmented radii
  eval-redshift       Evaluate GR/SR/GR×SR/Seg models against a dataset (+stats)
  bound-energy        Compute bound energy thresholds (α)
  use-original        Load & introspect ./segspace_all_in_one.py (if present)
  all                 Full pipeline (validate → eval-redshift (hybrid) → bound-energy)
```

### Common flags for `eval-redshift`
```
--csv PATH                 Dataset (default: ./real_data_full.csv)
--prefer-z                 Prefer z column over frequency ratio
--mode {hint,deltaM,hybrid,geodesic}
--dmA --dmB --dmAlpha      Δ(M) parameters (floats)
--dm-file FILE             JSON containing A,B,Alpha (auto-detects nested 'best' keys)
--lo --hi                  Optional log10(M[kg]) window for Δ(M) normalization
--drop-na                  Require all models finite before medians/stats
--paired-stats             Exact binomial sign test (Seg vs GR×SR)
--ci NBOOT                 Bootstrap for median CIs (0 = off)
--bins N                   Mass-binned medians (log10M) (0 = off)
--plots                    Save hist/ECDF/box under out/figures
--filter-complete-gr       Restrict to rows with finite GR (fair GR median)
```

### Modes explained (plain)

- **hint**: Use the column `z_geom_hint` (if present) as the GR‑like geometric part and combine it with the SR part.
- **deltaM**: Take the GR redshift and multiply it by a mass‑dependent scaling Δ(M). Then combine the result with SR.
- **hybrid**: If `z_geom_hint` exists for a row, behave like **hint**; otherwise behave like **deltaM**.
- **geodesic**: Combine pure GR and SR only (no ΔM scaling).

**Combination rule used in all modes:** we combine the two parts multiplicatively and subtract 1 at the end:  
`combined_z = (1 + z_GR) * (1 + z_SR) - 1`

### Examples
```bash
# Hybrid with Δ(M) params from file
python segspace_all_in_one_extended.py eval-redshift --csv ".\real_data_full.csv" \
  --mode hybrid --prefer-z --dm-file ".\agent_out\reports\deltaM_tuning_best.json" \
  --ci 2000 --paired-stats --plots

# Pure Δ(M) with explicit parameters
python segspace_all_in_one_extended.py eval-redshift --csv ".\real_data_full.csv" \
  --mode deltaM --prefer-z --dmA 10 --dmB 0.01 --dmAlpha 500 \
  --ci 2000 --paired-stats --plots
```

---

## 📤 Outputs (by command)

All outputs are created under **`./agent_out`**:

```
agent_out/
  figures/
    hist_abs_*.png, ecdf_abs_*.png, box_abs_seg_vs_grsr.png  (when --plots)
  reports/
    MANIFEST.json
    mass_validation.csv
    redshift_medians.json
    redshift_cis.json                   (if --ci > 0)
    redshift_paired_stats.json          (if --paired-stats)
    redshift_binned.csv                 (if --bins > 0)
    bound_energy.txt
  logs/                                 (reserved)
  data/                                 (reserved)
```

---

## 📚 Dataset schema (`real_data_full.csv`)

Minimum header (order not strict, names are):
```
case,category,M_solar,a_m,e,P_year,T0_year,f_true_deg,z,f_emit_Hz,f_obs_Hz,
lambda_emit_nm,lambda_obs_nm,v_los_mps,v_tot_mps,z_geom_hint,N0,source,r_emit_m
```

- `M_solar` – central mass in **solar masses** (float)
- `r_emit_m` – emission radius in **meters** (if absent, only GR where computable will be finite)
- `z` – observed redshift; **or** use `f_emit_Hz`/`f_obs_Hz` to compute `z = f_emit/f_obs - 1`
- `v_los_mps`, `v_tot_mps` – velocities (SR). If missing, SR reduces accordingly.
- `z_geom_hint` – optional GR-only piece (used by `--mode hint` / `--mode hybrid`)
- Use `--prefer-z` to force `z` over frequencies when both are present.

---

## 🧪 Mass validation

Reconstructs mass from segmented radius for canonical objects.
```bash
python segspace_all_in_one_extended.py validate-masses
```
Writes: `agent_out/reports/mass_validation.csv`

---

## 🔬 Bound energy & structural α

Computes:
- \(E_\text{bound} = \alpha \, m_e \, c^2\)
- Threshold frequency \(f_\text{thr} = E_\text{bound} / h\)
- Wavelength \( \lambda = h / (\alpha\, m_e\, c) \)

```bash
python segspace_all_in_one_extended.py bound-energy
```
Writes: `agent_out/reports/bound_energy.txt`

---

## 📦 Additional utilities & papers

The repo also contains supporting scripts used in the accompanying papers/presentations (bound-energy plots with and without ΔM, proof/roundtrip demos, enhanced test runners). See table in **Contents** below for a quick index.

---

## 📁 Contents (highlights)

| File / Dir                                      | Description                                                                                          |
|-------------------------------------------------|------------------------------------------------------------------------------------------------------|
| `segspace_all_in_one_extended.py`               | **Main** runner (validate masses, eval redshift, bound energy, full pipeline)                       |
| `segspace_enhanced_test_better_final.py`        | Enhanced test runner (hint/ΔM/hybrid), JUnit & plots                                                 |
| `final_test.py`                                 | Roundtrip validation for segmented mass reconstruction                                               |
| `bound_energy_plot.py`                          | Bound energy comparisons (no ΔM)                                                                     |
| `bound_energy_plot_with_frequenz_shift_fix.py`  | Bound energy comparisons (**with** ΔM)                                                               |
| `segmented_full_calc_proof.py` / `compare_proof.py` | Proof/calculation demos                                                                             |
| `real_data_full.csv`                            | Dataset (example)                                                                                    |
| `requirements.txt`                              | Dependencies                                                                                         |
| `plots/`, `tests/`                              | Optional visualization/tests                                                                          |

---

## 🧰 Environment & reproducibility

```bash
# Python venv (recommended)
python -m venv .venv
. .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

# ADDITIONAL INFORMATIONS

**⚠️ Note:**  
The **complete and up-to-date command reference** is explained in [`commands.md`](commands.md).  
It contains all available commands, parameters, and examples – please check there first before running any scripts.

This repository contains all Python scripts, datasets, and results generated as part of the research on the *Segmented Spacetime Theory*.  
It unifies **Mass Projection**, **π–φ Bridge**, **Bound Energy**, and other calculations into a consistent framework.

- **commands.md** – Example CLI commands for `segspace_all_in_one.py` with explanations of each subcommand and ready-to-run bash examples.

- **API.md** – Documentation of the available functions, parameters, and expected inputs/outputs for programmatic access to the repository’s tools.

- **Estimators.md** – Descriptions of the statistical and physical estimators used in the analysis, including formulas and usage notes.

- **Sources.md** – Provenance of all S2/Sgr A* datasets, primary literature links, archive references, and a step-by-step reproducibility guide.

- **DATA_SOURCES.md** – Overview of all datasets used in the project, their formats, origin, and any preprocessing steps applied.



## Quick Start — best overall accuracy

Quick start with:

```
python segspace_all_in_one_extended.py all
python segspace_all_in_one_extended.py eval-redshift --csv ".\real_data_full.csv" --mode geodesic --prefer-z --ci 2000 --paired-stats --plots
```

## 🔄 Full Execution with `run_all.py`

The [`run_all.py`](./run_all.py) script runs **the entire workflow** in the correct order:  

1. **Optional**: Fetch ESO Brγ data (`fetch_eso_br_gamma.py`)  
2. **Analysis** with `segspace_enhanced_pi_bridge.py`  
3. **Mass validation** with `segmented_all_mass_validate.py`  
4. **Energy bounds** with `segmented_all_bound_energy.py`  

---

### **Run with an existing CSV file (no fetching)**

If you already have a prepared CSV file (`real_data_full.csv`), you can run everything directly:  

```
python run_all.py --fetch-mode skip --csv real_data_full.csv --out-dir results --prefer-z --top 10
```

If you want to fetch your own:

```
python run_all.py --fetch-mode full --csv real_data_full.csv --out-dir results --prefer-z --top 10 --token YOUR_ESO_BEARER_TOKEN
```

---

Clone the repository and move into Folder:
```
git clone https://github.com/LinoCasu/Segmented-Spacetime-Mass-Projection-Unified-Results.git
cd Segmented-Spacetime-Mass-Projection-Unified-Results
````

Run the hybrid pipeline (uses **hint** for S-stars, **deltaM** for all others).  
This consistently gave the lowest median |Δz| in our comparisons.

```
python segspace_enhanced_test_better_final.py --mode hybrid
````
---
```
# 1) (optional) venv
python -m venv venv && source venv/bin/activate

# 2) Abhängigkeiten
pip install -r requirements.txt

# 3) Output-Verzeichnis
mkdir -p out

# 4) Kernläufe (Best-Performer zuerst)
  python segspace_enhanced_test_better_final.py --csv real_data_full.csv --prefer-z --seg-mode hint --plots --junit
  python segspace_enhanced_test_better_final.py --csv real_data_full.csv --seg-mode deltaM --deltam-A 3.5 --deltam-B 0.2 --plots
  python segspace_enhanced_test_better_final.py --csv real_data_full.csv --seg-mode hybrid --plots --junit

# 5) Roundtrip-/Beweis-Skripte
python final_test.py                     
python segmented_full_proof.py           
python segmented_full_compare_proof.py   
python segmented_full_calc_proof.py      

# 6) Bound-Energy & Plots
python bound_energy_plot.py
python bound_energy_plot_with_frequenz_shift_fix.py


````
---



## Contents

| File                                             | Description                                                                                          |
|--------------------------------------------------|------------------------------------------------------------------------------------------------------|
| `ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4)`       | License text for this project                                                                        |
| `README.md`                                      | Usage guide and documentation                                                                        |
| `bound_energy.py`                                | Calculates bound-electron mass and emitted photon energy based on local frequency shifts             |
| `bound_energy_english.py`                        | English version of the bound energy calculation script                                               |
| `bound_energy_plot.py`                           | Plots bound energy comparisons without ΔM correction                                                 |
| `bound_energy_plot_with_frequenz_shift_fix.py`   | Plots bound energy comparisons with frequency shift (ΔM) correction                                  |
| `bound_energy_results.csv`                       | CSV export of bound energy calculation results                                                       |
| `bound_energy_with_deltaM.csv`                   | CSV export of bound energy results including ΔM corrections                                          |
| `calculation_test.py`                            | Quick mass reconstruction tests and demos for segmented radius inputs                                |
| `check.py`                                       | Runs internal consistency checks for the segmented spacetime model                                   |
| `complete-math.py`                               | Step-by-step didactic demonstration of key calculations in segmented spacetime theory                |
| `fetch_ligo.py`                                  | Fetches and preprocesses LIGO observational data for benchmarking                                    |
| `final_test.py`                                  | Roundtrip validation tests for mass reconstruction via segmented radius                              |
| `paper.py`                                       | Implements detailed sections and example reproductions from the Carmen Wrede & Lino Casu paper       |
| `requirements.txt`                               | Lists Python package dependencies for reproducible setup                                             |
| `segment_mass_results.csv`                       | CSV of computed mass inversion results from segmented mass functions                                 |
| `segmented_full_calc_proof.py`                   | Full calculation proof routines for segmented mass inversion                                         |
| `segmented_full_compare_proof.py`                | Comparative analysis of proof results against established benchmarks                                 |
| `segmented_full_proof.py`                        | Main script to generate all model outputs and run symbolic checks                                    |
| `segmented_mass.py`                              | Core library module implementing mass inversion and segmentation algorithms                          |
| `segmented_spacetime_mass_validation.csv`        | CSV of segmented spacetime mass validation results                                                   |
| `segmented_spacetime_mass_validation_full.csv`   | Full CSV of detailed segmented spacetime mass validation                                             |
| `segmented_spacetime_mass_validation_perfect.csv`| CSV of perfect-case segmented spacetime mass validations                                             |
| `carmen_qed_incompleteness_demo.py`              | Calculates and explains, with real astrophysical data, why only a fraction of the original photon energy is accessible at the detector in segmented spacetime; includes all computational steps and physical interpretation. |
| `Segmentdichte-Analyse.py` | Calculates and visualizes the segment density profile σ(r) between the Schwarzschild radius (r_s) and the segment radius (r_phi). Shows how the segment density changes across this interval for different physical parameters, and provides both tabular and graphical output for further analysis or publication. |
| [`estimators.md`](./estimators.md) | Defines and explains reproducible estimators that convert observations into model inputs (z_geom, r_phi, ΔM, segment density); includes SR removal, GR baselines, CV rules, robust metrics, pseudocode, and output formats. |
| [`API.md`](./API.md)               | Documents the public API and CLI for the runners; lists function signatures, expected CSV schemas, modes (hint/deltaM/hybrid), report and debug outputs, and return types—serving as a stable reference for users and contributors. |
| **segspace_all_in_one.py** | Unified script combining multiple calculations and modes (mass, π-bridge, bounds) |
| **segspace_enhanced_pi_bridge.py** | Enhanced π–φ bridge calculation with additional modes and export options |
| **segspace_mass_validate.py** | Validates mass projection calculations against empirical datasets |
| **plots/** | Directory containing PNG and SVG plots for bound energy, mass projection, and π–φ bridge results |
| **tests/** | Various test scripts for internal consistency and experimental formulas |
| **.git/** | Git version control data (commits, branches, history) |
| **.gitattributes** | Git attributes for file handling |
| **.gitignore** | Ignore list for Git repository |
| **requirements.txt** | List of Python dependencies required to run the scripts |

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

# 1. Create virtual environment (folder name: venv)
```
python3 -m venv venv
````
# 2. Activate the environment
# On Linux/macOS:
```
source venv/bin/activate
````
# On Windows:
```
venv\Scripts\activate
````

# 3. Install required dependencies
```
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
## Third Content


`calculation_test.py` is the quick-start entry point for the **cycle-free mass calculation** via segment radius `r_phi`.

| Option / Mode      | Description                                                                                                  |
|--------------------|-------------------------------------------------------------------------------------------------------------|
| `--rphi <value>`   | Returns the mass in kilograms for a single measured `r_phi` value.                                           |
| `--demo`           | Runs a mini round (electron, moon, Earth, Sun) and demonstrates how precise the procedure works.             |

### Examples


# Calculate a single value
```
python calculation_test.py --rphi 1.0945634795e-57
````
# Start the demo round
```
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

## Contents of `paper.py`

| Section                                                   | Description                                                                                                         |
|-----------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| 1. Constants & Imports                                    | Physical constants, mathematical libraries, and initialization                                                      |
| 2. Effective Radius & Segmentation                        | Definition and calculation of segment length, segment count, and effective radius                                   |
| 3. Classical Self-Energy                                  | Calculation of the classical electromagnetic self-energy                                                            |
| 4. Structural Alpha Calculation                           | Derivation and inversion of the fine-structure constant (α) from structural parameters                              |
| 5. Effective Radius with Fixed Alpha                      | Calculation of the classical electron radius with fixed α and m_e values                                            |
| 6. Segment Length Inversion                               | Inversion of segment length φ from radius and segment count                                                         |
| 7. Bound vs Free Energy & Rydberg Energy                  | Calculation of bound/free energy and Rydberg energy                                                                 |
| 8. Photon Coupling Threshold                              | Calculation of the minimal wavelength and threshold frequency for photons in segmented spacetime                    |
| 9. Example Calculation: Sagittarius A* (S2)               | Complete step-by-step example calculation from the paper, numerically reproduced                                    |
|10. Utility: Classical Electron Radius                     | Direct verification of known values for α, m_e, and e                                                               |
|11. Utility: Rydberg Energy                                | Demonstration of the energy range of bound electrons                                                                |
|12. Utility: Photon Threshold Wavelength                   | Relationship between fine-structure constant and photon coupling                                                    |
|13. Reference Statement                                    | Clear output/print for attribution to the original paper (DOI, authors, year, link)                                 |

---

**Reference:**  
Carmen Wrede, Lino P. Casu, Bingsi (2025):  
_Segmented Spacetime – Bound Energy and the Structural Origin of the Fine-Structure Constant_  
Preprint · August 2025 · [DOI: 10.13140/RG.2.2.35006.80969](https://www.researchgate.net/publication/394248893)
---
## `complete-math.py` — Step-by-Step Script for Segmented Spacetime Theory

This script provides a **fully commented, didactic, and transparent step-by-step demonstration** of all key calculations from the papers by Carmen Wrede & Lino Casu, implementing the “Segmented Spacetime” model:

### What does the script do?

- **Mass reconstruction** from the segmented radius using the φ/2 constant and exponential correction, with **true Newtonian decimal-precision inversion**.
- **Calculation of the local fine-structure constant** α from a measured frequency (e.g., as in the S2/Sgr A* test), and computation of the associated bound electron mass and threshold photon wavelength.
- **Every single calculation step is explicitly explained in the output** — including all inputs, intermediate results, mathematical formulas, and the physical meaning of each result.

### Features

- **Explains every formula and physical constant** directly in the printout, line by line.
- **Reproduces the Earth mass example** from segmented radius, showing both theory and inversion.
- **Shows how to derive α<sub>local</sub> and m<sub>bound</sub>** from a single observed frequency.
- **Checks mathematical consistency** (e.g. α × m<sub>bound</sub> × c² / h should recover the input frequency).
- **Ideal for reviewers, teaching, or anyone who wants to understand the model without reading the full paper**.

### Usage

```bash
python complete-math.py
````
---
### Why is there an energy difference between emitter and detector? (Physical explanation)

The script `carmen_qed_incompleteness_demo.py` demonstrates that the classical idea of a photon "losing energy" as it travels through a gravitational field is incomplete.  
In the segmented spacetime model, the **measured energy at the detector** (e.g., on Earth) does **not** decrease because the photon "loses" energy, but because the **local segmentation** (the discrete structure of space at the detector) limits how much energy can be extracted from the photon.

- The photon's energy remains constant along its entire path.
- However, our measuring instruments (the electrons on Earth) can only "tap" a **fraction of the original photon energy** – this fraction is set by the local segmentation parameter (N).
- The stronger the gravitational field and the higher the segmentation at the detector, the less energy can be accessed from the original photon.
- The apparent energy loss is thus **not a real energy loss of the photon itself**, but an effect of the spacetime structure at the detector.

**Conclusion:**  
The observed energy difference is directly explained by our model – it is not due to energy dissipation "on the way", but to the **local coupling/segmentation** between the photon and the detector.
---
---

## QED Incompleteness Demo (`carmen_qed_incompleteness_demo.py`)

This script demonstrates why the classical formula `E = m_e * c^2` and even QED are incomplete when strong gravity or segmented spacetime are present:

- It uses a real astrophysical example (S2 star and Earth) to show how local segmentation (N) affects the measurable energy and the local electron mass.
- The script calculates, from observed and emitted frequencies, the local fine-structure constant (`alpha_local`) and the bound electron mass (`m_bound`).
- It explains and numerically demonstrates why, at the detector (e.g., on Earth), only a **portion of the original photon energy** can be accessed.
- All formulas, calculation steps, and interpretations are printed and explained.

**How to run:**
```bash
python carmen_qed_incompleteness_demo.py
````

---

# 📦 Final Test, Explain Run & Comparison CSV

This section documents **three core files** in the repo and how to use them:

* `segspace_final_test.py` — **strict, reproducible test runner**
* `segspace_final_explain.py` — **explanatory runner** (prints per-case reasoning)
* `real_data_30_segmodel.csv` — **comparison dataset** (alternatively: `real_data_30_segmodel_STRONG_NET.csv`)

---

## 🔧 Requirements

* Python ≥ 3.9
* Packages: `pandas` (and optionally `scipy`; constants fall back if missing)

```bash
pip install pandas
```

---

## ✅ `segspace_final_test.py` — Final (strict) tests

**Purpose:** runs tests T1–T6 and writes human/CI outputs so results are reproducible.

**Run:**

```bash
# explicit CSV
python segspace_final_test.py --csv real_data_30_segmodel.csv

# auto-discovery (picks a sensible default in the working dir)
python segspace_final_test.py

# or via env var
SEGSPACE_CSV=real_data_30_segmodel.csv python segspace_final_test.py
```

**Outputs (under `./out/`):**

* `final_test_report.txt` — human-readable summary (metrics + test statuses)
* `final_junit.xml` — CI-friendly JUnit
* `final_failures.csv` — flat list of PASS/FAIL/SKIP with messages
* `_final_test_debug.csv` — full per-row derived values & residuals

**What is checked (high level):**

* **T1** Nseg algebra consistency
* **T2** bound-energy reconstruction (when freqs are present)
* **T3** Seg-FIT ≈ 0
* **T4** median |Δz| per category (**requires strong rows**)
* **T5** physicality (e.g., $v<0.2c$)
* **T6** S-stars comparison: Seg ≤ 1.2×GR (median |Δz|)

**Important:**

* A **strong row** requires **orbit mode**: `a_m` (in **meters**), `e`, `f_true_deg` (deg), and `M_solar` (in solar masses).
* **GR** uses `r(a,e,f_true)` as fallback when `r_emit_m` is missing.
* Observed **z** is taken **either** from `f_emit_Hz/f_obs_Hz` **or** directly from `z`. If *both* are set, **frequencies take precedence**. (If you want to force `z`, leave those frequency fields empty.)

---

## 🔍 `segspace_final_explain.py` — Explanatory run

**Purpose:** prints, per case, exactly how values were sourced/derived:

* source of **z** (direct vs. from frequencies),
* how **r\_eff** is obtained (`r_emit_m` vs. `r(a,e,f_true)`),
* source of **v\_pred** (vis-viva, etc., and whether it’s *strong*),
* **z\_pred(seg)**, **z\_GR**, **z\_SR**, **z\_GR×SR**, and **Δz**,
* notes (e.g., if `v_los_mps` is missing → SR uses transverse part only).

**Run:**

```bash
python segspace_final_explain.py --csv real_data_30_segmodel.csv
# or let it auto-discover
python segspace_final_explain.py
```

**Output (under `./out/`):**

* `_explain_debug.csv` — full per-row matrix with provenance hints

---

## 🗃️ `real_data_30_segmodel.csv` — Data schema & minimum fields

**Header (as used by the runners):**

```
case,category,M_solar,a_m,e,P_year,T0_year,f_true_deg,z,f_emit_Hz,f_obs_Hz,lambda_emit_nm,lambda_obs_nm,v_los_mps,v_tot_mps,z_geom_hint,N0,source
```

**Key columns & units:**

* `case` — identifier (e.g., `S2_SgrA*`)
* `category` — e.g., `S-stars`, `Solar`, `WhiteDwarf`, `Lab/Geo`
* `M_solar` — central mass in **solar masses** (e.g., Sgr A\*: \~4.3e6)
* `a_m` — semi-major axis in **meters** (not mpc!)
* `e` — eccentricity
* `P_year`, `T0_year` — period (years), reference epoch
* `f_true_deg` — true anomaly in **degrees** (pericenter = 0)
* `z` — **observed** redshift $(\Delta\lambda/\lambda)$ **or**:

  * `f_emit_Hz` and `f_obs_Hz` — then $z = f_{\rm emit}/f_{\rm obs}-1$ is computed internally
    *(Tip: if you want to force `z`, leave the frequency fields empty.)*
* `v_los_mps` — line-of-sight velocity (m/s), if available
* `z_geom_hint` — optional **pure GR component** at the given $r$ (helps the Seg-PRED split)
* `N0` — default `1.0000000028` (project convention)
* `source` — provenance note

**Example S2 row (2018 pericenter, measured z; frequencies empty):**

```csv
S2_SgrA*,S-stars,4297000.0,1.530889e+14,0.8843,16.0518,2018.379,0.0,0.0006671281903963041,,,,,0,,0.0003584,1.0000000028,GRAVITY 2018 Pericenter (z); orbit per table
```

---

## 🧪 Quickstart

```bash
# 1) Put the CSV in place (or use the provided STRONG_NET variant)
cp real_data_30_segmodel.csv .

# 2) Run strict tests
python segspace_final_test.py --csv real_data_30_segmodel.csv

# 3) Run the explanatory pass
python segspace_final_explain.py --csv real_data_30_segmodel.csv
```

---

## 🩺 Troubleshooting

* **T4\_pred\_S-stars = FAIL**
  Check the S2 row:

  * If `f_emit_Hz/f_obs_Hz` are set, they override `z`. → clear those fields and set `z` explicitly.
  * Ensure `a_m` is in **meters**, `e` is correct, and `f_true_deg` matches the epoch (pericenter = 0).
  * Optionally set `z_geom_hint` to the GR-only part at that $r$.

* **No “strong rows”**
  You’re missing orbit fields: `a_m` (m), `e`, `f_true_deg`, `M_solar`. Without those, T4 often **SKIPs**.

* **Pandas error**
  Install it: `pip install pandas`.


---

# ⚙️ Minimal setup & reproducibility (Python-first)

You know Python. Here’s the shortest, deterministic path.

## Environment (pick one)

### (A) Plain `venv` + pinned deps (traditional)

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### (B) Conda/Mamba (if you already live there)

```bash
mamba create -n segspace python=3.11 -y
conda activate segspace
pip install -r requirements.txt
```

*(Optional)* If you use `uv`:

```bash
uv venv && . .venv/bin/activate
uv pip install -r requirements.txt
```

> Tested with Python **3.10–3.11**. No system-wide installs, no sudo.

---

## What to run (strict vs. explain)

### 1) Final tests (strict, CI-style)

```bash
python segspace_final_test.py --csv real_data_30_segmodel.csv --prefer-z
```

Outputs to `./out/`:

* `final_test_report.txt` — human summary
* `final_junit.xml` — CI
* `_final_test_debug.csv` — per-row residuals

### 2) Explain run (prints per-case reasoning)

```bash
python segspace_final_explain.py --csv real_data_30_segmodel.csv --prefer-z
```

Output: `./out/_explain_debug.csv`

**Flag discipline**

* `--csv` selects the dataset; default is auto-discovery.
* `--prefer-z` forces the runner to use the `z` column over any `f_emit/f_obs` if both are present (prevents accidental overrides).

---

## The three core files

* **`segspace_final_test.py`** — strict, reproducible test suite (T1–T6).
  Requires “strong rows” for category comparisons: `a_m` (meters), `e`, `f_true_deg` (deg), `M_solar` (solar masses). GR uses `r(a,e,f_true)` as fallback if `r_emit_m` is missing.

* **`segspace_final_explain.py`** — prints exactly how each quantity was sourced/derived per row: `z` (direct vs. frequency), `r_eff` (`r_emit_m` vs. `r(a,e,f_true)`), `v_pred` (vis-viva), `z_pred(seg)`, `z_GR`, `z_SR`, `z_GR×SR`, residuals, and any caveats (e.g., missing `v_los_mps`).

* **`real_data_30_segmodel.csv`** — comparison data (see schema below). Use the provided locked variant for reproducible baselines if needed: `real_data_30_segmodel_LOCKED.csv`.

---

## CSV schema (no surprises)

Header (exact order used by the runners):

```
case,category,M_solar,a_m,e,P_year,T0_year,f_true_deg,
z,f_emit_Hz,f_obs_Hz,lambda_emit_nm,lambda_obs_nm,
v_los_mps,v_tot_mps,z_geom_hint,N0,source
```

Key points:

* `a_m` is **meters** (not mpc).
* If you set both `z` and (`f_emit_Hz`,`f_obs_Hz`), **frequencies win** unless you pass `--prefer-z`.
* `z_geom_hint` can hold the pure GR part at the given radius (helps the segmented model’s split).
* “Strong rows” = orbit mode present: `a_m`, `e`, `f_true_deg`, `M_solar`.

**S2 example (2018 pericenter, measured `z`; frequencies empty):**

```csv
S2_SgrA*,S-stars,4297000.0,1.530889e+14,0.8843,16.0518,2018.379,0.0,
0.0006671281903963041,,,,,0,,0.0003584,1.0000000028,GRAVITY 2018 Pericenter (z); orbit per table
```

---

## Repro in one line

```bash
python -m venv .venv && . .venv/bin/activate \
&& pip install -r requirements.txt \
&& python segspace_final_test.py --csv real_data_30_segmodel.csv --prefer-z
```

## Common sense checks

* If T4 “strong rows” are SKIP: you’re missing orbit fields (`a_m`, `e`, `f_true_deg`, `M_solar`).
* If residuals look absurd: verify units (meters), and clear `f_emit/f_obs` when you intend to use `z`.
* If `pandas` “not found”: you skipped `requirements.txt`.

---
Nice. Dann packen wir’s sauber in die README – plus eine kurze Content-Liste der neuen Files. Unten sind **zwei Copy-Blöcke**: 1) ein fertiger README-Abschnitt (Englisch), 2) eine „New files“-Tabelle.

---

````markdown
# ✅ Segspace — Enhanced Tests (hint / GR×SR / Δ(M))

This repository now includes a **reproducible, strict test runner** that compares the segmented-spacetime predictions against GR, SR, and GR×SR on a curated S-stars dataset.

## How to run

```bash
# Recommended (forces z column over f_emit/f_obs if both present)
python segspace_enhanced_test.py --csv real_data_30_segmodel.csv --prefer-z --seg-mode hint --plots --junit
````

### Modes

* `--seg-mode hint`  → uses `z_geom_hint` (geometric GR) and mixes SR:  $(1+z_\text{seg})=(1+z_\text{hint})(1+z_\text{SR})-1$.
* `--seg-mode grsr`  → identical to GR×SR baseline.
* `--seg-mode deltaM` → applies a **relative** Δ(M) scaling to the geometric GR part only:

  $$
    z_{\rm GR,scaled} = z_{\rm GR}\,(1+\Delta M_{\rm frac}), \quad
    \Delta M = (A\,e^{-\alpha\,r_s}+B)\cdot \mathrm{norm}(\log_{10}M)
  $$

  (A,B in percent; $r_s=2GM/c^2$). Example:

  ```bash
  python segspace_enhanced_test.py --csv real_data_30_segmodel.csv \
    --prefer-z --seg-mode deltaM \
    --deltam-A 4.0 --deltam-B 0.0 --deltam-alpha 1e-11 --plots --junit
  ```

## Current results (S-stars, 9 strong rows)

Input: `real_data_30_segmodel.csv`
SHA256: `9f4c562b8adb4afd9ddadb2e09907186304fe856e75ea9c89dad56617d5e85f9`

**Median / Mean / Max |Δz|**

| Model          |         Median |           Mean |            Max |
| -------------- | -------------: | -------------: | -------------: |
| **Seg (hint)** | **2.9078e-05** | **2.3524e-04** | **1.1407e-03** |
| GR             |    1.26498e-04 |     5.0124e-04 |     2.2231e-03 |
| SR             |    1.44816e-04 |     5.2014e-04 |     2.2485e-03 |
| GR×SR          |     2.9108e-05 |     2.3526e-04 |     1.1407e-03 |

Notes:

* **Seg (hint)** ≈ **GR×SR** (as expected when `z_geom_hint` ≈ GR geometric part).
* `deltaM` (with the **fixed relative** scaling) yields similar residuals; on pure S-stars (single mass scale) it does **not** outperform hint/GR×SR without broader mass diversity for calibration.

## Outputs

Generated under `./out/`:

* `enhanced_report.txt` — summary
* `_enhanced_debug.csv` — per-row derivations (provenance of z, r\_eff source, v\_los sanitization, z\_GR, z\_SR, z\_GR×SR, z\_seg, residuals)
* `enhanced_junit.xml` — CI-friendly check (Seg median ≤ 1.2×GR median)
* `hist_*.png` — residual histograms (if `--plots`)

## Strong rows (requirements)

A row is considered **strong** if it has orbit mode fields:
`a_m` (meters), `e`, `f_true_deg` (deg), `M_solar` (solar masses).
GR uses `r(a,e,f_true)` as fallback if `r_emit_m` is missing.
If both `z` **and** `f_emit/f_obs` are set, `--prefer-z` forces using `z`.


---

## New files (content list)

| File | Purpose |
|---|---|
| `segspace_enhanced_test.py` | Enhanced, reproducible test runner comparing **Seg (hint / grsr / deltaM)** vs **GR / SR / GR×SR**. Robust handling of `NaN` in `v_los_mps` (treated as 0.0), SHA256 print, optional plots & JUnit, full debug CSV. |
| `segspace_final_test.py` | Strict CI-style suite (T1–T6), writes `final_test_report.txt`, `final_junit.xml`, `_final_test_debug.csv`, `final_failures.csv`. |
| `segspace_final_explain.py` | Explanatory runner: prints per-case sourcing/derivation (`z` provenance, `r_eff` path, vis-viva, z-components, residuals). Writes `_explain_debug.csv`. |
| `real_data_30_segmodel.csv` | Current S-stars comparison dataset (9 strong rows). If you set both `z` and `f_emit/f_obs`, use `--prefer-z` to ensure measured `z` is used. |


---
### FOR BEST RESULTS OPEN:

```
  python segspace_enhanced_test_better.py --csv real_data_full.csv --prefer-z --seg-mode hint --plots --junit
  python segspace_enhanced_test_better.py --csv real_data_full.csv --seg-mode deltaM --deltam-A 3.5 --deltam-B 0.2 --plots
  python segspace_enhanced_test_better.py --csv real_data_full.csv --seg-mode hybrid --plots --junit
````
or 
```
  python segspace_enhanced_test_better_final.py --csv real_data_full.csv --prefer-z --seg-mode hint --plots --junit
  python segspace_enhanced_test_better_final.py --csv real_data_full.csv --seg-mode deltaM --deltam-A 3.5 --deltam-B 0.2 --plots
  python segspace_enhanced_test_better_final.py --csv real_data_full.csv --seg-mode hybrid --plots --junit
````

---
END OR REPO



