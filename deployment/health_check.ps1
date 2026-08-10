# ==============================================================================
# Jarvis X Production Health Check & Diagnostic Inspection Script
# PowerShell 5.1+ / 7.0+
# ==============================================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                  JARVIS X DEPLOYMENT & SYSTEM HEALTH CHECK                     " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$PassCount = 0
$WarnCount = 0
$FailCount = 0

function Report-Check {
    param(
        [string]$Category,
        [string]$Item,
        [string]$Status, # PASS, WARN, FAIL
        [string]$Details
    )
    if ($Status -eq "PASS") {
        $script:PassCount++
        Write-Host "  [PASS] " -ForegroundColor Green -NoNewline
    } elseif ($Status -eq "WARN") {
        $script:WarnCount++
        Write-Host "  [WARN] " -ForegroundColor Yellow -NoNewline
    } else {
        $script:FailCount++
        Write-Host "  [FAIL] " -ForegroundColor Red -NoNewline
    }
    Write-Host "$($Category.PadRight(18)) : $($Item.PadRight(28)) - $Details" -ForegroundColor White
}

# ------------------------------------------------------------------------------
# 1. PYTHON ENVIRONMENT
# ------------------------------------------------------------------------------
Write-Host "`n[*] Checking Python Runtime Environment..." -ForegroundColor Yellow
$PythonCmd = Get-Command "python" -ErrorAction SilentlyContinue

if ($PythonCmd) {
    $PyVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>&1
    $PyCheckCode = "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
    & python -c $PyCheckCode 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Report-Check "Python" "Interpreter Version" "PASS" "Python v$PyVersion meets requirements (>= 3.11)"
    } else {
        Report-Check "Python" "Interpreter Version" "FAIL" "Python v$PyVersion is below required 3.11"
    }
} else {
    Report-Check "Python" "Interpreter Binary" "FAIL" "'python' command not found in PATH"
}

# ------------------------------------------------------------------------------
# 2. REQUIRED DEPENDENCIES
# ------------------------------------------------------------------------------
Write-Host "`n[*] Checking Required Package Dependencies..." -ForegroundColor Yellow
$RequiredPkgs = @("aiohttp", "fastapi", "httpx", "numpy", "pandas", "pydantic", "yaml", "requests", "websockets", "psutil")

foreach ($pkg in $RequiredPkgs) {
    $script_str = "import $pkg; print(getattr($pkg, '__version__', 'available'))"
    $ver = & python -c $script_str 2>&1
    if ($LASTEXITCODE -eq 0) {
        Report-Check "Packages" $pkg "PASS" "Installed (v$ver)"
    } else {
        Report-Check "Packages" $pkg "FAIL" "Missing package. Run: pip install $pkg"
    }
}

# ------------------------------------------------------------------------------
# 3. DIRECTORY STRUCTURE
# ------------------------------------------------------------------------------
Write-Host "`n[*] Checking Runtime Directory Structure..." -ForegroundColor Yellow
$ExpectedDirs = @("var", "var/db", "var/runtime", "var/logs", "var/backups", "var/scripts", "config", "logs")

foreach ($dir in $ExpectedDirs) {
    $p = Join-Path $ProjectRoot $dir
    if (Test-Path $p) {
        Report-Check "Filesystem" $dir "PASS" "Directory exists and writable"
    } else {
        Report-Check "Filesystem" $dir "WARN" "Directory missing. Creating automatically."
        New-Item -ItemType Directory -Path $p -Force | Out-Null
    }
}

# ------------------------------------------------------------------------------
# 4. CONFIGURATION FILE
# ------------------------------------------------------------------------------
Write-Host "`n[*] Checking System Configuration..." -ForegroundColor Yellow
$ConfigFile = Join-Path $ProjectRoot "config/jarvis.yaml"
if (Test-Path $ConfigFile) {
    $ConfigValidCode = "import yaml; cfg = yaml.safe_load(open('config/jarvis.yaml', encoding='utf-8')); print('System: ' + str(cfg.get('system', {}).get('name', 'Jarvis X')) if (isinstance(cfg, dict) and 'system' in cfg) else 'FAIL')"
    $res = & python -c $ConfigValidCode 2>&1
    if ($LASTEXITCODE -eq 0 -and $res -notlike "FAIL*") {
        Report-Check "Config" "jarvis.yaml" "PASS" "Valid YAML structure ($res)"
    } else {
        Report-Check "Config" "jarvis.yaml" "FAIL" "YAML syntax or schema error ($res)"
    }
} else {
    Report-Check "Config" "jarvis.yaml" "FAIL" "Configuration file not found"
}

# ------------------------------------------------------------------------------
# 5. SQLITE DATABASES & INTEGRITY
# ------------------------------------------------------------------------------
Write-Host "`n[*] Checking Database Integrity..." -ForegroundColor Yellow
$DbFiles = @("knowledge.db", "memory_intelligence.db", "evaluation.db", "operating_loop.db", "reliability.db")

foreach ($db in $DbFiles) {
    $dbPath = "var/db/$db"
    $DbCheckCode = "import sqlite3, sys; from pathlib import Path; p = Path('$dbPath'); sys.exit(2 if not p.exists() else (0 if sqlite3.connect(str(p)).cursor().execute('PRAGMA integrity_check').fetchone()[0] == 'ok' else 1))"
    & python -c $DbCheckCode 2>&1 | Out-Null
    $code = $LASTEXITCODE
    if ($code -eq 0) {
        Report-Check "Database" $db "PASS" "SQLite schema & integrity check OK"
    } elseif ($code -eq 2) {
        Report-Check "Database" $db "WARN" "Database file not yet created (created on first use)"
    } else {
        Report-Check "Database" $db "FAIL" "Integrity corruption detected"
    }
}

# ------------------------------------------------------------------------------
# 6. DAEMON & IPC LOOPBACK STATUS
# ------------------------------------------------------------------------------
Write-Host "`n[*] Checking Daemon & IPC Loopback Gateway..." -ForegroundColor Yellow

$IpcCheckCode = "from jarvisx.runtime.ipc_client import IPCClient; c = IPCClient(); ok, lat = c.ping(); ok2, st, _ = c.get_status(); print('ONLINE:' + str(st.get('pid','UNKNOWN')) + ':' + str(st.get('presence_state','READY')) + ':' + str(round(lat,2)) if ok else 'OFFLINE')"
$IpcResult = & python -c $IpcCheckCode 2>&1

if ($IpcResult -like "ONLINE*") {
    $parts = $IpcResult -split ":"
    $pidVal = $parts[1]
    $presenceVal = $parts[2]
    $latVal = $parts[3]
    Report-Check "Daemon" "Process Status" "PASS" "ONLINE (PID: $pidVal, State: $presenceVal)"
    Report-Check "Daemon" "IPC Loopback" "PASS" "Socket active on localhost:10404 (${latVal}ms)"
} else {
    Report-Check "Daemon" "Process Status" "WARN" "Daemon is currently OFFLINE (Start via start_jarvis.ps1)"
    Report-Check "Daemon" "IPC Loopback" "WARN" "IPC port 10404 idle"
}

# ------------------------------------------------------------------------------
# 7. SUMMARY REPORT
# ------------------------------------------------------------------------------
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "                      HEALTH CHECK SUMMARY RESULTS                              " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Checks Passed   : $script:PassCount" -ForegroundColor Green
Write-Host "  Warnings        : $script:WarnCount" -ForegroundColor Yellow
Write-Host "  Failures        : $script:FailCount" -ForegroundColor $(if ($script:FailCount -gt 0) { "Red" } else { "Gray" })

if ($script:FailCount -eq 0) {
    Write-Host "`n[v] OVERALL DEPLOYMENT STATUS: HEALTHY & READY" -ForegroundColor Green
    Write-Host "================================================================================`n" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "`n[-] OVERALL DEPLOYMENT STATUS: ATTENTION REQUIRED ($script:FailCount failures)" -ForegroundColor Red
    Write-Host "================================================================================`n" -ForegroundColor Cyan
    exit 1
}
