"""Command-line control plane for the agentic harness orchestration layer.

    python -m jarvisx.agentic doctor                    # <- start here
    python -m jarvisx.agentic roles
    python -m jarvisx.agentic tools
    python -m jarvisx.agentic plan  "Build a CSV deduplicator with tests"
    python -m jarvisx.agentic run   "Build a CSV deduplicator with tests"
    python -m jarvisx.agentic task  "List the primes below 100"
    python -m jarvisx.agentic runs
    python -m jarvisx.agentic trace var/agentic/runs/<run_id>.jsonl
    python -m jarvisx.agentic serve --port 8123
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from jarvisx.agentic.backends import AutoBackend, HeuristicBackend
from jarvisx.agentic.builtin_tools import build_default_tools
from jarvisx.agentic.env import redact
from jarvisx.agentic.graph import TaskGraph
from jarvisx.agentic.harness import AgentHarness
from jarvisx.agentic.roles import RoleRegistry
from jarvisx.agentic.sandbox import SandboxedRunner
from jarvisx.agentic.scheduler import DEFAULT_TRACE_ROOT, Orchestrator
from jarvisx.agentic.trace import TraceRecorder, render_trace
from jarvisx.agentic.types import Budget, OrchestrationReport, RunResult, RunStatus
from jarvisx.agentic.verifier import Verifier

# ANSI colours, disabled automatically when not attached to a terminal.
_TTY = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _TTY else text


def _green(t: str) -> str:
    return _c("32", t)


def _red(t: str) -> str:
    return _c("31", t)


def _yellow(t: str) -> str:
    return _c("33", t)


def _dim(t: str) -> str:
    return _c("2", t)


def _bold(t: str) -> str:
    return _c("1", t)


# --------------------------------------------------------------------------- #
# Live event renderer
# --------------------------------------------------------------------------- #


_STATUS_COLOUR = {
    "succeeded": _green,
    "failed": _red,
    "skipped": _yellow,
    "budget_exceeded": _yellow,
    "denied": _yellow,
}


class LivePrinter:
    """Renders orchestrator/harness events as they happen."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.started = time.time()

    def __call__(self, event: Dict[str, Any]) -> None:
        kind = event.get("kind", "")
        stamp = _dim(f"[{time.time() - self.started:6.2f}s]")

        if kind == "orchestration_start":
            print(f"{stamp} {_bold('GOAL')} {event.get('goal')}")
            print(f"{stamp} strategy={event.get('strategy')} waves={event.get('waves')}")
        elif kind == "wave_start":
            nodes = event.get("nodes") or []
            mode = "parallel" if event.get("parallel") else "serial"
            print(f"{stamp} {_bold('WAVE')} {event.get('wave')} ({mode}): {', '.join(nodes)}")
        elif kind == "node_start":
            attempt = f" attempt {event['attempt']}" if event.get("attempt", 1) > 1 else ""
            print(f"{stamp}   {_bold('->')} {event.get('node')} [{event.get('role')}]{attempt}")
            print(f"{stamp}      {str(event.get('instruction'))[:110]}")
        elif kind == "tool_call":
            args = json.dumps(event.get("arguments", {}), default=str)
            if len(args) > 90:
                args = args[:90] + "..."
            repeat = f" (repeat {event['repeat']})" if event.get("repeat", 1) > 1 else ""
            print(f"{stamp}      {_dim('call')} {event.get('name')} {args}{repeat}")
        elif kind == "observation":
            if event.get("denied"):
                print(f"{stamp}      {_yellow('DENIED')} {event.get('tool')}")
            elif not event.get("ok"):
                print(f"{stamp}      {_red('error')} {event.get('tool')}: {str(event.get('error'))[:90]}")
            elif self.verbose:
                print(f"{stamp}      {_green('ok')} {event.get('tool')}")
        elif kind == "node_end":
            colour = _STATUS_COLOUR.get(event.get("status", ""), str)
            line = f"{stamp}   {_bold('<-')} {event.get('node')} {colour(event.get('status', ''))}"
            if event.get("error"):
                line += f" — {str(event['error'])[:90]}"
            print(line)
        elif kind == "node_skipped":
            print(f"{stamp}   {_yellow('SKIP')} {event.get('node')} (blocked by {event.get('blocked_by')})")
        elif kind == "orchestration_end":
            ok = event.get("ok")
            print(
                f"{stamp} {_bold('DONE')} "
                + (_green("ok") if ok else _red("failed"))
                + f" succeeded={event.get('succeeded')} failed={event.get('failed')} "
                f"skipped={event.get('skipped')} tool_calls={event.get('tool_calls')}"
            )
        elif self.verbose:
            print(f"{stamp} {kind} {event}")


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #


def cmd_roles(_args: argparse.Namespace) -> int:
    print(_bold("Registered agent roles"))
    print(RoleRegistry().describe())
    return 0


def cmd_tools(args: argparse.Namespace) -> int:
    with SandboxedRunner() as sandbox:
        registry = build_default_tools(sandbox)
        print(_bold(f"{len(registry)} harness tools"))
        for schema in registry.flat_schemas():
            tier = schema["permission"]
            coloured = _green(tier) if tier == "SAFE" else _yellow(tier)
            print(f"  {schema['name']:<14} [{coloured}] {schema['description']}")
            params = schema["parameters"].get("properties", {})
            if params:
                required = set(schema["parameters"].get("required", []))
                rendered = ", ".join(
                    f"{name}{'' if name not in required else '*'}:{spec.get('type')}"
                    for name, spec in params.items()
                )
                print(f"      {_dim(rendered)}")
    return 0


def _make_backend(name: str):
    if name == "offline":
        return HeuristicBackend()
    return AutoBackend()


def cmd_plan(args: argparse.Namespace) -> int:
    with Orchestrator(backend=_make_backend(args.backend)) as orch:
        graph = orch.plan(args.goal)
        print(_bold("Task graph"))
        print(graph.render())
        if args.json:
            print(json.dumps(graph.to_dict(), indent=2))
        strategy = getattr(orch.planner, "last_strategy", "unknown")
        print(_dim(f"\nplanning strategy: {strategy}"))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    printer = LivePrinter(verbose=args.verbose)
    budget = Budget(
        max_steps=args.max_steps,
        max_tool_calls=args.max_tool_calls,
        max_seconds=args.max_seconds,
    )
    with Orchestrator(
        backend=_make_backend(args.backend),
        default_budget=budget,
        max_workers=args.workers,
        trace_root=args.trace_root,
        on_event=printer,
    ) as orch:
        report = orch.run(args.goal)

    print()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        print(_bold("Result"))
        print(report.final_output() or _dim("(no output produced)"))
        print()
        print(_dim(f"report: {orch.trace_root / (report.graph_id + '.orchestration.json')}"))
    return 0 if report.ok else 1


def cmd_task(args: argparse.Namespace) -> int:
    printer = LivePrinter(verbose=args.verbose)
    roles = RoleRegistry()
    spec = roles.get(args.role)
    with SandboxedRunner() as sandbox:
        harness = AgentHarness(
            backend=_make_backend(args.backend),
            registry=build_default_tools(sandbox),
            sandbox=sandbox,
            role=spec.name,
            role_prompt=spec.system_prompt(),
            budget=Budget(
                max_steps=args.max_steps,
                max_tool_calls=args.max_tool_calls,
                max_seconds=args.max_seconds,
            ),
            verifier=Verifier(),
            trace_root=args.trace_root,
            on_event=printer,
        )
        result = harness.run(args.task)
        files = sandbox.list_files()

    print()
    print(_bold(f"[{spec.name}] {result.status.value}"))
    if result.output:
        print(result.output)
    if result.error:
        print(_red(result.error))
    print(
        _dim(
            f"\nsteps={result.usage.steps} tool_calls={result.usage.tool_calls} "
            f"tokens={result.usage.prompt_tokens + result.usage.completion_tokens} "
            f"wall={result.usage.wall_seconds:.2f}s"
        )
    )
    if files:
        print(_dim(f"workspace files: {files}"))
    return 0 if result.status is RunStatus.SUCCEEDED else 1


def cmd_runs(args: argparse.Namespace) -> int:
    root = Path(args.trace_root)
    if not root.exists():
        print(_dim(f"no runs recorded yet in {root}"))
        return 0
    traces = sorted(root.glob("*.jsonl"))
    if not traces:
        print(_dim(f"no trace files in {root}"))
        return 0
    print(_bold(f"{len(traces)} recorded runs in {root}"))
    for path in traces[-args.limit :]:
        summary = TraceRecorder.summarize(path)
        final = summary["final"]
        status = final.get("status", "?") if final.get("kind") == "run_end" else "?"
        colour = _STATUS_COLOUR.get(status, str)
        print(
            f"  {path.stem:<34} {colour(status):<12} "
            f"events={summary['events']:<4} {summary['duration_seconds']}s"
        )
    return 0


def cmd_trace(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(_red(f"no such trace file: {path}"), file=sys.stderr)
        return 2
    if args.json:
        for event in TraceRecorder.iter_file(path):
            print(json.dumps(event, default=str))
    else:
        print(render_trace(path))
        print()
        print(json.dumps(TraceRecorder.summarize(path), indent=2, default=str))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """One command that tells you exactly what is wired and what is not."""
    from jarvisx.agentic.env import (
        describe_credentials,
        loaded_files,
        load_dotenv,
        required_model_env,
    )
    from jarvisx.agentic.sandbox import SandboxedRunner

    ok_all = True

    def line(symbol: str, label: str, detail: str = "") -> None:
        pad = " " * max(1, 26 - len(label))
        print(f"  {symbol} {label}{pad}{_dim(detail) if detail else ''}")

    print(_bold("\nAlfred agentic doctor\n"))

    # -- 1. credentials ---------------------------------------------------- #
    print(_bold("1. Credentials"))
    load_dotenv()
    creds = describe_credentials()
    if creds["configured"]:
        for name in creds["configured"]:
            line(_green("OK"), name, f"fingerprint {creds['fingerprints'][name]}")
    else:
        ok_all = False
        line(_yellow("--"), "no API key found", "agent will run OFFLINE (heuristic)")
    line(_dim(".."), ".env files seen", ", ".join(creds["env_files"]) or "none")

    # -- 2. backend selection ---------------------------------------------- #
    print("\n" + _bold("2. Backend selection"))
    settings = required_model_env()
    for key, value in settings.items():
        if value:
            line(_dim(".."), key, str(value))
    backend = _make_backend(args.backend)
    line(_green("OK") if backend.name != "heuristic" else _yellow("--"),
         "selected backend", backend.name)
    if backend.name == "heuristic" and args.backend == "auto":
        ok_all = False
        print(_yellow("     -> offline mode writes a placeholder file, not real code."))

    # -- 3. live model round-trip ------------------------------------------ #
    print("\n" + _bold("3. Live model round-trip"))
    if backend.name == "heuristic":
        line(_yellow("--"), "skipped", "no model configured")
    else:
        try:
            message = backend.complete(
                [
                    {"role": "system", "content": "Reply with exactly: PONG"},
                    {"role": "user", "content": "ping"},
                ],
                tools=None,
            )
            reply = (message.content or "").strip()
            if reply:
                line(_green("OK"), "model responded", f"{reply[:60]!r} model={message.model}")
            else:
                ok_all = False
                line(_red("!!"), "empty response", "check model name / quota")
        except Exception as exc:  # noqa: BLE001 - report, never crash
            ok_all = False
            line(_red("!!"), "call failed", redact(str(exc))[:110])

    # -- 4. tool calling --------------------------------------------------- #
    print("\n" + _bold("4. Tool calling"))
    if backend.name == "heuristic":
        line(_yellow("--"), "skipped", "no model configured")
    else:
        try:
            with SandboxedRunner() as sandbox:
                registry = build_default_tools(sandbox)
                message = backend.complete(
                    [
                        {"role": "system", "content": "Use the list_files tool. Do not answer in prose."},
                        {"role": "user", "content": "What files are in the workspace?"},
                    ],
                    tools=registry.openai_schemas(),
                )
            if message.tool_calls:
                line(_green("OK"), "native tool calls", message.tool_calls[0].name)
            else:
                line(_yellow("--"), "no tool call returned",
                     "model may not support tools; set GROQ_MODEL to one that does")
        except Exception as exc:  # noqa: BLE001
            line(_red("!!"), "tool probe failed", redact(str(exc))[:110])

    # -- 5. sandbox --------------------------------------------------------- #
    print("\n" + _bold("5. Sandbox"))
    with SandboxedRunner() as sandbox:
        result = sandbox.run_python("print(6 * 7)")
        line(_green("OK") if "42" in result.stdout else _red("!!"),
             "code execution", f"exit={result.exit_code} out={result.stdout.strip()!r}")
        try:
            sandbox.resolve("../../etc/passwd")
            ok_all = False
            line(_red("!!"), "path jail", "ESCAPE NOT BLOCKED")
        except Exception:  # noqa: BLE001 - expected
            line(_green("OK"), "path jail", "escape blocked")
        pytest_check = sandbox.run_pytest("--version")
        line(_green("OK") if pytest_check.ok else _yellow("--"),
             "pytest available", "verification checks will run"
             if pytest_check.ok else "install pytest for real verification")

    # -- 6. verdict --------------------------------------------------------- #
    print()
    if ok_all:
        print("  " + _green(_bold("READY")) + "  run: python -m jarvisx.agentic run \"your goal\"")
    else:
        print("  " + _yellow(_bold("NOT READY")) + "  fix the items above, then re-run doctor")
        print(_dim("  quickest fix: add GROQ_API_KEY=gsk_... to .env in the repo root"))
    print()
    return 0 if ok_all else 1


def cmd_serve(args: argparse.Namespace) -> int:
    from jarvisx.agentic.control_plane import serve

    return serve(host=args.host, port=args.port, backend_name=args.backend)


# --------------------------------------------------------------------------- #
# Parser
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jarvisx.agentic",
        description="Alfred agentic harness orchestration control plane",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("roles", help="list agent roles").set_defaults(func=cmd_roles)
    sub.add_parser("tools", help="list harness tools").set_defaults(func=cmd_tools)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--backend", default="auto", choices=["auto", "offline"])
        p.add_argument("--trace-root", default=str(DEFAULT_TRACE_ROOT))
        p.add_argument("--max-steps", type=int, default=8)
        p.add_argument("--max-tool-calls", type=int, default=24)
        p.add_argument("--max-seconds", type=float, default=180.0)
        p.add_argument("--verbose", action="store_true")

    p_plan = sub.add_parser("plan", help="plan a goal without executing it")
    p_plan.add_argument("goal")
    p_plan.add_argument("--json", action="store_true")
    add_common(p_plan)
    p_plan.set_defaults(func=cmd_plan)

    p_run = sub.add_parser("run", help="plan and execute a goal")
    p_run.add_argument("goal")
    p_run.add_argument("--json", action="store_true")
    p_run.add_argument("--workers", type=int, default=4)
    add_common(p_run)
    p_run.set_defaults(func=cmd_run)

    p_task = sub.add_parser("task", help="run a single agent task (no orchestration)")
    p_task.add_argument("task")
    p_task.add_argument("--role", default="generalist")
    add_common(p_task)
    p_task.set_defaults(func=cmd_task)

    p_runs = sub.add_parser("runs", help="list recorded runs")
    p_runs.add_argument("--trace-root", default=str(DEFAULT_TRACE_ROOT))
    p_runs.add_argument("--limit", type=int, default=20)
    p_runs.set_defaults(func=cmd_runs)

    p_trace = sub.add_parser("trace", help="render a recorded trace")
    p_trace.add_argument("path")
    p_trace.add_argument("--json", action="store_true")
    p_trace.set_defaults(func=cmd_trace)

    p_doctor = sub.add_parser(
        "doctor", help="diagnose credentials, model, tool calling and sandbox"
    )
    add_common(p_doctor)
    p_doctor.set_defaults(func=cmd_doctor)

    p_serve = sub.add_parser("serve", help="start the HTTP control plane")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8123)
    p_serve.add_argument("--backend", default="auto")
    p_serve.set_defaults(func=cmd_serve)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
