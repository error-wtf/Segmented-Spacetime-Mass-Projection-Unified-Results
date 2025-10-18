@echo off
REM Clear Python cache and restart fresh

echo ================================================================================
echo CLEARING PYTHON CACHE
echo ================================================================================
echo.

REM 1. Kill all Python processes
echo [1/4] Stopping all Python processes...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo   ^> Python processes stopped
) else (
    echo   ^> No Python processes running
)
echo.

REM 2. Delete __pycache__ directories
echo [2/4] Deleting __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo   ^> Deleting: %%d
    rd /s /q "%%d" 2>nul
)
echo   ^> Done
echo.

REM 3. Delete .pyc files
echo [3/4] Deleting .pyc files...
del /s /q *.pyc 2>nul
echo   ^> Done
echo.

REM 4. Delete .pyo files
echo [4/4] Deleting .pyo files...
del /s /q *.pyo 2>nul
echo   ^> Done
echo.

echo ================================================================================
echo CACHE CLEARED!
echo ================================================================================
echo.
echo You can now run your scripts with fresh code:
echo   python run_full_suite.py
echo   python run_all_ssz_terminal.py
echo.
pause
