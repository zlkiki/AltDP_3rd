# =======================================================================
#   🚀 AltDP_3rd - Web-based Structural Member Design Platform
#      PowerShell Application Launcher (run.ps1)
# =======================================================================

$Host.UI.RawUI.WindowTitle = "AltDP_3rd - Structural Member Design Platform"

Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "  🚀 AltDP_3rd - Structural Member Design Platform" -ForegroundColor Green
Write-Host "     KDS 14 20 00 / KDS 14 31 00 Web Engineering System" -ForegroundColor White
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory to script location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($ScriptDir) {
    Set-Location $ScriptDir
}

# -----------------------------------------------------------------------
# 1. Check and terminate existing AltDP_3rd or Port 8000 instances
# -----------------------------------------------------------------------
$Port = 8000
$terminated = $false

# 1-A. Terminate processes running AltDP_3rd uvicorn server
try {
    $existingServers = Get-CimInstance Win32_Process -Filter "CommandLine LIKE '%src.api.server:app%'" -ErrorAction SilentlyContinue
    if ($existingServers) {
        foreach ($srv in $existingServers) {
            Write-Host "[!] Existing AltDP_3rd server detected (PID: $($srv.ProcessId)). Terminating..." -ForegroundColor Yellow
            Stop-Process -Id $srv.ProcessId -Force -ErrorAction SilentlyContinue
            $terminated = $true
        }
    }
} catch {}

# 1-B. Terminate any remaining process occupying port 8000
try {
    $portConnections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($portConnections) {
        $occupyingPids = $portConnections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pidToKill in $occupyingPids) {
            if ($pidToKill -gt 0) {
                $proc = Get-Process -Id $pidToKill -ErrorAction SilentlyContinue
                $procName = if ($proc) { $proc.ProcessName } else { "Unknown" }
                Write-Host "[!] Port $Port is in use by '$procName' (PID: $pidToKill). Terminating..." -ForegroundColor Yellow
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                $terminated = $true
            }
        }
    }
} catch {}

if ($terminated) {
    Start-Sleep -Milliseconds 700
    Write-Host "[✓] Previous instance cleaned up successfully." -ForegroundColor Green
    Write-Host ""
}

# -----------------------------------------------------------------------
# 2. Detect Python Environment
# -----------------------------------------------------------------------
$PythonExe = "$PSScriptRoot\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
    Write-Host "[*] Virtual environment (.venv) not found. Using system python." -ForegroundColor Yellow
} else {
    Write-Host "[*] Python virtual environment (.venv) detected: $PythonExe" -ForegroundColor DarkGray
}

$ServerUrl = "http://127.0.0.1:8000/"
Write-Host "[*] Main Dashboard : $ServerUrl" -ForegroundColor Cyan
Write-Host "[*] API Swagger    : ${ServerUrl}docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Launching web browser automatically..." -ForegroundColor Gray
Write-Host "[*] Press Ctrl+C at any time to terminate the server." -ForegroundColor Yellow
Write-Host ""

# Open web browser after 1.5 seconds via background job
Start-Job -ScriptBlock {
    Start-Sleep -Milliseconds 1500
    Start-Process "http://127.0.0.1:8000/"
} | Out-Null

# Run Uvicorn server in foreground (supports graceful exit via Ctrl+C)
& $PythonExe -m uvicorn src.api.server:app --host 127.0.0.1 --port 8000 --reload
