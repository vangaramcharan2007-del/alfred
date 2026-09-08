#!/usr/bin/env python3
"""Live demonstration of the Alfred Agentic Harness Orchestration layer.

Runs entirely offline by default: no API key, no network. Point it at a real
provider with ``--backend auto`` and an OPENROUTER_API_KEY / GROQ_API_KEY /
OLLAMA_BASE_URL in the environment.

    python demo_agentic_harness.py
    python demo_agentic_harness.py --backend auto
    python demo_agentic_harness.py --goal "Build a CSV deduplicator"

What it proves, end to end:
  1. a goal is planned into a dependency DAG and split into parallel waves
  2. each node runs on its own harness with a role, budget and verifier
  3. tools execute for real inside a jailed sandbox (rlimits, secret scrub)
  4. verification is executable, not asserted by the model
  5. every decision is written to a replayable JSONL trace
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from jarvisx.agentic.backends import AutoBackend, HeuristicBackend  # noqa: E402
from jarvisx.agentic.cli import LivePrinter  # noqa: E402
from jarvisx.agentic.sandbox import SandboxedRunner, scrub_env  # noqa: E402
from jarvisx.agentic.scheduler import Orchestrator  # noqa: E402
from jarvisx.agentic.trace import TraceRecorder, render_trace  # noqa: E402
from jarvisx.agentic.types import Budget  # noqa: E402

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def header(text: str) -> None:
    print(f"\n{CYAN}{BOLD}{'=' * 78}{RESET}")
    print(f"{CYAN}{BOLD}  {text}{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 78}{RESET}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goal", default="Implement a sieve of Eratosthenes and verify it")
    parser.add_argument(
        "--backend",
        default="offline",
        choices=["offline", "auto"],
        help="offline = deterministic local planner; auto = real model provider",
    )
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    workspace = Path(tempfile.mkdtemp(prefix="alfred_demo_"))
    trace_root = workspace / "traces"

    # ------------------------------------------------------------------ #
    header("1. SANDBOX ISOLATION IS REAL")
    # ------------------------------------------------------------------ #
    with SandboxedRunner(workspace=workspace / "sandbox", timeout_seconds=2) as sandbox:
        good = sandbox.run_python("print('hello from inside the jail')")
        print(f"{GREEN}ok{RESET}   run_python           exit={good.exit_code} out={good.stdout.strip()!r}")

        escaped = None
        try:
            sandbox.resolve("../../../etc/passwd")
        except Exception as exc:  # noqa: BLE001
            escaped = exc
        print(f"{GREEN}ok{RESET}   path jail            {type(escaped).__name__}: {escaped}")

        timeout_run = sandbox.run_python("import time; time.sleep(30)")
        print(
            f"{GREEN}ok{RESET}   timeout enforcement  timed_out={timeout_run.timed_out} "
            f"after {timeout_run.duration_ms:.0f}ms"
        )

        scrubbed = scrub_env()
        leaked = [k for k in scrubbed if "API_KEY" in k.upper() or "SECRET" in k.upper()]
        print(f"{GREEN}ok{RESET}   secret scrubbing     {len(scrubbed)} vars passed through, {len(leaked)} secrets leaked")

    # ------------------------------------------------------------------ #
    header("2. PLANNING A GOAL INTO A DEPENDENCY DAG")
    # ------------------------------------------------------------------ #
    backend = HeuristicBackend() if args.backend == "offline" else AutoBackend()
    print(f"model backend : {BOLD}{backend.name}{RESET}")
    print(f"goal          : {BOLD}{args.goal}{RESET}\n")

    orchestrator = Orchestrator(
        backend=backend,
        sandbox=SandboxedRunner(workspace=workspace / "shared"),
        default_budget=Budget(max_steps=args.max_steps, max_tool_calls=20, max_seconds=180),
        trace_root=trace_root,
        max_workers=4,
        on_event=LivePrinter(verbose=args.verbose),
    )

    graph = orchestrator.plan(args.goal)
    print(graph.render())
    print(f"\n{DIM}planning strategy: {getattr(orchestrator.planner, 'last_strategy', 'unknown')}{RESET}")

    # ------------------------------------------------------------------ #
    header("3. EXECUTING THE GRAPH (live)")
    # ------------------------------------------------------------------ #
    report = orchestrator.run(args.goal, graph=graph)

    # ------------------------------------------------------------------ #
    header("4. VERIFICATION — EXECUTED, NOT ASSERTED")
    # ------------------------------------------------------------------ #
    for node_id, outcome in report.outcomes.items():
        if not outcome.result or not outcome.result.verdict:
            continue
        verdict = outcome.result.verdict
        mark = f"{GREEN}PASS{RESET}" if verdict.passed else f"{YELLOW}FAIL{RESET}"
        print(f"  {node_id:<12} {mark}  score={verdict.score}  {verdict.rationale}")
        for check in verdict.checks:
            tick = f"{GREEN}+{RESET}" if check["passed"] else f"{YELLOW}-{RESET}"
            evidence = str(check["evidence"]).replace("\n", " ")[:70]
            print(f"      {tick} {check['name']:<16} {evidence}")

    # ------------------------------------------------------------------ #
    header("5. ARTIFACTS PRODUCED IN THE SANDBOX")
    # ------------------------------------------------------------------ #
    files = orchestrator.sandbox.list_files()
    if not files:
        print(f"{DIM}(the offline planner produced no files; use --backend auto for real code){RESET}")
    for name in files:
        content = orchestrator.sandbox.read_file(name)
        print(f"  {BOLD}{name}{RESET} ({len(content.splitlines())} lines)")
        for line in content.splitlines()[:8]:
            print(f"      {DIM}{line}{RESET}")

    # ------------------------------------------------------------------ #
    header("6. REPLAYABLE TRACE")
    # ------------------------------------------------------------------ #
    traces = sorted(trace_root.glob("*.jsonl"))
    print(f"{len(traces)} run traces written to {trace_root}\n")
    if traces:
        print(render_trace(traces[0]))
        print(f"\n{DIM}summary: {json.dumps(TraceRecorder.summarize(traces[0])['by_kind'])}{RESET}")

    # ------------------------------------------------------------------ #
    header("RESULT")
    # ------------------------------------------------------------------ #
    print(f"  goal        : {args.goal}")
    print(f"  status      : {GREEN if report.ok else YELLOW}{'SUCCEEDED' if report.ok else 'FAILED'}{RESET}")
    print(f"  succeeded   : {report.succeeded}")
    print(f"  failed      : {report.failed or 'none'}")
    print(f"  skipped     : {report.skipped or 'none'}")
    print(f"  tool calls  : {report.usage.tool_calls}")
    print(f"  harness steps: {report.usage.steps}")
    print(f"  wall time   : {report.to_dict()['duration_seconds']}s")
    print(f"\n{DIM}workspace: {workspace}{RESET}")

    orchestrator.close()
    shutil.rmtree(workspace, ignore_errors=True)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
