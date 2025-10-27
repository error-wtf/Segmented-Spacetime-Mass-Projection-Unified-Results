# ============================================================================
# Copy Missing Files Script - Alle fehlenden Scripts ins Repository
# ============================================================================
# Datum: 2025-10-27
# Funktion: Kopiert alle Scripts aus D:\ und G:\ ins evidenz-ssz Repository
# ============================================================================

param(
    [switch]$DryRun = $false  # Test-Modus (keine echten Änderungen)
)

$ErrorActionPreference = "Stop"
$repoRoot = "h:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00"

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "SSZ Repository - Missing Files Copy Script" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n⚠️  DRY RUN MODE - Keine Dateien werden kopiert!`n" -ForegroundColor Yellow
}

# ============================================================================
# 1. Erstelle neue Verzeichnisse
# ============================================================================

Write-Host "`n[1/5] Erstelle neue Verzeichnisse..." -ForegroundColor Green

$directories = @(
    "evidenz-ssz\scripts\animations",
    "evidenz-ssz\scripts\video_production",
    "evidenz-ssz\scripts\cosmology",
    "evidenz-ssz\scripts\black_hole_bomb",
    "evidenz-ssz\scripts\proof_systems\v6",
    "evidenz-ssz\scripts\proof_systems\legacy",
    "evidenz-ssz\scripts\tools"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $repoRoot $dir
    if (-not (Test-Path $fullPath)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✓  Exists:  $dir" -ForegroundColor Gray
    }
}

# ============================================================================
# 2. Kopiere Animation Scripts (D:\)
# ============================================================================

Write-Host "`n[2/5] Kopiere Animation Scripts..." -ForegroundColor Green

$animationScripts = @(
    "ssz_animation_master.py",
    "ssz_animation_scientific.py",
    "ssz_animation_perfect.py",
    "ssz_animator.py",
    "ssz_simple_render.py",
    "make_ssz_anim.py",
    "blackhole_animation.py"
)

$destDir = Join-Path $repoRoot "evidenz-ssz\scripts\animations"
$copied = 0
$skipped = 0

foreach ($script in $animationScripts) {
    $source = "D:\$script"
    $dest = Join-Path $destDir $script
    
    if (Test-Path $source) {
        if (-not (Test-Path $dest)) {
            if (-not $DryRun) {
                Copy-Item $source $dest -Force
            }
            Write-Host "  ✅ Copied: $script" -ForegroundColor Green
            $copied++
        } else {
            Write-Host "  ⏩ Skip (exists): $script" -ForegroundColor Yellow
            $skipped++
        }
    } else {
        Write-Host "  ❌ Not found: $script" -ForegroundColor Red
    }
}

Write-Host "  📊 Animations: $copied copied, $skipped skipped" -ForegroundColor Cyan

# ============================================================================
# 3. Kopiere Video Production Scripts (D:\)
# ============================================================================

Write-Host "`n[3/5] Kopiere Video Production Scripts..." -ForegroundColor Green

$videoScripts = @(
    "ssz_bigbang_vs_ssz_anim.py",
    "ssz_bigbang_video_producer.py",
    "ssz_final_video_producer.py",
    "ssz_simple_video_producer.py",
    "ssz_video_scripts_final.py",
    "ssz_video_renderer.py"
)

$destDir = Join-Path $repoRoot "evidenz-ssz\scripts\video_production"
$copied = 0
$skipped = 0

foreach ($script in $videoScripts) {
    $source = "D:\$script"
    $dest = Join-Path $destDir $script
    
    if (Test-Path $source) {
        if (-not (Test-Path $dest)) {
            if (-not $DryRun) {
                Copy-Item $source $dest -Force
            }
            Write-Host "  ✅ Copied: $script" -ForegroundColor Green
            $copied++
        } else {
            Write-Host "  ⏩ Skip (exists): $script" -ForegroundColor Yellow
            $skipped++
        }
    } else {
        Write-Host "  ❌ Not found: $script" -ForegroundColor Red
    }
}

Write-Host "  📊 Video Production: $copied copied, $skipped skipped" -ForegroundColor Cyan

# ============================================================================
# 4. Kopiere Cosmology Scripts (D:\)
# ============================================================================

Write-Host "`n[4/5] Kopiere Cosmology Scripts..." -ForegroundColor Green

$cosmoScripts = @(
    "ssz_cosmo_animator.py",
    "ssz_cosmo_core.py",
    "ssz_cosmo_data.py",
    "ssz_cosmo_models.py"
)

$destDir = Join-Path $repoRoot "evidenz-ssz\scripts\cosmology"
$copied = 0
$skipped = 0

foreach ($script in $cosmoScripts) {
    $source = "D:\$script"
    $dest = Join-Path $destDir $script
    
    if (Test-Path $source) {
        if (-not (Test-Path $dest)) {
            if (-not $DryRun) {
                Copy-Item $source $dest -Force
            }
            Write-Host "  ✅ Copied: $script" -ForegroundColor Green
            $copied++
        } else {
            Write-Host "  ⏩ Skip (exists): $script" -ForegroundColor Yellow
            $skipped++
        }
    } else {
        Write-Host "  ❌ Not found: $script" -ForegroundColor Red
    }
}

Write-Host "  📊 Cosmology: $copied copied, $skipped skipped" -ForegroundColor Cyan

# ============================================================================
# 5. Kopiere Black Hole Bomb Scripts (D:\ + G:\)
# ============================================================================

Write-Host "`n[5/5] Kopiere Black Hole Bomb System..." -ForegroundColor Green

$bombScripts = @(
    "ssz_blackhole_bomb.py",
    "ssz_blackhole_bomb_complete.py",
    "ssz_blackhole_bomb_full.py",
    "ssz_bomb_animation.py",
    "ssz_gr_bridge.py",
    "ssz_live_visualizer.py",
    "ssz_parameter_scan.py",
    "ssz_plot_packager.py",
    "ssz_resonance_explorer.py"
)

$destDir = Join-Path $repoRoot "evidenz-ssz\scripts\black_hole_bomb"
$copied = 0
$skipped = 0

foreach ($script in $bombScripts) {
    $source = "D:\$script"
    $dest = Join-Path $destDir $script
    
    if (Test-Path $source) {
        if (-not (Test-Path $dest)) {
            if (-not $DryRun) {
                Copy-Item $source $dest -Force
            }
            Write-Host "  ✅ Copied: $script" -ForegroundColor Green
            $copied++
        } else {
            Write-Host "  ⏩ Skip (exists): $script" -ForegroundColor Yellow
            $skipped++
        }
    } else {
        Write-Host "  ❌ Not found: $script" -ForegroundColor Red
    }
}

Write-Host "  📊 Black Hole Bomb: $copied copied, $skipped skipped" -ForegroundColor Cyan

# ============================================================================
# 6. Kopiere Black Hole Bomb Results (G:\)
# ============================================================================

Write-Host "`n[6/8] Kopiere Black Hole Bomb Results & Data..." -ForegroundColor Green

$bombResultsDir = "G:\Black_Hole_Bomb"
$destBombDir = Join-Path $repoRoot "evidenz-ssz\scripts\black_hole_bomb"

if (Test-Path $bombResultsDir) {
    # Kopiere Results Files
    $resultFiles = @(
        "spectrum_results.csv",
        "growth_best_mode.csv",
        "summary.json",
        "run_config.json",
        "ssz_scan_analysis.ipynb"
    )
    
    $resultsDestDir = Join-Path $destBombDir "results"
    if (-not (Test-Path $resultsDestDir)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $resultsDestDir -Force | Out-Null
        }
    }
    
    foreach ($file in $resultFiles) {
        $source = Join-Path $bombResultsDir $file
        $dest = Join-Path $resultsDestDir $file
        
        if (Test-Path $source) {
            if (-not (Test-Path $dest)) {
                if (-not $DryRun) {
                    Copy-Item $source $dest -Force
                }
                Write-Host "  ✅ Copied: $file" -ForegroundColor Green
            } else {
                Write-Host "  ⏩ Skip: $file" -ForegroundColor Yellow
            }
        }
    }
    
    # Kopiere extended_results komplett
    $extSource = Join-Path $bombResultsDir "extended_results"
    $extDest = Join-Path $resultsDestDir "extended_results"
    
    if ((Test-Path $extSource) -and (-not (Test-Path $extDest))) {
        if (-not $DryRun) {
            Copy-Item $extSource $extDest -Recurse -Force
        }
        Write-Host "  ✅ Copied: extended_results\ (komplett)" -ForegroundColor Green
    }
    
    # Kopiere README (rename)
    $readmeSource = Join-Path $bombResultsDir "SSZ_BLACKHOLE_BOMB_RESULTS.md"
    $readmeDest = Join-Path $destBombDir "README.md"
    
    if ((Test-Path $readmeSource) -and (-not (Test-Path $readmeDest))) {
        if (-not $DryRun) {
            Copy-Item $readmeSource $readmeDest -Force
        }
        Write-Host "  ✅ Copied: README.md (from SSZ_BLACKHOLE_BOMB_RESULTS.md)" -ForegroundColor Green
    }
    
    # Kopiere GIF Animation
    $gifSource = Join-Path $bombResultsDir "ssz_bomb_animation.gif"
    $gifDest = Join-Path $destBombDir "ssz_bomb_animation.gif"
    
    if ((Test-Path $gifSource) -and (-not (Test-Path $gifDest))) {
        if (-not $DryRun) {
            Copy-Item $gifSource $gifDest -Force
        }
        Write-Host "  ✅ Copied: ssz_bomb_animation.gif (Git LFS)" -ForegroundColor Green
    }
    
} else {
    Write-Host "  ⚠️  G:\Black_Hole_Bomb\ nicht gefunden!" -ForegroundColor Red
}

# ============================================================================
# 7. Kopiere Proof Systems v6 (D:\)
# ============================================================================

Write-Host "`n[7/8] Kopiere Proof Systems v6..." -ForegroundColor Green

$proofScripts = @(
    "ssz_proof_check_v6.py",
    "ssz_proof_sweep_v6.py",
    "ssz_viz_v6.py"
)

$destDir = Join-Path $repoRoot "evidenz-ssz\scripts\proof_systems\v6"
$copied = 0
$skipped = 0

foreach ($script in $proofScripts) {
    $source = "D:\$script"
    $dest = Join-Path $destDir $script
    
    if (Test-Path $source) {
        if (-not (Test-Path $dest)) {
            if (-not $DryRun) {
                Copy-Item $source $dest -Force
            }
            Write-Host "  ✅ Copied: $script" -ForegroundColor Green
            $copied++
        } else {
            Write-Host "  ⏩ Skip (exists): $script" -ForegroundColor Yellow
            $skipped++
        }
    } else {
        Write-Host "  ❌ Not found: $script" -ForegroundColor Red
    }
}

Write-Host "  📊 Proof Systems v6: $copied copied, $skipped skipped" -ForegroundColor Cyan

# ============================================================================
# 8. Kopiere Tools (D:\ + G:\UNSORTED\)
# ============================================================================

Write-Host "`n[8/8] Kopiere Tools..." -ForegroundColor Green

$toolScripts = @(
    "segmented_space_time_full_proof.py",
    "create_all_language_versions.py",
    "researchgate_weinberg_response.py",
    "test_pipeline_quick.py",
    "text_safety_check.py"
)

$destDir = Join-Path $repoRoot "evidenz-ssz\scripts\tools"
$copied = 0
$skipped = 0

foreach ($script in $toolScripts) {
    $source = "D:\$script"
    $dest = Join-Path $destDir $script
    
    if (Test-Path $source) {
        if (-not (Test-Path $dest)) {
            if (-not $DryRun) {
                Copy-Item $source $dest -Force
            }
            Write-Host "  ✅ Copied: $script" -ForegroundColor Green
            $copied++
        } else {
            Write-Host "  ⏩ Skip (exists): $script" -ForegroundColor Yellow
            $skipped++
        }
    } else {
        Write-Host "  ❌ Not found: $script" -ForegroundColor Red
    }
}

# Galilean Redshift (aus UNSORTED)
$galileanSource = "G:\UNSORTED\galilean redshift.py"
$galileanDest = Join-Path $destDir "galilean_redshift.py"

if ((Test-Path $galileanSource) -and (-not (Test-Path $galileanDest))) {
    if (-not $DryRun) {
        Copy-Item $galileanSource $galileanDest -Force
    }
    Write-Host "  ✅ Copied: galilean_redshift.py (from UNSORTED)" -ForegroundColor Green
    $copied++
}

Write-Host "  📊 Tools: $copied copied, $skipped skipped" -ForegroundColor Cyan

# ============================================================================
# Zusammenfassung
# ============================================================================

Write-Host "`n" + "="*80 -ForegroundColor Cyan
Write-Host "✅ KOPIER-PROZESS ABGESCHLOSSEN" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n⚠️  DRY RUN MODE - Keine Dateien wurden kopiert!" -ForegroundColor Yellow
    Write-Host "   Führe das Script ohne -DryRun aus, um zu kopieren.`n" -ForegroundColor Yellow
} else {
    Write-Host "`n📊 Nächste Schritte:" -ForegroundColor Cyan
    Write-Host "   1. Prüfe die kopierten Dateien" -ForegroundColor White
    Write-Host "   2. git add evidenz-ssz/scripts/*" -ForegroundColor White
    Write-Host "   3. git commit -m 'Add animation, video, and black hole bomb systems'" -ForegroundColor White
    Write-Host "   4. git push`n" -ForegroundColor White
}

Write-Host "📄 Siehe MISSING_FILES_INVENTORY.md für Details`n" -ForegroundColor Gray
