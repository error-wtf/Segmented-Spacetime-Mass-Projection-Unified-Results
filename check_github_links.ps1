# GitHub Link Checker for docs/INDEX.md
# Tests if referenced files exist on GitHub

$repo = "error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results"
$branch = "main"
$baseUrl = "https://raw.githubusercontent.com/$repo/$branch"

# Key files to test from docs/INDEX.md
$testLinks = @(
    # Root files (referenced with ../)
    @{Path="../INSTALL_README.md"; Display="INSTALL_README.md"},
    @{Path="../COMPREHENSIVE_TESTING_GUIDE.md"; Display="COMPREHENSIVE_TESTING_GUIDE.md"},
    @{Path="../TROUBLESHOOTING.md"; Display="TROUBLESHOOTING.md"},
    @{Path="../CONTRIBUTING.md"; Display="CONTRIBUTING.md"},
    @{Path="../REPOSITORY_SECURITY_PERMISSIONS.md"; Display="REPOSITORY_SECURITY_PERMISSIONS.md"},
    @{Path="../DATA_ACCESS_REPRODUCIBILITY_CRISIS.md"; Display="DATA_ACCESS_REPRODUCIBILITY_CRISIS.md"},
    @{Path="../OUT_OF_DATA_LINO_CASU_STATEMENT.md"; Display="OUT_OF_DATA_LINO_CASU_STATEMENT.md"},
    @{Path="../LABORATORY_COMPARABILITY.md"; Display="LABORATORY_COMPARABILITY.md"},
    @{Path="../Sources.md"; Display="Sources.md"},
    @{Path="../DATA_CHANGELOG.md"; Display="DATA_CHANGELOG.md"},
    @{Path="../COMPREHENSIVE_DATA_ANALYSIS.md"; Display="COMPREHENSIVE_DATA_ANALYSIS.md"},
    @{Path="../SSZ_EXECUTIVE_SUMMARY.md"; Display="SSZ_EXECUTIVE_SUMMARY.md"},
    @{Path="../SSZ_COMPLETE_FINAL_REPORT.md"; Display="SSZ_COMPLETE_FINAL_REPORT.md"},
    @{Path="../DOCUMENTATION_INDEX.md"; Display="DOCUMENTATION_INDEX.md"},
    @{Path="../CHANGELOG.md"; Display="CHANGELOG.md"},
    @{Path="../TEST_SUITE_README.md"; Display="TEST_SUITE_README.md"},
    
    # Docs files (same directory)
    @{Path="THEORY_AND_CODE_INDEX.md"; Display="docs/THEORY_AND_CODE_INDEX.md"},
    @{Path="PHYSICS_FOUNDATIONS.md"; Display="docs/PHYSICS_FOUNDATIONS.md"},
    @{Path="MATHEMATICAL_FORMULAS.md"; Display="docs/MATHEMATICAL_FORMULAS.md"},
    @{Path="CODE_IMPLEMENTATION_GUIDE.md"; Display="docs/CODE_IMPLEMENTATION_GUIDE.md"},
    @{Path="DATA_ACQUISITION_COMPLETE_GUIDE.md"; Display="docs/DATA_ACQUISITION_COMPLETE_GUIDE.md"},
    
    # Papers
    @{Path="../papers/validation/README.md"; Display="papers/validation/README.md"},
    
    # Theory
    @{Path="theory/README.md"; Display="docs/theory/README.md"}
)

Write-Host "`n=== GITHUB LINK CHECK ===" -ForegroundColor Cyan
Write-Host "Repository: $repo" -ForegroundColor Gray
Write-Host "Branch: $branch`n" -ForegroundColor Gray

$working = 0
$broken = 0
$brokenLinks = @()

foreach ($link in $testLinks) {
    # Convert relative path to GitHub URL
    $urlPath = $link.Path -replace '^\.\.\/', '' -replace '^', 'docs/'
    $urlPath = $urlPath -replace 'docs/docs/', 'docs/'
    $urlPath = $urlPath -replace 'docs/\.\.\/', ''
    $url = "$baseUrl/$urlPath"
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK]  " -ForegroundColor Green -NoNewline
            Write-Host $link.Display -ForegroundColor White
            $working++
        }
    }
    catch {
        Write-Host "[404] " -ForegroundColor Red -NoNewline
        Write-Host $link.Display -ForegroundColor White -NoNewline
        Write-Host " -> $url" -ForegroundColor DarkGray
        $broken++
        $brokenLinks += $link.Display
    }
}

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Working: $working" -ForegroundColor Green
Write-Host "Broken:  $broken" -ForegroundColor $(if ($broken -gt 0) { "Red" } else { "Green" })

if ($broken -gt 0) {
    Write-Host "`nBroken files:" -ForegroundColor Yellow
    $brokenLinks | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}

Write-Host ""
