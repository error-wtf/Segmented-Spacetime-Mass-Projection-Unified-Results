# SSZ Segment-Redshift Add-on Runner
# Ruft das Add-on mit Standard-Parametern auf
# Keine Änderungen an der Pipeline - nur zusätzlicher Output!

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SSZ Segment-Redshift Add-on" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Standard-Parameter (anpassbar!)
$params = @(
    "--segment-redshift",
    "--proxy", "N",
    "--nu-em", "1.0e18",
    "--r-em", "2.0",
    "--r-out", "50.0",
    "--seg-plot"
)

Write-Host "Parameter:" -ForegroundColor Yellow
Write-Host "  proxy:   N (Segment-Dichte)" -ForegroundColor Gray
Write-Host "  nu_em:   1.0e18 Hz (X-ray)" -ForegroundColor Gray
Write-Host "  r_em:    2.0 r_s" -ForegroundColor Gray
Write-Host "  r_out:   50.0 r_s" -ForegroundColor Gray
Write-Host "  plot:    aktiviert" -ForegroundColor Gray
Write-Host ""

# Skript ausführen
python scripts/addons/segment_redshift_addon.py @params

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "FEHLER: Add-on fehlgeschlagen!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "Add-on erfolgreich!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Outputs:" -ForegroundColor Yellow
Write-Host "  - reports/segment_redshift.csv" -ForegroundColor Gray
Write-Host "  - reports/segment_redshift.md" -ForegroundColor Gray
Write-Host "  - reports/figures/fig_shared_segment_redshift_profile.png" -ForegroundColor Gray
Write-Host ""
