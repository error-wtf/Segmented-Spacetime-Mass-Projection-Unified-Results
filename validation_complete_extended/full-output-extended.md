
[1/13] Formula Verification
--------------------------------------------------------------------------------

================================================================================
STEP: Formula Verification
================================================================================
Script: verify_theory_scientific.py
Category: validation
Timeout: 60s
Critical: True
Started: 00:40:20

================================================================================
WISSENSCHAFTLICHE VALIDIERUNG DER SSZ THEORIE-DOKUMENTATION
================================================================================

[TEST 1] FORMEL-KORREKTHEIT
--------------------------------------------------------------------------------
  Formel: Xi(r) = Xi_max * (1 - exp(-phi * r_s / r))
  Bei r = 2r_s:
    Xi(2r_s) = 0.554704
    D(2r_s) = 0.643209
  [OK] PASS

[TEST 2] VERGLEICH MIT TEST-DATEN
--------------------------------------------------------------------------------
  Aus CSV-Daten: tau_SSZ = 510.027s
  Aus Formel: tau_SSZ = 643.209s
  Differenz: 133.182s (26.113%)
  [FAIL] FAIL

[TEST 3] UNIVERSAL INTERSECTION
--------------------------------------------------------------------------------
  Berechnet: r*/r_s = 1.594811
  Publiziert: r*/r_s = 1.594811
  Abweichung: 0.00000045

  Berechnet: D* = 0.610710
  Publiziert: D* = 0.61071
  Abweichung: 0.00000006
  [OK] PASS (< 1e-5)

[TEST 4] CAUSALITY CHECK
--------------------------------------------------------------------------------
  Tested range: r in [1.01r_s, 10r_s]
  D_min = 0.556016
  D_max = 0.870026
  0 < D <= 1: True
  [OK] PASS

[TEST 5] SSZ ASYMPTOTIC BEHAVIOR (INFO ONLY)
--------------------------------------------------------------------------------
  D(r -> infinity) theoretical: 0.500000
  D(r = 10r_s) numerical: 0.870026
  Difference: 0.37002551

  SSZ Key Feature: D never reaches 1.0!
  Vacuum segment density exists even at r -> infinity
  [INFO] False (This is expected SSZ behavior)

[TEST 6] GOLDEN RATIO VERIFICATION
--------------------------------------------------------------------------------
  phi = (1 + sqrt(5)) / 2
  Berechnet: phi = 1.618034
  Verwendet: phi = 1.618034
  Abweichung: 0.00000001

  phi^2 = 2.618034
  phi + 1 = 2.618034
  phi^2 = phi + 1: True
  [OK] PASS

================================================================================
ZUSAMMENFASSUNG
================================================================================
  [OK] PASS Formel-Korrektheit
  [FAIL] FAIL Vergleich mit Daten
  [OK] PASS Universal Intersection
  [OK] PASS Causality
  [OK] PASS Golden Ratio
  [INFO] INFO SSZ Asymptotic Behavior

Ergebnis: 4/5 Critical Tests bestanden
Info Tests: 1 (not counted as pass/fail)

================================================================================
[FAIL] CRITICAL FAILURES DETECTED
================================================================================

================================================================================
WISSENSCHAFTLICHE VALIDIERUNG DER SSZ THEORIE-DOKUMENTATION
================================================================================

[TEST 1] FORMEL-KORREKTHEIT
--------------------------------------------------------------------------------
  Formel: Xi(r) = Xi_max * (1 - exp(-phi * r_s / r))
  Bei r = 2r_s:
    Xi(2r_s) = 0.554704
    D(2r_s) = 0.643209
  [OK] PASS

[TEST 2] VERGLEICH MIT TEST-DATEN
--------------------------------------------------------------------------------
  Aus CSV-Daten: tau_SSZ = 510.027s
  Aus Formel: tau_SSZ = 643.209s
  Differenz: 133.182s (26.113%)
  [FAIL] FAIL

[TEST 3] UNIVERSAL INTERSECTION
--------------------------------------------------------------------------------
  Berechnet: r*/r_s = 1.594811
  Publiziert: r*/r_s = 1.594811
  Abweichung: 0.00000045

  Berechnet: D* = 0.610710
  Publiziert: D* = 0.61071
  Abweichung: 0.00000006
  [OK] PASS (< 1e-5)

[TEST 4] CAUSALITY CHECK
--------------------------------------------------------------------------------
  Tested range: r in [1.01r_s, 10r_s]
  D_min = 0.556016
  D_max = 0.870026
  0 < D <= 1: True
  [OK] PASS

[TEST 5] SSZ ASYMPTOTIC BEHAVIOR (INFO ONLY)
--------------------------------------------------------------------------------
  D(r -> infinity) theoretical: 0.500000
  D(r = 10r_s) numerical: 0.870026
  Difference: 0.37002551

  SSZ Key Feature: D never reaches 1.0!
  Vacuum segment density exists even at r -> infinity
  [INFO] False (This is expected SSZ behavior)

[TEST 6] GOLDEN RATIO VERIFICATION
--------------------------------------------------------------------------------
  phi = (1 + sqrt(5)) / 2
  Berechnet: phi = 1.618034
  Verwendet: phi = 1.618034
  Abweichung: 0.00000001

  phi^2 = 2.618034
  phi + 1 = 2.618034
  phi^2 = phi + 1: True
  [OK] PASS

================================================================================
ZUSAMMENFASSUNG
================================================================================
  [OK] PASS Formel-Korrektheit
  [FAIL] FAIL Vergleich mit Daten
  [OK] PASS Universal Intersection
  [OK] PASS Causality
  [OK] PASS Golden Ratio
  [INFO] INFO SSZ Asymptotic Behavior

Ergebnis: 4/5 Critical Tests bestanden
Info Tests: 1 (not counted as pass/fail)

================================================================================
[FAIL] CRITICAL FAILURES DETECTED
================================================================================


Completed: 00:40:20
Exit Code: 1
Status: [FAIL] FAILED

[FAIL] CRITICAL STEP FAILED: Formula Verification
  Stopping pipeline.

================================================================================
COLLECTING ALL OUTPUTS
================================================================================

================================================================================
COLLECTING OUTPUTS
================================================================================
  [OK] step6_ns_prediction.png
  [OK] step4_time_emergence.png
  [OK] step2_intersection.png
  [OK] step3_bh_stability.png
  [OK] step5_chaos_boundary.png
  [OK] step9_toe_architecture.png
  [OK] D_of_r_M2.png
  [OK] redshift_M2.png
  [OK] D_of_r_M4.1e+06.png
  [OK] sensitivity_heatmap_M4.1e+06.png
  [OK] redshift_M4.1e+06.png
  [OK] sensitivity_heatmap_M2.png
  [OK] shapiro_proxy_M4.1e+06.png
  [OK] shapiro_proxy_M2.png
  [OK] ToE_DASHBOARD.png
  [OK] theory_validation_dilation.png
  [OK] theory_validation_chaos.png
  [OK] theory_validation_stability.png
  [OK] gr_ssz_time_dilation_plot.png
  [OK] gr_vs_ssz_sensitivity.png
  [OK] debug_alpha_sweep.png
  [OK] gr_ssz_sensitivity_map.png
  [OK] gr_ssz_intersection_neutron_star_2_mmsun.png
  [OK] gr_vs_ssz_ns.png
  [OK] gr_ssz_intersection_sgr_a_4p1x10_mmsun.png
  [OK] gr_vs_ssz_sgra.png
  [OK] segspace_comparison.png
  [OK] dz_SR.png
  [OK] ssz_test_report.png
  [OK] hist_sr.png
  [OK] dz_GR.png
  [OK] redshift_segment_density_clean_plot.png
  [OK] hist_grsr.png
  [OK] redshift_ratio_with_deltaM_plot.png
  [OK] dz_seg_pred.png
  [OK] dz_comb.png
  [OK] test_hawking_fit.png
  [OK] hist_gr.png
  [OK] mass_binned_medians.png
  [OK] hist_seg.png

Collected 40 plots
Collected 399 reports
Collected 17 data files

================================================================================
EXTENDED VALIDATION SUMMARY
================================================================================

Total Steps: 1
Passed: 0
Failed: 1
Skipped: 0
Critical Failures: 1
Success Rate: 0.0%

Results by Category:
--------------------------------------------------------------------------------
  validation: 0/1 PASS (1 failed, 0 skipped)

Step Results:
--------------------------------------------------------------------------------
  [FAIL] FAIL Formula Verification [validation] (CRITICAL)

Error Summary:
--------------------------------------------------------------------------------
Total Errors: 1
By Type: {'ScriptFailure': 1}
By Step: {'Formula Verification': 1}
See error_log.txt for full details

================================================================================

[FAIL] CRITICAL FAILURES DETECTED
  Some critical validation steps failed!

================================================================================
SAVING OUTPUTS
================================================================================
