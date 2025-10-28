# Complete SSZ Test Suite - Summary Report

**Generated:** 2025-10-28 10:12:42

© 2025 Carmen Wrede & Lino Casu

---

## Executive Summary

**Overall Status:** ⚠️ SOME ISSUES

All tests, validations, and analysis scripts in the repository were executed.

---

## Test Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Tests** | 53 | 100% |
| **Passed** | 33 | 62.3% |
| **Failed** | 20 | 37.7% |
| **Timeout** | 0 | 0.0% |
| **Error** | 0 | 0.0% |

**Success Rate:** 62.3%

---

## Results by Category

### Root Level

**Tests:** 38 | **Passed:** 26 | **Rate:** 68.4%

| File | Status | Duration |
|------|--------|----------|
| calculation_test.py | ❌ FAILED | 0.24s |
| conftest.py | ✅ PASSED | 0.21s |
| extend_all_tests.py | ✅ PASSED | 0.27s |
| final_test.py | ✅ PASSED | 0.18s |
| generate_test_data.py | ✅ PASSED | 0.46s |
| investigate_paired_test.py | ✅ PASSED | 2.23s |
| lagrangian_tests.py | ❌ FAILED | 0.23s |
| lino_qed_test.py | ✅ PASSED | 0.64s |
| perfect_paired_test.py | ✅ PASSED | 3.26s |
| phi_bic_test.py | ❌ FAILED | 1.50s |
| phi_test.py | ❌ FAILED | 2.09s |
| run_comprehensive_tests.py | ❌ FAILED | 7.14s |
| segspacetime_quick_tests.py | ✅ PASSED | 2.14s |
| segspace_enhanced_test.py | ✅ PASSED | 1.61s |
| segspace_enhanced_test_better.py | ✅ PASSED | 1.71s |
| segspace_enhanced_test_better_final.py | ✅ PASSED | 1.73s |
| segspace_final_test.py | ✅ PASSED | 2.09s |
| segspace_pairtest_vs_sr.py | ❌ FAILED | 0.62s |
| smoke_test_all.py | ✅ PASSED | 3.68s |
| ssz_blackhole_bomb_template.py | ✅ PASSED | 152.08s |
| ssz_covariant_smoketest_verbose_lino_casu.py | ✅ PASSED | 0.17s |
| ssz_interactive_gui.py | ❌ FAILED | 4.25s |
| ssz_stability_animation.py | ✅ PASSED | 39.70s |
| ssz_stability_three_figures.py | ✅ PASSED | 3.96s |
| ssz_test_suite.py | ❌ FAILED | 8.76s |
| ssz_theory_segmented.py | ❌ FAILED | 1.98s |
| ssz_unified_suite.py | ❌ FAILED | 3.21s |
| stratified_paired_test.py | ✅ PASSED | 12.00s |
| test_c1_segments.py | ✅ PASSED | 0.13s |
| test_c2_curvature_proxy.py | ✅ PASSED | 0.21s |
| test_c2_segments_strict.py | ✅ PASSED | 0.13s |
| test_clone_and_verify.py | ❌ FAILED | 0.24s |
| test_energy_conditions.py | ✅ PASSED | 0.13s |
| test_phi_impact.py | ✅ PASSED | 4.27s |
| test_ppn_exact.py | ✅ PASSED | 0.13s |
| test_theory_predictions_cross_platform.py | ❌ FAILED | 2.90s |
| test_utf8_encoding.py | ✅ PASSED | 0.82s |
| test_vfall_duality.py | ✅ PASSED | 0.24s |

### Scripts

**Tests:** 14 | **Passed:** 6 | **Rate:** 42.9%

| File | Status | Duration |
|------|--------|----------|
| check_test_documentation.py | ✅ PASSED | 8.85s |
| conftest.py | ✅ PASSED | 0.13s |
| test_cosmo_fields.py | ❌ FAILED | 2.01s |
| test_cosmo_multibody.py | ❌ FAILED | 0.32s |
| test_data_fetch.py | ❌ FAILED | 1.44s |
| test_data_validation.py | ❌ FAILED | 1.52s |
| test_gaia_required_columns.py | ❌ FAILED | 1.44s |
| test_hawking_spectrum_continuum.py | ✅ PASSED | 2.76s |
| test_horizon_hawking_predictions.py | ✅ PASSED | 2.49s |
| test_plot_ssz_maps.py | ❌ FAILED | 2.06s |
| test_segmenter.py | ❌ FAILED | 1.26s |
| test_ssz_invariants.py | ✅ PASSED | 1.25s |
| test_ssz_kernel.py | ❌ FAILED | 0.33s |
| test_utf8_encoding.py | ✅ PASSED | 0.48s |

### Validation

**Tests:** 1 | **Passed:** 1 | **Rate:** 100.0%

| File | Status | Duration |
|------|--------|----------|
| run_ssz_validation.py | ✅ PASSED | 3.85s |

---

## Failed Tests

20 test(s) failed or encountered errors:

### calculation_test.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
usage: calculation_test.py [-h] [--rphi RPHI] [--demo]
calculation_test.py: error: Please specify --rphi <value> or --demo to run calculations.

```

### lagrangian_tests.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
usage: lagrangian_tests.py [-h] [--object {sun,sgrA}] [--mass MASS]
                           [--label LABEL] [--eps3 EPS3]
lagrangian_tests.py: error: Provide --object or --mass

```

### phi_bic_test.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
usage: phi_bic_test.py [-h] --in INP --outdir OUTDIR [--tol TOL] [--phi PHI]
                       [--ratio-col RATIO_COL] [--z-col Z_COL]
                       [--f-emit F_EMIT] [--f-obs F_OBS]
                       [--lambda-obs LAMBDA_OBS] [--lambda-rest LAMBDA_REST]
                       [--jitter JITTER] [--n-rand N_RAND]
phi_bic_test.py: error: the following arguments are required: --in, --outdir

```

### phi_test.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
usage: phi_test.py [-h] --in INP --outdir OUTDIR [--tol TOL]
                   [--ratio-col RATIO_COL] [--f-emit F_EMIT] [--f-obs F_OBS]
                   [--lambda-obs LAMBDA_OBS] [--lambda-rest LAMBDA_REST]
                   [--z-col Z_COL]
phi_test.py: error: the following arguments are required: --in, --outdir

```

### run_comprehensive_tests.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
orig()
  File "C:\Users\linoc\AppData\Roaming\Python\Python310\site-packages\_pytest\capture.py", line 659, in pop_outerr_to_orig
    out, err = self.readouterr()
  File "C:\Users\linoc\AppData\Roaming\Python\Python310\site-packages\_pytest\capture.py", line 706, in readouterr
    out = self.out.snap() if self.out else ""
  File "C:\Users\linoc\AppData\Roaming\Python\Python310\site-packages\_pytest\capture.py", line 591, in snap
    self.tmpfile.seek(0)
ValueError: I/O operation on closed file.

```

### segspace_pairtest_vs_sr.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
Unknown error
```

### ssz_interactive_gui.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
 self.update_plots()
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\ssz_interactive_gui.py", line 328, in update_plots
    self.update_parameter_study()
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\ssz_interactive_gui.py", line 349, in update_parameter_study
    axes = self.fig_comparison.subplots(1, 2, figsize=(10, 4))
TypeError: FigureBase.subplots() got an unexpected keyword argument 'figsize'

```

### ssz_test_suite.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
Unknown error
```

### ssz_theory_segmented.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
0 RHO0]
                               [--max-step-rs MAX_STEP_RS]
                               [--abort-on-horizon]
                               [--horizon-margin HORIZON_MARGIN]
                               [--seg-frac SEG_FRAC]
                               [--seg-scale {r_s,r_phi,auto}]
                               [--kernel {gauss,exp,box}] [--eps3 EPS3]
                               [--rphi-hint RPHI_HINT]
ssz_theory_segmented.py: error: the following arguments are required: --M

```

### ssz_unified_suite.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
am Files\Python310\lib\json\encoder.py", line 405, in _iterencode_dict
    yield from chunks
  File "C:\Program Files\Python310\lib\json\encoder.py", line 405, in _iterencode_dict
    yield from chunks
  File "C:\Program Files\Python310\lib\json\encoder.py", line 438, in _iterencode
    o = _default(o)
  File "C:\Program Files\Python310\lib\json\encoder.py", line 179, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type bool is not JSON serializable

```

### test_clone_and_verify.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
ram Files\Python310\lib\shutil.py", line 620, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Program Files\Python310\lib\shutil.py", line 618, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 5] Zugriff verweigert: 'H:\\WINDSURF\\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\\temp_test_clone\\Segmented-Spacetime-Mass-Projection-Unified-Results\\.git\\objects\\pack\\pack-6ddaf2e49d841dd3391c8fc7fcde982aadb7e202.idx'

```

### test_theory_predictions_cross_platform.py

**Category:** root_level  
**Status:** FAILED  
**Error:**
```
Unknown error
```

### test_cosmo_fields.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_cosmo_fields.py", line 2, in <module>
    from scripts.ssz.cosmology import build_cosmo_fields
ModuleNotFoundError: No module named 'scripts.ssz'

```

### test_cosmo_multibody.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_cosmo_multibody.py", line 2, in <module>
    from ssz_cosmos.field import MultiBodyField, BodyState
ModuleNotFoundError: No module named 'ssz_cosmos'

```

### test_data_fetch.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_data_fetch.py", line 4, in <module>
    from scripts.tests.data_smoke_fetch import fetch_gaia_quick, fetch_sdss_quick, smoke_paths
ModuleNotFoundError: No module named 'scripts.tests'

```

### test_data_validation.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Unknown error
```

### test_gaia_required_columns.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_gaia_required_columns.py", line 5, in <module>
    from scripts.preprocess.gaia_clean_map import REQUIRED_COLUMNS, SOFT_REQUIRED_ERROR, harmonize_columns
ModuleNotFoundError: No module named 'scripts.preprocess'

```

### test_plot_ssz_maps.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_plot_ssz_maps.py", line 3, in <module>
    from scripts.viz.plot_ssz_maps import plot_mollweide, VizConfig
ModuleNotFoundError: No module named 'scripts.viz'

```

### test_segmenter.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_segmenter.py", line 2, in <module>
    from scripts.ssz.segmenter import assign_segments_xy, SegParams
ModuleNotFoundError: No module named 'scripts.ssz'

```

### test_ssz_kernel.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_ssz_kernel.py", line 2, in <module>
    from scripts.ssz.gamma import gamma_seg_from_density
ModuleNotFoundError: No module named 'scripts.ssz'

```

---

## Next Steps

**Action Required:**
- Review 20 failed/timeout/error test(s)
- Check error messages above
- Fix issues and re-run: `python run_complete_test_suite.py`

---

**Generated by:** `run_complete_test_suite.py`  
**License:** ANTI-CAPITALIST SOFTWARE LICENSE v1.4
