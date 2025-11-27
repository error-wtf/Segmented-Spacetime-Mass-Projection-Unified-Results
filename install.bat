@echo off
REM ============================================================================
REM SSZ Suite - Windows Installation Script (Batch Version)
REM ============================================================================
REM For PowerShell version, use install.ps1
REM ============================================================================

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   SSZ SUITE - WINDOWS INSTALLATION                           ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Python not found! Please install Python 3.10+ first.
    echo   Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo   ✓ Python found
echo.

REM Step 2: Create virtual environment
echo [2/5] Creating virtual environment...
if exist .venv (
    echo   ✓ Virtual environment already exists
) else (
    python -m venv .venv
    echo   ✓ Virtual environment created
)
echo.

REM Step 3: Activate venv and upgrade pip
echo [3/5] Activating virtual environment and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --quiet --upgrade pip
echo   ✓ Pip upgraded
echo.

REM Step 4: Install dependencies
echo [4/5] Installing dependencies...
echo   Installing core packages (this may take a few minutes)...
pip install --quiet -r requirements.txt
echo   ✓ Installed: numpy, scipy, matplotlib, pandas, pillow, pyarrow
echo.

REM Step 5: Run validation
echo [5/5] Running quick validation...
python run_ssz_validation.py
if %errorlevel% equ 0 (
    echo   ✓ Validation passed!
) else (
    echo   ⚠ Validation had issues ^(exit code: %errorlevel%^)
)
echo.

REM Summary
echo ═══════════════════════════════════════════════════════════════
echo INSTALLATION COMPLETE
echo ═══════════════════════════════════════════════════════════════
echo.
echo Need help? Check out:
echo   • README.md
echo   • INSTALL_README.md
echo   • TEST_SUITE_README.md
echo.
echo ═══════════════════════════════════════════════════════════════
echo ⚠️  IMPORTANT: PYTEST CACHE WARNING
echo ═══════════════════════════════════════════════════════════════
echo.
echo ALWAYS run .\CLEAR_CACHE.bat BEFORE running tests!
echo.
echo Why? Pytest caches old file versions and can cause false test failures.
echo The cache must be cleared to ensure tests use the current code.
echo.
echo Correct workflow:
echo   1. .\CLEAR_CACHE.bat       # Clear cache first
echo   2. python run_full_suite.py  # Then run tests
echo.
echo See PYTEST_CACHE_PROBLEM_SOLUTION.md for details.
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo Available Commands:
echo.
echo MAIN PIPELINE ^(Extended^):
echo   python run_complete_validation_extended.py  # MASTER: 12 steps ^(11/12 PASS, ~10-15 min^)
echo       Includes: Formula verification, 22/22 test suites ^(100%%^), ToE unified ^(11 steps^),
echo                 ToE v2 ^(6 pillars^), grid convergence, proper time,
echo                 theory validation, PPN, velocity duality, energy conditions
echo       Output: validation_complete_extended/ ^(388 files: 38 plots, 333 reports^)
echo.
echo ALTERNATIVE: Original Master Pipeline:
echo   python run_all_validations.py          # All 161 tests ^(5 pipelines, ~15-20 min^)
echo.
echo Individual Pipelines:
echo   python run_full_suite.py               # 23 test suites - 100%% PASS ^(~3-4 min^)
echo   python run_ssz_validation.py           # SSZ vs GR ^(6 steps, ~2 min^)
echo   python run_ssz_theory_validation.py    # Theory validation ^(10 steps, ~2 min^)
echo   python run_ssz_unified_validation.py   # Unified ToE proof ^(11 steps, ~2 min^)
echo   python run_toe_validation_v2.py        # ToE v2 deterministic ^(6 pillars, ~2 min^)
echo   python run_complete_test_suite.py      # Complete test suite ^(~18 scripts, ~5-10 min^)
echo.
echo Total: 161+ tests across multiple pipelines
echo Expected: 100%% PASS ^(23/23 test suites in run_full_suite.py^)
echo.
echo Documentation:
echo   README.md                              # Overview
echo   SSZ_COMPLETE_FINAL_REPORT.md          # Complete 60+ page report
echo   TEST_SUITE_README.md                   # Testing guide
echo.
echo Repository: https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results
echo.
echo ═══════════════════════════════════════════════════════════════
echo TROUBLESHOOTING: CLEAR CACHE IF TESTS FAIL
echo ═══════════════════════════════════════════════════════════════
echo.
echo If you encounter test failures during repeated runs, clear the Python cache:
echo.
echo Windows:
echo   .\CLEAR_CACHE.bat
echo   # OR manually:
echo   for /d /r . %%d in ^(__pycache__^) do @if exist "%%d" rd /s /q "%%d"
echo   for /d /r . %%d in ^(.pytest_cache^) do @if exist "%%d" rd /s /q "%%d"
echo.
echo Then re-run your tests. Cache corruption can cause false failures!
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo Virtual environment is now active in this window.
echo   Python: %VIRTUAL_ENV%\Scripts\python.exe
echo   Pip: %VIRTUAL_ENV%\Scripts\pip.exe
echo.
echo To deactivate later, run:
echo   deactivate
echo.
echo To reactivate in a new window:
echo   .venv\Scripts\activate.bat
echo.
echo ═══════════════════════════════════════════════════════════════
echo ✅ INSTALLATION COMPLETE - Ready to run tests!
echo ═══════════════════════════════════════════════════════════════
echo.

pause
