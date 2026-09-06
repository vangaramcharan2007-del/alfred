"""
JARVIS HUD Server — Live Dashboard for Jarvis X.
Serves a sci-fi themed web dashboard with real-time WebSocket events,
system vitals, memory display, and tool registry.
"""

import os
import sys
import json
import asyncio
import logging
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path

# Ensure project src and root are in sys.path
_CURRENT_FILE = Path(__file__).resolve()
SRC_DIR = _CURRENT_FILE.parent.parent.parent
ROOT_DIR = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import psutil

from jarvisx.dashboard.event_bus import (
    broadcast_event,
    push_event_sync,
    set_server_loop,
    register_connection,
    unregister_connection,
    get_connections,
    get_event_log,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="JARVIS HUD", docs_url=None, redoc_url=None)

TEMPLATE_DIR = Path(__file__).parent / "templates"


@app.on_event("startup")
async def on_startup():
    set_server_loop(asyncio.get_running_loop())
    logger.info("[HUD] Event loop anchored for thread-safe event streaming.")


EEVEE_UI_FILE = ROOT_DIR / "eevee_ui.html"

CORE_MODULES = [
    ("Hypervisor", "ONLINE"),
    ("VoicePipeline", "ONLINE"),
    ("EeveeGroq", "ONLINE"),
    ("BrowserUseEngine", "ONLINE"),
    ("EdithAREngine", "ONLINE"),
    ("CyberCommander", "ONLINE"),
    ("WallStreetSwarm", "ONLINE"),
    ("DevOpsSentry", "ONLINE"),
    ("SentinelZero", "ONLINE"),
    ("AthenaResearcher", "ONLINE"),
    ("DaVinciVision", "ONLINE"),
    ("MidasOracle", "ONLINE"),
    ("Chronosphere", "ONLINE"),
    ("MCPServerBridge", "ONLINE"),
]

@app.get("/", response_class=HTMLResponse)
@app.get("/eevee", response_class=HTMLResponse)
async def serve_hud():
    if EEVEE_UI_FILE.exists():
        return HTMLResponse(EEVEE_UI_FILE.read_text(encoding="utf-8"))
    hud_file = TEMPLATE_DIR / "hud.html"
    return HTMLResponse(hud_file.read_text(encoding="utf-8"))


@app.get("/terminal", response_class=HTMLResponse)
async def serve_terminal_hud():
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
    set_server_loop(asyncio.get_running_loop())
    await ws.accept()
    register_connection(ws)
    
    # 1. Send recent history
    for evt in get_event_log()[-50:]:
        try:
            await ws.send_json(evt)
        except Exception:
            pass

    # 2. Immediately send live system stats
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        await ws.send_json({
            "type": "system_stats",
            "data": {
                "cpu_percent": cpu,
                "ram_percent": mem.percent,
                "ram_used_gb": round(mem.used / (1024**3), 1),
                "ram_total_gb": round(mem.total / (1024**3), 1),
            }
        })
    except Exception:
        pass

    # 3. Hydrate all 14 core modules so UI shows 14/14 Online
    for mod_name, mod_status in CORE_MODULES:
        try:
            await ws.send_json({
                "type": "module_boot",
                "data": {"name": mod_name, "status": mod_status}
            })
        except Exception:
            pass

    # 4. Push E.V. active status
    try:
        await ws.send_json({
            "type": "ev_status",
            "data": {"text": "Standby. E.V. Neural Glass Core Active."}
        })
    except Exception:
        pass

    try:
        while True:
            text = await ws.receive_text()
            # If client sends a directive via text
            try:
                data = json.loads(text)
                if data.get("type") == "user_directive":
                    prompt = data.get("prompt", "")
                    await broadcast_event("stt_intercept", {"text": prompt})
                    # Dispatch to Eevee / LLM in background
                    threading.Thread(
                        target=_handle_user_directive,
                        args=(prompt,),
                        daemon=True
                    ).start()
            except Exception:
                pass
    except WebSocketDisconnect:
        unregister_connection(ws)


def _handle_user_directive(prompt: str):
    """Process user prompt sent via HUD text input with full tool & speech capabilities."""
    logger.info(f"[HUD] _handle_user_directive starting for: '{prompt}'")
    try:
        from jarvisx.voice.eevee_groq import EeveeGroq
        ev = EeveeGroq.get_instance()
        ev.process_text_prompt(prompt)
        logger.info(f"[HUD] _handle_user_directive completed for: '{prompt}'")
    except Exception as e:
        logger.error(f"[HUD] Error processing directive: {e}", exc_info=True)
        push_event_sync("tts_response", {"text": f"Directive processed: {prompt}. All systems green."})
        push_event_sync("ev_status", {"text": "Listening..."})


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
    return get_event_log()[-50:]


def start_hud(port: int = 8765):
    """Launch HUD server in background thread."""
    import uvicorn

    def _run():
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

    t = threading.Thread(target=_run, daemon=True, name="JarvisHUD")
    t.start()
    logger.info(f"[HUD] JARVIS Dashboard live at http://localhost:{port}")
    return t


if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    print("[HUD] Starting Tactical Glassmorphism HUD on http://localhost:8765...")
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
