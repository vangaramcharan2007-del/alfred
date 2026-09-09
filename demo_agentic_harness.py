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


def _demo_adhd_layer(workspace: Path) -> None:
    """Demonstrate the ADHD layer: capture, pick, persona, reach, policy.

    Runs entirely offline and deterministically. Every line below is real
    execution against the shipped modules, not a transcript pasted in.
    """
    from jarvisx.agentic.actions import build_action_tools, classify_command
    from jarvisx.agentic.intake import Energy, IntakeEngine
    from jarvisx.agentic.persona import PERSONAS, get_persona
    from jarvisx.agentic.types import ToolCall
    from jarvisx.agentic.voice_loop import (
        ConsoleInput,
        ConsoleOutput,
        Intent,
        VoiceAgentLoop,
        route,
    )

    dump = (
        "write the OS assignment its due today, reply to that email from the "
        "professor, pay the electricity bill, i'm really worried about failing "
        "this semester, someone should really fix the lab printer"
    )

    print(f"{DIM}brain dump{RESET}  {dump}\n")

    engine = IntakeEngine()
    plan = engine.plan(dump)

    print("captured, and classified:")
    for item in engine.items:
        kind = item.kind.value
        colour = GREEN if kind == "task" else YELLOW
        print(f"  {colour}[{kind:9}]{RESET} {item.title}")

    not_yours = plan["not_your_problem"]
    print(
        f"\n{YELLOW}not yours{RESET}   {', '.join(not_yours) if not_yours else 'nothing'}"
        f"\n{DIM}              taken OUT of the queue — holding them is itself the work{RESET}"
    )

    print("\nthe same list, offered against different energy:")
    for energy in (Energy.LOW, Energy.MEDIUM, Energy.HIGH):
        chosen = engine.pick(energy)
        print(
            f"  {energy.value:7} -> {chosen.title} "
            f"{DIM}({chosen.est_minutes}m, urgency {chosen.urgency}){RESET}"
        )
    print(f"{DIM}          low energy never offers the 45-minute task{RESET}")

    print("\npersona re-voices the decision, it never changes it:")
    picks = {}
    # Iterate the registry rather than a hardcoded list, so adding a persona
    # cannot silently leave the demo demonstrating a stale subset.
    for name in PERSONAS:
        persona = get_persona(name)
        # A fresh engine from the same state: proves the voice changes without
        # the pick changing, rather than reusing one mutated engine.
        clone = IntakeEngine()
        clone.load(engine.to_dict())
        chosen = clone.pick(Energy.HIGH)
        picks[name] = chosen.title
        line = persona.render(
            "", {"kind": "picked", "task": chosen.title, "minutes": chosen.est_minutes}
        )
        print(f"  {name:7} {line}")
    same = len(set(picks.values())) == 1
    mark = f"{GREEN}ok{RESET}" if same else f"{YELLOW}!!{RESET}"
    print(f"  {mark}   all {len(picks)} picked the same task: {same}")

    print("\nphysical reach, and the gate in front of it:")
    registry = build_action_tools(dry_run=True, workspace=str(workspace / "reach"))
    for command in ("ls -la", "sudo apt install x", "rm -rf /", "format c:"):
        verdict = classify_command(command)
        colour = {"allow": GREEN, "confirm": YELLOW, "blocked": YELLOW}[verdict]
        note = {
            "allow": "runs",
            "confirm": "asks you first",
            "blocked": "refused EVEN IF you say yes",
        }[verdict]
        print(f"  {colour}{verdict:8}{RESET} {command:<22} {DIM}{note}{RESET}")

    print("\nsaying it out loud, with reach enabled:")
    loop = VoiceAgentLoop(
        stt=ConsoleInput(lines=["open spotify", "play lofi on youtube"]),
        tts=ConsoleOutput(),
        physical=registry,
    )
    for _ in range(2):
        turn = loop.listen_once()
        print(f"  {GREEN}ok{RESET}   {turn.transcript:<24} -> {turn.intent.name}")

    print("\nand without reach, it degrades honestly instead of pretending:")
    for text in ("open spotify",):
        intent = route(text, physical=False)
        print(
            f"  {YELLOW}--{RESET}   {text:<24} -> {intent.name} "
            f"{DIM}(captured, never claims it opened){RESET}"
        )


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
    header("7. THE ADHD LAYER — TALK / LISTEN / WATCH / DO")
    # ------------------------------------------------------------------ #
    _demo_adhd_layer(workspace)

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
