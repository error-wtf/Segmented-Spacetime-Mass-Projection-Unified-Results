# Check if running inside virtual environment
# Usage: .\check_venv.ps1

if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  WARNING: Not running in virtual environment!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Python packages (pyarrow, etc.) are installed in .venv/" -ForegroundColor Cyan
    Write-Host "but you're using system Python." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To activate the virtual environment:" -ForegroundColor Green
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run your command again." -ForegroundColor Cyan
    Write-Host ""
    exit 1
} else {
    Write-Host "✓ Virtual environment active: $env:VIRTUAL_ENV" -ForegroundColor Green
    exit 0
}
