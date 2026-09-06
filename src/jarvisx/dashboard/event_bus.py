"""
JARVIS Central Event Bus — Thread-Safe Real-time WebSocket Streaming
=====================================================================
Ensures a shared singleton event dispatcher across all threads, modules,
and runtime execution contexts (regardless of whether hud_server is run as
a script, package module, or daemon process).
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("jarvisx.dashboard.event_bus")

_connections: List[Any] = []
_event_log: List[Dict[str, Any]] = []
_server_loop: Optional[asyncio.AbstractEventLoop] = None
MAX_LOG = 200


def set_server_loop(loop: asyncio.AbstractEventLoop):
    """Anchors the active asyncio event loop from uvicorn / FastAPI."""
    global _server_loop
    _server_loop = loop
    logger.info(f"[EventBus] Active server loop registered: {loop}")


def get_server_loop() -> Optional[asyncio.AbstractEventLoop]:
    return _server_loop


def register_connection(ws: Any):
    """Registers an active WebSocket connection."""
    if ws not in _connections:
        _connections.append(ws)
    logger.info(f"[EventBus] Client connected. Total active connections: {len(_connections)}")


def unregister_connection(ws: Any):
    """Removes a closed or disconnected WebSocket connection."""
    if ws in _connections:
        _connections.remove(ws)
    logger.info(f"[EventBus] Client disconnected. Total active connections: {len(_connections)}")


def get_connections() -> List[Any]:
    return list(_connections)


def get_event_log() -> List[Dict[str, Any]]:
    return list(_event_log)


async def broadcast_event(event_type: str, data: Any):
    """Push an event to all connected HUD clients asynchronously."""
    evt = {"type": event_type, "data": data}
    _event_log.append(evt)
    if len(_event_log) > MAX_LOG:
        _event_log.pop(0)

    logger.info(f"[EventBus] Broadcasting '{event_type}' to {len(_connections)} client(s)")
    dead = []
    for ws in list(_connections):
        try:
            await ws.send_json(evt)
        except Exception as e:
            logger.warning(f"[EventBus] Client send failed: {e}")
            dead.append(ws)

    for ws in dead:
        unregister_connection(ws)


def push_event_sync(event_type: str, data: Any):
    """
    Thread-safe synchronous wrapper for broadcasting events from any
    worker thread, tool execution, or background agent.
    """
    global _server_loop
    logger.info(f"[EventBus] push_event_sync: '{event_type}' (loop active: {bool(_server_loop and _server_loop.is_running())})")

    if _server_loop is not None and _server_loop.is_running():
        try:
            asyncio.run_coroutine_threadsafe(broadcast_event(event_type, data), _server_loop)
            return
        except Exception as e:
            logger.warning(f"[EventBus] run_coroutine_threadsafe failed: {e}")

    # Fallback to current thread event loop if one exists
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_event(event_type, data))
        else:
            loop.run_until_complete(broadcast_event(event_type, data))
    except Exception as e:
        logger.warning(f"[EventBus] fallback event push failed: {e}")
