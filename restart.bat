@echo off
REM Quick restart script - works in PowerShell

echo Stopping Python...
taskkill /F /IM python.exe 2>nul

echo Clearing cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul

echo Starting fresh...
python run_full_suite.py --quick
