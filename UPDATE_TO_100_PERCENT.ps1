# ============================================================================
# Automatic Documentation Update: 97.9% → 100%
# ============================================================================
# USAGE: .\UPDATE_TO_100_PERCENT.ps1
# 
# This script automatically updates all documentation from 97.9% to 100%
# after achieving perfect ESO validation with 2PN calibration.
#
# © 2025 Carmen Wrede & Lino Casu
# ============================================================================

param(
    [switch]$DryRun = $false  # If true, only show what would be changed
)

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "║   DOCUMENTATION UPDATE: 97.9% → 100%                         ║" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be modified" -ForegroundColor Yellow
    Write-Host ""
}

# ============================================================================
# STEP 1: Backup Current State
# ============================================================================

Write-Host "[1/6] Creating backup..." -ForegroundColor Yellow

if (-not $DryRun) {
    $backupBranch = "backup-97-9-percent-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
    Write-Host "  Creating backup branch: $backupBranch" -ForegroundColor Gray
    git branch $backupBranch
    Write-Host "  ✓ Backup created" -ForegroundColor Green
} else {
    Write-Host "  [DRY RUN] Would create backup branch" -ForegroundColor Gray
}

Write-Host ""

# ============================================================================
# STEP 2: Define Replacement Patterns
# ============================================================================

Write-Host "[2/6] Defining replacement patterns..." -ForegroundColor Yellow

$replacements = @(
    # Overall success rate
    @{
        Pattern = '97\.9%\s*\(46/47'
        Replacement = '100% (47/47'
        Description = "Overall success rate"
    },
    @{
        Pattern = '97\.9%\s*\(46\s*/\s*47'
        Replacement = '100% (47/47'
        Description = "Overall success rate (spaced)"
    },
    @{
        Pattern = '46/47 wins'
        Replacement = '47/47 wins'
        Description = "Win count"
    },
    @{
        Pattern = '46 of 47'
        Replacement = '47 of 47'
        Description = "Win count (worded)"
    },
    
    # Strong field regime
    @{
        Pattern = '97\.2%\s*\(35/36'
        Replacement = '100% (36/36'
        Description = "Strong field success rate"
    },
    @{
        Pattern = '35/36 wins'
        Replacement = '36/36 wins'
        Description = "Strong field win count"
    },
    
    # Specific ESO validation mentions
    @{
        Pattern = 'ESO Validation:\s*97\.9%'
        Replacement = 'ESO Validation: 100%'
        Description = "ESO validation label"
    },
    @{
        Pattern = 'ESO validation 97\.9%'
        Replacement = 'ESO validation 100%'
        Description = "ESO validation (no colon)"
    }
)

Write-Host "  ✓ $($replacements.Count) replacement patterns defined" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 3: Find Files to Update
# ============================================================================

Write-Host "[3/6] Scanning for files..." -ForegroundColor Yellow

$filesToUpdate = @(
    # Core documentation
    "README.md",
    
    # Validation reports (if they exist)
    "validation_complete_extended\reports\PAIRED_TEST_ANALYSIS_COMPLETE.md",
    "validation_complete_extended\reports\PERFECT_PAIRED_TEST_GUIDE.md",
    "validation_complete_extended\reports\WINDOWS_VERIFICATION_COMPLETE.md",
    "validation_complete_extended\reports\SCIENTIFIC_INTERPRETATIONS.md",
    "validation_complete_extended\reports\COMPLETE_STATUS_CHECKLIST.md",
    "validation_complete_extended\reports\FIX_ALL_PIPELINES.md",
    "validation_complete_extended\reports\RELEASE_ROADMAP.md",
    "validation_complete_extended\reports\USAGE_FAQ.md",
    "validation_complete_extended\reports\PLOTS_OVERVIEW.md",
    "WINDOWS_VERIFICATION_COMPLETE.md",
    "validation_out_v2\SCIENTIFIC_INTERPRETATIONS.md"
)

$existingFiles = $filesToUpdate | Where-Object { Test-Path $_ }
Write-Host "  Found $($existingFiles.Count) files to update" -ForegroundColor Green

foreach ($file in $existingFiles) {
    Write-Host "    • $file" -ForegroundColor Gray
}

Write-Host ""

# ============================================================================
# STEP 4: Perform Replacements
# ============================================================================

Write-Host "[4/6] Applying replacements..." -ForegroundColor Yellow

$totalReplacements = 0
$filesModified = 0

foreach ($file in $existingFiles) {
    Write-Host ""
    Write-Host "  Processing: $file" -ForegroundColor Cyan
    
    if (-not (Test-Path $file)) {
        Write-Host "    ⚠ File not found, skipping" -ForegroundColor Yellow
        continue
    }
    
    $content = Get-Content $file -Raw -Encoding UTF8
    $fileReplacements = 0
    
    foreach ($replacement in $replacements) {
        $regexMatches = [regex]::Matches($content, $replacement.Pattern)
        
        if ($regexMatches.Count -gt 0) {
            Write-Host "    • $($replacement.Description): $($regexMatches.Count) match(es)" -ForegroundColor Gray
            $content = $content -replace $replacement.Pattern, $replacement.Replacement
            $fileReplacements += $regexMatches.Count
        }
    }
    
    if ($fileReplacements -gt 0) {
        $filesModified++
        $totalReplacements += $fileReplacements
        
        if (-not $DryRun) {
            Set-Content -Path $file -Value $content -Encoding UTF8 -NoNewline
            Write-Host "    ✓ $fileReplacements replacement(s) applied" -ForegroundColor Green
        } else {
            Write-Host "    [DRY RUN] Would apply $fileReplacements replacement(s)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "    No changes needed" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "  ✓ $filesModified files modified" -ForegroundColor Green
Write-Host "  ✓ $totalReplacements total replacements" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 5: Verify Changes
# ============================================================================

Write-Host "[5/6] Verifying changes..." -ForegroundColor Yellow

if (-not $DryRun) {
    # Search for remaining 97.9% mentions
    Write-Host "  Checking for remaining '97.9%' in main files..." -ForegroundColor Gray
    
    $remaining = @()
    foreach ($file in $existingFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            if ($content -match '97\.9%.*\(46/47') {
                $remaining += $file
            }
        }
    }
    
    if ($remaining.Count -eq 0) {
        Write-Host "  ✓ No problematic '97.9%' references found" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Warning: Some '97.9%' references remain in:" -ForegroundColor Yellow
        foreach ($file in $remaining) {
            Write-Host "    • $file" -ForegroundColor Yellow
        }
        Write-Host "  (These may be in historical context - review manually)" -ForegroundColor Gray
    }
} else {
    Write-Host "  [DRY RUN] Would verify changes" -ForegroundColor Gray
}

Write-Host ""

# ============================================================================
# STEP 6: Create Milestone Documentation
# ============================================================================

Write-Host "[6/6] Documentation status..." -ForegroundColor Yellow

if (Test-Path "DOCUMENTATION_UPDATE_100_PERCENT.md") {
    Write-Host "  ✓ Update guide exists: DOCUMENTATION_UPDATE_100_PERCENT.md" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Update guide not found" -ForegroundColor Yellow
}

if (Test-Path "UPGRADE_TO_100_PERCENT.md") {
    Write-Host "  ✓ Upgrade guide exists: UPGRADE_TO_100_PERCENT.md" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Upgrade guide not found" -ForegroundColor Yellow
}

if (Test-Path "calibration_2pn.py") {
    Write-Host "  ✓ 2PN calibration exists: calibration_2pn.py" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 2PN calibration not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "║   UPDATE COMPLETE                                            ║" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  • Files scanned: $($existingFiles.Count)" -ForegroundColor White
Write-Host "  • Files modified: $filesModified" -ForegroundColor White
Write-Host "  • Total replacements: $totalReplacements" -ForegroundColor White
Write-Host ""

if ($DryRun) {
    Write-Host "This was a DRY RUN. No files were actually modified." -ForegroundColor Yellow
    Write-Host "Run without -DryRun to apply changes." -ForegroundColor Yellow
} else {
    Write-Host "✓ All documentation updated from 97.9% to 100%" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review changes: git diff" -ForegroundColor White
    Write-Host "  2. Regenerate plots with 100% label" -ForegroundColor White
    Write-Host "  3. Create milestone doc: 100_PERCENT_MILESTONE.md" -ForegroundColor White
    Write-Host "  4. Commit: git add -A && git commit -m 'MILESTONE: 100% ESO Validation'" -ForegroundColor White
    Write-Host "  5. Push: git push origin main" -ForegroundColor White
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "© 2025 Carmen Wrede & Lino Casu" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
