from __future__ import annotations

import asyncio
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional
from urllib.parse import urlparse
from uuid import uuid4

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


def serve(
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    runtime: Optional[JarvisRuntime] = None,
) -> None:
    server = create_alfred_api_server(runtime, host=host, port=port)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _make_handler(runtime: JarvisRuntime) -> type[BaseHTTPRequestHandler]:
    class AlfredRequestHandler(BaseHTTPRequestHandler):
        server_version = "JarvisXAlfred/0.1"

        def do_GET(self) -> None:
            route = urlparse(self.path).path
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
            message = str(payload.get("message", "")).strip()
            if not message:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {"handled": False, "trace_id": trace_id, "message": "Chat message was empty."},
                )
                return
            response = asyncio.run(runtime.alfred.process(message, trace_id=trace_id, source="edith"))
            self._write_agent_response(response)

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
    healthy = all(check["healthy"] for check in checks.values())
    return {
        "handled": healthy,
        "trace_id": trace_id,
        "status": "ok" if healthy else "degraded",
        "checks": checks,
    }


if __name__ == "__main__":
    serve()
