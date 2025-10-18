# SSZ Complete Analysis Pipeline

## Overview

`python run_all_ssz_terminal.py` executes the **complete SSZ analysis pipeline** with 20+ scripts organized in phases.

---

## Phase 0: All-in-One Extended Analysis

```bash
python segspace_all_in_one_extended.py all
```

**Comprehensive analysis:**
- Paired sign tests (SEG vs SR/GR)
- Redshift analysis
- Bound energy calculations
- Mass validation (12 orders of magnitude)
- Statistical significance tests

---

## Phase 1: Covariant Tests & Basic Validation

```bash
python ssz_covariant_smoketest_verbose_lino_casu.py  # Covariant formulation
python test_ppn_exact.py                              # PPN parameters β=γ=1
python test_c1_segments.py                            # C1 continuity
python test_c2_segments_strict.py                     # C2 strict continuity
python test_energy_conditions.py                      # WEC/DEC/SEC
python shadow_predictions_exact.py                    # Black hole shadows
python qnm_eikonal.py                                 # Quasi-normal modes
python test_vfall_duality.py --mass Earth --r-mults 1.1,2.0  # Dual velocity
```

---

## Phase 2: φ-Lattice Tests

```bash
python phi_test.py --in real_data_full.csv --outdir out/
python phi_bic_test.py --in real_data_full.csv --outdir out/
```

**Tests:**
- Golden ratio (φ) lattice hypothesis
- BIC (Bayesian Information Criterion) comparison
- Frequency emission/observation analysis

---

## Phase 3: Velocity from Redshift

```bash
python compute_vfall_from_z.py --in real_data_full.csv --outdir vfall_out/
```

**Computes:**
- Fall velocities from redshift data
- Dual velocity validation
- Statistical distributions

---

## Phase 4: Segspace Analysis Suite

```bash
python segspace_final_test.py --csv real_data_30_segmodel.csv
python segspace_final_explain.py
python segspace_enhanced_test_better_final.py --csv real_data_full.csv --prefer-z --seg-mode hint
```

**Optional demos:**
```bash
python final_test.py
python segmented_full_proof.py
python segmented_full_calc_proof.py
python segmented_full_compare_proof.py
```

---

## Phase 5: Advanced Analysis

### 5.6 Lagrangian Geodesic Tests

```bash
python lagrangian_tests.py --object sun
python lagrangian_tests.py --object sgrA
python lagrangian_tests.py --mass 8.544456e36 --label "Sgr A*" --eps3 -4.8
```

**Tests:**
- Geodesic equations
- Effective potentials
- ISCO calculations
- Orbital stability

### 5.7 Effective Stress-Energy Tensor

```bash
python derive_effective_stress_energy.py --M 1.98847e30 --eps3 -4.8 --r-mults 1.2,2,3,5,10
python derive_effective_stress_energy.py --M 8.544456e36 --eps3 -4.8 --r-mults 1.2,2,3,5 --latex reports/ssz_sources_latex.txt
```

**Derives:**
- T_μν components
- Energy density ρ
- Pressure components (p_r, p_t)
- LaTeX output for papers

### 5.8 Theory Calculations (Action-Based Scalar)

```bash
python ssz_theory_segmented.py \
    --M 1.98847e30 \
    --mode exterior \
    --coord lnr \
    --rmin-mult 1.05 \
    --rmax-mult 12 \
    --grid 200 \
    --phi0 1e-4 --phip0 0 \
    --pr0 0 --rho0 0 --cs2 0.30 \
    --mphi 1e-7 --lam 1e-6 \
    --Z0 1.0 --alpha 3e-3 --beta=-8e-3 \
    --Zmin 1e-8 --Zmax 1e8 \
    --phi-cap 5e-3 --phip-cap 1e-3 \
    --max-step-rs 0.02 \
    --export out_theory_exterior.csv
```

**Computes:**
- Scalar field evolution
- Action-based formulation
- Exterior spacetime
- Full numerical integration

---

## Phase 6: Final Interpretation & Summary

**Generates:**
- `full_pipeline/reports/summary_full_terminal_v4.json`
- Dual velocity blocks with invariants
- Quality assessment
- Statistical significance summary
- ASCII-safe interpretation (Windows compatible)

---

## Complete Output

**Analysis Reports:**
- `agent_out/reports/redshift_paired_stats.json`
- `agent_out/reports/redshift_medians.json`
- `agent_out/reports/bound_energy.txt`
- `agent_out/reports/segmented_spacetime_mass_validation.csv`
- `full_pipeline/reports/summary_full_terminal_v4.json`

**Data Files:**
- `out_theory_exterior.csv`
- `vfall_out/*.csv`
- Various validation CSVs

**Visualizations:**
- Shadow predictions
- QNM calculations
- Lagrangian effective potentials
- Bound energy plots

---

## Execution Time

**Total: ~10-15 minutes**

Breakdown:
- Phase 0: ~3-4 min (All-in-one)
- Phase 1: ~2-3 min (Covariant tests)
- Phase 2: ~1 min (φ-tests)
- Phase 3: ~1 min (v_fall)
- Phase 4: ~2-3 min (Segspace suite)
- Phase 5: ~2-3 min (Advanced analysis)
- Phase 6: <1 min (Summary)

---

## Scientific Results

Expected validation:
- ✅ PPN: β = γ = 1 (GR match in weak field)
- ✅ Mass roundtrip: error < 1e-42
- ✅ Dual velocity invariant: v_esc × v_fall = c²
- ✅ Energy conditions: WEC/DEC/SEC hold for r ≥ 5r_s
- ✅ Paired sign test: p < 1e-18
- ✅ φ-lattice: ΔBIC > +100
- ✅ Shadow predictions: Finite photon sphere
- ✅ QNM: Stable quasi-normal modes

---

## Copyright

© 2025 Carmen Wrede und Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
