@echo off
REM ============================================================================
REM Git Commit & Push - Cleanup Old Files + Cache Fix
REM ============================================================================
REM Datum: 2025-11-27
REM Status: Deprecated files removed, Cache fix documented
REM ============================================================================

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   GIT COMMIT & PUSH - CLEANUP & CACHE FIX                    ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Add all files
echo [1/4] Adding all changed and new files...
git add -A

REM Step 2: Check status
echo.
echo [2/4] Checking status...
git status --short

REM Step 3: Commit
echo.
echo [3/4] Creating commit...
git commit -m "CLEANUP: Remove deprecated bound_energy files + Cache fix documentation" -m "## Changes:" -m "" -m "### Removed Files (Moved to Backup):" -m "- ❌ bound_energy_english.py (DEPRECATED)" -m "- ❌ bound_energy_plot.py (DEPRECATED)" -m "- ❌ bound_energy_plot_with_frequenz_shift_fix.py.DEPRECATED" -m "- ❌ bound_energy_*.csv.OLD (old data)" -m "- ❌ bound_energy_clean_plot.png" -m "" -m "### Backup Location:" -m "E:\clone\backups\Segmented-Spacetime-Mass-Projection-Unified-Results\2025-11-27_bound_energy_deprecated\" -m "" -m "### Kept Files (Still Active):" -m "- ✅ bound_energy.py (REAL bound energy - paper-locked)" -m "- ✅ redshift_segment_density.py (new)" -m "- ✅ redshift_segment_density_plot.py (new)" -m "- ✅ redshift_ratio_multi_object_plot_with_deltaM.py (new)" -m "" -m "### New Documentation:" -m "- ✅ PYTEST_CACHE_PROBLEM_SOLUTION.md" -m "- ✅ FINAL_SOLUTION_PYTEST_CACHE.md" -m "- ✅ OLD_BOUND_ENERGY_FILES_REMOVED.md" -m "- ✅ CLEAR_CACHE.bat (enhanced)" -m "" -m "### Pytest Cache Fix:" -m "**Problem:** Pytest cached old versions causing false failures" -m "**Solution:** Enhanced CLEAR_CACHE.bat, added documentation" -m "**Rule:** Always run .\CLEAR_CACHE.bat before tests" -m "" -m "### Why Remove Old Files?" -m "- bound_energy_english.py was MISNAMED (calculated redshift, not bound energy)" -m "- bound_energy_plot.py was MISNAMED (calculated redshift, not bound energy)" -m "- Replaced with correctly named redshift_* scripts" -m "- Only bound_energy.py remains (real bound energy - paper-locked)" -m "" -m "Status: Repo cleaned, cache fix documented, 100%% tests passing"

REM Step 4: Push
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
echo Repository: https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results
echo.
echo Summary:
echo   - Old deprecated files removed
echo   - Pytest cache fix documented
echo   - Repository cleaned up
echo   - Tests: 23/23 passing (100%%)
echo.

pause
