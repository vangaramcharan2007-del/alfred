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

# Same default the CLI uses, so `serve` and `alfred` share one list.
DEFAULT_INTAKE_PATH = Path("var/agentic/intake.json")

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
        intake_path: Optional[Path | str] = None,
    ):
        self.backend = backend or AutoBackend()
        self.trace_root = Path(trace_root) if trace_root else DEFAULT_TRACE_ROOT
        self.sandbox = sandbox or SandboxedRunner()
        self.max_workers = max_workers
        # Shared with the CLI and the voice loop, so every surface shows the
        # same list instead of three private copies of it.
        self.intake_path = Path(intake_path) if intake_path else DEFAULT_INTAKE_PATH
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

    # -- the ADHD layer ----------------------------------------------------- #

    def intake(self) -> Dict[str, Any]:
        """The shared task list plus the one next thing at each energy level.

        Reading the state file rather than holding an IntakeEngine here means
        the CLI, the voice loop and the browser all see the same list.
        """
        from jarvisx.agentic.intake import Energy, IntakeEngine

        engine = IntakeEngine()
        path = self.intake_path
        if path and Path(path).exists():
            try:
                engine.load(json.loads(Path(path).read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError) as exc:
                return {"error": f"could not read state: {exc}", "items": []}

        picks = {}
        for level in (Energy.LOW, Energy.MEDIUM, Energy.HIGH):
            chosen = engine.pick(level)
            picks[level.value] = chosen.to_dict() if chosen else None

        not_yours = [
            i.to_dict()
            for i in engine.items
            if not i.done and i.kind.value != "task"
        ]
        return {
            "items": [i.to_dict() for i in engine.items],
            "open": len(engine.open_items),
            "tasks_open": len([i for i in engine.open_items if i.kind.value == "task"]),
            "next_at_energy": picks,
            "not_your_problem": not_yours,
        }

    def capture(self, dump: str) -> Dict[str, Any]:
        """Add a brain dump to the shared list."""
        from jarvisx.agentic.intake import IntakeEngine

        if not (dump or "").strip():
            return {"error": "nothing to capture", "captured": []}
        engine = self._load_engine()
        # engine.capture(), not engine.plan(): plan() returns a dict and also
        # picks a next action, which this endpoint has no business doing.
        captured = engine.capture(dump)
        self._persist(engine)
        _publish({"event": "intake.captured", "count": len(captured)})
        return {
            "captured": [i.to_dict() for i in captured],
            "total": len(engine.items),
        }

    def complete(self, item_id: str) -> Dict[str, Any]:
        """Mark an item done. Returns what to do next, because momentum is free."""
        from jarvisx.agentic.intake import Energy

        engine = self._load_engine()
        found = engine.complete(item_id)
        if not found:
            return {"error": f"no item {item_id}", "ok": False}
        self._persist(engine)
        chosen = engine.pick(Energy.MEDIUM)
        _publish({"event": "intake.completed", "item_id": item_id})
        return {"ok": True, "next": chosen.to_dict() if chosen else None}

    def _load_engine(self):
        from jarvisx.agentic.intake import IntakeEngine

        engine = IntakeEngine()
        path = self.intake_path
        if path and Path(path).exists():
            try:
                engine.load(json.loads(Path(path).read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                logger.warning("could not read intake state at %s", path)
        return engine

    def _persist(self, engine) -> None:
        path = self.intake_path
        if not path:
            return
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(
                json.dumps(engine.to_dict(), indent=2), encoding="utf-8"
            )
        except OSError as exc:  # pragma: no cover - disk/permission issues
            logger.warning("could not persist intake state: %s", exc)

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


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #

# One big "do this next" card and nothing else competing for attention. A list
# of twelve equally-weighted tasks is not a tool for an ADHD brain, it is the
# problem. The list is below the fold and deliberately quieter.
_DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alfred</title>
<style>
  :root {
    --bg: #0f1115; --card: #171a21; --line: #262b36;
    --ink: #e8eaed; --dim: #8b93a1; --accent: #6ee7b7; --warn: #fbbf24;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px; background: var(--bg); color: var(--ink);
    font: 16px/1.5 ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
  }
  .wrap { max-width: 720px; margin: 0 auto; }
  h1 { font-size: 15px; letter-spacing: .12em; text-transform: uppercase;
       color: var(--dim); margin: 0 0 20px; font-weight: 600; }
  .card { background: var(--card); border: 1px solid var(--line);
          border-radius: 14px; padding: 22px; margin-bottom: 14px; }
  .next { border-left: 4px solid var(--accent); }
  .label { color: var(--dim); font-size: 13px; letter-spacing: .08em;
           text-transform: uppercase; margin-bottom: 8px; }
  .title { font-size: 26px; font-weight: 600; line-height: 1.25; margin: 0 0 10px; }
  .step { color: var(--accent); font-size: 16px; margin-bottom: 12px; }
  .meta { color: var(--dim); font-size: 14px; }
  .energy { display: flex; gap: 8px; margin-bottom: 18px; }
  .energy button {
    flex: 1; padding: 9px; background: var(--card); color: var(--dim);
    border: 1px solid var(--line); border-radius: 9px; cursor: pointer; font: inherit;
  }
  .energy button.on { color: var(--ink); border-color: var(--accent); }
  textarea {
    width: 100%; min-height: 74px; background: var(--bg); color: var(--ink);
    border: 1px solid var(--line); border-radius: 9px; padding: 11px;
    font: inherit; resize: vertical;
  }
  .row { display: flex; gap: 8px; margin-top: 10px; }
  button.act {
    padding: 10px 16px; background: var(--accent); color: #06281c; border: 0;
    border-radius: 9px; cursor: pointer; font: inherit; font-weight: 600;
  }
  button.done {
    background: none; color: var(--dim); border: 1px solid var(--line);
    border-radius: 8px; padding: 4px 10px; cursor: pointer; font-size: 13px;
  }
  button.done:hover { color: var(--ink); border-color: var(--accent); }
  li { display: flex; justify-content: space-between; align-items: center;
       gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--line); }
  li:last-child { border-bottom: 0; }
  ul { list-style: none; margin: 0; padding: 0; }
  .kind { color: var(--dim); font-size: 12px; text-transform: uppercase;
          letter-spacing: .06em; margin-right: 8px; }
  .empty { color: var(--dim); padding: 8px 0; }
  .aside { color: var(--dim); font-size: 14px; }
  .aside b { color: var(--warn); font-weight: 600; }
</style>
</head>
<body>
<div class="wrap">
  <h1>Alfred</h1>

  <div class="energy" id="energy">
    <button data-e="low">low energy</button>
    <button data-e="medium" class="on">medium</button>
    <button data-e="high">high energy</button>
  </div>

  <div class="card next">
    <div class="label">do this next</div>
    <p class="title" id="nextTitle">Loading&hellip;</p>
    <div class="step" id="nextStep"></div>
    <div class="meta" id="nextMeta"></div>
  </div>

  <div class="card">
    <div class="label">dump your head</div>
    <textarea id="dump" placeholder="everything on your mind, commas are fine"></textarea>
    <div class="row"><button class="act" id="capture">capture</button></div>
  </div>

  <div class="card">
    <div class="label">everything else</div>
    <ul id="list"></ul>
  </div>

  <div class="card aside" id="aside"></div>
</div>

<script>
let energy = "medium";

async function api(path, body) {
  const opts = body
    ? { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body) }
    : {};
  const res = await fetch(path, opts);
  return res.json();
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g,
    c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

async function refresh() {
  const data = await api("/intake");
  const pick = (data.next_at_energy || {})[energy];

  document.getElementById("nextTitle").textContent =
    pick ? pick.title : "Nothing on the list. Dump your head below.";
  document.getElementById("nextStep").textContent =
    pick && pick.next_action ? pick.next_action : "";
  document.getElementById("nextMeta").textContent =
    pick ? "about " + pick.est_minutes + " minutes &middot; nothing else until this is done"
         : "";

  const tasks = (data.items || []).filter(i => !i.done);
  const list = document.getElementById("list");
  list.innerHTML = tasks.length
    ? tasks.map(i =>
        '<li><span><span class="kind">' + esc(i.kind) + '</span>' +
        esc(i.title) + '</span>' +
        '<button class="done" data-id="' + esc(i.id) + '">done</button></li>').join("")
    : '<li class="empty">empty</li>';

  for (const btn of list.querySelectorAll("button.done")) {
    btn.onclick = async () => {
      await api("/intake/" + encodeURIComponent(btn.dataset.id) + "/done", {});
      refresh();
    };
  }

  const away = data.not_your_problem || [];
  document.getElementById("aside").innerHTML = away.length
    ? "<b>Not your problem:</b> " + esc(away.map(i => i.title).join(", ")) +
      ". Holding these is the work. Put them down."
    : data.open + " open items.";
}

document.getElementById("energy").onclick = e => {
  if (!e.target.dataset.e) return;
  energy = e.target.dataset.e;
  for (const b of document.querySelectorAll("#energy button"))
    b.classList.toggle("on", b === e.target);
  refresh();
};

document.getElementById("capture").onclick = async () => {
  const box = document.getElementById("dump");
  if (!box.value.trim()) return;
  await api("/intake", { dump: box.value });
  box.value = "";
  refresh();
};

document.getElementById("dump").addEventListener("keydown", e => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter")
    document.getElementById("capture").click();
});

refresh();
setInterval(refresh, 4000);
</script>
</body>
</html>
"""


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

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
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
                elif path == "/intake":
                    self._send(200, plane.intake())
                elif path == "/":
                    if "text/html" in (self.headers.get("Accept") or ""):
                        self._send_html(_DASHBOARD_HTML)
                    else:
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
                                    "GET /intake",
                                    "POST /intake",
                                    "POST /intake/{item_id}/done",
                                    "POST /plan",
                                    "POST /run",
                                    "POST /tasks",
                                ],
                                "dashboard": "GET / with Accept: text/html",
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
                elif path == "/intake":
                    dump = str(body.get("dump") or "").strip()
                    if not dump:
                        self._send(400, {"error": "'dump' is required"})
                        return
                    self._send(200, plane.capture(dump))
                elif path.startswith("/intake/") and path.endswith("/done"):
                    item_id = path[len("/intake/") : -len("/done")]
                    result = plane.complete(item_id)
                    self._send(404 if "error" in result else 200, result)
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
    intake_path: Optional[Path | str] = None,
) -> int:
    """Start the control plane. Blocks until interrupted."""
    backend = HeuristicBackend() if backend_name == "offline" else AutoBackend()
    plane = ControlPlane(backend=backend, trace_root=trace_root, intake_path=intake_path)
    server = ThreadingHTTPServer((host, port), _make_handler(plane))
    print(f"Alfred agentic control plane on http://{host}:{port}")
    print(f"  backend : {plane.backend.name}")
    print(f"  traces  : {plane.trace_root}")
    print(f"  sandbox : {plane.sandbox.workspace}")
    print(f"  tasks   : {plane.intake_path}")
    print(f"  dashboard: http://{host}:{port}/ (open in a browser)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.server_close()
        plane.sandbox.cleanup()
    return 0
