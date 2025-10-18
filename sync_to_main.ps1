# Sync Project to Main Branch
# Synchronisiert alle Änderungen zum main branch (ohne große Dateien)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Git Sync to Main Branch" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob wir in einem Git-Repository sind
if (-not (Test-Path ".git")) {
    Write-Host "[ERROR] Kein Git-Repository gefunden!" -ForegroundColor Red
    Write-Host "Bitte erst 'git init' ausführen oder in Repository-Root wechseln." -ForegroundColor Yellow
    exit 1
}

# Git Status anzeigen
Write-Host "[1/6] Git Status:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Prüfe Branch
$current_branch = git rev-parse --abbrev-ref HEAD
Write-Host "[INFO] Aktueller Branch: $current_branch" -ForegroundColor Cyan

if ($current_branch -ne "main" -and $current_branch -ne "master") {
    Write-Host "[WARNING] Nicht auf main/master Branch!" -ForegroundColor Yellow
    $switch = Read-Host "Zu main branch wechseln? (y/n)"
    if ($switch -eq "y") {
        Write-Host "[2/6] Wechsle zu main branch..." -ForegroundColor Yellow
        git checkout main 2>$null
        if ($LASTEXITCODE -ne 0) {
            git checkout -b main
        }
    }
}

# Zeige was ignoriert wird
Write-Host ""
Write-Host "[INFO] .gitignore prüfen..." -ForegroundColor Cyan
Write-Host "  Große Dateien (werden NICHT committed):" -ForegroundColor Gray
Write-Host "    - data/planck/*.txt (Planck-Daten, ~2 GB)" -ForegroundColor Gray
Write-Host "    - __pycache__/ (Python Cache)" -ForegroundColor Gray
Write-Host "    - .pytest_cache/ (Test Cache)" -ForegroundColor Gray
Write-Host "    - reports/*.log (Log-Dateien)" -ForegroundColor Gray
Write-Host ""

# Stage alle Änderungen (respektiert .gitignore)
Write-Host "[3/6] Stage alle Änderungen..." -ForegroundColor Yellow
git add -A
Write-Host "  ✓ Alle Dateien staged (außer .gitignore Einträge)" -ForegroundColor Green
Write-Host ""

# Zeige was gestaged wurde
Write-Host "[4/6] Gestagte Änderungen:" -ForegroundColor Yellow
$staged = git diff --cached --stat
if ($staged) {
    Write-Host $staged -ForegroundColor Gray
} else {
    Write-Host "  [INFO] Keine Änderungen zu committen." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Repository ist bereits synchronisiert!" -ForegroundColor Green
    exit 0
}
Write-Host ""

# Commit Message
$default_msg = "Update: Pipeline fixes, Add-ons, SI units ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
Write-Host "[5/6] Commit Message:" -ForegroundColor Yellow
Write-Host "  Default: $default_msg" -ForegroundColor Gray
$custom_msg = Read-Host "  Custom message (oder Enter für Default)"

if ($custom_msg) {
    $commit_msg = $custom_msg
} else {
    $commit_msg = $default_msg
}

git commit -m $commit_msg
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Commit fehlgeschlagen!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Commit erstellt" -ForegroundColor Green
Write-Host ""

# Push zu Remote
Write-Host "[6/6] Push zu main branch..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Bereit zum Pushen?" -ForegroundColor Yellow
Write-Host "  Branch: main" -ForegroundColor Gray
Write-Host "  Commit: $commit_msg" -ForegroundColor Gray
Write-Host ""
$confirm = Read-Host "Jetzt pushen? (y/n)"

if ($confirm -eq "y") {
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host "✓ Erfolgreich zu main branch gepusht!" -ForegroundColor Green
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Repository-Status:" -ForegroundColor Cyan
        git log -1 --oneline
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "[ERROR] Push fehlgeschlagen!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Mögliche Ursachen:" -ForegroundColor Yellow
        Write-Host "  - Remote nicht konfiguriert: git remote add origin <URL>" -ForegroundColor Gray
        Write-Host "  - Keine Push-Rechte" -ForegroundColor Gray
        Write-Host "  - Branch muss gemergt werden: git pull --rebase" -ForegroundColor Gray
        Write-Host ""
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "[INFO] Push abgebrochen." -ForegroundColor Yellow
    Write-Host "Später manuell pushen mit: git push origin main" -ForegroundColor Gray
    Write-Host ""
}
