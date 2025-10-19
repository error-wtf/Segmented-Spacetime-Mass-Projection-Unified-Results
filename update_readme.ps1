#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Updates README.md with v1.1.0 information
    
.DESCRIPTION
    Adds new sections for Test System Overhaul without removing old content
#>

$ErrorActionPreference = "Stop"

$readmePath = "README.md"
$backupPath = "README_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"

Write-Host "Backing up README.md to $backupPath..." -ForegroundColor Cyan
Copy-Item $readmePath $backupPath

Write-Host "Reading README.md..." -ForegroundColor Cyan
$content = Get-Content $readmePath -Raw

# Insert badges after first line
$badges = @"

[![Tests](https://img.shields.io/badge/tests-58%20passing-brightgreen)](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Anti--Capitalist-red)](LICENSE)
"@

$content = $content -replace '(# Segmented Spacetime – Mass Projection & Unified Results)', "`$1$badges"

# Insert "What's New" section after copyright line
$whatsNew = @"


**Latest Release:** v1.1.0 (2025-10-18) - Complete Test System Overhaul

---

## 📢 What's New in v1.1.0 (2025-10-18)

### 🎉 Major Update: Complete Test System Overhaul

✅ **35 physics tests** with detailed physical interpretations  
✅ **23 technical tests** in silent background mode  
✅ **Complete logging system** capturing all test output  
✅ **Smart data fetching** (auto-fetch 2GB Planck, no overwrites)  
✅ **Bug fixes**: pytest crash, import errors, false failure counts  
✅ **Documentation**: 10+ comprehensive guides  
✅ **Papers**: Both MD and PDF formats included  

**Key Features:**
- Complete output logging to `reports/summary-output.md` (~100-500 KB)
- Smart data fetching (never overwrites existing files)
- Detailed physical interpretations for all physics tests
- Technical tests run silently in background
- 10 new comprehensive documentation files

**Critical Bug Fixes:**
- 🔴 Pytest I/O crash: Changed `--disable-warnings` to `-s` flag
- 🔴 test_segmenter.py: Fixed import error
- 🔴 Summary counts: Fixed false "Failed: 3"

**Performance:**
- Test suite: ~2-3 minutes
- Installation: ~2-20 minutes (with/without Planck download)
- Re-installation: ~2 minutes (skips existing data)

[See full changelog →](CHANGELOG.md)

---
"@

$content = $content -replace '(Note: This is not a formal proof.*?\n\n---)', "`$1$whatsNew"

# Update Changelog section
$newChangelog = @"
## Changelog

### Version 1.1.0 (2025-10-18) - Test System Overhaul

**Major Features:**
- ✅ **35 physics tests** with detailed physical interpretations
- ✅ **23 technical tests** in silent background mode
- ✅ Complete logging system capturing all test output
- ✅ Smart data fetching (auto-fetch Planck 2GB, never overwrites)
- ✅ Papers in both MD and PDF formats
- ✅ 10+ new comprehensive documentation files

**Bug Fixes:**
- 🔴 Fixed pytest I/O crash (use `-s` not `--disable-warnings`)
- 🔴 Fixed test_segmenter.py import error
- 🔴 Fixed false "Failed: 3" in summary counts
- 🔴 Python cache issues documented

**New Documentation:**
- TESTING_COMPLETE_GUIDE.md - Master testing guide
- tests/README_TESTS.md - Tests directory docs
- scripts/tests/README_SCRIPTS_TESTS.md - Scripts tests docs
- LINUX_TEST_PLAN.md - Linux testing procedure
- LOGGING_SYSTEM_README.md - Logging documentation
- INSTALL_README.md - Installation guide
- DATA_FETCHING_README.md - Data management
- REPO_UPDATE_CHECKLIST.md - Repo update checklist
- And 2 more...

**Performance:**
- Test suite: ~2-3 minutes (full), ~30 seconds (quick)
- Installation: ~2 minutes (without Planck), ~20 minutes (with Planck)
- Re-installation: ~2 minutes (skips existing data)

See [CHANGELOG.md](CHANGELOG.md) for complete details.

### Version 2.0 (Previous Update)
"@

$content = $content -replace '## Changelog\s+### Version 2\.0 \(This Update\)', $newChangelog

Write-Host "Writing updated README.md..." -ForegroundColor Cyan
$content | Out-File -FilePath $readmePath -Encoding UTF8 -NoNewline

Write-Host "" 
Write-Host "✅ README.md updated successfully!" -ForegroundColor Green
Write-Host "   Backup saved to: $backupPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Changes made:" -ForegroundColor Yellow
Write-Host "  ✓ Added status badges" -ForegroundColor Green
Write-Host "  ✓ Added 'What's New v1.1.0' section" -ForegroundColor Green
Write-Host "  ✓ Updated Changelog with v1.1.0" -ForegroundColor Green
Write-Host ""
Write-Host "Review the changes and commit when ready:" -ForegroundColor Cyan
Write-Host "  git diff README.md" -ForegroundColor White
Write-Host ""
