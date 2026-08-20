# ==============================================================================
# JARVIS X: WORKER NODE 4 ONBOARDING (ASUS TUF - RTX 3050, 16GB RAM, AMD Ryzen)
# ==============================================================================
# Send this file to Friend 4. They run it ONCE in PowerShell (no admin needed).
# It sets up Ollama silently in the background forever, surviving reboots.
# ==============================================================================

param ([string]$AuthKey = "")
$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n========================================================"
Write-Host "  JARVIS X: WORKER NODE 4 - ASUS TUF ONBOARDING"
Write-Host "========================================================`n"

# 1. Install Tailscale & Ollama
Write-Host "[1/5] Installing Tailscale and Ollama..."
winget install Tailscale.Tailscale Ollama.Ollama --accept-package-agreements --accept-source-agreements --silent

# 2. Join Tailscale Mesh (Charan will provide the auth key)
Write-Host "[2/5] Joining Jarvis X private mesh network..."
if ($AuthKey -ne "") {
    tailscale up --authkey=$AuthKey --unattended --reset
} else {
    Write-Host "  [!] No auth key provided. Ask Charan for the Tailscale auth key."
    Write-Host "  [!] Then run: tailscale up --authkey=YOUR_KEY --unattended --reset"
}

# 3. Set permanent environment variables (user-level, no admin needed)
Write-Host "[3/5] Setting permanent Ollama environment variables..."
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', '*', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE', '24h', 'User')
$env:OLLAMA_HOST = '0.0.0.0:11434'
$env:OLLAMA_ORIGINS = '*'
$env:OLLAMA_KEEP_ALIVE = '24h'

# 4. Install zero-privilege VBS startup (no admin needed)
Write-Host "[4/5] Installing silent background auto-start on login..."
$startupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$vbsPath = "$startupDir\JarvisDaemon.vbs"
$vbsContent = @"
Set ws = CreateObject("WScript.Shell")
ws.Environment("PROCESS")("OLLAMA_HOST") = "0.0.0.0:11434"
ws.Environment("PROCESS")("OLLAMA_ORIGINS") = "*"
ws.Environment("PROCESS")("OLLAMA_KEEP_ALIVE") = "24h"
ws.Run "ollama serve", 0, False
"@
Set-Content -Path $vbsPath -Value $vbsContent -Encoding ASCII
Write-Host "  [+] Auto-start installed: $vbsPath"

# 5. Pull the model & start Ollama now
Write-Host "[5/5] Pulling AI model (qwen2.5-coder:7b ~4.7GB) and starting Ollama..."
Write-Host "  [i] This download may take 10-20 minutes depending on your internet speed."
Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 5
ollama pull qwen2.5-coder:7b-instruct

# Done - print Tailscale IP
Write-Host "`n========================================================"
Write-Host "  SUCCESS! Worker Node 4 is live!"
Write-Host "  Send this IP to Charan:"
tailscale ip -4
Write-Host "========================================================"
