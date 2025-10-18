<#
.SYNOPSIS
Safe wrapper to run Python scripts without crashing PowerShell Extension

.DESCRIPTION
This wrapper redirects Python output to prevent PowerShell Extension from
parsing Python code fragments and crashing.

.PARAMETER ScriptPath
Path to the Python script to run

.PARAMETER Arguments
Arguments to pass to the Python script

.EXAMPLE
.\run_safe.ps1 -ScriptPath "ci\autorun_suite.py" -Arguments "--config", "ci\suite_config.yaml"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptPath,
    
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

$ErrorActionPreference = "Continue"

# Use Start-Process to isolate the Python process from PowerShell Extension
$processArgs = @{
    FilePath = "python"
    ArgumentList = @($ScriptPath) + $Arguments
    NoNewWindow = $true
    Wait = $true
    RedirectStandardOutput = "python_output.log"
    RedirectStandardError = "python_error.log"
}

Write-Host "🔒 Running Python script in isolated mode..." -ForegroundColor Cyan
Write-Host "   Script: $ScriptPath" -ForegroundColor Gray
Write-Host "   Output: python_output.log" -ForegroundColor Gray
Write-Host "   Errors: python_error.log" -ForegroundColor Gray
Write-Host ""

$process = Start-Process @processArgs -PassThru

if ($process.ExitCode -eq 0) {
    Write-Host "✅ Script completed successfully!" -ForegroundColor Green
    Get-Content "python_output.log" -ErrorAction SilentlyContinue
} else {
    Write-Host "❌ Script failed with exit code: $($process.ExitCode)" -ForegroundColor Red
    Write-Host "`n--- ERROR OUTPUT ---" -ForegroundColor Yellow
    Get-Content "python_error.log" -ErrorAction SilentlyContinue
    Write-Host "`n--- STANDARD OUTPUT ---" -ForegroundColor Yellow
    Get-Content "python_output.log" -ErrorAction SilentlyContinue
}

exit $process.ExitCode
