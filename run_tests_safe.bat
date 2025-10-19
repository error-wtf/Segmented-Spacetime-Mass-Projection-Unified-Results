@echo off
REM Safe Test Runner - Bypasses PowerShell Extension Issues
REM For comprehensive SSZ tests that output lots of text

setlocal enabledelayedexpansion

echo ================================================================================
echo SAFE TEST RUNNER - Bypassing PowerShell Extension
echo ================================================================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM Check if test path provided
if "%~1"=="" (
    echo ERROR: No test path provided
    echo.
    echo Usage:
    echo   run_tests_safe.bat tests/test_ssz_real_data_comprehensive.py
    echo   run_tests_safe.bat scripts/tests/
    echo   run_tests_safe.bat tests/ -k "SgrA"
    exit /b 1
)

set TEST_PATH=%~1
shift

REM Collect remaining args
set "EXTRA_ARGS="
:collect_args
if "%~1"=="" goto run_tests
set "EXTRA_ARGS=%EXTRA_ARGS% %~1"
shift
goto collect_args

:run_tests
echo Test Path: %TEST_PATH%
if not "%EXTRA_ARGS%"=="" echo Extra Args:%EXTRA_ARGS%
echo.
echo Running pytest with safe flags...
echo   -s             (no output capture)
echo   --tb=short     (short tracebacks)
echo   -v             (verbose)
echo.
echo ================================================================================
echo.

REM Run pytest with flags that prevent the crash:
REM -s : Disable output capture (prevents I/O closed file error)
REM --tb=short : Short tracebacks
REM -v : Verbose output
python -X utf8 -m pytest "%TEST_PATH%" -s --tb=short -v%EXTRA_ARGS%

set EXIT_CODE=%errorlevel%

echo.
echo ================================================================================
if %EXIT_CODE% equ 0 (
    echo SUCCESS: All tests passed!
) else (
    echo FAILED: Tests failed with exit code %EXIT_CODE%
)
echo ================================================================================

exit /b %EXIT_CODE%
