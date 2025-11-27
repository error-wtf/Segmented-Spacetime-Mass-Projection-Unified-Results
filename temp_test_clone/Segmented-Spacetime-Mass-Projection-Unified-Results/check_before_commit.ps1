# Pre-Commit Safety Check
# Prüft ob Cache-Dateien versehentlich gestaged wurden

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Pre-Commit Safety Check" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob wir in einem Git-Repository sind
if (-not (Test-Path ".git")) {
    Write-Host "[ERROR] Kein Git-Repository gefunden!" -ForegroundColor Red
    exit 1
}

# Liste der Dateien die NICHT committed werden sollten
$forbidden_patterns = @(
    "__pycache__",
    ".pytest_cache",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "summary-output.md",
    "*.log"
)

Write-Host "[1/3] Prüfe gestagte Dateien..." -ForegroundColor Yellow
$staged_files = git diff --cached --name-only

if (-not $staged_files) {
    Write-Host "  [INFO] Keine Dateien gestaged." -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

Write-Host "  Gestagte Dateien:" -ForegroundColor Gray
$staged_files | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
Write-Host ""

# Prüfe auf verbotene Dateien
Write-Host "[2/3] Prüfe auf Cache/Temp-Dateien..." -ForegroundColor Yellow
$found_forbidden = $false

foreach ($pattern in $forbidden_patterns) {
    $matches = $staged_files | Where-Object { $_ -like "*$pattern*" }
    if ($matches) {
        $found_forbidden = $true
        Write-Host "  ⚠️  WARNUNG: Cache/Temp-Dateien gefunden!" -ForegroundColor Red
        Write-Host "    Pattern: $pattern" -ForegroundColor Yellow
        $matches | ForEach-Object { Write-Host "      $_" -ForegroundColor Red }
        Write-Host ""
    }
}

if ($found_forbidden) {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host "❌ COMMIT BLOCKIERT!" -ForegroundColor Red
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Du versuchst Cache/Temp-Dateien zu committen!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Diese Dateien sollten NICHT ins Repository:" -ForegroundColor Yellow
    Write-Host "  - __pycache__/ (Python Bytecode)" -ForegroundColor Gray
    Write-Host "  - .pytest_cache/ (Test Cache)" -ForegroundColor Gray
    Write-Host "  - *.pyc, *.pyo (Kompilierte Dateien)" -ForegroundColor Gray
    Write-Host "  - summary-output.md (Temporäre Logs)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Lösung:" -ForegroundColor Cyan
    Write-Host "  1. Cache löschen: .\CLEAR_CACHE.bat" -ForegroundColor Green
    Write-Host "  2. Dateien unstagen: git reset HEAD <datei>" -ForegroundColor Green
    Write-Host "  3. Nur Source-Dateien stagen: git add <spezifische-datei>" -ForegroundColor Green
    Write-Host ""
    Write-Host "Oder .gitignore prüfen!" -ForegroundColor Yellow
    Write-Host ""
    
    $force = Read-Host "Trotzdem committen? (yes/NO)"
    if ($force -ne "yes") {
        Write-Host ""
        Write-Host "Commit abgebrochen." -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
}

Write-Host "[3/3] Syntax-Check für Python-Dateien..." -ForegroundColor Yellow
$python_files = $staged_files | Where-Object { $_ -like "*.py" }

if ($python_files) {
    $syntax_errors = $false
    foreach ($file in $python_files) {
        if (Test-Path $file) {
            $result = python -m py_compile $file 2>&1
            if ($LASTEXITCODE -ne 0) {
                $syntax_errors = $true
                Write-Host "  ❌ Syntax-Fehler: $file" -ForegroundColor Red
                Write-Host "    $result" -ForegroundColor Gray
            } else {
                Write-Host "  ✓ $file" -ForegroundColor Green
            }
        }
    }
    
    if ($syntax_errors) {
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Red
        Write-Host "❌ COMMIT BLOCKIERT - Syntax-Fehler!" -ForegroundColor Red
        Write-Host "================================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Bitte Syntax-Fehler beheben vor dem Commit!" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
} else {
    Write-Host "  [INFO] Keine Python-Dateien zu prüfen." -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "✓ Alle Checks bestanden!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Bereit zum Committen." -ForegroundColor Cyan
Write-Host ""
