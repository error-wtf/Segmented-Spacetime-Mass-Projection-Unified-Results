# SSZ Projection Suite - Windows Installation Script
# 
# Copyright © 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# Usage:
#   .\install.ps1              # Full install
#   .\install.ps1 -SkipTests   # Skip test suite
#   .\install.ps1 -DevMode     # Install in editable mode
#   .\install.ps1 -RunFullSuite # Run full test suite
#   .\install.ps1 -QuickSuite  # Run quick test suite

param(
    [switch]$SkipTests,
    [switch]$DevMode,
    [switch]$DryRun,
    [switch]$RunFullSuite,
    [switch]$QuickSuite
)

$ErrorActionPreference = "Stop"

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "SSZ PROJECTION SUITE - WINDOWS INSTALLER" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
    
    # Check version >= 3.8
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "  ERROR: Python 3.8+ required (found $major.$minor)" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "  ERROR: Python not found. Install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Step 2: Create virtual environment
Write-Host ""
Write-Host "[2/8] Setting up virtual environment..." -ForegroundColor Yellow
$venvPath = ".venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
$linuxActivate = Join-Path $venvPath "bin\activate"

# Check if venv exists and is compatible with Windows
if (Test-Path $venvPath) {
    if (Test-Path $activateScript) {
        Write-Host "  Virtual environment already exists (Windows-compatible)" -ForegroundColor Green
    } elseif (Test-Path $linuxActivate) {
        Write-Host "  WARNING: Existing .venv is Linux/WSL-only (bin/activate)" -ForegroundColor Yellow
        Write-Host "  Removing incompatible venv and recreating for Windows..." -ForegroundColor Yellow
        if (-not $DryRun) {
            Remove-Item -Recurse -Force $venvPath
            python -m venv $venvPath
            Write-Host "  Created new Windows-compatible venv: $venvPath" -ForegroundColor Green
        } else {
            Write-Host "  [DRY-RUN] Would remove and recreate: $venvPath" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  WARNING: .venv exists but is corrupted" -ForegroundColor Yellow
        Write-Host "  Removing and recreating..." -ForegroundColor Yellow
        if (-not $DryRun) {
            Remove-Item -Recurse -Force $venvPath
            python -m venv $venvPath
            Write-Host "  Created: $venvPath" -ForegroundColor Green
        } else {
            Write-Host "  [DRY-RUN] Would remove and recreate: $venvPath" -ForegroundColor Cyan
        }
    }
} else {
    if (-not $DryRun) {
        python -m venv $venvPath
        Write-Host "  Created: $venvPath" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would create: $venvPath" -ForegroundColor Cyan
    }
}

# Step 3: Activate venv and upgrade pip
Write-Host ""
Write-Host "[3/8] Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path $activateScript) {
    if (-not $DryRun) {
        & $activateScript
        Write-Host "  Activated: $venvPath" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would activate: $venvPath" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ERROR: Activation script not found at: $activateScript" -ForegroundColor Red
    Write-Host "  This should not happen. Venv creation may have failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/8] Upgrading pip, setuptools, wheel..." -ForegroundColor Yellow
if (-not $DryRun) {
    python -m pip install --upgrade pip setuptools wheel | Out-Null
    Write-Host "  Upgraded core packages" -ForegroundColor Green
} else {
    Write-Host "  [DRY-RUN] Would upgrade: pip, setuptools, wheel" -ForegroundColor Cyan
}

# Step 4: Install dependencies
Write-Host ""
Write-Host "[5/8] Installing dependencies..." -ForegroundColor Yellow

# Check for requirements.txt or pyproject.toml
if (Test-Path "requirements.txt") {
    Write-Host "  Found: requirements.txt" -ForegroundColor Cyan
    if (-not $DryRun) {
        python -m pip install -r requirements.txt
        Write-Host "  Installed from requirements.txt" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would install from requirements.txt" -ForegroundColor Cyan
    }
} elseif (Test-Path "pyproject.toml") {
    Write-Host "  Found: pyproject.toml" -ForegroundColor Cyan
    if (-not $DryRun) {
        # Install common scientific packages
        python -m pip install numpy scipy pandas matplotlib astropy pyyaml
        Write-Host "  Installed core scientific packages" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would install core packages" -ForegroundColor Cyan
    }
} else {
    Write-Host "  WARNING: No requirements.txt or pyproject.toml found" -ForegroundColor Yellow
}

# Step 5: Install package
Write-Host ""
Write-Host "[6/8] Installing SSZ Suite package..." -ForegroundColor Yellow
if ($DevMode) {
    Write-Host "  Mode: Editable (development)" -ForegroundColor Cyan
    if (-not $DryRun) {
        python -m pip install -e .
        Write-Host "  Installed in editable mode" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would install: pip install -e ." -ForegroundColor Cyan
    }
} else {
    Write-Host "  Mode: Standard" -ForegroundColor Cyan
    if (-not $DryRun) {
        python -m pip install .
        Write-Host "  Installed package" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would install: pip install ." -ForegroundColor Cyan
    }
}

# Step 6: Run tests
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "[7/8] Running test suite..." -ForegroundColor Yellow
    if (-not $DryRun) {
        try {
            # Run ALL tests with full output
            Write-Host "  Running ALL tests (root + tests/ + scripts/tests/)..." -ForegroundColor Cyan
            Write-Host ""
            
            # Collect all test files
            $allTests = @()
            
            # Root-level tests
            $rootTests = @(
                "test_vfall_duality.py",
                "test_ppn_exact.py", 
                "test_energy_conditions.py",
                "test_c1_segments.py",
                "test_c2_segments_strict.py",
                "test_c2_curvature_proxy.py",
                "test_utf8_encoding.py"
            )
            foreach ($test in $rootTests) {
                if (Test-Path $test) {
                    $allTests += $test
                }
            }
            
            # tests/ directory
            $allTests += "tests/"
            
            # scripts/tests/ directory
            if (Test-Path "scripts/tests") {
                $allTests += "scripts/tests/"
            }
            
            # Run all tests together with full output
            pytest $allTests -v --tb=short --disable-warnings
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "  ✓ All tests passed" -ForegroundColor Green
            } else {
                Write-Host ""
                Write-Host "  ✗ Some tests FAILED - Fix before continuing!" -ForegroundColor Red
                exit 1
            }
        } catch {
            Write-Host "  ✗ ERROR: pytest not installed or tests failed" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  [DRY-RUN] Would run: All tests (root, tests/, scripts/tests/)" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "[7/8] Skipping tests (--SkipTests flag)" -ForegroundColor Yellow
}

# Step 8: Verify installation
Write-Host ""
Write-Host "[8/8] Verifying installation..." -ForegroundColor Yellow
if (-not $DryRun) {
    # Check CLI commands
    try {
        $commands = @("ssz-rings --help", "ssz-print-md --help")
        foreach ($cmd in $commands) {
            $cmdName = $cmd.Split()[0]
            Write-Host "  Checking: $cmdName" -ForegroundColor Cyan
            Invoke-Expression $cmd | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "    [OK] $cmdName" -ForegroundColor Green
            } else {
                Write-Host "    [WARN] $cmdName not available" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "  WARNING: Some commands not available" -ForegroundColor Yellow
    }
    
    # Check bundled papers
    Write-Host "  Checking bundled papers..." -ForegroundColor Cyan
    $papersValidation = "papers\validation"
    $papersTheory = "docs\theory"
    
    if (Test-Path $papersValidation) {
        $validationCount = (Get-ChildItem $papersValidation -Filter *.md).Count
        Write-Host "    [OK] Validation papers: $validationCount files" -ForegroundColor Green
    } else {
        Write-Host "    [WARN] Validation papers directory not found" -ForegroundColor Yellow
    }
    
    if (Test-Path $papersTheory) {
        $theoryCount = (Get-ChildItem $papersTheory -Filter *.md).Count
        Write-Host "    [OK] Theory papers: $theoryCount files" -ForegroundColor Green
    } else {
        Write-Host "    [WARN] Theory papers directory not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [DRY-RUN] Would verify commands and papers" -ForegroundColor Cyan
}

# Summary
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Yellow
Write-Host "  1. Activate venv: .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Run example:   ssz-rings --csv data/observations/G79_29+0_46_CO_NH3_rings.csv --v0 12.5 --fit-alpha" -ForegroundColor White
Write-Host "  3. Print all MD:  ssz-print-md --root . --order path" -ForegroundColor White
Write-Host "  4. View docs:     Get-Content docs\segwave_guide.md" -ForegroundColor White
Write-Host ""
Write-Host "Resources:" -ForegroundColor Yellow
Write-Host "  - Validation Papers: papers\validation\ (10 files, ~593 KB)" -ForegroundColor Cyan
Write-Host "  - Theory Papers:     docs\theory\ (20 files, ~380 KB)" -ForegroundColor Cyan
Write-Host "  - License:           ANTI-CAPITALIST SOFTWARE LICENSE v1.4" -ForegroundColor Cyan
Write-Host ""

# Optional: Run Full Test Suite
if ($RunFullSuite -or $QuickSuite) {
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 98) -ForegroundColor Cyan
    if ($QuickSuite) {
        Write-Host "RUNNING QUICK TEST SUITE" -ForegroundColor Yellow
    } else {
        Write-Host "RUNNING FULL TEST SUITE" -ForegroundColor Yellow
    }
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * 98) -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path "run_full_suite.py") {
        $suiteArgs = if ($QuickSuite) { "--quick" } else { "" }
        Write-Host "  Executing: python run_full_suite.py $suiteArgs" -ForegroundColor Cyan
        
        try {
            & python run_full_suite.py $suiteArgs
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "  [SUCCESS] All tests passed!" -ForegroundColor Green
            } else {
                Write-Host ""
                Write-Host "  [WARNING] Some tests failed (see output above)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  [ERROR] Test suite execution failed: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  [SKIP] run_full_suite.py not found" -ForegroundColor Yellow
    }
    Write-Host ""
}
