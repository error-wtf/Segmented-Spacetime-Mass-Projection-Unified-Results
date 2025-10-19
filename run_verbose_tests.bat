@echo off
REM Quick runner for verbose tests with physical interpretations

setlocal enabledelayedexpansion

echo ================================================================================
echo VERBOSE SSZ TESTS - With Physical Interpretations
echo ================================================================================
echo.

REM Set UTF-8
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM Parse arguments
if "%~1"=="" (
    set "TEST_PATH=scripts\tests\"
    echo No test path provided, using default: scripts\tests\
) else (
    set "TEST_PATH=%~1"
)

echo Test Path: %TEST_PATH%
echo.
echo Running pytest with verbose output and physical interpretations...
echo   -s            (show print output)
echo   -v            (verbose test names)
echo   --tb=short    (short tracebacks)
echo.
echo ================================================================================
echo.

REM Run pytest with -s flag to show all print() outputs
python -X utf8 -m pytest "%TEST_PATH%" -s -v --tb=short

set EXIT_CODE=%errorlevel%

echo.
echo ================================================================================
if %EXIT_CODE% equ 0 (
    echo SUCCESS: All tests passed with detailed output!
) else (
    echo FAILED: Some tests failed (exit code %EXIT_CODE%)
)
echo ================================================================================

exit /b %EXIT_CODE%
