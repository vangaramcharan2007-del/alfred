"""Alfred Agentic Harness Orchestration.

One coherent stack that turns a goal into verified, traced work:

    backends   -> provider-agnostic model access (incl. fully offline)
    registry   -> schema-validated, permission-gated tools
    sandbox    -> real jailed execution with rlimits and secret scrubbing
    harness    -> the think/act/observe loop with budgets and a loop guard
    verifier   -> executable checks that decide whether work is actually done
    graph      -> DAG of work items
    planner    -> goal -> graph (model-driven, with a deterministic fallback)
    scheduler  -> parallel wave execution, retries, failure propagation, reports
    trace      -> append-only JSONL record of every decision, replayable

Minimal use::

    from jarvisx.agentic import run_goal

    report = run_goal("Write and test a sieve of Eratosthenes")
    print(report.ok, report.final_output())

Single-agent use::

    from jarvisx.agentic import AgentHarness, build_default_tools, SandboxedRunner

    with SandboxedRunner() as sandbox:
        harness = AgentHarness(registry=build_default_tools(sandbox), sandbox=sandbox)
        result = harness.run("List the primes below 100")
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from jarvisx.agentic.backends import (
    AutoBackend,
    BackendError,
    HeuristicBackend,
    LLMRouterBackend,
    ModelBackend,
    OpenAICompatibleBackend,
    ScriptedBackend,
)
from jarvisx.agentic.builtin_tools import build_default_tools
from jarvisx.agentic.graph import GraphError, TaskGraph
from jarvisx.agentic.harness import AgentHarness
from jarvisx.agentic.intake import (
    CapturedItem,
    Energy,
    IntakeEngine,
    ItemKind,
    breakdown,
    classify,
    next_action,
    split_brain_dump,
)
from jarvisx.agentic.planner import (
    AutoPlanner,
    HeuristicPlanner,
    LLMPlanner,
    Planner,
    extract_json,
)
from jarvisx.agentic.registry import (
    AgentTool,
    AgentToolRegistry,
    ToolDenied,
    ToolValidationError,
    UnknownTool,
    validate_arguments,
)
from jarvisx.agentic.roles import RoleRegistry, RoleSpec
from jarvisx.agentic.sandbox import PathEscape, SandboxResult, SandboxedRunner, scrub_env
from jarvisx.agentic.scheduler import Orchestrator
from jarvisx.agentic.trace import TraceRecorder, render_trace
from jarvisx.agentic.types import (
    Budget,
    ModelMessage,
    NodeOutcome,
    Observation,
    OrchestrationReport,
    RunResult,
    RunStatus,
    StepRecord,
    TaskNode,
    ToolCall,
    Usage,
    Verdict,
)
from jarvisx.agentic.verifier import (
    Check,
    CustomCheck,
    FileExistsCheck,
    JsonOutputCheck,
    NonEmptyOutputCheck,
    OutputContainsCheck,
    PythonAssertCheck,
    TestsPassCheck,
    Verifier,
)
from jarvisx.agentic.watch import (
    ActiveWindowSource,
    AttentionLedger,
    ClipboardSource,
    ContextSource,
    ContextWatcher,
    Nudge,
    NudgeKind,
    Observation,
    ScriptedSource,
    is_distraction,
    looks_capturable,
)
from jarvisx.agentic.voice_loop import (
    ConsoleInput,
    ConsoleOutput,
    Intent,
    SpeechInput,
    SpeechOutput,
    TTSOutput,
    VoiceAgentLoop,
    VoiceTurn,
    WhisperMicInput,
    route,
    strip_trigger,
)

__all__ = [
    # backends
    "AutoBackend",
    "BackendError",
    "HeuristicBackend",
    "LLMRouterBackend",
    "ModelBackend",
    "OpenAICompatibleBackend",
    "ScriptedBackend",
    # tools
    "AgentTool",
    "AgentToolRegistry",
    "ToolDenied",
    "ToolValidationError",
    "UnknownTool",
    "build_default_tools",
    "validate_arguments",
    # sandbox
    "PathEscape",
    "SandboxResult",
    "SandboxedRunner",
    "scrub_env",
    # harness
    "AgentHarness",
    "TraceRecorder",
    "render_trace",
    # verification
    "Check",
    "CustomCheck",
    "FileExistsCheck",
    "JsonOutputCheck",
    "NonEmptyOutputCheck",
    "OutputContainsCheck",
    "PythonAssertCheck",
    "TestsPassCheck",
    "Verifier",
    # orchestration
    "AutoPlanner",
    "GraphError",
    "HeuristicPlanner",
    "LLMPlanner",
    "Orchestrator",
    "Planner",
    "RoleRegistry",
    "RoleSpec",
    "TaskGraph",
    "extract_json",
    # types
    "Budget",
    "ModelMessage",
    "NodeOutcome",
    "Observation",
    "OrchestrationReport",
    "RunResult",
    "RunStatus",
    "StepRecord",
    "TaskNode",
    "ToolCall",
    "Usage",
    "Verdict",
    # intake (ADHD task capture)
    "CapturedItem",
    "Energy",
    "IntakeEngine",
    "ItemKind",
    "breakdown",
    "classify",
    "next_action",
    "split_brain_dump",
    # voice loop
    "ConsoleInput",
    "ConsoleOutput",
    "Intent",
    "SpeechInput",
    "SpeechOutput",
    "TTSOutput",
    "VoiceAgentLoop",
    "VoiceTurn",
    "WhisperMicInput",
    "route",
    "strip_trigger",
    # ambient watching
    "ActiveWindowSource",
    "AttentionLedger",
    "ClipboardSource",
    "ContextSource",
    "ContextWatcher",
    "Nudge",
    "NudgeKind",
    "Observation",
    "ScriptedSource",
    "is_distraction",
    "looks_capturable",
    # entry points
    "run_goal",
    "run_task",
]


def run_task(
    task: str,
    *,
    role: str = "generalist",
    backend: Optional[ModelBackend] = None,
    sandbox: Optional[SandboxedRunner] = None,
    budget: Optional[Budget] = None,
    verifier: Optional[Verifier] = None,
    trace_root: Optional[Any] = None,
    **harness_kwargs: Any,
) -> RunResult:
    """Run a single agent task through a fully wired harness.

    Creates and cleans up its own sandbox unless one is supplied.
    """
    roles = RoleRegistry()
    spec = roles.get(role)
    owns_sandbox = sandbox is None
    sandbox = sandbox or SandboxedRunner()
    try:
        harness = AgentHarness(
            backend=backend or AutoBackend(),
            registry=build_default_tools(sandbox),
            sandbox=sandbox,
            role=spec.name,
            role_prompt=spec.system_prompt(),
            budget=budget or spec.budget,
            verifier=verifier or Verifier(),
            trace_root=trace_root,
            **harness_kwargs,
        )
        return harness.run(task)
    finally:
        if owns_sandbox:
            sandbox.cleanup()


def run_goal(
    goal: str,
    *,
    backend: Optional[ModelBackend] = None,
    planner: Optional[Planner] = None,
    roles: Optional[RoleRegistry] = None,
    budget: Optional[Budget] = None,
    max_workers: int = 4,
    trace_root: Optional[Any] = None,
    on_event: Optional[Any] = None,
) -> OrchestrationReport:
    """Plan a goal into a graph and execute it with a harness workforce."""
    with Orchestrator(
        backend=backend or AutoBackend(),
        planner=planner,
        roles=roles,
        default_budget=budget,
        max_workers=max_workers,
        trace_root=trace_root,
        on_event=on_event,
    ) as orchestrator:
        return orchestrator.run(goal)
