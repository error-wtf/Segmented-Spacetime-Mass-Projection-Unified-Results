# Check Progress of Final Validation Run
# © 2025 Carmen Wrede & Lino Casu

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "FINAL VALIDATION RUN - PROGRESS CHECK" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Check if Python is running
$pythonProc = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProc) {
    Write-Host "✅ Pipeline is RUNNING" -ForegroundColor Green
    Write-Host "   Process ID: $($pythonProc.Id)" -ForegroundColor White
    Write-Host "   CPU Time: $($pythonProc.CPU)" -ForegroundColor White
    Write-Host "   Memory: $([math]::Round($pythonProc.WorkingSet64/1MB, 2)) MB" -ForegroundColor White
} else {
    Write-Host "⚠️  No Python process found - Pipeline may be finished or not started" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "RECENTLY MODIFIED FILES (Last 10 minutes)" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan

$recent = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-10) } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 20 |
    Select-Object Name, @{Name="Size (KB)";Expression={[math]::Round($_.Length/1KB, 2)}}, LastWriteTime

if ($recent) {
    $recent | Format-Table -AutoSize
} else {
    Write-Host "No files modified in last 10 minutes" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "OUTPUT DIRECTORIES STATUS" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan

$dirs = @("reports", "outputs", "validation_complete_extended", "validation_out_v2", 
          "outputs_propertime", "outputs_shapiro_proxy")

foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        $count = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
        $size = [math]::Round((Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | 
                               Measure-Object -Property Length -Sum).Sum / 1MB, 2)
        Write-Host "✅ $dir" -ForegroundColor Green
        Write-Host "   Files: $count | Size: $size MB" -ForegroundColor White
    } else {
        Write-Host "⚠️  $dir - NOT FOUND" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "ESTIMATED TIME REMAINING" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan

# Read start time from FINAL_RUN_PLAN.md if exists
$planFile = "FINAL_RUN_PLAN.md"
if (Test-Path $planFile) {
    $content = Get-Content $planFile -Raw
    if ($content -match 'Started:\*\* (\d{4}-\d{2}-\d{2} \d{2}:\d{2})') {
        $startTime = [DateTime]::ParseExact($matches[1], "yyyy-MM-dd HH:mm", $null)
        $elapsed = (Get-Date) - $startTime
        $remaining = [TimeSpan]::FromMinutes(90) - $elapsed
        
        Write-Host "Start Time: $($startTime.ToString('HH:mm'))" -ForegroundColor White
        Write-Host "Elapsed: $([math]::Round($elapsed.TotalMinutes, 1)) minutes" -ForegroundColor White
        
        if ($remaining.TotalMinutes -gt 0) {
            Write-Host "Remaining: ~$([math]::Round($remaining.TotalMinutes, 0)) minutes" -ForegroundColor Yellow
            $eta = (Get-Date).Add($remaining)
            Write-Host "Estimated Finish: $($eta.ToString('HH:mm'))" -ForegroundColor Cyan
        } else {
            Write-Host "Should be finished! Check if pipeline completed." -ForegroundColor Green
        }
    }
} else {
    Write-Host "⚠️  FINAL_RUN_PLAN.md not found - cannot estimate time" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "To check again, run: .\check_progress.ps1" -ForegroundColor White
Write-Host "="*80 -ForegroundColor Cyan
