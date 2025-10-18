# SSZ Projection Suite - Complete Analysis Output Printer
# 
# Copyright © 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# This script prints ALL Markdown content in the repository:
# - Validation papers (papers/validation/)
# - Theory papers (docs/theory/)
# - Analysis reports (reports/)
# - Test summaries (reports/)
# - Root-level documentation
# - Any other MD outputs
#
# Usage:
#   .\print_all_analysis.ps1

$ErrorActionPreference = "Stop"

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "SSZ PROJECTION SUITE - COMPLETE MARKDOWN OUTPUT" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""

# Section 1: Validation Papers (list only, no content)
Write-Host "[1/5] Validation Papers (papers/validation/)" -ForegroundColor Yellow
if (Test-Path "papers/validation") {
    $validationPapers = Get-ChildItem -Path "papers/validation" -Filter *.md -Recurse
    foreach ($paper in $validationPapers) {
        Write-Host "  - $($paper.FullName)" -ForegroundColor Cyan
    }
    Write-Host "  Total: $($validationPapers.Count) papers" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "  [SKIP] No validation papers found" -ForegroundColor Yellow
}

# Section 2: Theory Papers (list only, no content)
Write-Host "[2/5] Theory Papers (docs/theory/)" -ForegroundColor Yellow
if (Test-Path "docs/theory") {
    $theoryPapers = Get-ChildItem -Path "docs/theory" -Filter *.md -Recurse
    foreach ($paper in $theoryPapers) {
        Write-Host "  - $($paper.FullName)" -ForegroundColor Cyan
    }
    Write-Host "  Total: $($theoryPapers.Count) papers" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "  [SKIP] No theory papers found" -ForegroundColor Yellow
}

# Section 3: Analysis Reports
Write-Host "[3/5] Analysis Reports (reports/)" -ForegroundColor Yellow
if (Test-Path "reports") {
    ssz-print-md --root reports --order path
    Write-Host ""
} else {
    Write-Host "  [SKIP] No reports found" -ForegroundColor Yellow
}

# Section 4: Documentation (list only, no content)
Write-Host "[4/5] Documentation (docs/*.md, root *.md)" -ForegroundColor Yellow
if (Test-Path "docs") {
    $docFiles = Get-ChildItem -Path "docs" -Filter *.md -Recurse
    foreach ($doc in $docFiles) {
        Write-Host "  - $($doc.FullName)" -ForegroundColor Cyan
    }
    Write-Host "  Total: $($docFiles.Count) documentation files" -ForegroundColor Green
}
# Root-level MD files (excluding directories)
$rootMd = Get-ChildItem -Path . -Filter *.md -File | Where-Object { 
    $_.Name -ne "README.md"  # README still important to show
}
foreach ($md in $rootMd) {
    Write-Host "  - $($md.FullName)" -ForegroundColor Cyan
}
Write-Host ""

# Section 5: Full Pipeline Outputs
Write-Host "[5/5] Pipeline Outputs (full_pipeline/)" -ForegroundColor Yellow
if (Test-Path "full_pipeline") {
    ssz-print-md --root full_pipeline --order path
    Write-Host ""
} else {
    Write-Host "  [SKIP] No pipeline outputs found (run python run_all_ssz_terminal.py first)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "COMPLETE MARKDOWN OUTPUT FINISHED" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
