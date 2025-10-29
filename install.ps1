# SSZ Complete Analysis - Installation Script (Windows)
# © 2025 Carmen Wrede, Lino Casu

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "SSZ COMPLETE ANALYSIS - INSTALLATION" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[2/5] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv .venv
    Write-Host "  ✓ Created .venv" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/5] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[4/5] Installing dependencies..." -ForegroundColor Yellow
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
Write-Host "  ✓ Installed: numpy, scipy, matplotlib, pandas, pillow, pyarrow" -ForegroundColor Green

# Run validation
Write-Host ""
Write-Host "[5/5] Running quick validation..." -ForegroundColor Yellow
python run_ssz_validation.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Validation passed!" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Validation had issues (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Available Commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "MAIN PIPELINE (Extended):" -ForegroundColor Cyan
Write-Host "  python run_complete_validation_extended.py  # MASTER: 12 steps (11/12 PASS, ~10-15 min)" -ForegroundColor Green
Write-Host "      Includes: Formula verification, 22/22 test suites (100%), ToE unified (11 steps)," -ForegroundColor DarkGray
Write-Host "                ToE v2 (6 pillars), grid convergence, proper time," -ForegroundColor DarkGray
Write-Host "                theory validation, PPN, velocity duality, energy conditions" -ForegroundColor DarkGray
Write-Host "      Output: validation_complete_extended/ (388 files: 38 plots, 333 reports)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "ALTERNATIVE: Original Master Pipeline:" -ForegroundColor Yellow
Write-Host "  python run_all_validations.py          # All 161 tests (5 pipelines, ~15-20 min)" -ForegroundColor White
Write-Host ""
Write-Host "Individual Pipelines:" -ForegroundColor Yellow
Write-Host "  python run_full_suite.py               # 22 test suites - 100% PASS (~3-4 min)" -ForegroundColor White
Write-Host "  python run_ssz_validation.py           # SSZ vs GR (6 steps, ~2 min)" -ForegroundColor White
Write-Host "  python run_ssz_theory_validation.py    # Theory validation (10 steps, ~2 min)" -ForegroundColor White
Write-Host "  python run_ssz_unified_validation.py   # Unified ToE proof (11 steps, ~2 min)" -ForegroundColor White
Write-Host "  python run_toe_validation_v2.py        # ToE v2 deterministic (6 pillars, ~2 min)" -ForegroundColor White
Write-Host "  python run_complete_test_suite.py      # Complete test suite (~18 scripts, ~5-10 min)" -ForegroundColor White
Write-Host ""
Write-Host "Total: 161+ tests across multiple pipelines" -ForegroundColor Cyan
Write-Host "Expected: 100% PASS (22/22 test suites in run_full_suite.py)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  README.md                              # Overview" -ForegroundColor White
Write-Host "  SSZ_COMPLETE_FINAL_REPORT.md          # Complete 60+ page report" -ForegroundColor White
Write-Host "  TEST_SUITE_README.md                   # Testing guide" -ForegroundColor White
Write-Host ""
Write-Host "Repository: https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results" -ForegroundColor Cyan
Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "TROUBLESHOOTING: CLEAR CACHE IF TESTS FAIL" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""
Write-Host "If you encounter test failures during repeated runs, clear the Python cache:" -ForegroundColor White
Write-Host ""
Write-Host "Windows (PowerShell):" -ForegroundColor Yellow
Write-Host "  .\CLEAR_CACHE.bat" -ForegroundColor Green
Write-Host "  # OR manually:" -ForegroundColor DarkGray
Write-Host "  Get-ChildItem -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force" -ForegroundColor DarkGray
Write-Host "  Get-ChildItem -Recurse -Directory -Filter '.pytest_cache' | Remove-Item -Recurse -Force" -ForegroundColor DarkGray
Write-Host "  Get-ChildItem -Recurse -File -Include '*.pyc','*.pyo' | Remove-Item -Force" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Then re-run your tests. Cache corruption can cause false failures!" -ForegroundColor White
Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "ACTIVATING VIRTUAL ENVIRONMENT..." -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Auto-activate venv for current shell
& .\.venv\Scripts\Activate.ps1

Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "You are now in the SSZ virtual environment." -ForegroundColor Cyan
$pythonPath = (Get-Command python).Source
$pipPath = (Get-Command pip).Source
Write-Host "Python: $pythonPath" -ForegroundColor White
Write-Host "Pip: $pipPath" -ForegroundColor White
Write-Host ""
Write-Host "To deactivate later, run:" -ForegroundColor Yellow
Write-Host "  deactivate" -ForegroundColor Green
Write-Host ""
Write-Host "To reactivate in a new shell:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host ""
