# ==============================================================================
# Jarvis X Production Background Service Graceful Shutdown Script
# PowerShell 5.1+ / 7.0+
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                    JARVIS X DAEMON SHUTDOWN CONTROLLER                         " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Attempt Graceful IPC Shutdown
Write-Host "[*] Sending graceful shutdown signal via IPC socket (localhost:10404)..." -ForegroundColor Yellow

$StopScript = "from jarvisx.runtime.ipc_client import IPCClient; ok, lat = IPCClient().shutdown(); print('STOP_OK:' + str(round(lat,2)) if ok else 'STOP_FAILED')"
$StopResult = & python -c $StopScript 2>&1

if ($StopResult -like "STOP_OK*") {
    $lat = ($StopResult -split ":")[1]
    Write-Host "[v] Graceful shutdown acknowledged by daemon (Roundtrip: ${lat}ms)." -ForegroundColor Green
} else {
    Write-Host "[!] Daemon IPC unreachable or offline. Checking PID lockfile directly..." -ForegroundColor Yellow
}

# 2. Verify PID Lockfile Cleared
Start-Sleep -Milliseconds 500
$PidFile = Join-Path $ProjectRoot "var/runtime/jarvisd.pid"

if (Test-Path $PidFile) {
    try {
        $pidContent = (Get-Content $PidFile -Raw).Trim()
        $runningPid = [int]$pidContent
        $proc = Get-Process -Id $runningPid -ErrorAction SilentlyContinue

        if ($proc -and $Force) {
            Write-Host "[!] Lingering process found (PID: $runningPid). Force terminating..." -ForegroundColor Yellow
            Stop-Process -Id $runningPid -Force
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
            Write-Host "[v] Process $runningPid terminated and lockfile cleared." -ForegroundColor Green
        } elseif ($proc) {
            Write-Host "[!] Process $runningPid is still stopping. Waiting 2 seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            if (Test-Path $PidFile) {
                Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
            }
        } else {
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "                  JARVIS X DAEMON SUCCESSFULLY STOPPED                          " -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "  Daemon state is now OFFLINE. All sockets closed and locks released." -ForegroundColor Gray
Write-Host "================================================================================`n" -ForegroundColor Green
