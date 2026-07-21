from __future__ import annotations

import asyncio
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse
from uuid import uuid4

from jarvisx.adapters.vision_interface import VisionManager
from jarvisx.adapters.voice_interface import VoiceManager
from jarvisx.agents.base import AgentResponse
from jarvisx.runtime import JarvisRuntime, create_default_runtime


class AlfredApiServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], runtime: JarvisRuntime) -> None:
        self.runtime = runtime
        super().__init__(server_address, _make_handler(runtime))


def create_alfred_api_server(
    runtime: Optional[JarvisRuntime] = None,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> AlfredApiServer:
    return AlfredApiServer((host, port), runtime or create_default_runtime())


import threading

def serve(
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    runtime: Optional[JarvisRuntime] = None,
) -> None:
    runtime = runtime or create_default_runtime()
    
    # 1. Run boot sequence in a background thread to prevent blocking server
    boot_thread = threading.Thread(
        target=lambda: asyncio.run(runtime.startup_manager.boot()),
        daemon=True
    )
    boot_thread.start()
    
    # 2. Start continuous health monitor in a background thread
    runtime.continuous_health.stop() # Ensure clean state
    runtime.continuous_health._running = True
    monitor_thread = threading.Thread(
        target=lambda: asyncio.run(runtime.continuous_health._monitor_loop()),
        daemon=True
    )
    monitor_thread.start()
    
    # 3. Start proactive intelligence monitor in a background thread
    runtime.proactive_monitor.stop()
    # Start proactive monitor in background thread
    runtime.proactive_monitor._running = True
    threading.Thread(
        target=lambda: asyncio.run(runtime.proactive_monitor._monitor_loop()),
        daemon=True
    ).start()
    
    # 4. Start the Complete Voice Interaction Stack
    from jarvisx.core.voice.interaction_loop import InteractionLoop
    from jarvisx.core.voice.websocket_server import VoiceWebsocketServer
    from jarvisx.core.voice_router import VoiceRouter
    
    voice_router = VoiceRouter()
    ws_server = VoiceWebsocketServer(host=host, port=8766)
    
    def on_state(state: str):
        # Fire-and-forget broadcast
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(ws_server.broadcast_state(state))
        finally:
            loop.close()

    def on_transcript(text: str, is_user: bool):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(ws_server.broadcast_transcript(text, is_user))
        finally:
            loop.close()
            
    interaction_loop = InteractionLoop(voice_router=voice_router, state_callback=on_state, transcript_callback=on_transcript)
    
    def run_voice_stack():
        async def voice_main():
            await ws_server.start()
            interaction_loop.initialize()
            await interaction_loop.start()
            # Keep loop alive
            while True:
                await asyncio.sleep(3600)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(voice_main())
        
    threading.Thread(target=run_voice_stack, daemon=True).start()
    
    server = create_alfred_api_server(runtime, host=host, port=port)
    try:
        server.serve_forever()
    finally:
        runtime.shutdown()
        server.server_close()


def _make_handler(runtime: JarvisRuntime) -> type[BaseHTTPRequestHandler]:
    class AlfredRequestHandler(BaseHTTPRequestHandler):
        server_version = "JarvisXAlfred/0.1"
        voice_manager = VoiceManager(runtime)
        vision_manager = VisionManager(runtime)

        def do_GET(self) -> None:
            route = urlparse(self.path).path
            if runtime.startup_manager.setup_mode and route not in {"/setup", "/api/setup"}:
                self._serve_setup_redirect()
                return
            if route == "/setup":
                self._serve_setup()
                return
            if route == "/spatial":
                self._serve_spatial()
                return
            if route == "/dashboard":
                self._serve_dashboard()
                return
            if route == "/api/status":
                self._handle_status_get()
                return
            if route == "/api/diagnostics":
                self._handle_diagnostics_get()
                return
            if route == "/api/agents":
                self._handle_api_agents()
                return
            if route == "/api/state":
                self._handle_api_state()
                return
            if route == "/api/logs":
                self._handle_api_logs()
                return
            if route == "/status":
                trace_id = self.headers.get("X-Trace-ID") or uuid4().hex
                self._write_json(HTTPStatus.OK, _status_payload(runtime, trace_id=trace_id))
                return
            self._write_json(
                HTTPStatus.NOT_FOUND,
                {"handled": False, "trace_id": uuid4().hex, "message": "Endpoint not found."},
            )

        def do_POST(self) -> None:
            route = urlparse(self.path).path
            
            if route == "/voice":
                self._handle_voice()
                return

            if route == "/vision":
                self._handle_vision()
                return

            payload, parse_error = self._read_json()
            trace_id = _trace_id(payload, self.headers.get("X-Trace-ID"))
            if parse_error:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "handled": False,
                        "trace_id": trace_id,
                        "message": parse_error,
                    },
                )
                return

            if route == "/api/setup":
                self._handle_api_setup(payload, trace_id)
                return
            if route == "/chat":
                self._handle_chat(payload, trace_id)
                return
            if route == "/status":
                self._write_json(HTTPStatus.OK, _status_payload(runtime, trace_id=trace_id))
                return
            if route == "/notify":
                self._handle_notify(payload, trace_id)
                return
            if route == "/device_action":
                self._handle_device_action(payload, trace_id)
                return
            if route == "/api/mode":
                self._handle_api_mode(payload, trace_id)
                return
            if route == "/api/autonomy":
                self._handle_api_autonomy(payload, trace_id)
                return
            if route == "/api/settings":
                self._handle_api_settings(payload, trace_id)
                return
            if route == "/api/personality":
                self._handle_api_personality(payload, trace_id)
                return
            if route == "/api/test/stress":
                self._handle_api_stress_test(payload, trace_id)
                return

            self._write_json(
                HTTPStatus.NOT_FOUND,
                {"handled": False, "trace_id": trace_id, "message": "Endpoint not found."},
            )

        def log_message(self, format: str, *args: object) -> None:
            runtime.alfred.logger.write(
                "info",
                "alfred.api.request",
                method=self.command,
                path=urlparse(self.path).path,
                client=self.client_address[0],
            )

        def _handle_chat(self, payload: dict[str, Any], trace_id: str) -> None:
            if not runtime.startup_manager.is_ready:
                self._write_json(HTTPStatus.SERVICE_UNAVAILABLE, {"handled": False, "message": "Jarvis X is still initializing."})
                return
            message = str(payload.get("message", "")).strip()
            if not message:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {"handled": False, "trace_id": trace_id, "message": "Chat message was empty."},
                )
                return
            response = asyncio.run(runtime.alfred.process(message, trace_id=trace_id, source="edith"))
            self._write_agent_response(response)

        def _handle_voice(self) -> None:
            if not runtime.startup_manager.is_ready:
                self._write_json(HTTPStatus.SERVICE_UNAVAILABLE, {"handled": False, "message": "Jarvis X is still initializing."})
                return
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length == 0:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {"handled": False, "trace_id": uuid4().hex, "message": "No audio data provided."},
                )
                return
            audio_data = self.rfile.read(length)
            trace_id = self.headers.get("X-Trace-ID") or uuid4().hex
            
            audio_response = asyncio.run(self.voice_manager.process_voice_input(audio_data, trace_id=trace_id))
            
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(audio_response)))
            self.end_headers()
            self.wfile.write(audio_response)

        def _handle_vision(self) -> None:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length == 0:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {"handled": False, "trace_id": uuid4().hex, "message": "No image data provided."},
                )
                return
            image_data = self.rfile.read(length)
            trace_id = self.headers.get("X-Trace-ID") or uuid4().hex
            
            vision_response = asyncio.run(self.vision_manager.process_image_input(image_data, trace_id=trace_id))
            
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(vision_response)))
            self.end_headers()
            self.wfile.write(vision_response)

        def _handle_notify(self, payload: dict[str, Any], trace_id: str) -> None:
            title = str(payload.get("title", "Jarvis X"))
            body = str(payload.get("body", ""))
            response = asyncio.run(
                runtime.alfred.notify(title=title, body=body, trace_id=trace_id, source="edith")
            )
            self._write_agent_response(response)

        def _handle_device_action(self, payload: dict[str, Any], trace_id: str) -> None:
            action = str(payload.get("action", "")).strip()
            parameters = payload.get("parameters")
            if not isinstance(parameters, dict):
                parameters = {
                    key: value
                    for key, value in payload.items()
                    if key not in {"action", "trace_id"}
                }
            response = asyncio.run(
                runtime.alfred.device_action(
                    action,
                    parameters,
                    trace_id=trace_id,
                    source="edith",
                )
            )
            self._write_agent_response(response)

        def _read_json(self) -> tuple[dict[str, Any], Optional[str]]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length == 0:
                return {}, None
            raw_body = self.rfile.read(length)
            try:
                parsed = json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                return {}, f"Invalid JSON: {exc.msg}."
            if not isinstance(parsed, dict):
                return {}, "JSON body must be an object."
            return parsed, None

        def _write_agent_response(self, response: AgentResponse) -> None:
            status = HTTPStatus.OK if response.handled else HTTPStatus.BAD_REQUEST
            self._write_json(status, response.to_dict())

        def _write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        # ── Dashboard & API Endpoints ──

        def _serve_setup_redirect(self) -> None:
            self.send_response(HTTPStatus.TEMPORARY_REDIRECT.value)
            self.send_header("Location", "/setup")
            self.end_headers()

        def _serve_setup(self) -> None:
            html_path = Path(__file__).resolve().parent / "dashboard" / "setup.html"
            if not html_path.exists():
                self._write_json(
                    HTTPStatus.NOT_FOUND,
                    {"handled": False, "message": "Setup HTML not found."},
                )
                return
            body = html_path.read_bytes()
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_spatial(self) -> None:
            html_path = Path(__file__).resolve().parent / "dashboard" / "spatial.html"
            if not html_path.exists():
                self._write_json(
                    HTTPStatus.NOT_FOUND,
                    {"handled": False, "message": "Spatial HTML not found."},
                )
                return
            body = html_path.read_bytes()
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_dashboard(self) -> None:
            html_path = Path(__file__).resolve().parent / "dashboard" / "index.html"
            if not html_path.exists():
                self._write_json(
                    HTTPStatus.NOT_FOUND,
                    {"handled": False, "message": "Dashboard HTML not found."},
                )
                return
            body = html_path.read_bytes()
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _handle_api_state(self) -> None:
            mode_result = runtime.personalization.get_mode()
            personalities_result = runtime.personalization.list_personalities()
            health_checks = {
                name: {"healthy": status.healthy, "message": status.message}
                for name, status in runtime.health.run_all().items()
            }
            recent_logs = runtime.alfred.logger.recent(20)
            world_summary = runtime.world_model.get_world_summary()
            
            self._write_json(HTTPStatus.OK, {
                "mode": mode_result.data.get("mode", {}),
                "autonomy_level": mode_result.data.get("autonomy_level", 1),
                "personalities": personalities_result.data.get("personalities", {}),
                "health": health_checks,
                "recent_logs": recent_logs,
                "world_model": world_summary,
                "config": runtime.config_manager.get_config(),
            })

        def _handle_api_setup(self, payload: dict[str, Any], trace_id: str) -> None:
            # Save API keys to config
            providers = payload.get("providers", {})
            runtime.config_manager.set("providers", providers)
            
            # Save preferences if provided
            preferences = payload.get("preferences", {})
            if "primary_personality" in preferences:
                runtime.config_manager.set("personalities.primary", preferences["primary_personality"])
            
            # TODO: We should verify them before completing setup
            # For now, mark setup completed
            runtime.config_manager.complete_setup()
            runtime.startup_manager.setup_mode = False
            runtime.startup_manager._setup_event.set()
            
            self._write_json(HTTPStatus.OK, {"success": True, "message": "Setup completed."})

        def _handle_api_settings(self, payload: dict[str, Any], trace_id: str) -> None:
            # Save API keys and provider endpoints
            providers = payload.get("providers", {})
            if providers:
                # Merge into existing so we don't wipe out other providers
                current_providers = runtime.config_manager.get("providers", {})
                for cat, props in providers.items():
                    if cat not in current_providers:
                        current_providers[cat] = {}
                    current_providers[cat].update(props)
                runtime.config_manager.set("providers", current_providers)
            
            # Save preferences
            preferences = payload.get("preferences", {})
            if "primary_personality" in preferences:
                runtime.config_manager.set("personalities.primary", preferences["primary_personality"])
            if "primary_voice" in preferences:
                runtime.config_manager.set("providers.tts.preferred_provider", preferences["primary_voice"])
                
            self._write_json(HTTPStatus.OK, {"success": True, "message": "Settings updated successfully."})

        def _handle_api_agents(self) -> None:
            agents = runtime.registry.describe()
            self._write_json(HTTPStatus.OK, {"agents": agents})
            
        def _handle_status_get(self) -> None:
            status = {
                "alfred_status": "online",
                "health_summary": runtime.health.run_all(),
            }
            # Convert HealthStatus to dict for JSON serialization
            serializable_status = {
                "alfred_status": status["alfred_status"],
                "health_summary": {k: {"healthy": v.healthy, "message": v.message} for k, v in status["health_summary"].items()}
            }
            self._write_json(HTTPStatus.OK, serializable_status)
            
        def _handle_diagnostics_get(self) -> None:
            stats = runtime.continuous_health.stats
            active_threads = __import__('threading').active_count()
            
            # Get workflow stats
            try:
                db_conn = runtime.workflow_tool.engine.db._get_connection()
                cursor = db_conn.execute("SELECT COUNT(*) FROM workflows WHERE state = 'RUNNING'")
                running_workflows = cursor.fetchone()[0]
                db_conn.close()
            except Exception:
                running_workflows = 0
                
            payload = {
                "threads": active_threads,
                "running_workflows": running_workflows,
                "system_stats": stats
            }
            self._write_json(HTTPStatus.OK, payload)

        def _handle_api_logs(self) -> None:
            logs = runtime.alfred.logger.recent(50)
            self._write_json(HTTPStatus.OK, {"logs": logs})

        def _handle_api_mode(self, payload: dict[str, Any], trace_id: str) -> None:
            mode = str(payload.get("mode", "")).strip()
            if not mode:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {"success": False, "message": "Mode was empty."},
                )
                return
            result = runtime.personalization.set_mode(mode, trace_id=trace_id)
            self._write_json(
                HTTPStatus.OK if result.success else HTTPStatus.BAD_REQUEST,
                {"success": result.success, "message": result.message, "data": result.data},
            )

        def _handle_api_autonomy(self, payload: dict[str, Any], trace_id: str) -> None:
            level = payload.get("level")
            if not isinstance(level, int):
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {"success": False, "message": "Autonomy level must be an integer."},
                )
                return
            result = runtime.personalization.set_autonomy_level(level, trace_id=trace_id)
            self._write_json(
                HTTPStatus.OK if result.success else HTTPStatus.BAD_REQUEST,
                {"success": result.success, "message": result.message, "data": result.data},
            )

        def _handle_api_personality(self, payload: dict[str, Any], trace_id: str) -> None:
            agent_id = str(payload.get("agent_id", "")).strip()
            profile = payload.get("profile", {})
            if not agent_id:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {"success": False, "message": "Agent id was empty."},
                )
                return
            if not isinstance(profile, dict):
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {"success": False, "message": "Profile must be a JSON object."},
                )
                return
            result = runtime.personalization.set_personality(agent_id, profile, trace_id=trace_id)
            self._write_json(
                HTTPStatus.OK if result.success else HTTPStatus.BAD_REQUEST,
                {"success": result.success, "message": result.message, "data": result.data},
            )

        def _handle_api_stress_test(self, payload: dict[str, Any], trace_id: str) -> None:
            """Simulates heavy load by launching parallel dummy workflows."""
            import time
            from jarvisx.core.workflows import Workflow, WorkflowStep
            
            count = payload.get("count", 10)
            
            def dummy_task(ctx):
                time.sleep(0.5)
                return {}

            started = 0
            for i in range(count):
                wf = Workflow(name=f"StressTest_{i}", steps=[WorkflowStep(name="Dummy", action=dummy_task)])
                runtime.workflow_tool.engine.start(wf)
                started += 1
                
            self._write_json(
                HTTPStatus.OK,
                {"success": True, "message": f"Started {started} stress test workflows."},
            )

    return AlfredRequestHandler


def _trace_id(payload: dict[str, Any], header_trace_id: Optional[str]) -> str:
    body_trace_id = payload.get("trace_id")
    if isinstance(body_trace_id, str) and body_trace_id.strip():
        return body_trace_id.strip()
    if header_trace_id and header_trace_id.strip():
        return header_trace_id.strip()
    return uuid4().hex


def _status_payload(runtime: JarvisRuntime, *, trace_id: str) -> dict[str, Any]:
    checks = {
        name: {"healthy": status.healthy, "message": status.message}
        for name, status in runtime.health.run_all().items()
    }
    
    providers = {}
    for cat in runtime.fallback_manager.registry.get_all_categories():
        active = runtime.fallback_manager.get_active(cat)
        providers[cat] = active.capability.name if active else "NONE"
        
    healthy = all(check["healthy"] for check in checks.values())
    return {
        "handled": healthy,
        "trace_id": trace_id,
        "status": "ok" if healthy else "degraded",
        "checks": checks,
        "providers": providers,
    }


if __name__ == "__main__":
    serve()
