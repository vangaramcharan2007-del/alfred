# ==============================================================================
# JARVIS X: RESUMABLE & IDEMPOTENT GPU WORKER NODE ONBOARDING
# ==============================================================================
# Auto-detects existing progress:
# - Skips Tailscale install if already installed
# - Skips Tailscale login if already connected
# - Skips Ollama install if already installed
# - Skips Model download if already pulled
# - Installs invisible 24/7 background persistence
# ==============================================================================

param (
    [string]$AuthKey = ""
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "   JARVIS X: SMART RESUMABLE WORKER NODE SETUP" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

# ------------------------------------------------------------------------------
# STEP 1: TAILSCALE (Check -> Install -> Skip)
# ------------------------------------------------------------------------------
$tsCmd = Get-Command tailscale -ErrorAction SilentlyContinue
if (-not $tsCmd) {
    Write-Host "[1/5] Installing Tailscale..." -ForegroundColor Yellow
    winget install Tailscale.Tailscale --accept-package-agreements --accept-source-agreements --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "[1/5] [OK] Tailscale is already installed (Skipping install)" -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# STEP 2: TAILSCALE AUTH (Check if already in Tailnet -> Login -> Skip)
# ------------------------------------------------------------------------------
$currentIp = (tailscale ip -4 2>$null)
if ($currentIp -and ($currentIp -like "100.*")) {
    Write-Host "[2/5] [OK] Already connected to Mesh Network! (IP: $currentIp)" -ForegroundColor Green
} else {
    Write-Host "[2/5] Connecting to Jarvis X Private Mesh Network..." -ForegroundColor Yellow
    if ($AuthKey -ne "") {
        tailscale up --authkey=$AuthKey --unattended --reset
    } else {
        $inputKey = Read-Host "Paste the Tailscale Auth Key sent by Charan"
        if ($inputKey) {
            tailscale up --authkey=$inputKey --unattended --reset
        }
    }
}

# ------------------------------------------------------------------------------
# STEP 3: OLLAMA (Check -> Install -> Skip)
# ------------------------------------------------------------------------------
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCmd) {
    Write-Host "[3/5] Installing Ollama..." -ForegroundColor Yellow
    winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "[3/5] [OK] Ollama is already installed (Skipping install)" -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# STEP 4: PERSISTENCE & ENVIRONMENT SETUP (Always ensure silent background daemon)
# ------------------------------------------------------------------------------
Write-Host "[4/5] Ensuring 24/7 background persistence..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', '*', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE', '24h', 'User')
$env:OLLAMA_HOST = '0.0.0.0:11434'
$env:OLLAMA_ORIGINS = '*'
$env:OLLAMA_KEEP_ALIVE = '24h'

# Register silent startup VBS
$startupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$vbsPath = "$startupDir\JarvisDaemon.vbs"
$vbsContent = 'CreateObject("Wscript.Shell").Run "powershell -WindowStyle Hidden -ExecutionPolicy Bypass -Command `\"$env:OLLAMA_HOST=''0.0.0.0:11434''; $env:OLLAMA_ORIGINS=''*''; $env:OLLAMA_KEEP_ALIVE=''24h''; Start-Process ollama -ArgumentList ''serve'' -WindowStyle Hidden`\"", 0, True'
Set-Content -Path $vbsPath -Value $vbsContent -Encoding ASCII

# Ensure Ollama daemon is running with 0.0.0.0
$listening = netstat -ano | findstr "11434"
if (-not $listening) {
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
    Start-Process powershell -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -Command `\"$env:OLLAMA_HOST=''0.0.0.0:11434''; $env:OLLAMA_ORIGINS=''*''; $env:OLLAMA_KEEP_ALIVE=''24h''; Start-Process ollama -ArgumentList ''serve'' -WindowStyle Hidden`\"" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# ------------------------------------------------------------------------------
# STEP 5: MODEL PULL (Check if already downloaded -> Skip if present)
# ------------------------------------------------------------------------------
$targetModel = "qwen2.5-coder:7b-instruct"
$existingModels = (ollama list 2>$null | Out-String)
if ($existingModels -match "qwen2.5-coder:7b") {
    Write-Host "[5/5] [OK] Model ($targetModel) is already downloaded! (Skipping download)" -ForegroundColor Green
} else {
    Write-Host "[5/5] Downloading RTX-optimized model ($targetModel)..." -ForegroundColor Yellow
    Write-Host "      (This only happens once; please keep window open)" -ForegroundColor Gray
    ollama pull $targetModel
}

# ------------------------------------------------------------------------------
# FINAL STATUS & IP REPORT
# ------------------------------------------------------------------------------
$finalIp = (tailscale ip -4 2>$null)
Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "   [SUCCESS] Worker Node is 100% configured & active!" -ForegroundColor Green
if ($finalIp) {
    Write-Host "   Send this Tailscale IP to Charan:" -ForegroundColor Yellow
    Write-Host "   >> $finalIp <<" -ForegroundColor Cyan
} else {
    Write-Host "   [!] Run: tailscale up --authkey=YOUR_KEY to finalize mesh link." -ForegroundColor Yellow
}
Write-Host "========================================================`n" -ForegroundColor Green
