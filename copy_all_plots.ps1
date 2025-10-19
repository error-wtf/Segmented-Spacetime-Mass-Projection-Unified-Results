# Copy all plots to h:\WINDSURF\plots
# Sammelt alle Plot-Dateien aus der Pipeline

$ErrorActionPreference = "Stop"

$source_base = "h:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00"
$target_dir = "h:\WINDSURF\plots"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SSZ Plot Collection - Alle Plots kopieren" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Ziel-Ordner erstellen
if (-not (Test-Path $target_dir)) {
    New-Item -ItemType Directory -Path $target_dir -Force | Out-Null
    Write-Host "[CREATED] $target_dir" -ForegroundColor Green
} else {
    Write-Host "[EXISTS]  $target_dir" -ForegroundColor Yellow
}

# Plot-Quellen definieren
$plot_sources = @(
    "reports\figures",
    "agent_out\figures",
    "out",
    "vfall_out",
    "full_pipeline\figures",
    "final_reports\figures"
)

# Plot-Extensions
$plot_extensions = @("*.png", "*.svg", "*.pdf", "*.jpg", "*.jpeg")

$total_copied = 0
$total_skipped = 0

Write-Host ""
Write-Host "Scanning sources..." -ForegroundColor Yellow
Write-Host ""

foreach ($source in $plot_sources) {
    $source_path = Join-Path $source_base $source
    
    if (-not (Test-Path $source_path)) {
        Write-Host "  [SKIP] $source (nicht vorhanden)" -ForegroundColor Gray
        continue
    }
    
    Write-Host "  [SCAN] $source" -ForegroundColor Cyan
    
    foreach ($ext in $plot_extensions) {
        $files = Get-ChildItem -Path $source_path -Filter $ext -Recurse -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            # Relativer Pfad vom source_path
            $rel_path = $file.FullName.Substring($source_path.Length + 1)
            
            # Ziel-Pfad (flache Struktur mit Präfix)
            $prefix = $source -replace '\\', '_' -replace '/', '_'
            $target_name = "${prefix}_${rel_path}" -replace '\\', '_' -replace '/', '_'
            $target_file = Join-Path $target_dir $target_name
            
            try {
                Copy-Item -Path $file.FullName -Destination $target_file -Force
                Write-Host "    [COPY] $($file.Name) -> $target_name" -ForegroundColor Green
                $total_copied++
            } catch {
                Write-Host "    [FAIL] $($file.Name): $_" -ForegroundColor Red
                $total_skipped++
            }
        }
    }
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "Fertig!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Kopiert:    $total_copied Dateien" -ForegroundColor Green
Write-Host "  Übersprungen: $total_skipped Dateien" -ForegroundColor Yellow
Write-Host "  Ziel:       $target_dir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Öffne Ordner:" -ForegroundColor Yellow
Write-Host "  explorer `"$target_dir`"" -ForegroundColor Gray
Write-Host ""
