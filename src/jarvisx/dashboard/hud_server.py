"""
JARVIS HUD Server — Live Dashboard for Jarvis X.
Serves a sci-fi themed web dashboard with real-time WebSocket events,
system vitals, memory display, and tool registry.
"""

import json
import asyncio
import logging
import threading
from typing import List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import psutil

logger = logging.getLogger(__name__)

app = FastAPI(title="JARVIS HUD", docs_url=None, redoc_url=None)

# Global event bus
_connections: List[WebSocket] = []
_event_log: List[Dict[str, Any]] = []
MAX_LOG = 200

TEMPLATE_DIR = Path(__file__).parent / "templates"


async def broadcast_event(event_type: str, data: Any):
    """Push an event to all connected HUD clients."""
    evt = {"type": event_type, "data": data}
    _event_log.append(evt)
    if len(_event_log) > MAX_LOG:
        _event_log.pop(0)
    dead = []
    for ws in _connections:
        try:
            await ws.send_json(evt)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.remove(ws)


def push_event_sync(event_type: str, data: Any):
    """Thread-safe sync wrapper for broadcasting events."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_event(event_type, data))
        else:
            loop.run_until_complete(broadcast_event(event_type, data))
    except RuntimeError:
        pass


@app.get("/", response_class=HTMLResponse)
async def serve_hud():
    hud_file = TEMPLATE_DIR / "hud.html"
    return HTMLResponse(hud_file.read_text(encoding="utf-8"))


@app.get("/memory-palace", response_class=HTMLResponse)
async def serve_memory_palace():
    file = TEMPLATE_DIR / "memory_palace.html"
    return HTMLResponse(file.read_text(encoding="utf-8"))


@app.get("/swarm-matrix", response_class=HTMLResponse)
async def serve_swarm_matrix():
    file = TEMPLATE_DIR / "swarm_matrix.html"
    return HTMLResponse(file.read_text(encoding="utf-8"))


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _connections.append(ws)
    # Send recent history
    for evt in _event_log[-50:]:
        await ws.send_json(evt)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if ws in _connections:
            _connections.remove(ws)


@app.get("/api/status")
async def api_status():
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 1),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "disk_percent": psutil.disk_usage("/").percent if hasattr(psutil.disk_usage, '__call__') else 0,
        "boot_time": psutil.boot_time(),
    }


@app.get("/api/memory")
async def api_memory():
    from jarvisx.memory.vector_memory import VectorMemory
    vm = VectorMemory("alfred_rag_memory")
    recent = vm.records[-10:] if vm.records else []
    return [{"text": r["text"], "metadata": r.get("metadata", {})} for r in recent]


@app.get("/api/tools")
async def api_tools():
    try:
        from jarvisx.engineering.dynamic_tool_forge import DynamicToolForge
        forge = DynamicToolForge.get_instance()
        tools = []
        for name, info in forge.get_loaded_tools().items():
            tools.append({"name": name, "description": info["schema"].get("description", "")})
        return tools
    except Exception:
        return []


@app.get("/api/events")
async def api_events():
    return _event_log[-50:]


def start_hud(port: int = 8765):
    """Launch HUD server in background thread."""
    import uvicorn

    def _run():
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

    t = threading.Thread(target=_run, daemon=True, name="JarvisHUD")
    t.start()
    logger.info(f"[HUD] JARVIS Dashboard live at http://localhost:{port}")
    return t
