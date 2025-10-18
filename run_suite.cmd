@echo off
REM ====================================================================
REM  SSZ Pipeline Suite Runner - Windows Batch Launcher
REM ====================================================================
REM  Ensures the script always runs from the correct repository directory
REM  No PowerShell required - just double-click or type "run_suite"
REM ====================================================================
setlocal enabledelayedexpansion

cd /d "H:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00"

echo.
echo ======================================================================
echo  Starting SSZ Autorun Suite
echo ======================================================================
echo  Working directory: %CD%
echo  Python executable: .venv\Scripts\python.exe
echo ======================================================================
echo.

".venv\Scripts\python.exe" -X utf8 ci\autorun_suite.py

echo.
echo ======================================================================
echo  Suite execution completed (exit code: %ERRORLEVEL%)
echo ======================================================================
echo.

endlocal
pause
