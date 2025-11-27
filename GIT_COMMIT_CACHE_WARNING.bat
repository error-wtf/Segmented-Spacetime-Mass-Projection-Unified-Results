@echo off
REM ============================================================================
REM Git Commit - Cache Warning in Install Scripts
REM ============================================================================

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   GIT COMMIT - CACHE WARNING ADDED                           ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo [1/4] Adding all files...
git add -A

echo.
echo [2/4] Status check...
git status --short

echo.
echo [3/4] Committing...
git commit -m "INSTALL: Add pytest cache warning to install scripts" -m "## Changes:" -m "" -m "### Enhanced CLEAR_CACHE scripts:" -m "- ✅ CLEAR_CACHE.bat: Better formatting, cache problem explanation" -m "- ✅ CLEAR_CACHE.sh: Better formatting, cache problem explanation" -m "- ✅ Both scripts now clearly explain WHY cache clearing is needed" -m "" -m "### Updated Install Scripts:" -m "- ✅ install.ps1: Added prominent cache warning at end" -m "- ✅ install.sh: Added prominent cache warning at end" -m "" -m "### Warning Content:" -m "```" -m "⚠️  IMPORTANT: PYTEST CACHE WARNING" -m "" -m "ALWAYS run ./CLEAR_CACHE.bat (or .sh) BEFORE running tests!" -m "" -m "Why? Pytest caches old file versions and can cause false test failures." -m "The cache must be cleared to ensure tests use the current code." -m "" -m "Correct workflow:" -m "  1. ./CLEAR_CACHE.bat        # Clear cache first" -m "  2. python run_full_suite.py   # Then run tests" -m "" -m "See PYTEST_CACHE_PROBLEM_SOLUTION.md for details." -m "```" -m "" -m "### Documentation:" -m "- ✅ DOCUMENTATION_STATUS_FINAL.md created" -m "- ✅ All documentation reviewed and verified" -m "- ✅ No repairs needed - all docs correct" -m "" -m "Status: User will now be warned about cache issue on every install!"

echo.
echo [4/4] Pushing to GitHub...
git push origin main

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   ✅ COMMIT & PUSH COMPLETE                                  ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

pause
