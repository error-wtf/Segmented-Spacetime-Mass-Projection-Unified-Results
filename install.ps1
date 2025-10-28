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
pip install --quiet numpy scipy matplotlib pandas pillow
Write-Host "  ✓ Installed: numpy, scipy, matplotlib, pandas, pillow" -ForegroundColor Green

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
Write-Host "  python run_ssz_validation.py           # SSZ vs GR validation (~2 min)" -ForegroundColor White
Write-Host "  python run_ssz_theory_validation.py    # 10-step ToE validation (~2 min)" -ForegroundColor White
Write-Host "  python run_complete_test_suite.py      # All tests (~5-10 min)" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  README.md                              # Overview" -ForegroundColor White
Write-Host "  SSZ_COMPLETE_FINAL_REPORT.md          # Complete 60+ page report" -ForegroundColor White
Write-Host "  TEST_SUITE_README.md                   # Testing guide" -ForegroundColor White
Write-Host ""
Write-Host "Repository: https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results" -ForegroundColor Cyan
Write-Host ""
