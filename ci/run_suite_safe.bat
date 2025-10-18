@echo off
REM Safe wrapper to prevent PowerShell Extension crashes
setlocal enabledelayedexpansion

echo ========================================
echo SSZ CI Suite - Safe Runner
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."

REM Default to suite_config.yaml
set "CONFIG=%SCRIPT_DIR%suite_config.yaml"
if not "%~1"=="" set "CONFIG=%~1"

echo Starting CI Suite...
echo Config: %CONFIG%
echo Root: %ROOT_DIR%
echo.
echo ----------------------------------------

REM Run Python script with output redirection to prevent PowerShell crashes
python "%SCRIPT_DIR%autorun_suite.py" --config "%CONFIG%" 2>&1 | findstr /V /C:"main()" /C:"subprocess.run" /C:"CalledProcessError"

set EXIT_CODE=%errorlevel%

echo.
echo ----------------------------------------
if %EXIT_CODE% equ 0 (
    echo SUCCESS: CI Suite completed
) else (
    echo ERROR: CI Suite failed with code %EXIT_CODE%
)
echo ========================================

exit /b %EXIT_CODE%
