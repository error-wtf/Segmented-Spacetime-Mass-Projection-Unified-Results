# Cleanup Script für SSZ Projekt (Windows PowerShell)
# © 2025 Carmen Wrede & Lino Casu

Write-Host "🧹 SSZ Project Cleanup" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# 1. Clean Python cache
Write-Host "`n[1/3] Cleaning Python cache..." -ForegroundColor Yellow
$cacheItems = Get-ChildItem -Path . -Include __pycache__,.pytest_cache -Recurse -Force -ErrorAction SilentlyContinue
$pycFiles = Get-ChildItem -Path . -Include *.pyc,*.pyo -Recurse -Force -ErrorAction SilentlyContinue

if ($cacheItems -or $pycFiles) {
    $cacheItems | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $pycFiles | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Cache cleaned" -ForegroundColor Green
} else {
    Write-Host "  ✓ No cache found" -ForegroundColor Green
}

# 2. Check for syntax errors
Write-Host "`n[2/3] Checking for syntax errors..." -ForegroundColor Yellow
$errors = 0
$files = Get-ChildItem -Path tests,scripts\tests -Filter *.py -Recurse -ErrorAction SilentlyContinue

foreach ($file in $files) {
    $result = python -m py_compile $file.FullName 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $($file.Name)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($file.Name): $result" -ForegroundColor Red
        $errors++
    }
}

if ($errors -eq 0) {
    Write-Host "  ✓ All files passed syntax check" -ForegroundColor Green
} else {
    Write-Host "  ✗ $errors files have syntax errors" -ForegroundColor Red
}

# 3. Summary
Write-Host "`n[3/3] Summary" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  Cache: Cleaned" -ForegroundColor Green
Write-Host "  Syntax: $($files.Count - $errors)/$($files.Count) files OK" -ForegroundColor $(if ($errors -eq 0) { "Green" } else { "Yellow" })

if ($errors -eq 0) {
    Write-Host "`n✅ Cleanup complete - Ready for testing!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Cleanup complete - Fix syntax errors before testing" -ForegroundColor Yellow
}

Write-Host "=" * 60 -ForegroundColor Cyan
