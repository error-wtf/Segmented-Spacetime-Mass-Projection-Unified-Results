#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    Quick Test Runner for Paper Export Tools

.DESCRIPTION
    Tests the complete paper export pipeline:
    - Plot helpers
    - Caption catalog
    - I/O utilities
    - Figure orchestrator
    - Manifest generation

.EXAMPLE
    .\test_paper_exports.ps1
#>

# © 2025 Carmen Wrede, Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SSZ Paper Export Tools - TEST RUNNER" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check dependencies
Write-Host "[2/5] Checking dependencies..." -ForegroundColor Yellow
$missing = @()
foreach ($module in @("matplotlib", "numpy")) {
    python -c "import $module" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $missing += $module
        Write-Host "✗ Missing: $module" -ForegroundColor Red
    } else {
        Write-Host "✓ Found: $module" -ForegroundColor Green
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Installing missing packages..." -ForegroundColor Yellow
    pip install $missing
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Installation failed!" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Clean old outputs
Write-Host "[3/5] Cleaning old test outputs..." -ForegroundColor Yellow
if (Test-Path "reports/figures/demo") {
    Remove-Item -Recurse -Force "reports/figures/demo"
    Write-Host "✓ Removed old demo figures" -ForegroundColor Green
}
if (Test-Path "reports/DEMO_MANIFEST.json") {
    Remove-Item -Force "reports/DEMO_MANIFEST.json"
    Write-Host "✓ Removed old demo manifest" -ForegroundColor Green
}
if (Test-Path "reports/figures/FIGURE_INDEX.md") {
    Remove-Item -Force "reports/figures/FIGURE_INDEX.md"
    Write-Host "✓ Removed old figure index" -ForegroundColor Green
}
Write-Host ""

# Run demo
Write-Host "[4/5] Running demo script..." -ForegroundColor Yellow
Write-Host ""
python demo_paper_exports.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Demo failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Verify outputs
Write-Host "[5/5] Verifying outputs..." -ForegroundColor Yellow

$checks = @{
    "reports/figures/demo/fig_demo_line.png" = "Line plot PNG"
    "reports/figures/demo/fig_demo_line.svg" = "Line plot SVG"
    "reports/figures/demo/fig_demo_scatter.png" = "Scatter plot PNG"
    "reports/figures/demo/fig_demo_scatter.svg" = "Scatter plot SVG"
    "reports/figures/demo/fig_demo_heatmap.png" = "Heatmap PNG"
    "reports/figures/FIGURE_INDEX.md" = "Figure index"
    "reports/DEMO_MANIFEST.json" = "Demo manifest"
}

$allGood = $true
foreach ($path in $checks.Keys) {
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        Write-Host "✓ $($checks[$path]): $path ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "✗ MISSING: $($checks[$path]): $path" -ForegroundColor Red
        $allGood = $false
    }
}
Write-Host ""

# Final verdict
if ($allGood) {
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "✅ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. View figures: explorer reports\figures\demo" -ForegroundColor White
    Write-Host "  2. Check index: code reports\figures\FIGURE_INDEX.md" -ForegroundColor White
    Write-Host "  3. Read guide: code QUICK_START_PAPER_EXPORTS.md" -ForegroundColor White
    Write-Host "  4. Integrate: Follow PAPER_EXPORTS_README.md" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host "✗ SOME TESTS FAILED!" -ForegroundColor Red
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  - Check Python version (need 3.7+)" -ForegroundColor White
    Write-Host "  - Verify matplotlib installation: pip install matplotlib" -ForegroundColor White
    Write-Host "  - Run from project root directory" -ForegroundColor White
    Write-Host "  - Check permissions on reports/ folder" -ForegroundColor White
    Write-Host ""
    exit 1
}
