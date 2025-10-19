# Update script after git pull
# Regenerates all outputs with latest real data

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SSZ - Update After Pull" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script regenerates all analysis outputs with the latest data."
Write-Host "Run this after every 'git pull' to ensure consistency."
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "run_all_ssz_terminal.py")) {
    Write-Host "❌ Error: run_all_ssz_terminal.py not found" -ForegroundColor Red
    Write-Host "   Please run this script from the repository root"
    exit 1
}

Write-Host "[1/4] Checking data files..."
if (-not (Test-Path "real_data_full.csv")) {
    Write-Host "❌ Error: real_data_full.csv not found" -ForegroundColor Red
    Write-Host "   Please ensure you have pulled the latest version"
    exit 1
}

# Check number of rows in real_data_full.csv
$rows = (Get-Content "real_data_full.csv" | Measure-Object -Line).Lines
Write-Host "   ✓ Found real_data_full.csv ($rows rows)" -ForegroundColor Green

if ($rows -lt 167) {
    Write-Host "⚠️  Warning: Expected 167+ rows, found $rows" -ForegroundColor Yellow
    Write-Host "   You may not have the latest data. Consider running:"
    Write-Host "   git pull"
    $reply = Read-Host "Continue anyway? (y/n)"
    if ($reply -ne 'y') {
        exit 1
    }
}

Write-Host ""
Write-Host "[2/4] Cleaning old outputs..."
Remove-Item -Path "out\*.csv", "out\*.png", "out\*.txt" -ErrorAction SilentlyContinue
Remove-Item -Path "reports\*.md", "reports\*.csv" -ErrorAction SilentlyContinue
Remove-Item -Path "reports\figures\*" -Recurse -ErrorAction SilentlyContinue
Write-Host "   ✓ Old outputs removed" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Running SSZ pipeline (this takes ~7-10 minutes)..." -ForegroundColor Yellow
Write-Host "   Processing 167 real data points (ALMA/Chandra/VLT)..."
Write-Host ""

python run_all_ssz_terminal.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Pipeline failed!" -ForegroundColor Red
    Write-Host "   Check error messages above"
    exit 1
}

Write-Host ""
Write-Host "[4/4] Verifying outputs..."
if (Test-Path "out\phi_step_debug_full.csv") {
    $outRows = (Get-Content "out\phi_step_debug_full.csv" | Measure-Object -Line).Lines
    Write-Host "   ✓ out\phi_step_debug_full.csv created ($outRows rows)" -ForegroundColor Green
} else {
    Write-Host "   ❌ out\phi_step_debug_full.csv not found" -ForegroundColor Red
    exit 1
}

if (Test-Path "reports\info_preservation_by_source.csv") {
    Write-Host "   ✓ reports\info_preservation_by_source.csv created" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  reports\info_preservation_by_source.csv not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "✅ UPDATE COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "What was updated:"
Write-Host "  • out\phi_step_debug_full.csv ($outRows rows with real data)"
Write-Host "  • out\_enhanced_debug.csv"
Write-Host "  • reports\hawking_proxy_fit.md"
Write-Host "  • reports\info_preservation_by_source.csv"
Write-Host "  • All plots in reports\figures\"
Write-Host ""
Write-Host "You can now run:"
Write-Host "  python scripts\tests\test_horizon_hawking_predictions.py"
Write-Host ""
Write-Host "Expected result:"
Write-Host "  ✅ All 3 warnings RESOLVED" -ForegroundColor Green
Write-Host "  ✅ HIGH confidence validation" -ForegroundColor Green
Write-Host "  ✅ 167 real data points (ALMA/Chandra/VLT)" -ForegroundColor Green
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
