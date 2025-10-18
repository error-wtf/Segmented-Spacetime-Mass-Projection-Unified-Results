param(
    [Parameter(Mandatory = $true)]
    [string]$RunId,

    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot ".." )).Path,
    [string]$AdqlPath = "queries/gaia_dr3_core.sql",
    [string]$GaiaOutputName = "gaia_dr3_core.csv",

    [string]$PlanckSource,
    [string]$PlanckTargetName = "planck_map.fits",

    [string]$SdssSource,
    [string]$SdssTargetName = "sdss_catalog.csv",

    [string]$EphemeridesSource,
    [string]$EphemeridesTargetName = "solar_system.json",

    [switch]$SkipGaiaDownload,
    [switch]$SkipPipelineRun,

    [System.Management.Automation.PSCredential]$GaiaCredential,

    [string[]]$PipelineExtraArgs,
    [string]$LogDir = "data/logs"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-ProjectPath {
    param([string]$RelativePath)
    return (Resolve-Path (Join-Path $ProjectRoot $RelativePath)).Path
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        Write-Log -Message "Creating directory: $Path" -Level "INFO"
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
}

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("DEBUG","INFO","WARN","ERROR")] [string]$Level = "INFO",
        [switch]$NoConsole
    )

    if (-not $Script:LogPath) {
        if (-not $NoConsole) {
            Write-Host $Message
        }
        return
    }

    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK"
    $line = "$timestamp [$Level] $Message"
    if (-not $NoConsole) {
        $color = $null
        switch ($Level) {
            "INFO" { $color = "Green" }
            "WARN" { $color = "Yellow" }
            "ERROR" { $color = "Red" }
            "DEBUG" { $color = "Cyan" }
        }
        if ($color) {
            Write-Host $line -ForegroundColor $color
        }
        else {
            Write-Host $line
        }
    }
    Add-Content -Path $Script:LogPath -Value $line
}

$ProjectRoot = (Resolve-Path $ProjectRoot).Path
$logDirPath = Join-Path $ProjectRoot $LogDir
Ensure-Directory $logDirPath
$Script:LogPath = Join-Path $logDirPath ("pipeline_{0}_{1}.log" -f $RunId, (Get-Date -Format "yyyyMMdd_HHmmss"))
"" | Out-File -FilePath $Script:LogPath -Encoding utf8 -Force
Write-Log -Message "Using project root: $ProjectRoot" -Level "INFO"

$gaiaRawDir = Join-Path $ProjectRoot "data/raw/gaia/$RunId"
$planckRawDir = Join-Path $ProjectRoot "data/raw/planck/$RunId"
$sdssRawDir = Join-Path $ProjectRoot "data/raw/sdss/$RunId"
$ephemeridesDir = Join-Path $ProjectRoot "inputs/ephemerides"

Ensure-Directory $gaiaRawDir
Ensure-Directory $planckRawDir
Ensure-Directory $sdssRawDir
Ensure-Directory $ephemeridesDir

$planckTargetPath = Join-Path $planckRawDir $PlanckTargetName

if (-not $SkipGaiaDownload) {
    $adqlFullPath = Join-Path $ProjectRoot $AdqlPath
    if (-not (Test-Path $adqlFullPath)) {
        Write-Log -Message "ADQL file not found: $adqlFullPath" -Level "ERROR"
        throw "ADQL file not found: $adqlFullPath"
    }

    Write-Log -Message "[GAIA] Loading ADQL from $adqlFullPath" -Level "INFO"
    $adqlQuery = Get-Content -Raw -Path $adqlFullPath
    if ([string]::IsNullOrWhiteSpace($adqlQuery)) {
        Write-Log -Message "ADQL query is empty." -Level "ERROR"
        throw "ADQL query is empty."
    }

    if (-not $GaiaCredential) {
        Write-Log -Message "[GAIA] Prompting for TAP credentials..." -Level "WARN"
        $GaiaCredential = Get-Credential -Message "Enter Gaia TAP credentials"
    }

    $gaiaOutPath = Join-Path $gaiaRawDir $GaiaOutputName
    Write-Log -Message "[GAIA] Downloading catalogue to $gaiaOutPath" -Level "INFO"

    $body = @{
        REQUEST = "doQuery"
        LANG    = "ADQL"
        FORMAT  = "csv"
        QUERY   = $adqlQuery
    }

    try {
        Invoke-RestMethod -Uri "https://gea.esac.esa.int/tap-server/tap/sync" `
            -Method Post `
            -Headers @{ "Content-Type" = "application/x-www-form-urlencoded" } `
            -Body $body `
            -Credential $GaiaCredential `
            -OutFile $gaiaOutPath
        Write-Log -Message "[GAIA] Download complete." -Level "INFO"
    }
    catch {
        Write-Log -Message "Gaia download failed: $($_.Exception.Message)" -Level "ERROR"
        throw "Gaia download failed: $($_.Exception.Message)"
    }
}
else {
    Write-Log -Message "[GAIA] Skipping Gaia download." -Level "WARN"
}

function Copy-IfAvailable {
    param(
        [string]$Source,
        [string]$DestinationDir,
        [string]$TargetName,
        [string]$Label
    )

    if ([string]::IsNullOrWhiteSpace($Source)) {
        Write-Log -Message "[$Label] Source not provided. Skipping." -Level "WARN"
        return
    }
    if (-not (Test-Path $Source)) {
        Write-Log -Message "[$Label] Source not found: $Source" -Level "ERROR"
        return
    }

    $destPath = Join-Path $DestinationDir $TargetName
    $resolvedSource = (Resolve-Path $Source).Path
    $resolvedDest = $destPath
    if (Test-Path $destPath) {
        $resolvedDest = (Resolve-Path $destPath).Path
    }
    if ($resolvedSource -ieq $resolvedDest) {
        Write-Log -Message "[$Label] Source and destination are the same. Skipping copy." -Level "WARN"
        return
    }
    Write-Log -Message "[$Label] Copying $Source -> $destPath" -Level "INFO"
    Copy-Item $Source $destPath -Force
}

Copy-IfAvailable -Source $PlanckSource -DestinationDir $planckRawDir -TargetName $PlanckTargetName -Label "PLANCK"
Copy-IfAvailable -Source $SdssSource -DestinationDir $sdssRawDir -TargetName $SdssTargetName -Label "SDSS"
Copy-IfAvailable -Source $EphemeridesSource -DestinationDir $ephemeridesDir -TargetName $EphemeridesTargetName -Label "EPHEMERIDES"

if (-not (Test-Path $planckTargetPath)) {
    $fetchScript = Join-Path $ProjectRoot "scripts/planck/fetch_planck_map.py"
    if (-not (Test-Path $fetchScript)) {
        Write-Log -Message "Planck fetch script not found: $fetchScript" -Level "ERROR"
        throw "Planck fetch script not found: $fetchScript"
    }
    Write-Log -Message "[PLANCK] Source missing. Attempting automatic download." -Level "WARN"
    $pythonExeFetch = "python"
    & $pythonExeFetch $fetchScript --output $planckTargetPath
    if ($LASTEXITCODE -ne 0) {
        Write-Log -Message "Planck download failed." -Level "ERROR"
        throw "Planck download failed."
    }
}

if (-not (Test-Path $planckTargetPath)) {
    Write-Log -Message "Planck map not available at $planckTargetPath" -Level "ERROR"
    throw "Planck map not available at $planckTargetPath"
}

if (-not $SkipPipelineRun) {
    $pythonExe = "python"
    $pipelineArgs = @(
        "run_gaia_ssz_pipeline.py",
        "--run-id", $RunId,
        "--adql", (Join-Path $ProjectRoot $AdqlPath),
        "--cones-config", (Join-Path $ProjectRoot "configs/gaia_cones.json")
    )

    if ($PipelineExtraArgs) {
        $pipelineArgs += $PipelineExtraArgs
    }

    Write-Log -Message "[PIPELINE] Executing: $pythonExe $($pipelineArgs -join ' ')" -Level "INFO"
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $pythonExe
    $processInfo.WorkingDirectory = $ProjectRoot
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false

    foreach ($arg in $pipelineArgs) {
        [void]$processInfo.ArgumentList.Add($arg)
    }

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo
    $null = $process.Start()
    $process.WaitForExit()

    $stdout = $process.StandardOutput.ReadToEnd()
    if ($stdout) {
        foreach ($line in $stdout.Split([System.Environment]::NewLine, [System.StringSplitOptions]::RemoveEmptyEntries)) {
            Write-Log -Message "[PIPELINE][STDOUT] $line" -Level "INFO"
        }
    }
    $stderr = $process.StandardError.ReadToEnd()
    if ($stderr) {
        foreach ($line in $stderr.Split([System.Environment]::NewLine, [System.StringSplitOptions]::RemoveEmptyEntries)) {
            Write-Log -Message "[PIPELINE][STDERR] $line" -Level "ERROR"
        }
    }

    if ($process.ExitCode -ne 0) {
        Write-Log -Message "Pipeline run failed with exit code $($process.ExitCode)." -Level "ERROR"
        throw "Pipeline run failed with exit code $($process.ExitCode)."
    }
    Write-Log -Message "[PIPELINE] Completed successfully." -Level "INFO"
}
else {
    Write-Log -Message "[PIPELINE] Skipping pipeline execution." -Level "WARN"
}

Write-Log -Message "[NEXT STEPS] Review QA notebook: notebooks/qa/qa_checks.ipynb" -Level "INFO"
Write-Log -Message "[NEXT STEPS] Update documentation with results in docs/README.md" -Level "INFO"
Write-Log -Message "Pipeline script completed." -Level "INFO"
