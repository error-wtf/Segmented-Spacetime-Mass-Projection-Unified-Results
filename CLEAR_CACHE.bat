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

echo [2/5] Deleting .pytest_cache directories...
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" (
    echo   ^> Deleting: %%d
    rd /s /q "%%d" 2>nul
)

echo [3/5] Deleting __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo   ^> Deleting: %%d
    rd /s /q "%%d" 2>nul
)

echo [4/5] Deleting .pyc files...
del /s /q *.pyc 2>nul

echo [5/5] Deleting test-specific caches...
if exist "tests\.pytest_cache" rd /s /q "tests\.pytest_cache" 2>nul
if exist "tests\cosmos\.pytest_cache" rd /s /q "tests\cosmos\.pytest_cache" 2>nul
if exist "scripts\tests\.pytest_cache" rd /s /q "scripts\tests\.pytest_cache" 2>nul

REM 5. Delete pytest cache
echo [5/5] Deleting pytest cache directories...
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" (
    echo   ^> Deleting: %%d
    rd /s /q "%%d" 2>nul
)
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
