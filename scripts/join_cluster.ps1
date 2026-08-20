# ==============================================================================
# JARVIS X: 1-CLICK UNIVERSAL GPU WORKER NODE ONBOARDING
# ==============================================================================
# Can be run via:
# irm https://raw.githubusercontent.com/vangaramcharan2007-del/alfred/main/scripts/join_cluster.ps1 | iex
# ==============================================================================

param (
    [string]$AuthKey = ""
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "   JARVIS X: UNIVERSAL GPU WORKER NODE ONBOARDING" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

# 1. Install Tailscale & Ollama silently via Winget if missing
if (-not (Get-Command tailscale -ErrorAction SilentlyContinue)) {
    Write-Host "[1/5] Installing Tailscale..." -ForegroundColor Yellow
    winget install Tailscale.Tailscale --accept-package-agreements --accept-source-agreements --silent
} else {
    Write-Host "[1/5] Tailscale is already installed!" -ForegroundColor Green
}

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "[2/5] Installing Ollama..." -ForegroundColor Yellow
    winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements --silent
} else {
    Write-Host "[2/5] Ollama is already installed!" -ForegroundColor Green
}

# 2. Join Tailscale Mesh
Write-Host "[3/5] Connecting to Charan's Jarvis X Mesh Network..." -ForegroundColor Yellow
if ($AuthKey -ne "") {
    tailscale up --authkey=$AuthKey --unattended --reset
} else {
    # If no key passed in param, prompt user or check if already running
    $currentIp = tailscale ip -4 2>$null
    if (-not $currentIp) {
        $inputKey = Read-Host "Paste the Tailscale Auth Key sent by Charan"
        if ($inputKey) {
            tailscale up --authkey=$inputKey --unattended --reset
        }
    }
}

# 3. Configure Permanent Silent Background Server (User-Level, Zero Admin Needed)
Write-Host "[4/5] Configuring background persistence..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', '*', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE', '24h', 'User')
$env:OLLAMA_HOST = '0.0.0.0:11434'
$env:OLLAMA_ORIGINS = '*'
$env:OLLAMA_KEEP_ALIVE = '24h'

# Create silent startup VBS in user's Startup folder
$startupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$vbsPath = "$startupDir\JarvisDaemon.vbs"
$vbsContent = @"
Set ws = CreateObject("WScript.Shell")
ws.Environment("PROCESS")("OLLAMA_HOST") = "0.0.0.0:11434"
ws.Environment("PROCESS")("OLLAMA_ORIGINS") = "*"
ws.Environment("PROCESS")("OLLAMA_KEEP_ALIVE") = "24h"
ws.Run "powershell -WindowStyle Hidden -ExecutionPolicy Bypass -Command `"Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden`"", 0, False
"@
Set-Content -Path $vbsPath -Value $vbsContent -Encoding ASCII

# Kill existing GUI instances and start silent background daemon
Stop-Process -Name "ollama" -Force 2>$null
Start-Process powershell -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -Command `"`$env:OLLAMA_HOST='0.0.0.0:11434'; `$env:OLLAMA_ORIGINS='*'; `$env:OLLAMA_KEEP_ALIVE='24h'; Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden`"" -WindowStyle Hidden
Start-Sleep -Seconds 3

# 4. Pull Optimized RTX 3050 Coding & Reasoning Model
Write-Host "[5/5] Pulling RTX 3050 Optimized Model (qwen2.5-coder:7b-instruct)..." -ForegroundColor Yellow
Write-Host "      (This runs in background; please keep window open until done)" -ForegroundColor Gray
ollama pull qwen2.5-coder:7b-instruct

# 5. Done! Print IP
$nodeIp = (tailscale ip -4 2>$null)
Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "   SUCCESS! This node is now a Jarvis X Worker!" -ForegroundColor Green
Write-Host "   Send this Tailscale IP to Charan:" -ForegroundColor Yellow
Write-Host "   >> $nodeIp <<" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Green
