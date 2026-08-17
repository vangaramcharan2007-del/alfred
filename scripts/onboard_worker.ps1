# ==============================================================================
# JARVIS X: 1-Click Worker Node Onboarding Script (For Friends' Laptops)
# ==============================================================================
# Run this script in an Administrator PowerShell window on the friend's laptop.
# ==============================================================================

param (
    [string]$AuthKey = ""
)

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  🎩 JARVIS X: WORKER NODE MESH ONBOARDING" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

# 1. Install Tailscale & Ollama silently if not installed
Write-Host "[1/4] Installing / Verifying Tailscale & Ollama..." -ForegroundColor Yellow
winget install Tailscale.Tailscale Ollama.Ollama --accept-package-agreements --accept-source-agreements --silent

# 2. Connect to the Tailscale Mesh
Write-Host "[2/4] Connecting to Jarvis X Private Tailnet..." -ForegroundColor Yellow
if ($AuthKey -ne "") {
    tailscale up --authkey=$AuthKey --reset
} else {
    tailscale up --reset
}

# 3. Expose Ollama to the Tailscale network (0.0.0.0:11434)
Write-Host "[3/4] Exposing Ollama API to the mesh network..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'Machine')
$env:OLLAMA_HOST = '0.0.0.0:11434'

# 4. Restart Ollama in background
Write-Host "[4/4] Starting Ollama server..." -ForegroundColor Yellow
Stop-Process -Name "ollama" -ErrorAction SilentlyContinue
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 2

# Output the Tailscale IP
$tsIp = tailscale ip -4

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "  ✅ WORKER NODE ONLINE & READY FOR MESH INFERENCE!" -ForegroundColor Green
Write-Host "  👉 SEND THIS TAILSCALE IP TO NANI (MASTER CONTROL PLANE):" -ForegroundColor White
Write-Host "     $tsIp" -ForegroundColor Yellow -BackgroundColor Black
Write-Host "========================================================`n" -ForegroundColor Green
