# Safe Commit Script
# Verhindert versehentliches Committen von Cache/Temp-Dateien

param(
    [string]$Message = ""
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Safe Commit - Mit automatischen Checks" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob wir in einem Git-Repository sind
if (-not (Test-Path ".git")) {
    Write-Host "[ERROR] Kein Git-Repository gefunden!" -ForegroundColor Red
    exit 1
}

# SCHRITT 1: Cache löschen
Write-Host "[1/5] Cache löschen..." -ForegroundColor Yellow
if (Test-Path "CLEAR_CACHE.bat") {
    & .\CLEAR_CACHE.bat | Out-Null
    Write-Host "  ✓ Cache gelöscht" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] CLEAR_CACHE.bat nicht gefunden - überspringe" -ForegroundColor Yellow
}
Write-Host ""

# SCHRITT 2: Git Status
Write-Host "[2/5] Git Status:" -ForegroundColor Yellow
$status = git status --short
if ($status) {
    $status | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "  [INFO] Keine Änderungen." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Repository ist bereits synchronisiert!" -ForegroundColor Green
    exit 0
}
Write-Host ""

# SCHRITT 3: Zeige was committed werden würde
Write-Host "[3/5] Dateien zum Committen:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Welche Dateien sollen committed werden?" -ForegroundColor Cyan
Write-Host "  1) Alle Source-Dateien (*.py, *.md, *.txt - EMPFOHLEN)" -ForegroundColor Green
Write-Host "  2) Spezifische Dateien (manuell auswählen)" -ForegroundColor Yellow
Write-Host "  3) Alles (GEFÄHRLICH - nicht empfohlen!)" -ForegroundColor Red
Write-Host "  4) Abbrechen" -ForegroundColor Gray
Write-Host ""
$choice = Read-Host "Auswahl (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "  Stage nur Source-Dateien..." -ForegroundColor Yellow
        
        # Nur sichere Dateitypen
        $safe_patterns = @(
            "*.py",
            "*.md",
            "*.txt",
            "*.sh",
            "*.ps1",
            "*.bat",
            "*.json",
            "*.yaml",
            "*.yml",
            "*.toml",
            "*.ini",
            "*.cfg"
        )
        
        foreach ($pattern in $safe_patterns) {
            git add $pattern 2>$null
        }
        
        Write-Host "  ✓ Source-Dateien gestaged" -ForegroundColor Green
    }
    
    "2" {
        Write-Host ""
        Write-Host "  Gib Dateipfade ein (getrennt durch Leerzeichen):" -ForegroundColor Yellow
        $files = Read-Host "  Dateien"
        
        if ($files) {
            git add $files.Split(" ")
            Write-Host "  ✓ Dateien gestaged" -ForegroundColor Green
        } else {
            Write-Host "  [ERROR] Keine Dateien angegeben!" -ForegroundColor Red
            exit 1
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "  ⚠️  WARNUNG: Du stagst ALLES!" -ForegroundColor Red
        Write-Host "  Das kann Cache/Temp-Dateien enthalten!" -ForegroundColor Yellow
        Write-Host ""
        $confirm = Read-Host "  Wirklich fortfahren? (yes/NO)"
        
        if ($confirm -eq "yes") {
            git add -A
            Write-Host "  ✓ Alle Dateien gestaged" -ForegroundColor Yellow
        } else {
            Write-Host "  Abgebrochen." -ForegroundColor Gray
            exit 0
        }
    }
    
    "4" {
        Write-Host ""
        Write-Host "Abgebrochen." -ForegroundColor Gray
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "[ERROR] Ungültige Auswahl!" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# SCHRITT 4: Pre-Commit Check
Write-Host "[4/5] Pre-Commit Check..." -ForegroundColor Yellow
if (Test-Path "check_before_commit.ps1") {
    & .\check_before_commit.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Pre-Commit Check fehlgeschlagen!" -ForegroundColor Red
        Write-Host "Commit abgebrochen." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "  [WARNING] check_before_commit.ps1 nicht gefunden - überspringe" -ForegroundColor Yellow
}
Write-Host ""

# SCHRITT 5: Commit
Write-Host "[5/5] Commit erstellen..." -ForegroundColor Yellow

if (-not $Message) {
    Write-Host ""
    Write-Host "Commit Message:" -ForegroundColor Cyan
    $Message = Read-Host "  Message"
    
    if (-not $Message) {
        Write-Host ""
        Write-Host "[ERROR] Keine Commit-Message angegeben!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Gestagte Dateien:" -ForegroundColor Gray
git diff --cached --name-only | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
Write-Host ""
Write-Host "Commit Message: $Message" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Commit erstellen? (y/n)"

if ($confirm -eq "y") {
    git commit -m $Message
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host "✓ Commit erfolgreich erstellt!" -ForegroundColor Green
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Nächste Schritte:" -ForegroundColor Cyan
        Write-Host "  1. Pushen: git push origin main" -ForegroundColor Green
        Write-Host "  2. Oder mit sync_to_main.ps1" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "[ERROR] Commit fehlgeschlagen!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "Commit abgebrochen." -ForegroundColor Yellow
    Write-Host "Dateien bleiben gestaged. Unstagen mit: git reset HEAD" -ForegroundColor Gray
    Write-Host ""
}
