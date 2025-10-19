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
        # Install all critical dependencies
        python -m pip install numpy scipy pandas matplotlib astropy astroquery pyyaml pytest pytest-timeout pyarrow colorama
        Write-Host "  Installed core scientific + testing packages" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would install core packages" -ForegroundColor Cyan
    }
} else {
    Write-Host "  WARNING: No requirements.txt or pyproject.toml found" -ForegroundColor Yellow
}

# Step 6: Check and fetch missing data files (BEFORE tests)
Write-Host ""
Write-Host "[6/10] Checking and fetching data files..." -ForegroundColor Yellow

if (-not $DryRun) {
    $dataFetched = $false
    
    # Check for real_data_full.csv (should be in release)
    if (-not (Test-Path "data/real_data_full.csv")) {
        Write-Host "  ⚠ real_data_full.csv missing - should be included in release!" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ real_data_full.csv found" -ForegroundColor Green
    }
    
    # Check for small GAIA CSV (should be in release)
    $gaiaSmallFile = "data/gaia/gaia_sample_small.csv"
    
    if (-not (Test-Path $gaiaSmallFile)) {
        Write-Host "  ⚠ $gaiaSmallFile missing - should be in release!" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ GAIA sample data found" -ForegroundColor Green
    }
    
    # Optional cone files (generated on demand, not required)
    $gaiaConeFiles = @(
        "data/gaia/gaia_cone_g79.csv",
        "data/gaia/gaia_cone_cygx.csv"
    )
    
    foreach ($file in $gaiaConeFiles) {
        if (Test-Path $file) {
            Write-Host "  ✓ Optional: $file found" -ForegroundColor Green
        }
    }
    
    # Check for Planck data (2GB - fetch only if missing)
    $planckFile = "data/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt"
    
    if (-not (Test-Path $planckFile)) {
        Write-Host "  ⚠ Planck data missing (2GB) - fetching..." -ForegroundColor Yellow
        
        # Create directory
        New-Item -ItemType Directory -Force -Path "data/planck" | Out-Null
        
        try {
            Write-Host "    Downloading Planck CMB power spectrum..." -ForegroundColor Cyan
            Write-Host "    This may take several minutes (2GB file)..." -ForegroundColor Cyan
            
            # Run fetch script
            python scripts/fetch_planck.py
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✓ Planck data fetched successfully" -ForegroundColor Green
                $dataFetched = $true
            } else {
                Write-Host "  ⚠ Failed to fetch Planck data - continuing anyway" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  ⚠ Error fetching Planck data: $_" -ForegroundColor Yellow
            Write-Host "    You can fetch manually later with: python scripts/fetch_planck.py" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  ✓ Planck data found (skipping download)" -ForegroundColor Green
    }
    
    # Check for additional GAIA data (fetch if missing)
    $gaiaLargeFile = "data/gaia/gaia_full_sample.csv"
    
    if (-not (Test-Path $gaiaLargeFile)) {
        Write-Host "  ⚠ Full GAIA sample missing - you can fetch with:" -ForegroundColor Yellow
        Write-Host "    python scripts/fetch_gaia_full.py" -ForegroundColor Cyan
    } else {
        Write-Host "  ✓ Full GAIA sample found" -ForegroundColor Green
    }
    
    Write-Host ""
    if ($dataFetched) {
        Write-Host "  Note: Data files downloaded. They will NOT be overwritten on reinstall." -ForegroundColor Cyan
    }
} else {
    Write-Host "  [DRY-RUN] Would check and fetch: data files" -ForegroundColor Cyan
}

# Step 7: Install package
Write-Host ""
Write-Host "[7/10] Installing SSZ Suite package..." -ForegroundColor Yellow
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

# Step 8: Run tests
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "[8/10] Running test suite..." -ForegroundColor Yellow
    if (-not $DryRun) {
        try {
            # Run ALL tests with full output
            Write-Host "  Running ALL tests (root + tests/ + scripts/tests/)..." -ForegroundColor Cyan
            Write-Host ""
            
            $allPassed = $true
            
            # Root-level tests (run as Python scripts, not pytest)
            Write-Host "Root-level SSZ tests:" -ForegroundColor Cyan
            $rootTests = @(
                "test_ppn_exact.py",
                "test_vfall_duality.py", 
                "test_energy_conditions.py",
                "test_c1_segments.py",
                "test_c2_segments_strict.py",
                "test_c2_curvature_proxy.py",
                "test_utf8_encoding.py"
            )
            foreach ($test in $rootTests) {
                if (Test-Path $test) {
                    Write-Host "  $test" -NoNewline
                    python $test > $null 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host " PASSED" -ForegroundColor Green
                    } else {
                        Write-Host " FAILED" -ForegroundColor Red
                        $allPassed = $false
                    }
                }
            }
            Write-Host ""
            
            # pytest tests (tests/ and scripts/tests/)
            Write-Host "Pytest test suites:" -ForegroundColor Cyan
            pytest tests/ scripts/tests/ -s -v --tb=short
            
            if ($LASTEXITCODE -ne 0) {
                $allPassed = $false
            }
            
            Write-Host ""
            if ($allPassed) {
                Write-Host "  ✓ All tests passed" -ForegroundColor Green
            } else {
                Write-Host "  ✗ Some tests FAILED - Fix before continuing!" -ForegroundColor Red
                exit 1
            }
        } catch {
            Write-Host "  ✗ ERROR: Tests failed" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  [DRY-RUN] Would run: All tests (root, tests/, scripts/tests/)" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "[8/10] Skipping tests (--SkipTests flag)" -ForegroundColor Yellow
}

# Step 9: Verify installation
Write-Host ""
Write-Host "[9/10] Verifying installation..." -ForegroundColor Yellow
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

# Step 9: Generate complete summary (tests, papers, analyses, MD outputs)
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "[9/9] Generating complete summary and outputs..." -ForegroundColor Yellow
    if (-not $DryRun) {
        Write-Host "  Creating comprehensive summary..." -ForegroundColor Cyan
        
        # 1. Test Summary
        $summaryScript = "ci\summary-all-tests.py"
        if (Test-Path $summaryScript) {
            Write-Host "  [1/5] Test summary..." -ForegroundColor Cyan
            try {
                python $summaryScript 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "    [OK] Test results summary generated" -ForegroundColor Green
                }
            } catch {
                Write-Host "    [WARN] Could not generate test summary" -ForegroundColor Yellow
            }
        }
        
        # 2. Count validation papers
        Write-Host "  [2/5] Validation papers..." -ForegroundColor Cyan
        $papersValidation = "papers\validation"
        if (Test-Path $papersValidation) {
            $validationCount = (Get-ChildItem $papersValidation -Filter *.md -Recurse).Count
            Write-Host "    [OK] $validationCount validation papers available" -ForegroundColor Green
        }
        
        # 3. Count theory papers
        Write-Host "  [3/5] Theory papers..." -ForegroundColor Cyan
        $papersTheory = "docs\theory"
        if (Test-Path $papersTheory) {
            $theoryCount = (Get-ChildItem $papersTheory -Filter *.md -Recurse).Count
            Write-Host "    [OK] $theoryCount theory papers available" -ForegroundColor Green
        }
        
        # 4. Check analysis reports
        Write-Host "  [4/5] Analysis reports..." -ForegroundColor Cyan
        $reportsDir = "reports"
        if (Test-Path $reportsDir) {
            $reportCount = (Get-ChildItem $reportsDir -Filter *.md -Recurse -ErrorAction SilentlyContinue).Count
            if ($reportCount -gt 0) {
                Write-Host "    [OK] $reportCount analysis reports found" -ForegroundColor Green
            } else {
                Write-Host "    [INFO] No reports yet (run python run_all_ssz_terminal.py to generate)" -ForegroundColor Cyan
            }
        }
        
        # 5. Complete MD outputs catalog
        Write-Host "  [5/5] Complete MD catalog..." -ForegroundColor Cyan
        try {
            # Count ALL MD files
            $allMdFiles = (Get-ChildItem -Path . -Filter *.md -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.DirectoryName -notlike "*\.venv*" -and $_.DirectoryName -notlike "*\node_modules*" }).Count
            Write-Host "    [OK] $allMdFiles total MD files available" -ForegroundColor Green
            Write-Host "    [INFO] Run .\print_all_analysis.ps1 to view ALL outputs" -ForegroundColor Cyan
        } catch {
            Write-Host "    [WARN] Could not count MD files" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "  Summary ready! Available outputs:" -ForegroundColor Green
        Write-Host "    - Test results: ci/test_summary.html (if generated)" -ForegroundColor White
        Write-Host "    - Papers: papers/validation/ + docs/theory/" -ForegroundColor White
        Write-Host "    - Reports: reports/ (after running analysis)" -ForegroundColor White
        Write-Host "    - Complete: Run .\print_all_analysis.ps1 for everything" -ForegroundColor White
    } else {
        Write-Host "  [DRY-RUN] Would generate complete summary and outputs" -ForegroundColor Cyan
    }
    Write-Host "[9/9] Skipping summary generation (--SkipTests flag)" -ForegroundColor Yellow
}

# Step 10: Summary
Write-Host ""
Write-Host "[10/10] Installation complete!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 98) -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Start - All Test Scripts:" -ForegroundColor Yellow
Write-Host "  1. Activate venv:   .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "  Root-Level SSZ Tests (Python scripts):" -ForegroundColor Cyan
Write-Host "    python test_ppn_exact.py              # PPN parameters β=γ=1" -ForegroundColor White
Write-Host "    python test_vfall_duality.py          # Dual velocity invariant" -ForegroundColor White
Write-Host "    python test_energy_conditions.py      # WEC/DEC/SEC" -ForegroundColor White
Write-Host "    python test_c1_segments.py            # C1 continuity" -ForegroundColor White
Write-Host "    python test_c2_segments_strict.py     # C2 strict" -ForegroundColor White
Write-Host "    python test_c2_curvature_proxy.py     # C2 + curvature proxy" -ForegroundColor White
Write-Host "    python test_utf8_encoding.py          # UTF-8 validation" -ForegroundColor White
Write-Host ""
Write-Host "  Full Test Suite:" -ForegroundColor Cyan
Write-Host "    python run_full_suite.py              # All tests + analysis (~10-15 min)" -ForegroundColor White
Write-Host "    python run_full_suite.py --quick      # Essential tests only (~2 min)" -ForegroundColor White
Write-Host ""
Write-Host "  Complete SSZ Analysis (20+ scripts in pipeline):" -ForegroundColor Cyan
Write-Host "    python run_all_ssz_terminal.py        # Full SSZ pipeline (~10-15 min)" -ForegroundColor White
Write-Host "      → Runs: segspace_all_in_one_extended, covariant tests," -ForegroundColor DarkGray
Write-Host "        PPN tests, shadow predictions, QNM, φ-lattice, v_fall," -ForegroundColor DarkGray
Write-Host "        Lagrangian tests, stress-energy, theory calculations" -ForegroundColor DarkGray
Write-Host "      → See SSZ_COMPLETE_PIPELINE.md for full 20+ script list" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Example Data Analysis (SegWave):" -ForegroundColor Cyan
Write-Host "    ssz-rings --csv data/observations/G79_29+0_46_CO_NH3_rings.csv --v0 12.5 --fit-alpha" -ForegroundColor White
Write-Host "    ssz-rings --csv data/observations/CygnusX_DiamondRing_CII_rings.csv --v0 1.3" -ForegroundColor White
Write-Host ""
Write-Host "  Additional Analysis Scripts:" -ForegroundColor Cyan
Write-Host "    python scripts/analysis/eht_shadow_comparison.py    # EHT comparison matrix" -ForegroundColor White
Write-Host "    python scripts/analysis/redshift_robustness.py      # Redshift robustness" -ForegroundColor White
Write-Host "    python scripts/ring_temperature_to_velocity.py      # Ring temperature analysis" -ForegroundColor White
Write-Host "    python ci/summary-all-tests.py                      # Complete test summary" -ForegroundColor White
Write-Host "    python ci/summary_visualize.py                      # Visualization dashboard" -ForegroundColor White
Write-Host ""
Write-Host "  Print ALL Markdown (Papers + Reports + Summaries + Outputs):" -ForegroundColor Cyan
Write-Host "    ssz-print-md --root . --order path    # All MD files, alphabetically" -ForegroundColor White
Write-Host "    ssz-print-md --root . --order depth   # All MD files, shallow-first" -ForegroundColor White
Write-Host "    ssz-print-md --root papers            # Only validation papers" -ForegroundColor White
Write-Host "    ssz-print-md --root reports           # Only analysis reports" -ForegroundColor White
Write-Host "    ssz-print-md --root docs              # Only theory papers" -ForegroundColor White
Write-Host ""
Write-Host "Resources:" -ForegroundColor Yellow
Write-Host "  - Validation Papers: papers\validation\ (11 files)" -ForegroundColor Cyan
Write-Host "  - Theory Papers:     docs\theory\ (21 files)" -ForegroundColor Cyan
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

# Important notice about virtual environment
Write-Host ""
Write-Host ("=" * 100) -ForegroundColor Cyan
Write-Host "⚠️  IMPORTANT: Virtual Environment" -ForegroundColor Yellow
Write-Host ("=" * 100) -ForegroundColor Cyan
Write-Host ""
Write-Host "All packages are installed in the virtual environment: .venv\" -ForegroundColor Yellow
Write-Host ""
Write-Host "To use the installed packages, you MUST activate the venv:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you run tests WITHOUT activating, you'll get errors like:" -ForegroundColor Yellow
Write-Host "  ImportError: No module named 'pyarrow'" -ForegroundColor Red
Write-Host ""
Write-Host "To check if venv is active:" -ForegroundColor Green
Write-Host "  .\check_venv.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host ("=" * 100) -ForegroundColor Cyan
Write-Host ""
