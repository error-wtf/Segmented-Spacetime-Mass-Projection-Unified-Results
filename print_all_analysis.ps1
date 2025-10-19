# SSZ Projection Suite - Test Results & Analysis Output Printer
# 
# Copyright © 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# This script prints ONLY test results, summaries, and analysis outputs:
# - Test summary (ci/test_summary.html)
# - Analysis reports (reports/)
# - Pipeline outputs (full_pipeline/)
#
# Documentation/Papers are available but not printed (to avoid terminal spam)
#
# Usage:
#   .\print_all_analysis.ps1

$ErrorActionPreference = "Stop"

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "SSZ PROJECTION SUITE - TEST RESULTS & ANALYSIS OUTPUT" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""

# Info: Available documentation (not printed)
Write-Host "Available Documentation (not printed to avoid spam):" -ForegroundColor Yellow
Write-Host "  - Validation Papers: papers/validation/ (11 papers)" -ForegroundColor Cyan
Write-Host "  - Theory Papers: docs/theory/ (21 papers)" -ForegroundColor Cyan
Write-Host "  - README: README.md" -ForegroundColor Cyan
Write-Host ""

# Section 1: Test Summary
Write-Host "[1/3] Test Summary (ci/test_summary.html)" -ForegroundColor Yellow
if (Test-Path "ci/test_summary.html") {
    Write-Host "  Test summary available: ci/test_summary.html" -ForegroundColor Green
    Write-Host "  Open in browser to view complete test results" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "  [INFO] No test summary yet (run tests with install.ps1 or pytest)" -ForegroundColor Cyan
    Write-Host ""
}

# Section 2: Analysis Reports
Write-Host "[2/3] Analysis Reports (reports/)" -ForegroundColor Yellow
if (Test-Path "reports") {
    ssz-print-md --root reports --order path
    Write-Host ""
} else {
    Write-Host "  [INFO] No reports yet (run python run_all_ssz_terminal.py to generate)" -ForegroundColor Cyan
    Write-Host ""
}

# Section 3: Full Pipeline Outputs
Write-Host "[3/3] Pipeline Outputs (full_pipeline/)" -ForegroundColor Yellow
if (Test-Path "full_pipeline") {
    ssz-print-md --root full_pipeline --order path
    Write-Host ""
} else {
    Write-Host "  [INFO] No pipeline outputs yet (run python run_all_ssz_terminal.py to generate)" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "TEST RESULTS & ANALYSIS OUTPUT COMPLETE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
