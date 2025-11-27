@echo off
REM ============================================================================
REM Move Old Bound Energy Files to Backup (Not Used Anymore)
REM ============================================================================
REM These files were DEPRECATED and renamed to redshift_* scripts
REM Moving to E:\clone\backups\ for archival purposes
REM ============================================================================

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   MOVING OLD BOUND_ENERGY FILES TO BACKUP                    ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Create backup directory
set BACKUP_DIR=E:\clone\backups\Segmented-Spacetime-Mass-Projection-Unified-Results\2025-11-27_bound_energy_deprecated

echo [1/4] Creating backup directory...
if not exist "%BACKUP_DIR%" (
    mkdir "%BACKUP_DIR%"
    echo   ^> Created: %BACKUP_DIR%
) else (
    echo   ^> Already exists: %BACKUP_DIR%
)
echo.

echo [2/4] Moving DEPRECATED bound_energy Python scripts...
REM ONLY deprecated scripts (NOT bound_energy.py - that one is still used!)
if exist "bound_energy_english.py" (
    move "bound_energy_english.py" "%BACKUP_DIR%\"
    echo   ^> Moved: bound_energy_english.py (DEPRECATED - renamed to redshift_segment_density.py)
)
if exist "bound_energy_plot.py" (
    move "bound_energy_plot.py" "%BACKUP_DIR%\"
    echo   ^> Moved: bound_energy_plot.py (DEPRECATED - renamed to redshift_segment_density_plot.py)
)

REM NOTE: bound_energy.py is KEPT - it's the REAL bound energy (paper-locked)!

REM Already marked as deprecated/backup
if exist "bound_energy_plot_with_frequenz_shift_fix.py.DEPRECATED" (
    move "bound_energy_plot_with_frequenz_shift_fix.py.DEPRECATED" "%BACKUP_DIR%\"
    echo   ^> Moved: bound_energy_plot_with_frequenz_shift_fix.py.DEPRECATED
)
if exist "bound_energy_plot_with_frequenz_shift_fix.py.BACKUP" (
    move "bound_energy_plot_with_frequenz_shift_fix.py.BACKUP" "%BACKUP_DIR%\"
    echo   ^> Moved: bound_energy_plot_with_frequenz_shift_fix.py.BACKUP
)
echo.

echo [3/4] Moving old CSV and data files...
if exist "bound_energy_results.csv.OLD" (
    move "bound_energy_results.csv.OLD" "%BACKUP_DIR%\"
    echo   ^> Moved: bound_energy_results.csv.OLD
)
if exist "bound_energy_clean_objects.csv.OLD" (
    move "bound_energy_clean_objects.csv.OLD" "%BACKUP_DIR%\"
    echo   ^> Moved: bound_energy_clean_objects.csv.OLD
)
if exist "bound_energy_with_deltaM.csv" (
    move "bound_energy_with_deltaM.csv" "%BACKUP_DIR%\"
    echo   ^> Moved: bound_energy_with_deltaM.csv
)
if exist "bound_energy_clean_plot.png" (
    move "bound_energy_clean_plot.png" "%BACKUP_DIR%\"
    echo   ^> Moved: bound_energy_clean_plot.png
)
echo.

echo [4/4] Removing DEPRECATED files from Git...
git rm --cached bound_energy_english.py 2>nul
git rm --cached bound_energy_plot.py 2>nul
REM NOTE: NOT removing bound_energy.py - it's still used!
git rm --cached bound_energy_plot_with_frequenz_shift_fix.py.DEPRECATED 2>nul
git rm --cached bound_energy_plot_with_frequenz_shift_fix.py.BACKUP 2>nul
git rm --cached bound_energy_results.csv.OLD 2>nul
git rm --cached bound_energy_clean_objects.csv.OLD 2>nul
git rm --cached bound_energy_with_deltaM.csv 2>nul
git rm --cached bound_energy_clean_plot.png 2>nul
echo   ^> Removed deprecated files from Git index
echo.

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   ✅ OLD FILES MOVED TO BACKUP                               ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Backup Location: %BACKUP_DIR%
echo.
echo DEPRECATED Files moved (if they existed):
echo   ❌ bound_energy_english.py (DEPRECATED)
echo   ❌ bound_energy_plot.py (DEPRECATED)
echo   ❌ bound_energy_plot_with_frequenz_shift_fix.py.DEPRECATED
echo   ❌ bound_energy_plot_with_frequenz_shift_fix.py.BACKUP
echo   ❌ bound_energy_results.csv.OLD
echo   ❌ bound_energy_clean_objects.csv.OLD
echo   ❌ bound_energy_with_deltaM.csv
echo   ❌ bound_energy_clean_plot.png
echo.
echo NEW REDSHIFT FILES (KEPT):
echo   ✅ redshift_segment_density.py (replaces bound_energy_english.py)
echo   ✅ redshift_segment_density_plot.py (replaces bound_energy_plot.py)
echo   ✅ redshift_ratio_multi_object_plot_with_deltaM.py (replaces bound_energy_plot_with_frequenz_shift_fix.py)
echo.
echo STILL ACTIVE (NOT MOVED):
echo   ✅ bound_energy.py (REAL bound energy - paper-locked, still used!)
echo   ✅ bound_energy.txt files in agent_out/ (generated outputs)
echo.

pause
