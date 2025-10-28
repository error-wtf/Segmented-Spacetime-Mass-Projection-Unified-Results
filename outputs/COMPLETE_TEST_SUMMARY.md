# Complete SSZ Test Suite - Summary Report

**Generated:** 2025-10-28 10:28:43

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
| calculation_test.py | ❌ FAILED | 0.43s |
| conftest.py | ✅ PASSED | 0.20s |
| extend_all_tests.py | ✅ PASSED | 0.29s |
| final_test.py | ✅ PASSED | 0.21s |
| generate_test_data.py | ✅ PASSED | 0.38s |
| investigate_paired_test.py | ✅ PASSED | 3.01s |
| lagrangian_tests.py | ❌ FAILED | 0.31s |
| lino_qed_test.py | ✅ PASSED | 0.65s |
| perfect_paired_test.py | ✅ PASSED | 8.66s |
| phi_bic_test.py | ❌ FAILED | 1.80s |
| phi_test.py | ❌ FAILED | 3.19s |
| run_comprehensive_tests.py | ❌ FAILED | 8.30s |
| segspacetime_quick_tests.py | ✅ PASSED | 3.06s |
| segspace_enhanced_test.py | ✅ PASSED | 1.57s |
| segspace_enhanced_test_better.py | ✅ PASSED | 2.44s |
| segspace_enhanced_test_better_final.py | ✅ PASSED | 1.72s |
| segspace_final_test.py | ✅ PASSED | 3.03s |
| segspace_pairtest_vs_sr.py | ❌ FAILED | 0.52s |
| smoke_test_all.py | ✅ PASSED | 3.91s |
| ssz_blackhole_bomb_template.py | ✅ PASSED | 126.43s |
| ssz_covariant_smoketest_verbose_lino_casu.py | ✅ PASSED | 0.25s |
| ssz_interactive_gui.py | ❌ FAILED | 7.47s |
| ssz_stability_animation.py | ✅ PASSED | 45.13s |
| ssz_stability_three_figures.py | ✅ PASSED | 4.45s |
| ssz_test_suite.py | ❌ FAILED | 8.46s |
| ssz_theory_segmented.py | ❌ FAILED | 2.51s |
| ssz_unified_suite.py | ❌ FAILED | 4.73s |
| stratified_paired_test.py | ✅ PASSED | 14.52s |
| test_c1_segments.py | ✅ PASSED | 0.20s |
| test_c2_curvature_proxy.py | ✅ PASSED | 0.20s |
| test_c2_segments_strict.py | ✅ PASSED | 0.23s |
| test_clone_and_verify.py | ❌ FAILED | 0.39s |
| test_energy_conditions.py | ✅ PASSED | 0.26s |
| test_phi_impact.py | ✅ PASSED | 4.59s |
| test_ppn_exact.py | ✅ PASSED | 0.19s |
| test_theory_predictions_cross_platform.py | ❌ FAILED | 5.22s |
| test_utf8_encoding.py | ✅ PASSED | 1.22s |
| test_vfall_duality.py | ✅ PASSED | 0.34s |

### Scripts

**Tests:** 14 | **Passed:** 6 | **Rate:** 42.9%

| File | Status | Duration |
|------|--------|----------|
| check_test_documentation.py | ✅ PASSED | 34.82s |
| conftest.py | ✅ PASSED | 0.44s |
| test_cosmo_fields.py | ❌ FAILED | 1.61s |
| test_cosmo_multibody.py | ❌ FAILED | 3.16s |
| test_data_fetch.py | ❌ FAILED | 1.81s |
| test_data_validation.py | ❌ FAILED | 2.02s |
| test_gaia_required_columns.py | ❌ FAILED | 2.19s |
| test_hawking_spectrum_continuum.py | ✅ PASSED | 10.88s |
| test_horizon_hawking_predictions.py | ✅ PASSED | 5.24s |
| test_plot_ssz_maps.py | ❌ FAILED | 3.21s |
| test_segmenter.py | ❌ FAILED | 2.54s |
| test_ssz_invariants.py | ✅ PASSED | 2.38s |
| test_ssz_kernel.py | ❌ FAILED | 0.63s |
| test_utf8_encoding.py | ✅ PASSED | 0.66s |

### Validation

**Tests:** 1 | **Passed:** 1 | **Rate:** 100.0%

| File | Status | Duration |
|------|--------|----------|
| run_ssz_validation.py | ✅ PASSED | 4.78s |

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
ne 659, in pop_outerr_to_orig
    out, err = self.readouterr()
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\.venv\lib\site-packages\_pytest\capture.py", line 706, in readouterr
    out = self.out.snap() if self.out else ""
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\.venv\lib\site-packages\_pytest\capture.py", line 591, in snap
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
ModuleNotFoundError: No module named 'scripts'

```

### test_cosmo_multibody.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
d import MultiBodyField, BodyState
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\.venv\lib\site-packages\ssz_cosmos\__init__.py", line 6, in <module>
    from .field import MultiBodyField
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\.venv\lib\site-packages\ssz_cosmos\field.py", line 10, in <module>
    from ssz_unified_suite import SSZCore
ModuleNotFoundError: No module named 'ssz_unified_suite'

```

### test_data_fetch.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_data_fetch.py", line 4, in <module>
    from scripts.tests.data_smoke_fetch import fetch_gaia_quick, fetch_sdss_quick, smoke_paths
ModuleNotFoundError: No module named 'scripts'

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
ModuleNotFoundError: No module named 'scripts'

```

### test_plot_ssz_maps.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_plot_ssz_maps.py", line 3, in <module>
    from scripts.viz.plot_ssz_maps import plot_mollweide, VizConfig
ModuleNotFoundError: No module named 'scripts'

```

### test_segmenter.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_segmenter.py", line 2, in <module>
    from scripts.ssz.segmenter import assign_segments_xy, SegParams
ModuleNotFoundError: No module named 'scripts'

```

### test_ssz_kernel.py

**Category:** scripts  
**Status:** FAILED  
**Error:**
```
Traceback (most recent call last):
  File "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00\scripts\tests\test_ssz_kernel.py", line 2, in <module>
    from scripts.ssz.gamma import gamma_seg_from_density
ModuleNotFoundError: No module named 'scripts'

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
