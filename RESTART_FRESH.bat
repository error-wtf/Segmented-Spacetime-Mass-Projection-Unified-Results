@echo off
REM Restart run_full_suite.py with fresh code (no cache)

echo ================================================================================
echo RESTARTING WITH FRESH CODE
echo ================================================================================
echo.

REM 1. Stop all Python processes
echo [1/3] Stopping Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo   Done.
echo.

REM 2. Clear cache quickly
echo [2/3] Clearing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul
echo   Done.
echo.

REM 3. Run with unbuffered output
echo [3/3] Starting run_full_suite.py (fresh)...
echo.
echo ================================================================================
echo.

python -u run_full_suite.py --quick

echo.
echo ================================================================================
echo COMPLETE
echo ================================================================================
pause
