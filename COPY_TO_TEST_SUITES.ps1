#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Copy SSZ Suite to Test Suite directories
    
.DESCRIPTION
    Copies the complete project to:
    - H:\WINDSURF\Segmented-Spacetime-TEST-SUITE-Linux
    - H:\WINDSURF\Segmented-Spacetime-TEST-SUITE-Windows
    
    Excludes: .git, __pycache__, .venv, build directories
    
.NOTES
    Run from project root directory
#>

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "SSZ SUITE - COPY TO TEST SUITE DIRECTORIES" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""

# Source directory (current directory)
$SourceDir = Get-Location

# Target directories
$TargetLinux = "H:\WINDSURF\Segmented-Spacetime-TEST-SUITE-Linux"
$TargetWindows = "H:\WINDSURF\Segmented-Spacetime-TEST-SUITE-Windows"

Write-Host "Source: $SourceDir" -ForegroundColor Cyan
Write-Host "Target 1: $TargetLinux" -ForegroundColor Cyan
Write-Host "Target 2: $TargetWindows" -ForegroundColor Cyan
Write-Host ""

# Exclusions
$ExcludeDirs = @(
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "build",
    ".pybuild",
    "debian",
    "*.egg-info",
    "dist",
    ".mypy_cache",
    ".tox",
    "node_modules"
)

$ExcludeFiles = @(
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "Thumbs.db",
    "*.log"
)

Write-Host "[1/3] Preparing..." -ForegroundColor Yellow

# Build exclude pattern for robocopy
$ExcludeDirsStr = $ExcludeDirs -join " "
$ExcludeFilesStr = $ExcludeFiles -join " "

# Create target directories
Write-Host "[2/3] Creating target directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $TargetLinux | Out-Null
New-Item -ItemType Directory -Force -Path $TargetWindows | Out-Null
Write-Host "  ✓ Directories created" -ForegroundColor Green

# Copy to Linux directory
Write-Host ""
Write-Host "[3/3] Copying files..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  → Copying to TEST-SUITE-Linux..." -ForegroundColor Cyan

robocopy $SourceDir $TargetLinux /E /NP /NDL /NFL /XD $ExcludeDirs /XF $ExcludeFiles /R:1 /W:1

if ($LASTEXITCODE -le 7) {
    Write-Host "  ✓ Linux copy complete" -ForegroundColor Green
} else {
    Write-Host "  ✗ Linux copy failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
}

Write-Host ""
Write-Host "  → Copying to TEST-SUITE-Windows..." -ForegroundColor Cyan

robocopy $SourceDir $TargetWindows /E /NP /NDL /NFL /XD $ExcludeDirs /XF $ExcludeFiles /R:1 /W:1

if ($LASTEXITCODE -le 7) {
    Write-Host "  ✓ Windows copy complete" -ForegroundColor Green
} else {
    Write-Host "  ✗ Windows copy failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "COPY COMPLETE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""

# Get directory sizes
$LinuxSize = (Get-ChildItem -Path $TargetLinux -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
$WindowsSize = (Get-ChildItem -Path $TargetWindows -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "Directory Sizes:" -ForegroundColor Yellow
Write-Host "  Linux:   $($LinuxSize.ToString('N2')) MB" -ForegroundColor Cyan
Write-Host "  Windows: $($WindowsSize.ToString('N2')) MB" -ForegroundColor Cyan
Write-Host ""

# Get file counts
$LinuxFiles = (Get-ChildItem -Path $TargetLinux -Recurse -File).Count
$WindowsFiles = (Get-ChildItem -Path $TargetWindows -Recurse -File).Count

Write-Host "File Counts:" -ForegroundColor Yellow
Write-Host "  Linux:   $LinuxFiles files" -ForegroundColor Cyan
Write-Host "  Windows: $WindowsFiles files" -ForegroundColor Cyan
Write-Host ""

Write-Host "Test Suites Ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Linux Suite:   cd $TargetLinux" -ForegroundColor White
Write-Host "                    ./install.sh" -ForegroundColor White
Write-Host ""
Write-Host "  2. Windows Suite: cd $TargetWindows" -ForegroundColor White
Write-Host "                    .\install.ps1" -ForegroundColor White
Write-Host ""

# Pause at end
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
