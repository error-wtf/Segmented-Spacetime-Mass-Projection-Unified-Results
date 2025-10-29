# Run Complete Validation Suite with Full Logging
# Captures all output and errors to log files

$ErrorActionPreference = "Continue"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "validation_logs_$timestamp"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SSZ Complete Validation Suite - With Full Logging" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Log Directory: $logDir" -ForegroundColor Yellow
Write-Host "Start Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host ""

# Run validation suite
Write-Host "[1/2] Running complete validation suite..." -ForegroundColor Yellow
Write-Host ""

$output = & python run_all_validations.py 2>&1 | Tee-Object -FilePath "$logDir\validation_output.log"
$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "[2/2] Saving logs and reports..." -ForegroundColor Yellow

# Copy generated reports
if (Test-Path "reports") {
    Copy-Item "reports\*" "$logDir\" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Copied reports/" -ForegroundColor Green
}

if (Test-Path "outputs") {
    Copy-Item "outputs\*" "$logDir\" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Copied outputs/" -ForegroundColor Green
}

# Save exit code
$exitCode | Out-File "$logDir\exit_code.txt"

# Generate summary
$summaryFile = "$logDir\VALIDATION_SUMMARY.md"
@"
# SSZ Validation Suite - Run Summary

**Timestamp:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Exit Code:** $exitCode
**Status:** $(if ($exitCode -eq 0) { "✅ SUCCESS" } else { "❌ FAILED" })

## Log Files

- **validation_output.log** - Complete console output
- **exit_code.txt** - Process exit code
- **reports/** - Generated test reports
- **outputs/** - Generated output files

## Quick Links

- Full Output: reports/full-output.md
- Summary: reports/summary-output.md
- RUN_SUMMARY: reports/RUN_SUMMARY.md

---

© 2025 Carmen Wrede & Lino Casu
"@ | Out-File $summaryFile -Encoding UTF8

Write-Host "  ✓ Generated VALIDATION_SUMMARY.md" -ForegroundColor Green
Write-Host ""

# Final status
Write-Host "================================================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "✅ VALIDATION SUITE COMPLETED SUCCESSFULLY" -ForegroundColor Green
} else {
    Write-Host "❌ VALIDATION SUITE FAILED (Exit Code: $exitCode)" -ForegroundColor Red
}
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All logs saved to: $logDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "To review:" -ForegroundColor Cyan
Write-Host "  - Full output: type $logDir\validation_output.log" -ForegroundColor Gray
Write-Host "  - Summary: type $logDir\VALIDATION_SUMMARY.md" -ForegroundColor Gray
Write-Host "  - Reports: dir $logDir\reports\" -ForegroundColor Gray
Write-Host ""

exit $exitCode
