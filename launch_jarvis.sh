#!/usr/bin/env bash
# ==============================================================================
# JARVIS PROTOCOL: FUSION MODE MASTER LAUNCHER
# Bootstraps Barehands Spatial UI + Friday FastMCP Server + Friday Voice Agent
# ==============================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🚀 [JARVIS PROTOCOL] Initializing Fusion Mode from: $ROOT_DIR"

# 1. Start Barehands Hand-Tracking Server
echo "🖐️  [1/3] Starting Barehands Spatial UI Server (Port 8794)..."
cd "$ROOT_DIR/barehands"
python3 server.py &
PID_BAREHANDS=$!
echo "    -> Barehands Spatial Board live on http://127.0.0.1:8794/stage.html (PID: $PID_BAREHANDS)"

# 2. Start Friday FastMCP Server
echo "🧠 [2/3] Starting Friday FastMCP Server (Port 8000)..."
cd "$ROOT_DIR/friday-tony-stark-demo"
uv run friday &
PID_MCP=$!
echo "    -> Friday FastMCP Server live on http://127.0.0.1:8000/sse (PID: $PID_MCP)"

# 3. Start Friday LiveKit Voice Agent
echo "🎙️  [3/3] Starting Friday LiveKit Voice Agent..."
uv run friday_voice &
PID_VOICE=$!
echo "    -> Friday Voice Agent initialized (PID: $PID_VOICE)"

echo ""
echo "✨ [JARVIS PROTOCOL ACTIVE]"
echo "Open Chrome at: http://127.0.0.1:8794/stage.html"
echo "Press Ctrl+C to terminate all services."

cleanup() {
    echo ""
    echo "🛑 Shutting down Jarvis Protocol..."
    kill $PID_BAREHANDS $PID_MCP $PID_VOICE 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM
wait
