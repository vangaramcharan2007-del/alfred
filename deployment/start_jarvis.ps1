# ==============================================================================
# Jarvis X Production Background Service Startup Script
# PowerShell 5.1+ / 7.0+
# ==============================================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                    JARVIS X BACKGROUND DAEMON LAUNCHER                         " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Verify Environment
$PythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Host "[-] ERROR: 'python' not found in PATH." -ForegroundColor Red
    exit 1
}

# 2. Check if already alive via IPC
Write-Host "[*] Checking if daemon is already running..." -ForegroundColor Yellow
$PingScript = "from jarvisx.runtime.ipc_client import IPCClient; ok, lat = IPCClient().ping(); print('ALIVE:' + str(round(lat, 2)) if ok else 'OFFLINE')"
$PingResult = & python -c $PingScript 2>&1

if ($PingResult -like "ALIVE*") {
    $lat = ($PingResult -split ":")[1]
    Write-Host "[!] Jarvis X Daemon is ALREADY RUNNING (IPC Ping: ${lat}ms)." -ForegroundColor Green
    & python -m jarvisx daemon status
    exit 0
}

# 3. Launch Daemon as Detached Background Process
Write-Host "[*] Launching Jarvis X Daemon Subsystem in background..." -ForegroundColor Cyan
$DaemonProcess = Start-Process -FilePath "python" -ArgumentList "-m jarvisx daemon start --block" -WindowStyle Hidden -PassThru
Write-Host "    Spawned Daemon Process (PID: $($DaemonProcess.Id))" -ForegroundColor Gray

# 4. Wait & Verify Loopback IPC Connection
Start-Sleep -Seconds 2
$StatusScript = "from jarvisx.runtime.ipc_client import IPCClient; ok, st, lat = IPCClient().get_status(); print('STATUS_OK:' + str(st.get('pid','UNKNOWN')) + ':' + str(st.get('port',10404)) + ':' + str(st.get('presence_state','READY')) + ':' + str(round(lat,2)) if ok else 'STATUS_FAILED')"
$StatusCheck = & python -c $StatusScript 2>&1

if ($StatusCheck -like "STATUS_OK*") {
    $parts = $StatusCheck -split ":"
    $pidVal = $parts[1]
    $portVal = $parts[2]
    $presenceVal = $parts[3]
    $latVal = $parts[4]

    Write-Host "`n================================================================================" -ForegroundColor Green
    Write-Host "               JARVIS X DAEMON SUCCESSFULLY STARTED & READY                     " -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "  [+] Process ID (PID)   : $pidVal" -ForegroundColor White
    Write-Host "  [+] IPC Socket Port    : 127.0.0.1:$portVal" -ForegroundColor White
    Write-Host "  [+] Presence State     : $presenceVal" -ForegroundColor Cyan
    Write-Host "  [+] IPC Loopback Lat   : ${latVal}ms" -ForegroundColor Green
    Write-Host "  [+] Log File Location  : var/logs/daemon.log" -ForegroundColor Gray
    Write-Host "================================================================================`n" -ForegroundColor Green
} else {
    Write-Host "[-] WARNING: Daemon started but IPC probe timed out. Inspecting var/logs/daemon.log..." -ForegroundColor Yellow
    if (Test-Path "var/logs/daemon.log") {
        Get-Content "var/logs/daemon.log" -Tail 10
    }
}
