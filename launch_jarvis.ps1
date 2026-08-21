# ==============================================================================
# JARVIS PROTOCOL: FUSION MODE MASTER LAUNCHER (PowerShell)
# Bootstraps Barehands Spatial UI + Friday FastMCP Server + Friday Voice Agent
# ==============================================================================

$RootDir = $PSScriptRoot
Write-Host "🚀 [JARVIS PROTOCOL] Initializing Fusion Mode from: $RootDir" -ForegroundColor Cyan

# 1. Start Barehands Hand-Tracking Server
Write-Host "🖐️  [1/3] Starting Barehands Spatial UI Server (Port 8794)..." -ForegroundColor Yellow
$BarehandsProc = Start-Process python -ArgumentList "server.py" -WorkingDirectory "$RootDir\barehands" -PassThru
Write-Host "    -> Barehands Spatial Board live on http://127.0.0.1:8794/stage.html (PID: $($BarehandsProc.Id))" -ForegroundColor Green

# 2. Start Friday FastMCP Server
Write-Host "🧠 [2/3] Starting Friday FastMCP Server (Port 8000)..." -ForegroundColor Yellow
$McpProc = Start-Process uv -ArgumentList "run friday" -WorkingDirectory "$RootDir\friday-tony-stark-demo" -PassThru
Write-Host "    -> Friday FastMCP Server live on http://127.0.0.1:8000/sse (PID: $($McpProc.Id))" -ForegroundColor Green

# 3. Start Friday LiveKit Voice Agent
Write-Host "🎙️  [3/3] Starting Friday LiveKit Voice Agent..." -ForegroundColor Yellow
$VoiceProc = Start-Process uv -ArgumentList "run friday_voice" -WorkingDirectory "$RootDir\friday-tony-stark-demo" -PassThru
Write-Host "    -> Friday Voice Agent initialized (PID: $($VoiceProc.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "✨ [JARVIS PROTOCOL ACTIVE]" -ForegroundColor Magenta
Write-Host "Open Chrome at: http://127.0.0.1:8794/stage.html" -ForegroundColor Cyan
Write-Host "Press Enter in this console to terminate all services..." -ForegroundColor White

Read-Host
Write-Host "🛑 Shutting down Jarvis Protocol..." -ForegroundColor Red
Stop-Process -Id $BarehandsProc.Id -ErrorAction SilentlyContinue
Stop-Process -Id $McpProc.Id -ErrorAction SilentlyContinue
Stop-Process -Id $VoiceProc.Id -ErrorAction SilentlyContinue
