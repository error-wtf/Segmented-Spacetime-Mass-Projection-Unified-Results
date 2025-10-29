# Fix "Seg" → "SSZ" in all documentation files
# © 2025 Carmen Wrede & Lino Casu

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "FIXING: 'Seg' → 'SSZ' IN ALL DOCUMENTATION" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

$changed = 0
$files = 0

# Important documentation files to check
$docFiles = @(
    "README.md",
    "PAIRED_TEST_ANALYSIS_COMPLETE.md",
    "STRATIFIED_PAIRED_TEST_RESULTS.md",
    "CODE_DOCUMENTATION.md",
    "SCRIPT_GUIDES.md",
    "COMPLETE_SCIENTIFIC_DOCUMENTATION.md",
    "SSZ_COMPLETE_FINAL_REPORT.md",
    "SSZ_COMPLETE_VALIDATION_REPORT.md",
    "FULL_VALIDATION_REPORT.md",
    "TOE_VALIDATION_STATUS.md",
    "TEST_SUITE_STATUS.md",
    "USAGE_FAQ.md",
    "FAQ.md",
    "COLAB_TEST_CHECKLIST.md",
    "COLAB_MASTER_COMPLETE_GUIDE.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        $files++
        Write-Host "Processing: $file" -ForegroundColor Yellow
        
        $content = Get-Content $file -Raw -Encoding UTF8
        $originalContent = $content
        
        # Replace patterns (case-sensitive to avoid changing script names)
        # Pattern 1: " SEG " → " SSZ "
        $content = $content -replace ' SEG ', ' SSZ '
        
        # Pattern 2: " Seg " → " SSZ " (at start of sentence or after punctuation)
        $content = $content -replace '([^\w])Seg ', '$1SSZ '
        $content = $content -replace '^Seg ', 'SSZ '
        
        # Pattern 3: "SEG's" → "SSZ's"
        $content = $content -replace "SEG's", "SSZ's"
        $content = $content -replace "Seg's", "SSZ's"
        
        # Pattern 4: "SEG " at line start
        $content = $content -replace '(\r?\n)SEG ', '$1SSZ '
        
        # Pattern 5: "(SEG)" → "(SSZ)"
        $content = $content -replace '\(SEG\)', '(SSZ)'
        
        # Pattern 6: "**SEG**" → "**SSZ**"
        $content = $content -replace '\*\*SEG\*\*', '**SSZ**'
        
        # Pattern 7: "`SEG`" → "`SSZ`"
        $content = $content -replace '`SEG`', '`SSZ`'
        
        # Check if changed
        if ($content -ne $originalContent) {
            $content | Out-File -FilePath $file -Encoding UTF8 -NoNewline
            $changed++
            Write-Host "  ✅ Updated: $file" -ForegroundColor Green
        } else {
            Write-Host "  ⏭️  No changes: $file" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "Files processed: $files" -ForegroundColor White
Write-Host "Files changed: $changed" -ForegroundColor Green
Write-Host ""

if ($changed -gt 0) {
    Write-Host "Review changes with: git diff" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "If satisfied, commit with:" -ForegroundColor Yellow
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'FIX: Standardize Seg → SSZ in documentation'" -ForegroundColor White
    Write-Host "  git push origin main" -ForegroundColor White
}
