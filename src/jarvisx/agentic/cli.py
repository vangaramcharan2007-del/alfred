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


# --------------------------------------------------------------------------- #
# Doctor probes for the optional layers. Each returns (detail, ok) and must
# never raise: doctor is the thing you run when something is already wrong.
# --------------------------------------------------------------------------- #


def _probe_mic():
    from jarvisx.agentic.voice_loop import WhisperMicInput

    mic = WhisperMicInput()
    if mic.available:
        return "microphone ready — `alfred` will listen", True
    return "no microphone; `alfred --text` types instead", False


def _probe_tts():
    from jarvisx.agentic.voice_loop import TTSOutput

    tts = TTSOutput()
    if tts.available:
        return "speech output ready — replies are spoken", True
    return "no TTS engine; replies are printed", False


def _probe_window_sensor():
    from jarvisx.agentic.watch import ActiveWindowSource

    source = ActiveWindowSource()
    if source.available:
        return "can see the active window — `watch` works", True
    return "no desktop sensor; use `watch --demo`", False


def _probe_physical():
    from jarvisx.agentic.actions import build_action_tools, classify_command
    from jarvisx.agentic.types import ToolCall

    registry = build_action_tools(dry_run=True)
    names = set(registry.names())
    if "open_app_or_website" not in names:
        return "action tools failed to register", False
    # Prove the gate rather than assume it: physical reach with a soft policy
    # gate is worse than no physical reach at all.
    if classify_command("rm -rf /") != "blocked":
        return "POLICY GATE BROKEN — destructive commands not blocked", False
    registry.invoke(ToolCall(name="open_app_or_website", arguments={"target": "x"}))
    return f"{len(names)} tools; 'open spotify' works, rm -rf is blocked", True


def _probe_config():
    from jarvisx.agentic.config import load as load_config

    config = load_config()
    if not config.found:
        return "none; `alfred --persona jarvis --save-config` remembers your flags", False
    detail = f"{config.source}"
    if config.warnings:
        return f"{detail} — but {'; '.join(config.warnings)}", False
    return detail, True


def _probe_intake():
    from jarvisx.agentic.intake import Energy, IntakeEngine
    from jarvisx.agentic.persona import PERSONAS

    engine = IntakeEngine()
    engine.plan("write the assignment, pay the bill, i am so stressed")
    if len(engine.items) != 3:
        return f"brain dump split into {len(engine.items)}, expected 3", False
    if engine.pick(Energy.LOW) is None:
        return "energy-based picking returned nothing", False
    # Report the number, not just the claim. "blob splits" is unverifiable
    # prose; "3 items from 1 dump" is something a reader can check.
    return (
        f"1 dump -> {len(engine.items)} items; "
        f"{len(PERSONAS)} personas; low energy picks small",
        True,
    )


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

    # -- 6. the ADHD layer --------------------------------------------------- #
    # Ears, mouth, eyes and hands are all optional and all degrade. Reporting
    # them here means nobody has to read a README to find out what works.
    print("\n" + _bold("6. Alfred (talk / listen / watch / do)"))

    def probe(label, fn):
        try:
            detail, ok = fn()
        except Exception as exc:  # noqa: BLE001 - a probe must never crash doctor
            detail, ok = f"probe failed: {exc}", False
        line(_green("OK") if ok else _yellow("--"), label, detail)
        return ok

    probe("ears (microphone)", lambda: _probe_mic())
    probe("mouth (speech out)", lambda: _probe_tts())
    probe("eyes (active window)", lambda: _probe_window_sensor())
    probe("hands (physical reach)", lambda: _probe_physical())
    probe("preferences file", lambda: _probe_config())
    probe("intake + personas", lambda: _probe_intake())

    # -- 7. verdict --------------------------------------------------------- #
    print()
    if ok_all:
        print("  " + _green(_bold("READY")) + "  run: python -m jarvisx.agentic run \"your goal\"")
    else:
        print("  " + _yellow(_bold("NOT READY")) + "  fix the items above, then re-run doctor")
        print(_dim("  quickest fix: add GROQ_API_KEY=gsk_... to .env in the repo root"))
    print()
    return 0 if ok_all else 1


def cmd_talk(args: argparse.Namespace) -> int:
    """Interactive voice (or text) loop: listens, decides, acts, speaks."""
    from jarvisx.agentic.intake import Energy
    from jarvisx.agentic.voice_loop import (
        ConsoleInput,
        ConsoleOutput,
        TTSOutput,
        VoiceAgentLoop,
        WhisperMicInput,
    )

    intake = _load_intake(args.state)

    stt = WhisperMicInput(wake_word=args.wake_word) if not args.text else ConsoleInput()
    tts = ConsoleOutput() if args.text else TTSOutput()

    runner = None
    if args.enable_agent:
        backend = _make_backend(args.backend)

        def runner(goal: str) -> Dict[str, Any]:
            budget = Budget(
                max_steps=args.max_steps,
                max_tool_calls=args.max_tool_calls,
                max_seconds=args.max_seconds,
            )
            with Orchestrator(
                backend=backend,
                default_budget=budget,
                max_workers=args.workers,
                trace_root=args.trace_root,
                on_event=LivePrinter(verbose=args.verbose),
            ) as orch:
                return orch.run(goal).to_dict()

    loop = VoiceAgentLoop(
        stt=stt,
        tts=tts,
        intake=intake,
        runner=runner,
        wake_word=args.wake_word,
        energy=Energy(args.energy),
    )

    print(_bold("\nAlfred is listening.") + _dim("  (Ctrl-C or 'quit' to stop)\n"))
    if not getattr(stt, "available", True):
        print(_yellow("  microphone unavailable — falling back to typed input"))
    if not args.enable_agent:
        print(_dim("  agent hand-off disabled; add --enable-agent to run real work"))
    print()

    try:
        loop.run(max_turns=args.turns)
    except KeyboardInterrupt:
        print(_dim("\nstopping"))

    _save_intake(args.state, intake)
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    """One-shot: capture a brain dump and print the single next action."""
    from jarvisx.agentic.intake import Energy

    intake = _load_intake(args.state)
    # NB: plan() captures internally. Calling capture() here as well would
    # record every item twice.
    plan = intake.plan(args.dump, energy=Energy(args.energy)) if args.dump else None

    if plan:
        print(_bold(f"\nCaptured {len(plan['captured'])} things"))
        for item in plan["captured"]:
            print(f"  [{item['kind']:<8}] ~{item['est_minutes']:>3}m  {item['title']}")
        if plan["not_your_problem"]:
            print(_dim(f"\nnot yours: {', '.join(plan['not_your_problem'])}"))

    pick = intake.pick(Energy(args.energy))
    if pick is None:
        print(_yellow("\nNothing captured. Pass --dump \"everything on your mind\""))
        _save_intake(args.state, intake)
        return 1

    from jarvisx.agentic.intake import breakdown

    print(_bold(f"\nDO THIS NEXT: {pick.title}") + _dim(f"  (~{pick.est_minutes}m)"))
    for index, step in enumerate(breakdown(pick.raw, 3), start=1):
        print(f"  {index}. {step}")
    print()
    _save_intake(args.state, intake)
    return 0


def _load_intake(path: Optional[str]):
    """Restore the captured task list, if there is one."""
    from jarvisx.agentic.intake import IntakeEngine

    intake = IntakeEngine()
    if path and Path(path).exists():
        try:
            intake.load(json.loads(Path(path).read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            print(_yellow(f"could not read state {path}: {exc}"))
    return intake


def _save_intake(path: Optional[str], intake) -> None:
    if not path:
        return
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(intake.to_dict(), indent=2), encoding="utf-8")
    except OSError as exc:  # pragma: no cover - disk/permission issues
        print(_yellow(f"could not save state: {exc}"))


def cmd_alfred(args: argparse.Namespace) -> int:
    """One agent that talks, listens, watches and does at the same time."""
    from jarvisx.agentic.config import load as load_config
    from jarvisx.agentic.intake import Energy
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    config = load_config(getattr(args, "config", None))
    for warning in config.warnings:
        print(_yellow(f"  config: {warning}"))

    if getattr(args, "save_config", False):
        return _save_alfred_config(args, config)

    def setting(name: str, default):
        """CLI flag, else config file, else built-in default."""
        given = getattr(args, name, None)
        if given is not None:
            return given
        return config.get(name, default)

    if config.found:
        print(_dim(f"  prefs   {config.describe()}"))

    try:
        energy = Energy(setting("energy", "medium"))
    except ValueError:
        print(_red(f"unknown energy level '{setting('energy', '')}' — try low, medium or high"))
        return 2

    state = setting("state", "var/agentic/intake.json")
    runtime_config = RuntimeConfig(
        energy=energy,
        speak_nudges=not setting("quiet", False),
        # --no-agent is a store_true, so it can only ever turn the agent OFF;
        # it can never contradict a config file asking for it on.
        enable_agent=not args.no_agent,
        watch=not args.no_watch and bool(setting("watch", True)),
        watch_interval=float(setting("interval", 15.0)),
        switch_window_minutes=int(setting("switch_window", 5)),
        switch_threshold=int(setting("switch_threshold", 6)),
        off_task_grace_minutes=int(setting("grace", 5)),
        break_after_minutes=int(setting("break_after", 50)),
        force_text=args.text,
        demo_watch=args.demo,
        state_path=state,
        trace_root=args.trace_root,
        max_turns=int(setting("turns", 200)),
        persona=setting("persona", "plain"),
        wake_word=setting("wake_word", "alfred"),
        enable_physical=bool(setting("physical", False)),
        physical_dry_run=bool(setting("physical_dry_run", False)),
        auto_capture=bool(setting("auto_capture", True)),
    )

    # Hand the runtime an intake it can share, so speech and clipboard land in
    # one list rather than two.
    runtime = AlfredRuntime(runtime_config, intake=_load_intake(state))
    try:
        runtime.serve()
    finally:
        _save_intake(state, runtime.intake)
    return 0


def _save_alfred_config(args: argparse.Namespace, config) -> int:
    """Persist the flags given on this line, so next time needs none.

    Only writes what the user actually typed. Dumping argparse's defaults into
    the file would freeze them, and then a later change to a default would
    silently stop applying.
    """
    from jarvisx.agentic.config import KNOWN_KEYS, save as save_config

    # store_true flags are False whether or not the user passed them, so a
    # False value carries no information. Writing it anyway would freeze the
    # default into the file, and a later change to that default would silently
    # stop applying. Only record what the user actually asserted.
    explicit = {
        name: value
        for name in KNOWN_KEYS
        for value in (getattr(args, name, None),)
        if value is not None and value is not False
    }
    if args.no_watch:
        explicit["watch"] = False
    if args.physical:
        explicit["physical"] = True

    if not explicit:
        print(_yellow("  nothing to save — pass the flags you want remembered, e.g."))
        print(_dim("    python -m jarvisx.agentic alfred --persona jarvis --physical --save-config"))
        return 2

    merged = dict(config.values)
    merged.update(explicit)
    target = save_config(merged, getattr(args, "config", None))
    print(_green(f"  saved {len(explicit)} preference(s) to {target}"))
    for key, value in sorted(explicit.items()):
        print(_dim(f"    {key} = {value!r}"))
    print(_dim("  next time just run: python -m jarvisx.agentic alfred"))
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    """Ambient watcher: notice fragmentation, drift and stray thoughts."""
    from jarvisx.agentic.watch import (
        ActiveWindowSource,
        AttentionLedger,
        ClipboardSource,
        ContextWatcher,
        ScriptedSource,
        Observation,
    )

    intake = _load_intake(args.state)

    def on_nudge(nudge) -> None:
        colour = {
            "fragmented": _yellow,
            "off_task": _yellow,
            "time_check": _yellow,
            "break": _green,
            "captured": _green,
        }.get(nudge.kind.value, str)
        # flush: a long-running watcher piped to a file or a terminal must
        # show nudges as they happen, not buffer them until exit.
        print(f"{colour(f'[{nudge.kind.value}]')} {nudge.message}", flush=True)

    source = None
    demo_ticks = None
    if args.demo:
        # A fixed 20-minute session that drifts, so the signals are visible
        # without a desktop, a microphone or a model.
        script = []
        for index in range(12):
            app = "code" if index % 2 == 0 else "chrome"
            script.append(
                Observation(
                    app=app,
                    title="YouTube - lofi beats" if app == "chrome" else "assignment.py",
                    mode="CODING" if app == "code" else "WEB_RESEARCH",
                    timestamp=float(index * 60),
                )
            )
        source = ScriptedSource(script)
        # A scripted source exhausts; without a tick cap this would spin
        # forever polling a source that will never produce another sample.
        demo_ticks = len(script)
    elif not args.no_sensors:
        source = ActiveWindowSource()

    ledger = AttentionLedger(
        switch_window_seconds=args.switch_window * 60,
        fragmentation_threshold=args.switch_threshold,
        off_task_seconds=args.grace * 60,
        break_after_seconds=args.break_after * 60,
    )
    if args.task:
        ledger.set_intended_task(args.task)

    clipboard = None if args.no_sensors else ClipboardSource()
    watcher = ContextWatcher(
        ledger=ledger,
        source=source,
        clipboard=clipboard,
        intake=intake,
        on_nudge=on_nudge,
        auto_capture=not args.no_capture,
    )

    print(_bold("\nAlfred is watching.") + _dim("  (Ctrl-C to stop)\n"))
    # Both cases must be caught: a source that exists but cannot read the
    # desktop, and no source at all (--no-sensors). Otherwise run() below gets
    # max_ticks=None and polls forever with nothing to poll.
    if source is None or not source.available:
        print(_yellow("  no desktop sensor available — nothing to watch"))
        print(_dim("  use --demo to see the signals on a synthetic session"))
        return 1
    if args.task:
        print(_dim(f"  stated task: {args.task}"))
    print(_dim(f"  window {args.switch_window}m, threshold {args.switch_threshold} switches\n"))

    try:
        watcher.run(
            interval=args.interval,
            max_ticks=args.ticks if args.ticks is not None else demo_ticks,
        )
    except KeyboardInterrupt:
        print(_dim("\nstopping"))

    print("\n" + _bold("Session"))
    summary = watcher.summary()
    print(f"  samples          {summary['observations']}")
    print(f"  app switches     {summary['switches']}")
    print(f"  focus streak     {int(summary['focus_streak_seconds'] // 60)}m")
    print(f"  nudges           {summary['nudges']}")
    if summary["captured"]:
        print(f"  captured         {', '.join(summary['captured'])}")
    print()

    _save_intake(args.state, intake)
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from jarvisx.agentic.control_plane import serve

    return serve(
        host=args.host,
        port=args.port,
        backend_name=args.backend,
        intake_path=args.state,
    )


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

    p_talk = sub.add_parser("talk", help="interactive voice/text loop: listen, decide, act")
    p_talk.add_argument("--text", action="store_true", help="force typed input/output")
    p_talk.add_argument("--wake-word", default="alfred")
    p_talk.add_argument("--energy", default="medium", choices=["low", "medium", "high"])
    p_talk.add_argument("--turns", type=int, default=100)
    p_talk.add_argument("--workers", type=int, default=4)
    p_talk.add_argument(
        "--enable-agent",
        action="store_true",
        help="let explicit 'build/write/fix ...' commands run real agent work",
    )
    p_talk.add_argument("--state", default="var/agentic/intake.json")
    add_common(p_talk)
    p_talk.set_defaults(func=cmd_talk)

    p_next = sub.add_parser("next", help="capture a brain dump, print the one next action")
    p_next.add_argument("--dump", help="everything on your mind, in one go")
    p_next.add_argument("--energy", default="medium", choices=["low", "medium", "high"])
    p_next.add_argument("--state", default="var/agentic/intake.json")
    p_next.set_defaults(func=cmd_next)

    p_watch = sub.add_parser(
        "watch", help="ambient watcher: fragmentation, drift and stray thoughts"
    )
    p_watch.add_argument("--task", help="what you said you were going to work on")
    p_watch.add_argument("--interval", type=float, default=15.0, help="poll seconds")
    p_watch.add_argument("--ticks", type=int, default=None, help="stop after N polls")
    p_watch.add_argument("--switch-window", type=int, default=5, help="minutes")
    p_watch.add_argument("--switch-threshold", type=int, default=6, help="switches per window")
    p_watch.add_argument("--grace", type=int, default=5, help="minutes off-task before a nudge")
    p_watch.add_argument("--break-after", type=int, default=50, help="minutes before a break nudge")
    p_watch.add_argument("--demo", action="store_true", help="run a synthetic drifting session")
    p_watch.add_argument("--no-sensors", action="store_true", help="disable desktop/clipboard polling")
    p_watch.add_argument("--no-capture", action="store_true", help="do not capture clipboard notes")
    p_watch.add_argument("--state", default="var/agentic/intake.json")
    p_watch.set_defaults(func=cmd_watch)

    p_alfred = sub.add_parser(
        "alfred",
        help="the whole agent at once: talks, listens, watches and does",
        description="One shared state. Say what is on your mind, get the next "
        "small step, and let it watch for drift while you work.",
    )
    p_alfred.add_argument("--text", action="store_true", help="force typed input/output")
    p_alfred.add_argument("--energy", choices=["low", "medium", "high"],
                          help="default medium; low only offers tiny tasks")
    p_alfred.add_argument("--turns", type=int, help="default 200")
    p_alfred.add_argument("--quiet", action="store_true", help="print nudges instead of speaking them")
    p_alfred.add_argument("--no-agent", action="store_true", help="capture and nudge only, never execute")
    p_alfred.add_argument("--no-watch", action="store_true", help="disable ambient watching")
    p_alfred.add_argument("--demo", action="store_true", help="synthetic drift instead of real sensors")
    p_alfred.add_argument("--interval", type=float, help="watch poll seconds, default 15")
    p_alfred.add_argument("--switch-window", type=int, help="minutes, default 5")
    p_alfred.add_argument("--switch-threshold", type=int, help="switches per window, default 6")
    p_alfred.add_argument("--grace", type=int, help="minutes off-task before a nudge, default 5")
    p_alfred.add_argument("--break-after", type=int, help="minutes before a break nudge, default 50")
    p_alfred.add_argument("--wake-word", help="default 'alfred'")
    p_alfred.add_argument(
        "--persona", choices=["plain", "stark", "friday", "jarvis", "eevee"],
        help="how it talks; never changes what it decides",
    )
    p_alfred.add_argument(
        "--physical", action="store_true",
        help="let the agent open apps and run gated shell commands",
    )
    p_alfred.add_argument(
        "--physical-dry-run", action="store_true",
        help="resolve and validate physical actions without performing them",
    )
    p_alfred.add_argument("--state", help="task list path, default var/agentic/intake.json")
    p_alfred.add_argument(
        "--config", help="read preferences from this file instead of auto-discovering",
    )
    p_alfred.add_argument(
        "--save-config", action="store_true",
        help="remember the flags on this line, then just run `alfred` next time",
    )
    p_alfred.add_argument("--trace-root", default=str(DEFAULT_TRACE_ROOT))
    p_alfred.set_defaults(func=cmd_alfred)

    p_serve = sub.add_parser("serve", help="start the HTTP control plane")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8123)
    p_serve.add_argument("--backend", default="auto")
    p_serve.add_argument(
        "--state", default="var/agentic/intake.json",
        help="task list shared with `alfred`, shown on the dashboard",
    )
    p_serve.set_defaults(func=cmd_serve)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
