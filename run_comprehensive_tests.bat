@echo off
REM Quick runner for Comprehensive SSZ Real Data Tests (Windows)
setlocal enabledelayedexpansion

echo ================================================================================
echo SEGMENTED SPACETIME - COMPREHENSIVE TEST RUNNER
echo ================================================================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

REM Parse arguments
set "ARGS="
set "SHOW_HELP=0"

:parse_args
if "%~1"=="" goto run_tests
if "%~1"=="--help" set "SHOW_HELP=1"
if "%~1"=="-h" set "SHOW_HELP=1"
set "ARGS=%ARGS% %~1"
shift
goto parse_args

:run_tests
if "%SHOW_HELP%"=="1" (
    echo Usage:
    echo   run_comprehensive_tests.bat [OPTIONS]
    echo.
    echo Options:
    echo   --html              Generate HTML report
    echo   --object OBJECT     Test specific object (Sun, SgrA*, M87*)
    echo   --radius RADIUS     Test specific radius (e.g. 2.0 for 2r_s^)
    echo   --verbose, -v       Verbose output
    echo   --output DIR        Output directory (default: test_results^)
    echo   --help, -h          Show this help
    echo.
    echo Examples:
    echo   run_comprehensive_tests.bat --verbose
    echo   run_comprehensive_tests.bat --object SgrA* --html
    echo   run_comprehensive_tests.bat --radius 5.0 --verbose
    exit /b 0
)

echo Running comprehensive SSZ tests...
echo Command: python run_comprehensive_tests.py%ARGS%
echo.
echo ================================================================================
echo.

python run_comprehensive_tests.py%ARGS%
set EXIT_CODE=%errorlevel%

echo.
echo ================================================================================
if %EXIT_CODE% equ 0 (
    echo SUCCESS: All tests passed!
) else (
    echo FAILED: Some tests failed (exit code %EXIT_CODE%^)
)
echo ================================================================================

exit /b %EXIT_CODE%
