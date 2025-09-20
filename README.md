<img width="2400" height="1000" alt="segspace_comparison" src="https://github.com/user-attachments/assets/69e3e20d-6815-4a44-8d08-57ad646b96c5" />

# Segmented Spacetime – Mass Projection & Unified Results
© Carmen Wrede & Lino Casu

Status: Reproducible evidence of model functionality (theory + code + tests).
Note: Not a formal proof; independent replication and peer review remain pending.

---

## Verification Summary (Segmented Spacetime)

Autorunner Precision Test:  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LinoCasu/Segmented-Spacetime-Mass-Projection-Unified-Results/blob/main/SSZ_Colab_AutoRunner.ipynb)

---

## Technical Briefing (Scope & Internal Correctness)

**What SST (projection variant) is.**  
SST models spacetime as discrete segmentation and uses a local projection parameter (`α_loc`) to predict observables instead of explicit metric curvature. In this repo it is a phenomenology tuned to match weak-field tests and to generate strong-field observables for comparison.

**What the code actually demonstrates (in-repo).**
- **Weak-field parity with GR:** `ssz_covariant_smoketest_verbose_lino_casu.py` yields PPN γ=1 and β=1 and reproduces light deflection, Shapiro delay, and Mercury perihelion numerically equal to GR. The symbol β used elsewhere in SST is not PPN-β; the script disambiguates this.
- **Redshift fits (curated set, n=67):** `run_all_ssz_terminal.py` runs an SST projection with a documented noise model and Chauvenet outlier rule, logging MAE, ΔBIC/AIC, and a paired sign-test. Seeds and file/module SHA256 are recorded.
- **Strong-field curves:** `shadow_predictions_exact.py` outputs parameterized shadow radii for Sgr A* and M87* as functions of spin and inclination for downstream EHT-style comparisons.

**Internal consistency checks.**  
Deterministic runs with fixed seeds and checksummed inputs. Utility tests verify algebraic identities such as escape/fall duality within numerical tolerance.

---

## What This Repository *Is*

- A reproducible reference implementation of SST projection tests and parameterized strong-field outputs.
- A research artifact for independent re-runs, ablations, and plug-in comparisons.
- A living workspace for CI, datasets, and benchmark extensions.

## What This Repository *Is Not*

- Not a full field theory. No action/Lagrangian or derived field equations are shipped.
- Not a claim of intrinsic variation of fundamental constants. `α_loc` is a projection parameter for observables.
- Not an assertion about black-hole information release or “radio-emergence.”
- Not a proof of EHT agreement.
- Not a general-purpose cosmology/astrophysics pipeline beyond the documented tests.

---

## Verification & CI

Run (local):
```
python test_ppn_exact.py            # PPN: beta=1, gamma=1
python test_c1_segments.py          # C¹ at rL, rR
python test_energy_conditions.py    # WEC/SEC for r ≥ 5 r_s
python shadow_predictions_exact.py  # Shadows: Sgr A* ~50 µas, M87* ~38 µas
python qnm_eikonal.py               # Eikonal QNM (Ω_c, λ)
python test_c2_segments_strict.py   # C² continuity at joins
```

Acceptance:
- PPN: |β−1| < 1e-12 and |γ−1| < 1e-12 → PASS
- C¹ continuity thresholds at rL,rR → PASS
- Strong-field invariants equal to GR within machine precision → PASS
- Shadows: Sgr A* ≈ 50.025 µas, M87* ≈ 37.282 µas → PASS
- Energy conditions WEC/SEC for r/rs ≥ 5 → PASS
- Mass round-trip (electron → Sun → Sgr A*): relative error ≤ 1e-12 → PASS

### Exact shadow benchmarks (GR, analytic)
Inputs: Sgr A* M=4.297e6 M☉, D=8 277 pc; M87* M=6.5e9 M☉, D=16.8 Mpc.  
Method: r_ph=1.5 r_s, b_ph=(3√3/2) r_s, θ=b_ph/D, diameter=2θ.  
Deterministic; scales ∝ M/D.
```
python shadow_predictions_exact.py
```

---

# v_fall from z (Duality Check)

**Core idea**
- GR redshift: `gamma_GR = 1 / sqrt(1 - r_s/r)`
- Observation: `gamma_obs = 1 + z`
- Dual Lorentz form: `gamma_dual(v_fall) = 1 / sqrt(1 - (c/v_fall)^2)`
- Set `gamma_dual(v_fall) = gamma_obs` ⇒ `v_fall(z) = c / sqrt(1 - 1/(1+z)^2)`
- Newton/GR link: `v_esc(r) = sqrt(2GM/r)` and `v_esc * v_fall = c^2`

## Script: `compute_vfall_from_z.py`

Computes `v_fall` per row and checks:
- phi-step residual: `abs(round( ln(1+z)/ln(phi) ) − ln(1+z)/ln(phi))`
- Product test: if `M,r` are present, verify `(v_esc * v_fall)/c^2 ≈ 1`

**Inputs**
- CSV with one of: `z` or `f_emit,f_obs` (uses `1+z=f_emit/f_obs`) or `ratio=f_emit/f_obs`
- Optional: `M,r` for the product test

**Examples**
```bash
# use z directly
python compute_vfall_from_z.py --in real_data_full.csv --outdir vfall_out --z-col z

# use frequencies instead of z
python compute_vfall_from_z.py --in real_data_full.csv --outdir vfall_out   --f-emit f_emit_Hz --f-obs f_obs_Hz
```

**Console output (typical)**
- `rows used`: after cleaning
- `abs_residual_median`: median |phi-residual| (→0 means clearer φ-stepping)
- `prod_rel_err_median`: median relative error of `v_esc * v_fall = c^2` (0 ⇒ exact)

**Files in `--outdir`**
- `vfall_results.csv`, `vfall_summary.json`, optional plots

### Additional tests

**phi BIC / sign tests**
```bash
python phi_test.py     --in real_data_full.csv --outdir out
python phi_bic_test.py --in real_data_full.csv --outdir out   --f-emit f_emit_Hz --f-obs f_obs_Hz --tol 1e-3
```

**Quick duality smoke test**
```bash
python test_vfall_duality.py --mass Earth --r-mults 1.1,1.2,2,5,10
```
Verifies `v_esc * v_fall = c^2` and `gamma_GR(r) = gamma_dual(v_fall)`.

## Interpretation
- `abs_residual_median ≈ 0` → strong φ-stepping
- `ΔBIC (uniform − lattice) >> 0` → φ-lattice preferred
- `prod_rel_err_median ≈ 0` → product duality holds

### φ-Step (Phi) Metric Test
This checks if ratios align with discrete φ-steps (`R ≈ φ^n`). Quick start:
```bash
python phi_test.py --in real_data_full_filled.csv --outdir agent_out_phi2
python phi_bic_test.py --in real_data_full.csv --outdir out --f-emit f_emit_Hz --f-obs f_obs_Hz --tol 1e-3
python phi_bic_test.py --in real_data_full_filled.csv --outdir out --f-emit f_emit_Hz --f-obs f_obs_Hz --tol 0 --jitter 1e-12 --n-rand 20000
```

**Key points**
- `a_m` is meters.
- If both `z` and frequencies are set, frequencies win unless `--prefer-z`.
- `z_geom_hint` may hold the pure GR part.
- “Strong rows” require `a_m, e, f_true_deg, M_solar`.

**S2 example (2018 pericenter)**
```csv
S2_SgrA*,S-stars,4297000.0,1.530889e+14,0.8843,16.0518,2018.379,0.0,
0.0006671281903963041,,,,,0,,0.0003584,1.0000000028,GRAVITY 2018 Pericenter (z); orbit per table
```

---

## Quick Overview (Segmented Spacetime vs. GR/SR)

Result snapshot (median |Δz|, lower is better):
- SEG (φ/2 + Δ(M)): 1.31e-4
- SR: 1.34e-2
- GR ≈ GR×SR: 2.25e-1

Paired comparison: SEG better in 66/67 cases (two-sided binomial p ≈ 9.2e-19).
Mass bins: In all bins SEG < GR×SR.

### One-liner (auto mode, no fits)
```bash
python run_all_ssz_terminal.py
```
Output: verbose terminal explanation + JSON summary at `full_pipeline/reports/summary_full_terminal_v3.json`.
Run prints SHA-256 of dataset, code, and runner. PPN far-field unchanged.

---

## Repro in one line
```bash
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && python segspace_final_test.py --csv real_data_30_segmodel.csv --prefer-z
```

---

## Full Execution

### `run_all.py`
End-to-end workflow:
1) optional ESO Brγ fetch, 2) analysis, 3) mass validation, 4) energy bounds.

**Run with existing CSV**
```bash
python run_all.py --fetch-mode skip --csv real_data_full.csv --out-dir results --prefer-z --top 10
```
**Fetch your own**
```bash
python run_all.py --fetch-mode full --csv real_data_full.csv --out-dir results --prefer-z --top 10 --token YOUR_ESO_BEARER_TOKEN
```

**Clone**
```bash
git clone https://github.com/LinoCasu/Segmented-Spacetime-Mass-Projection-Unified-Results.git
cd Segmented-Spacetime-Mass-Projection-Unified-Results
```

### Hybrid pipeline (best median |Δz|)
```bash
python segspace_enhanced_test_better_final.py
```

**Recommended kernel runs**
```bash
# venv
python -m venv venv && source venv/bin/activate
# deps
pip install -r requirements.txt
# output dir
mkdir -p out
# core runs
python segspace_enhanced_test_better_final.py --csv real_data_full.csv --prefer-z --seg-mode hint --plots --junit
python segspace_enhanced_test_better_final.py --csv real_data_full.csv --seg-mode deltaM --deltam-A 3.5 --deltam-B 0.2 --plots
python segspace_enhanced_test_better_final.py --csv real_data_full.csv --seg-mode hybrid --plots --junit
# proofs / round-trips
python final_test.py
python segmented_full_proof.py
python segmented_full_compare_proof.py
python segmented_full_calc_proof.py
# bound-energy
python bound_energy_plot.py
python bound_energy_plot_with_frequenz_shift_fix.py
```

---

## Independent replication call

Environment: Python 3.11  
One-command run:
```
python ssz_covariant_smoketest_verbose_lino_casu.py && python test_ppn_exact.py && python test_c1_segments.py && python test_energy_conditions.py && python shadow_predictions_exact.py && python qnm_eikonal.py && python test_c2_segments_strict.py
```
Expected: PPN β=1, γ=1; Sgr A* shadow 53.255 µas; M87* 39.689 µas; no NaN/Inf. Report OS/CPU/Python/results.

---

## Additional Information

The complete and up-to-date command reference is in `commands.md`.
This repo unifies Mass Projection, π–φ Bridge, Bound Energy, and related calculations. See also `API.md`, `Estimators.md`, `Sources.md`, and `DATA_SOURCES.md`.

Quick start with:
```bash
python segspace_all_in_one_extended.py all
python segspace_all_in_one_extended.py eval-redshift --csv ".
eal_data_full.csv" --mode geodesic --prefer-z --ci 2000 --paired-stats --plots
```

---

## Complete File List

| File / Dir | Description |
|---|---|
| `run_all.py` | Top-level runner. |
| `run_all_ssz_terminal.py` | Deterministic SSZ CLI runner. |
| `segspace_all_in_one.py` | All-in-one toolkit (π-bridge, mass-validate, bound-energy, …). |
| `segspace_all_in_one_extended.py` | Enhanced v2 pipeline. |
| `segspace_final_test.py` | T1–T6 suite, report + JUnit XML. |
| `segspace_enhanced_test_better_final.py` | GR/SR/GR×SR comparisons. |
| `segspacetime_quick_tests.py` | Convenience wrapper. |
| `phi_test.py` | φ-step residuals and summary. |
| `phi_bic_test.py` | ΔBIC (uniform vs φ-lattice) + sign tests. |
| `compute_vfall_from_z.py` | Compute `v_fall` and check `v_esc v_fall=c^2`. |
| `test_vfall_duality.py` | Smoke test of γ-duality and product. |
| `segmented_full_proof.py` | Proof/round-trip routines. |
| `segmented_full_calc_proof.py` | Calculation trace. |
| `segmented_full_compare_proof.py` | Compare proof outputs vs baselines. |
| `segmented_mass.py` | Mass inversion utilities. |
| `bound_energy.py` | Bound-energy derivation. |
| `bound_energy_english.py` | Simplified bound-energy demo. |
| `bound_energy_plot.py` | Bound-energy comparisons; CSV + plot. |
| `bound_energy_plot_with_frequenz_shift_fix.py` | Bound-energy with emission-freq shift fix. |
| `paper.py` | Reproduces numeric example from bound-energy paper. |
| `check.py` | Fine-structure constant check. |
| `calculation_test.py` | Small calculation sanity tests. |
| `complete-math.py` | Collated formula path. |
| `shadow_predictions_exact.py` | Exact shadow sizes (Sgr A*, M87*). |
| `qnm_eikonal.py` | BH QNM (eikonal) cross-check. |
| `Segmentdichte-Analyse.py` | Segment density analysis σ(r). |
| `vergleich.py` | Comparison chart. |
| `vergleich_2.py` | Updated comparison chart. |
| `real_data_full.csv` | Master dataset. |
| `bound_energy_results.csv` | Bound-energy results. |
| `bound_energy_with_deltaM.csv` | Bound-energy with Δ(M). |
| `segmented_spacetime_mass_validation*.csv` | Mass validation tables. |
| `segment_mass_results.csv` | Per-object mass/segment outputs. |
| `README.md` | Project overview & quickstart. |
| `API.md` | Public API of scripts/modules. |
| `commands.md` | Usage guide. |
| `DATA_SOURCE(S).md` | Data provenance. |
| `Sources.md` | External sources and links. |
| `CITATION.cff` | Citation metadata. |
| `requirements.txt`, `requirements-freeze.txt` | Dependencies and pinned env. |
| `.github/workflows/ci.yml` | CI workflow. |
| `carmen_qed_incompleteness_demo.py` | Photon-energy accessibility demo with data and interpretation. |

---

## Notes on Reproducibility

- Deterministic execution. PPN far-field unchanged (β=γ=1).
- The run prints SHA-256 hashes of dataset, code, and runner.
- Please report OS/CPU/Python when replicating.

---

## Appendix: S-stars enhanced tests (hint / GR×SR / Δ(M))

This repo includes a strict test runner comparing SEG vs GR, SR, GR×SR on a curated S-stars set, with modes:
- `--seg-mode hint` uses `z_geom_hint` and mixes SR via `(1+z_seg)=(1+z_hint)(1+z_SR)-1`.
- `--seg-mode grsr` equals GR×SR.
- `--seg-mode deltaM` applies a **relative** Δ(M) scaling to the GR part only:  
  `z_GR,scaled = z_GR * (1+ΔM_frac)`, with `ΔM = (A*exp(-α*r_s)+B) * norm(log10 M)`; `r_s=2GM/c^2`.

Example:
```bash
python segspace_enhanced_test_better_final.py --csv real_data_30_segmodel.csv   --prefer-z --seg-mode deltaM   --deltam-A 4.0 --deltam-B 0.0 --deltam-alpha 1e-11 --plots --junit
```

**Current results (S-stars, 9 strong rows)**  
Median/Mean/Max |Δz| show Seg(hint) ≈ GR×SR where `z_geom_hint` ≈ GR geometric part. Δ(M) with fixed relative scaling is similar on a single mass scale.

---

**License:** ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4).

**Repository goal:** Cover theory, numerics, and validation needed to support segmented spacetime: φ/2 scale-link, Schwarzschild baseline, saturation of segment density near horizon, GR recovery in weak field, Δ(M) mass inversion. Validations include mass round-trip ≤1e-6 %, redshift/frequency checks ~1e-6, and PPN consistency.

**End.**



