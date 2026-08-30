"""
Jarvis X — Chrome Extension Bridge Server (Layer 4/6 - Automation & Runtime Interface).
Lightweight CORS-enabled HTTP server running on port 8765.
Connects Chrome browser extensions directly to AlfredOrganism.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional

logger = logging.getLogger("jarvisx.runtime.extension_server")


class ExtensionBridgeHandler(BaseHTTPRequestHandler):
    """Handles HTTP API requests from the Alfred Chrome Extension."""

    def _set_cors_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self._set_cors_headers(204)

    def do_GET(self) -> None:
        """Handle GET status and health checks."""
        if self.path in ("/api/status", "/health", "/status"):
            try:
                from jarvisx.organism import get_organism
                org = get_organism()
                body = {
                    "status": "online",
                    "persona": org.persona,
                    "llm_provider": "Groq LPU (Qwen 27B)",
                    "memory_active": True,
                    "fleet_online": True,
                }
            except Exception as e:
                body = {
                    "status": "online",
                    "persona": "ALFRED",
                    "llm_provider": "Local Gateway",
                    "error": str(e),
                }

            self._set_cors_headers(200)
            self.wfile.write(json.dumps(body).encode("utf-8"))
            return

        self._set_cors_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self) -> None:
        """Handle POST actions from extension."""
        if self.path in ("/api/action", "/api/chat", "/api/leetcode"):
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            try:
                payload = json.loads(post_data.decode("utf-8"))
            except Exception:
                payload = {}

            prompt = payload.get("prompt") or payload.get("message") or "Help with active page"
            action_type = payload.get("action", "chat")

            # Execute via living organism ReAct loop
            try:
                from jarvisx.organism import get_organism
                org = get_organism()

                # Run asynchronous react_turn in worker pool if event loop exists
                loop = None
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    pass

                if loop and loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        res = pool.submit(lambda: asyncio.run(org.react_turn(prompt))).result(timeout=40)
                else:
                    res = asyncio.run(org.react_turn(prompt))

                response_body = {
                    "status": "success",
                    "action": action_type,
                    "response": res.get("response") or res.get("spoken") or "Mission completed.",
                    "spoken": res.get("spoken"),
                    "decision": res.get("decision"),
                    "tool": res.get("tool"),
                    "details": res,
                }
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(response_body).encode("utf-8"))
                return

            except Exception as ex:
                logger.error(f"[ExtensionBridgeHandler] Action execution error: {ex}")
                self._set_cors_headers(500)
                self.wfile.write(json.dumps({"status": "error", "error": str(ex)}).encode("utf-8"))
                return

        self._set_cors_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress standard http.server stdout logging to avoid clutter."""
        logger.debug(f"[ChromeExtensionBridge] {self.address_string()} - {format % args}")


class ExtensionBridgeServer:
    """Manages the background HTTP daemon on port 8765."""

    _instance: Optional[ExtensionBridgeServer] = None
    _lock = threading.Lock()

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False

    @classmethod
    def get_instance(cls) -> ExtensionBridgeServer:
        with cls._lock:
            if cls._instance is None:
                cls._instance = ExtensionBridgeServer()
            return cls._instance

    def start(self) -> bool:
        """Start the extension bridge HTTP server in a background thread."""
        if self.running:
            return True

        try:
            self.server = HTTPServer((self.host, self.port), ExtensionBridgeHandler)
            self.running = True
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True,
                name="AlfredChromeExtensionBridge"
            )
            self.server_thread.start()
            logger.info(f"[ExtensionBridgeServer] Server online at http://{self.host}:{self.port}")
            return True
        except Exception as e:
            logger.warning(f"[ExtensionBridgeServer] Could not bind server to port {self.port}: {e}")
            return False

    def stop(self) -> None:
        """Stop the background server."""
        if self.server and self.running:
            self.server.shutdown()
            self.server.server_close()
            self.running = False


def start_extension_server() -> ExtensionBridgeServer:
    """Helper to start and retrieve singleton extension server."""
    server = ExtensionBridgeServer.get_instance()
    server.start()
    return server
