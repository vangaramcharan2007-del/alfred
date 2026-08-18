# ==============================================================================
# JARVIS X: 1-Click Silent & Permanent Worker Node Deployment (For Friends)
# ==============================================================================
# Run ONCE in Administrator PowerShell on your friend's laptop.
# Configures Ollama to run silently in the background forever (survives reboots).
# ==============================================================================

param (
    [string]$AuthKey = "",
    [switch]$HighVramNode = $true
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  🎩 JARVIS X: SILENT BACKGROUND WORKER NODE DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

# 1. Install Tailscale & Ollama silently
Write-Host "[1/5] Installing / Updating Tailscale & Ollama silently..." -ForegroundColor Yellow
winget install Tailscale.Tailscale Ollama.Ollama --accept-package-agreements --accept-source-agreements --silent

# 2. Join Tailscale Mesh
Write-Host "[2/5] Connecting to Jarvis X Private Tailnet..." -ForegroundColor Yellow
if ($AuthKey -ne "") {
    tailscale up --authkey=$AuthKey --unattended --reset
} else {
    tailscale up --unattended --reset
}

# 3. Set Permanent Machine-Level Environment Variables
Write-Host "[3/5] Setting permanent background environment variables..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', '*', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE', '24h', 'Machine')
$env:OLLAMA_HOST = '0.0.0.0:11434'
$env:OLLAMA_ORIGINS = '*'
$env:OLLAMA_KEEP_ALIVE = '24h'

# 4. Create Permanent Windows Boot Task Scheduler (Runs Hidden Forever on Startup)
Write-Host "[4/5] Registering permanent Windows background startup service..." -ForegroundColor Yellow
$taskName = "JarvisWorkerDaemon"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -Command `"`$env:OLLAMA_HOST='0.0.0.0:11434'; `$env:OLLAMA_ORIGINS='*'; `$env:OLLAMA_KEEP_ALIVE='24h'; Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 3650) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false 2>$null
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Jarvis X Background Compute Service" -User $env:USERNAME 2>$null

# Kill any existing foreground instance and start silent daemon
Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
Start-Process "powershell.exe" -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -Command `"`$env:OLLAMA_HOST='0.0.0.0:11434'; Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden`"" -WindowStyle Hidden

Start-Sleep -Seconds 3

# 5. Background Pull Heavy Models (Doesn't block user)
Write-Host "[5/5] Initiating background model preload..." -ForegroundColor Yellow
if ($HighVramNode) {
    # Start background job to pull models without freezing terminal
    Start-Job -ScriptBlock {
        ollama pull deepseek-r1:14b
        ollama pull qwen2.5-coder:14b
        ollama pull qwen2.5-vl:7b
    } | Out-Null
    Write-Host "      -> Models queued for background download (RTX 5050 tier)." -ForegroundColor Gray
}

# Output Tailscale IP for Master Node
$tsIp = tailscale ip -4

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "  ✅ ALL SET! RUNNING SILENTLY IN THE BACKGROUND FOREVER" -ForegroundColor Green
Write-Host "  🛡️  Zero popups. Survives restarts automatically." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  👉 COPY AND SEND THIS TAILSCALE IP TO YOUR FRIEND:" -ForegroundColor White
Write-Host "     $tsIp" -ForegroundColor Yellow -BackgroundColor Black
Write-Host "========================================================`n" -ForegroundColor Green
