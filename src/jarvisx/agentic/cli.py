"""Command-line control plane for the agentic harness orchestration layer.

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
