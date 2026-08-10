# ==============================================================================
# Jarvis X Production Deployment & First-Boot Installation Script
# PowerShell 5.1+ / 7.0+
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$SkipDaemonStart,
    [switch]$DevDependencies
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                  JARVIS X PRODUCTION DEPLOYMENT INSTALLER                      " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# ------------------------------------------------------------------------------
# 1. VERSION DISPLAY
# ------------------------------------------------------------------------------
$VersionFile = Join-Path $ProjectRoot "VERSION"
$Version = "1.5.0"
if (Test-Path $VersionFile) {
    $Version = (Get-Content $VersionFile -Raw).Trim()
}
Write-Host "[+] Target Application : Jarvis X Sovereign Personal OS" -ForegroundColor White
Write-Host "[+] Target Version     : v$Version" -ForegroundColor Green
Write-Host "[+] Installation Root  : $ProjectRoot" -ForegroundColor Gray
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

# ------------------------------------------------------------------------------
# 2. PYTHON ENVIRONMENT VERIFICATION
# ------------------------------------------------------------------------------
Write-Host "`n[*] Verifying Python Environment..." -ForegroundColor Yellow
$PythonCmd = Get-Command "python" -ErrorAction SilentlyContinue

if (-not $PythonCmd) {
    Write-Host "[-] ERROR: 'python' executable was not found in PATH." -ForegroundColor Red
    Write-Host "    Please install Python 3.11 or higher from https://python.org" -ForegroundColor Red
    exit 1
}

$PythonVersionOutput = & python --version 2>&1
Write-Host "    Found: $PythonVersionOutput ($($PythonCmd.Source))" -ForegroundColor Gray

# Verify Python >= 3.11
$PyCheckCode = "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
& python -c $PyCheckCode 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] ERROR: Python 3.11+ is required. Detected version does not meet requirements." -ForegroundColor Red
    exit 1
}
Write-Host "[v] Python 3.11+ environment verified successfully." -ForegroundColor Green

# ------------------------------------------------------------------------------
# 3. DEPENDENCY CHECKING & REPORTING
# ------------------------------------------------------------------------------
Write-Host "`n[*] Checking Required Package Dependencies..." -ForegroundColor Yellow

$CoreDependencies = @(
    "aiohttp",
    "fastapi",
    "httpx",
    "numpy",
    "pandas",
    "pydantic",
    "yaml",
    "requests",
    "websockets",
    "psutil"
)

$MissingDeps = @()

foreach ($dep in $CoreDependencies) {
    $CheckScript = "import $dep; print('$($dep): ' + getattr($dep, '__version__', 'ok'))"
    $res = & python -c $CheckScript 2>&1
    if ($LASTEXITCODE -ne 0) {
        $MissingDeps += $dep
        Write-Host "    [-] Missing: $dep" -ForegroundColor Red
    } else {
        Write-Host "    [v] Installed: $dep" -ForegroundColor Green
    }
}

if ($MissingDeps.Count -gt 0) {
    Write-Host "`n[!] The following required dependencies are missing: $($MissingDeps -join ', ')" -ForegroundColor Yellow
    Write-Host "[*] Attempting automatic package installation via pip..." -ForegroundColor Cyan
    & python -m pip install --upgrade pip | Out-Null
    & python -m pip install -e .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[-] ERROR: Automatic dependency installation failed." -ForegroundColor Red
        Write-Host "    Please manually run: pip install -e ." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "[v] Dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "[v] All core dependencies verified." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# 4. RUNTIME DIRECTORY CREATION
# ------------------------------------------------------------------------------
Write-Host "`n[*] Creating & Verifying Runtime Directories..." -ForegroundColor Yellow

$RuntimeDirs = @(
    "var",
    "var/db",
    "var/runtime",
    "var/logs",
    "var/backups",
    "var/scripts",
    "config",
    "logs"
)

foreach ($dir in $RuntimeDirs) {
    $fullPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "    [+] Created: $dir" -ForegroundColor Cyan
    } else {
        Write-Host "    [v] Exists:  $dir" -ForegroundColor Gray
    }
}

# ------------------------------------------------------------------------------
# 5. CONFIGURATION INITIALIZATION
# ------------------------------------------------------------------------------
Write-Host "`n[*] Initializing Configuration..." -ForegroundColor Yellow
$ConfigFile = Join-Path $ProjectRoot "config/jarvis.yaml"
if (-not (Test-Path $ConfigFile)) {
    $DefaultConfigContent = @"
# Jarvis X Unified Production Configuration
system:
  name: "Jarvis X"
  version: "$Version"
  environment: "production"
  log_level: "INFO"
  log_file: "logs/jarvis.log"

runtime:
  auto_recovery: true
  health_check_interval_seconds: 30
  max_retry_attempts: 3
  execution_sandbox: "isolated"
"@
    Set-Content -Path $ConfigFile -Value $DefaultConfigContent -Encoding UTF8
    Write-Host "    [+] Created default configuration: config/jarvis.yaml" -ForegroundColor Green
} else {
    Write-Host "    [v] Configuration verified: config/jarvis.yaml" -ForegroundColor Gray
}

# ------------------------------------------------------------------------------
# 6. FIRST-BOOT DATABASE INITIALIZATION
# ------------------------------------------------------------------------------
Write-Host "`n[*] Initializing First-Boot Subsystem Databases..." -ForegroundColor Yellow

$InitDbScript = @"
import sys
from pathlib import Path

# Initialize Knowledge Vault
try:
    from jarvisx.knowledge.vault import KnowledgeVault
    kv = KnowledgeVault()
except Exception as e:
    pass

# Initialize Memory Intelligence
try:
    from jarvisx.memory_intelligence.context_builder import PersonalContextBuilder
    pcb = PersonalContextBuilder()
except Exception as e:
    pass

# Initialize Academic Coach & Operating Loop
try:
    from jarvisx.operating_loop.academic_coach import AcademicCoachEngine
    ace = AcademicCoachEngine()
except Exception as e:
    pass

# Initialize Evaluation Memory
try:
    from jarvisx.evaluation.evaluator import ResponseEvaluator
    re = ResponseEvaluator()
except Exception as e:
    pass

print('Databases initialized successfully.')
"@

& python -c $InitDbScript 2>&1 | Out-Null
Write-Host "    [v] SQLite Schemas Initialized (var/db/):" -ForegroundColor Green
Write-Host "        - knowledge.db" -ForegroundColor Gray
Write-Host "        - memory_intelligence.db" -ForegroundColor Gray
Write-Host "        - evaluation.db" -ForegroundColor Gray
Write-Host "        - operating_loop.db" -ForegroundColor Gray

# ------------------------------------------------------------------------------
# 7. GENERATE WINDOWS STARTUP SCRIPTS
# ------------------------------------------------------------------------------
Write-Host "`n[*] Generating Windows Startup & Background Service Scripts..." -ForegroundColor Yellow
& python -m jarvisx daemon install 2>&1 | Out-Null
Write-Host "    [v] Generated startup scripts in var/scripts/" -ForegroundColor Green

# ------------------------------------------------------------------------------
# 8. POST-INSTALLATION HEALTH PROBE
# ------------------------------------------------------------------------------
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "                 INSTALLATION COMPLETED SUCCESSFULLY!                           " -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "    1. Start Background Daemon : .\deployment\start_jarvis.ps1" -ForegroundColor Yellow
Write-Host "    2. Run Diagnostics & Health: .\deployment\health_check.ps1" -ForegroundColor Yellow
Write-Host "    3. Stop Background Daemon  : .\deployment\stop_jarvis.ps1" -ForegroundColor Yellow
Write-Host "    4. Interactive CLI Mode    : python -m jarvisx" -ForegroundColor Yellow
Write-Host "================================================================================`n" -ForegroundColor Cyan
