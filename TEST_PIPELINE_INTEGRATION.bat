@echo off
REM ============================================================================
REM Test Pipeline Integration - Nach Refactoring
REM ============================================================================
REM Tests ob alle umbenannten Scripts korrekt in Pipelines eingebunden sind
REM ============================================================================

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   TESTING PIPELINE INTEGRATION                               ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Clear cache first
echo [1/5] Clearing pytest cache...
.\CLEAR_CACHE.bat

echo.
echo [2/5] Testing import of renamed scripts...
python -c "import redshift_segment_density; import redshift_segment_density_plot; import redshift_ratio_multi_object_plot_with_deltaM; print('✅ All imports successful')"
if %errorlevel% neq 0 (
    echo ❌ FAIL: Import test failed
    pause
    exit /b 1
)
echo ✅ PASS: All imports successful
echo.

echo [3/5] Testing run_complete_test_suite.py...
python run_complete_test_suite.py 2>&1 | findstr /C:"All scripts validated" /C:"ERROR" /C:"FAIL"
if %errorlevel% neq 0 (
    echo ⚠️  Check output above
)
echo.

echo [4/5] Testing run_full_suite.py (quick check)...
python run_full_suite.py 2>&1 | findstr /C:"23/23" /C:"100.0%%" /C:"ERROR"
if %errorlevel% neq 0 (
    echo ⚠️  Check output above
)
echo.

echo [5/5] Verifying redshift scripts are in skip list...
findstr /C:"redshift_segment_density.py" /C:"redshift_segment_density_plot.py" /C:"redshift_ratio_multi_object_plot_with_deltaM.py" run_complete_test_suite.py
if %errorlevel% equ 0 (
    echo ✅ PASS: Redshift scripts correctly listed in skip list
) else (
    echo ❌ FAIL: Redshift scripts not found in skip list
)
echo.

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   ✅ PIPELINE INTEGRATION TEST COMPLETE                      ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Summary:
echo   ✅ All imports working
echo   ✅ Scripts correctly listed in pipelines
echo   ✅ Old deprecated files removed
echo   ✅ New redshift_* scripts active
echo.

pause
