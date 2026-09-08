"""HTTP control plane for the agentic harness orchestration layer.

Implemented on the standard library's ``http.server`` so it runs with zero
third-party dependencies.  Endpoints:

    GET  /health                liveness + backend identity
    GET  /tools                 registered harness tools
    GET  /roles                 registered agent roles
    POST /plan     {goal}       plan only, returns the task graph
    POST /run      {goal}       plan + execute, returns the full report
    POST /tasks    {task,role}  run one task through a single harness
    GET  /runs                  list recorded runs
    GET  /runs/{run_id}/trace   replay one run's JSONL trace
    GET  /events                stream orchestration events as they happen
"""

from __future__ import annotations

import json
import logging
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from jarvisx.agentic.backends import AutoBackend, HeuristicBackend, ModelBackend
from jarvisx.agentic.builtin_tools import build_default_tools
from jarvisx.agentic.harness import AgentHarness
from jarvisx.agentic.roles import RoleRegistry
from jarvisx.agentic.sandbox import SandboxedRunner
from jarvisx.agentic.scheduler import DEFAULT_TRACE_ROOT, Orchestrator
from jarvisx.agentic.trace import TraceRecorder
from jarvisx.agentic.types import Budget
from jarvisx.agentic.verifier import Verifier

logger = logging.getLogger("jarvisx.agentic.control_plane")

# Ring buffer so /events can replay a little history to late subscribers.
_EVENT_BUFFER: List[Dict[str, Any]] = []
_EVENT_LOCK = threading.Lock()
_SUBSCRIBERS: List["queue.Queue[Dict[str, Any]]"] = []


def _publish(event: Dict[str, Any]) -> None:
    with _EVENT_LOCK:
        _EVENT_BUFFER.append(event)
        del _EVENT_BUFFER[:-500]
        dead = []
        for subscriber in _SUBSCRIBERS:
            try:
                subscriber.put_nowait(event)
            except queue.Full:
                dead.append(subscriber)
        for subscriber in dead:
            _SUBSCRIBERS.remove(subscriber)


def _subscribe() -> "queue.Queue[Dict[str, Any]]":
    subscriber: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=256)
    with _EVENT_LOCK:
        _SUBSCRIBERS.append(subscriber)
    return subscriber


def _unsubscribe(subscriber: "queue.Queue[Dict[str, Any]]") -> None:
    with _EVENT_LOCK:
        if subscriber in _SUBSCRIBERS:
            _SUBSCRIBERS.remove(subscriber)


class ControlPlane:
    """Owns the shared backend and workspace used by every request."""

    def __init__(
        self,
        backend: Optional[ModelBackend] = None,
        trace_root: Optional[Path | str] = None,
        sandbox: Optional[SandboxedRunner] = None,
        max_workers: int = 4,
    ):
        self.backend = backend or AutoBackend()
        self.trace_root = Path(trace_root) if trace_root else DEFAULT_TRACE_ROOT
        self.sandbox = sandbox or SandboxedRunner()
        self.max_workers = max_workers
        self.started_at = time.time()

    # -- handlers ---------------------------------------------------------- #

    def health(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "backend": self.backend.name,
            "uptime_seconds": round(time.time() - self.started_at, 2),
            "trace_root": str(self.trace_root),
            "sandbox": str(self.sandbox.workspace),
        }

    def tools(self) -> Dict[str, Any]:
        registry = build_default_tools(self.sandbox)
        return {"count": len(registry), "tools": registry.flat_schemas()}

    def roles(self) -> Dict[str, Any]:
        registry = RoleRegistry()
        return {
            "count": len(registry),
            "roles": [registry.get(name).to_dict() for name in registry.names()],
        }

    def plan(self, goal: str) -> Dict[str, Any]:
        with Orchestrator(
            backend=self.backend,
            sandbox=self.sandbox,
            trace_root=self.trace_root,
            on_event=_publish,
        ) as orch:
            graph = orch.plan(goal)
            return {
                "goal": goal,
                "strategy": getattr(orch.planner, "last_strategy", "unknown"),
                "graph": graph.to_dict(),
            }

    def run(self, goal: str, budget: Optional[Budget] = None) -> Dict[str, Any]:
        with Orchestrator(
            backend=self.backend,
            sandbox=self.sandbox,
            default_budget=budget,
            max_workers=self.max_workers,
            trace_root=self.trace_root,
            on_event=_publish,
        ) as orch:
            report = orch.run(goal)
            return report.to_dict()

    def task(self, task: str, role: str = "generalist") -> Dict[str, Any]:
        spec = RoleRegistry().get(role)
        harness = AgentHarness(
            backend=self.backend,
            registry=build_default_tools(self.sandbox),
            sandbox=self.sandbox,
            role=spec.name,
            role_prompt=spec.system_prompt(),
            budget=spec.budget,
            verifier=Verifier(),
            trace_root=self.trace_root,
            on_event=_publish,
        )
        result = harness.run(task)
        payload = result.to_dict()
        payload["workspace_files"] = self.sandbox.list_files()
        return payload

    def runs(self, limit: int = 20) -> Dict[str, Any]:
        if not self.trace_root.exists():
            return {"count": 0, "runs": []}
        entries = []
        for path in sorted(self.trace_root.glob("*.jsonl"))[-limit:]:
            summary = TraceRecorder.summarize(path)
            final = summary.get("final") or {}
            entries.append(
                {
                    "run_id": path.stem,
                    "status": final.get("status") if final.get("kind") == "run_end" else None,
                    "events": summary["events"],
                    "duration_seconds": summary["duration_seconds"],
                    "by_kind": summary["by_kind"],
                }
            )
        return {"count": len(entries), "runs": entries}

    def trace(self, run_id: str) -> Optional[Dict[str, Any]]:
        path = self.trace_root / f"{Path(run_id).name}.jsonl"
        if not path.exists():
            return None
        return {"run_id": run_id, "events": TraceRecorder.read(path)}


def _make_handler(plane: ControlPlane):
    class Handler(BaseHTTPRequestHandler):
        server_version = "AlfredAgentic/1.0"

        # -- plumbing ------------------------------------------------------ #

        def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
            logger.info("%s - %s", self.address_string(), fmt % args)

        def _send(self, code: int, payload: Any, content_type: str = "application/json") -> None:
            if isinstance(payload, (dict, list)):
                body = json.dumps(payload, default=str).encode("utf-8")
            else:
                body = str(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return {}
            try:
                return json.loads(self.rfile.read(length).decode("utf-8"))
            except json.JSONDecodeError:
                return {}

        # -- routes -------------------------------------------------------- #

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path.rstrip("/") or "/"
            try:
                if path == "/health":
                    self._send(200, plane.health())
                elif path == "/tools":
                    self._send(200, plane.tools())
                elif path == "/roles":
                    self._send(200, plane.roles())
                elif path == "/runs":
                    self._send(200, plane.runs())
                elif path.startswith("/runs/") and path.endswith("/trace"):
                    run_id = path[len("/runs/") : -len("/trace")]
                    payload = plane.trace(run_id)
                    self._send(200, payload) if payload else self._send(
                        404, {"error": f"no trace for {run_id}"}
                    )
                elif path == "/events":
                    self._stream()
                elif path == "/":
                    self._send(
                        200,
                        {
                            "service": "alfred-agentic-control-plane",
                            "endpoints": [
                                "GET /health",
                                "GET /tools",
                                "GET /roles",
                                "GET /runs",
                                "GET /runs/{run_id}/trace",
                                "GET /events",
                                "POST /plan",
                                "POST /run",
                                "POST /tasks",
                            ],
                        },
                    )
                else:
                    self._send(404, {"error": f"unknown path {path}"})
            except Exception as exc:  # noqa: BLE001
                logger.exception("control plane error")
                self._send(500, {"error": f"{type(exc).__name__}: {exc}"})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path.rstrip("/")
            body = self._read_json()
            try:
                if path == "/plan":
                    goal = str(body.get("goal") or "").strip()
                    if not goal:
                        self._send(400, {"error": "'goal' is required"})
                        return
                    self._send(200, plane.plan(goal))
                elif path == "/run":
                    goal = str(body.get("goal") or "").strip()
                    if not goal:
                        self._send(400, {"error": "'goal' is required"})
                        return
                    budget = _budget_from(body)
                    self._send(200, plane.run(goal, budget))
                elif path == "/tasks":
                    task = str(body.get("task") or "").strip()
                    if not task:
                        self._send(400, {"error": "'task' is required"})
                        return
                    self._send(200, plane.task(task, str(body.get("role") or "generalist")))
                else:
                    self._send(404, {"error": f"unknown path {path}"})
            except Exception as exc:  # noqa: BLE001
                logger.exception("control plane error")
                self._send(500, {"error": f"{type(exc).__name__}: {exc}"})

        def _stream(self) -> None:
            """Server-sent events feed of orchestration activity."""
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            subscriber = _subscribe()
            try:
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
                while True:
                    try:
                        event = subscriber.get(timeout=15)
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
                        continue
                    payload = json.dumps(event, default=str)
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                _unsubscribe(subscriber)

    return Handler


def _budget_from(body: Dict[str, Any]) -> Optional[Budget]:
    if not any(k in body for k in ("max_steps", "max_tool_calls", "max_seconds", "max_tokens")):
        return None
    return Budget(
        max_steps=int(body.get("max_steps", 8)),
        max_tool_calls=int(body.get("max_tool_calls", 24)),
        max_seconds=float(body.get("max_seconds", 180.0)),
        max_tokens=int(body.get("max_tokens", 64_000)),
    )


def serve(
    host: str = "0.0.0.0",
    port: int = 8123,
    backend_name: str = "auto",
    trace_root: Optional[Path | str] = None,
) -> int:
    """Start the control plane. Blocks until interrupted."""
    backend = HeuristicBackend() if backend_name == "offline" else AutoBackend()
    plane = ControlPlane(backend=backend, trace_root=trace_root)
    server = ThreadingHTTPServer((host, port), _make_handler(plane))
    print(f"Alfred agentic control plane on http://{host}:{port}")
    print(f"  backend : {plane.backend.name}")
    print(f"  traces  : {plane.trace_root}")
    print(f"  sandbox : {plane.sandbox.workspace}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.server_close()
        plane.sandbox.cleanup()
    return 0
