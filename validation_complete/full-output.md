
[1/7] Formula Verification
--------------------------------------------------------------------------------

================================================================================
STEP: Formula Verification
================================================================================
Script: verify_theory_scientific.py
Timeout: 60s
Critical: True
Started: 00:39:05

================================================================================
WISSENSCHAFTLICHE VALIDIERUNG DER SSZ THEORIE-DOKUMENTATION
================================================================================

[TEST 1] FORMEL-KORREKTHEIT
--------------------------------------------------------------------------------
  Formel: Xi(r) = Xi_max * (1 - exp(-phi * r_s / r))
  Bei r = 2r_s:
    Xi(2r_s) = 0.554704
    D(2r_s) = 0.643209
  [FAIL] FAIL

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
  [FAIL] FAIL Formel-Korrektheit
  [FAIL] FAIL Vergleich mit Daten
  [OK] PASS Universal Intersection
  [OK] PASS Causality
  [OK] PASS Golden Ratio
  [INFO] INFO SSZ Asymptotic Behavior

Ergebnis: 3/5 Critical Tests bestanden
Info Tests: 1 (not counted as pass/fail)

================================================================================
[FAIL] CRITICAL FAILURES DETECTED
================================================================================


Completed: 00:39:06
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

Collected 26 plots
Collected 394 reports
Collected 17 data files

================================================================================
VALIDATION SUMMARY
================================================================================

Total Steps: 1
Passed: 0
Failed: 1
Critical Failures: 1
Success Rate: 0.0%

Step Results:
--------------------------------------------------------------------------------
  [FAIL] FAIL Formula Verification (CRITICAL)

================================================================================

[FAIL] CRITICAL FAILURES DETECTED
  Some critical validation steps failed!

================================================================================
SAVING OUTPUTS
================================================================================
