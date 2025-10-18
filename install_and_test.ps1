# SSZ Projection Suite - Install + Full Test Suite Runner
# 
# Copyright © 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# This is a convenience wrapper that:
# 1. Runs the standard installation
# 2. Automatically runs the complete test suite
#
# Usage:
#   .\install_and_test.ps1          # Full suite (~10-15 min)
#   .\install_and_test.ps1 -Quick   # Quick suite (~2 min)

param(
    [switch]$Quick
)

$ErrorActionPreference = "Stop"

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "SSZ PROJECTION SUITE - INSTALL + TEST WORKFLOW" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""

# Step 1: Run standard installation
Write-Host "STEP 1: Running installation..." -ForegroundColor Yellow
& .\install.ps1

# Check if installation succeeded
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Installation failed" -ForegroundColor Red
    exit 1
}

# Step 2: Run full test suite
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "STEP 2: Running full test suite..." -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""

if ($Quick) {
    Write-Host "Mode: Quick suite (~2 min)" -ForegroundColor Yellow
    & python run_full_suite.py --quick
} else {
    Write-Host "Mode: Full suite (~10-15 min)" -ForegroundColor Yellow
    & python run_full_suite.py
}

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 98) -ForegroundColor Cyan
    Write-Host "[SUCCESS] Installation and all tests passed!" -ForegroundColor Green
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 98) -ForegroundColor Cyan
    exit 0
} else {
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 98) -ForegroundColor Cyan
    Write-Host "[WARNING] Some tests failed (see output above)" -ForegroundColor Yellow
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 98) -ForegroundColor Cyan
    exit 1
}
