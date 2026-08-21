# ==============================================================================
# JARVIS PROTOCOL: FUSION MODE MASTER LAUNCHER (Windows PowerShell)
# Bootstraps Barehands Spatial UI + Friday FastMCP + LiveKit / Offline Agent
# ==============================================================================

$RootDir = $PSScriptRoot
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  🚀 JARVIS PROTOCOL: MASTER FUSION LAUNCH SEQUENCE" -ForegroundColor Cyan
Write-Host "  Yoga 7i Master Node <-> 5-Node GPU Cluster Mesh" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Start Barehands Spatial Hand-Tracking Air-Board Server
Write-Host "`n🖐️  [1/3] Starting Barehands Spatial UI Server (Port 8794)..." -ForegroundColor Yellow
$BarehandsProc = Start-Process python -ArgumentList "server.py" -WorkingDirectory "$RootDir\barehands" -PassThru
Write-Host "    -> Barehands Spatial Board live on: http://127.0.0.1:8794/stage.html (PID: $($BarehandsProc.Id))" -ForegroundColor Green

# 2. Start Friday FastMCP Server
Write-Host "`n🧠 [2/3] Starting Friday FastMCP Server (Port 8000)..." -ForegroundColor Yellow
$McpProc = Start-Process uv -ArgumentList "run friday" -WorkingDirectory "$RootDir\friday-tony-stark-demo" -PassThru
Write-Host "    -> Friday FastMCP Server live on: http://127.0.0.1:8000/sse (PID: $($McpProc.Id))" -ForegroundColor Green

# 3. Check Docker status for LiveKit
Write-Host "`n🎙️  [3/3] Initializing Voice Intelligence Pipeline..." -ForegroundColor Yellow
$DockerRunning = $false
try {
    $DockerCheck = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $DockerRunning = $true
    }
} catch {
    $DockerRunning = $false
}

if ($DockerRunning) {
    Write-Host "    -> Docker detected! Checking/Starting local LiveKit server container..." -ForegroundColor Cyan
    docker run -d --name livekit-dev-server -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server --dev 2>$null
    Write-Host "    -> Starting Friday LiveKit Voice Agent..." -ForegroundColor Green
    $VoiceProc = Start-Process uv -ArgumentList "run friday_voice" -WorkingDirectory "$RootDir\friday-tony-stark-demo" -PassThru
} else {
    Write-Host "    -> Docker Desktop not running. Starting Sovereign Pure-Offline Agent (faster-whisper + Ollama + pyttsx3)..." -ForegroundColor Yellow
    $VoiceProc = Start-Process uv -ArgumentList "run python offline_agent.py" -WorkingDirectory "$RootDir\friday-tony-stark-demo" -PassThru
}

Write-Host "`n✨ [JARVIS PROTOCOL ACTIVE]" -ForegroundColor Magenta
Write-Host "🖐️  Open Chrome at: http://127.0.0.1:8794/stage.html" -ForegroundColor Cyan
Write-Host "Press Enter in this console to terminate all services..." -ForegroundColor White

Read-Host
Write-Host "🛑 Shutting down Jarvis Protocol..." -ForegroundColor Red
Stop-Process -Id $BarehandsProc.Id -ErrorAction SilentlyContinue
Stop-Process -Id $McpProc.Id -ErrorAction SilentlyContinue
if ($VoiceProc) {
    Stop-Process -Id $VoiceProc.Id -ErrorAction SilentlyContinue
}
