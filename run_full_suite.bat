@echo off
REM SSZ Projection Suite - Complete Test & Analysis Runner (Windows Batch)
REM
REM Copyright (c) 2025
REM Carmen Wrede und Lino Casu
REM Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
REM
REM Usage:
REM   run_full_suite.bat
REM   run_full_suite.bat --quick
REM   run_full_suite.bat --skip-slow-tests

echo Starting SSZ Full Suite Runner...
python run_full_suite.py %*
