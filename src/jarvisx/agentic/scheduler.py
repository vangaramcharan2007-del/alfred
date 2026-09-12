"""The orchestrator: plans a goal and runs its graph to completion.

Responsibilities:

* turn a goal into a :class:`TaskGraph` via a :class:`Planner`
* execute the graph wave by wave, nodes within a wave in parallel
* give each node its own harness, role, budget and verifier
* retry transient failures with linear backoff
* skip everything downstream of a failed node instead of running doomed work
* roll resource usage up into one :class:`OrchestrationReport`
"""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from jarvisx.agentic.backends import ModelBackend
from jarvisx.agentic.builtin_tools import build_default_tools
from jarvisx.agentic.graph import GraphError, TaskGraph
from jarvisx.agentic.clarifier import ClarificationGate
from jarvisx.agentic.harness import AgentHarness, Approver
from jarvisx.agentic.planner import AutoPlanner, Planner
from jarvisx.agentic.registry import AgentToolRegistry
from jarvisx.agentic.roles import RoleRegistry, RoleSpec
from jarvisx.agentic.sandbox import SandboxedRunner
from jarvisx.agentic.trace import TraceRecorder
from jarvisx.agentic.types import (
    Budget,
    NodeOutcome,
    OrchestrationReport,
    RunStatus,
    RunResult,
    TaskNode,
    new_id,
)
from jarvisx.agentic.verifier import Verifier

logger = logging.getLogger("jarvisx.agentic.scheduler")

DEFAULT_TRACE_ROOT = Path("var") / "agentic" / "runs"


class Orchestrator:
    """Coordinates a workforce of harnesses over a shared sandboxed workspace."""

    def __init__(
        self,
        backend: Optional[ModelBackend] = None,
        planner: Optional[Planner] = None,
        roles: Optional[RoleRegistry] = None,
        sandbox: Optional[SandboxedRunner] = None,
        tool_factory: Optional[Callable[[SandboxedRunner], AgentToolRegistry]] = None,
        trace_root: Optional[Path | str] = None,
        max_workers: int = 4,
        default_budget: Optional[Budget] = None,
        approver: Optional[Approver] = None,
        clarifier: Optional[ClarificationGate] = None,
        on_event: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        if backend is None:
            from jarvisx.agentic.backends import AutoBackend

            backend = AutoBackend()
        self.backend = backend
        self.roles = roles or RoleRegistry()
        self.default_budget = default_budget or Budget()
        self.planner = planner or AutoPlanner(backend, self.roles, self.default_budget)
        self.sandbox = sandbox or SandboxedRunner()
        self._owns_sandbox = sandbox is None
        self.tool_factory = tool_factory or build_default_tools
        self.trace_root = Path(trace_root) if trace_root else DEFAULT_TRACE_ROOT
        self.max_workers = max(1, max_workers)
        self.approver = approver
        # Threaded down to every harness this orchestrator builds, so a caller
        # can switch the ambiguity gate on once rather than per node. Stays
        # None unless asked: an orchestrator running unattended has nobody to
        # answer a question, and a question nobody can answer is just a stall.
        self.clarifier = clarifier
        self.on_event = on_event

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def plan(self, goal: str) -> TaskGraph:
        """Produce (but do not execute) the task graph for `goal`."""
        return self.planner.plan(goal)

    def run(
        self,
        goal: str,
        graph: Optional[TaskGraph] = None,
        shared_context: Optional[Dict[str, str]] = None,
    ) -> OrchestrationReport:
        """Plan and execute `goal`, returning an aggregate report."""
        graph = graph or self.planner.plan(goal)
        report = OrchestrationReport(goal=goal, graph_id=graph.graph_id, nodes=graph.nodes)
        context: Dict[str, str] = dict(shared_context or {})

        self._emit(
            "orchestration_start",
            goal=goal,
            graph_id=graph.graph_id,
            strategy=getattr(self.planner, "last_strategy", "explicit"),
            nodes=[n.id for n in graph.nodes],
            waves=[[n.id for n in wave] for wave in graph.waves()],
        )

        try:
            waves = graph.waves()
        except GraphError as exc:
            logger.error("graph is not executable: %s", exc)
            for node in graph.nodes:
                report.outcomes[node.id] = NodeOutcome(
                    node_id=node.id, status=RunStatus.SKIPPED, error=str(exc)
                )
            report.ended_at = time.time()
            return report

        blocked: set[str] = set()

        for wave_index, wave in enumerate(waves, start=1):
            runnable = []
            for node in wave:
                blocking = [d for d in node.depends_on if d in blocked]
                if blocking:
                    report.outcomes[node.id] = NodeOutcome(
                        node_id=node.id,
                        status=RunStatus.SKIPPED,
                        error=f"upstream failed or skipped: {blocking}",
                        ended_at=time.time(),
                    )
                    blocked.add(node.id)
                    self._emit("node_skipped", node=node.id, blocked_by=blocking)
                else:
                    runnable.append(node)

            if not runnable:
                continue

            self._emit(
                "wave_start",
                wave=wave_index,
                nodes=[n.id for n in runnable],
                parallel=len(runnable) > 1,
            )

            with ThreadPoolExecutor(
                max_workers=min(self.max_workers, len(runnable)),
                thread_name_prefix="alfred-agent",
            ) as pool:
                futures = {
                    pool.submit(self._run_node, node, dict(context)): node
                    for node in runnable
                }
                for future, node in futures.items():
                    outcome = future.result()
                    report.outcomes[node.id] = outcome
                    if outcome.status is not RunStatus.SUCCEEDED:
                        blocked.add(node.id)
                    elif outcome.result:
                        report.usage.merge(outcome.result.usage)
                        context[node.id] = outcome.result.output
                    self._emit(
                        "node_end",
                        node=node.id,
                        status=outcome.status.value,
                        attempts=outcome.attempt,
                        error=outcome.error,
                    )

        report.ended_at = time.time()
        self._persist(report)
        self._emit(
            "orchestration_end",
            graph_id=report.graph_id,
            ok=report.ok,
            succeeded=report.succeeded,
            failed=report.failed,
            skipped=report.skipped,
            tool_calls=report.usage.tool_calls,
        )
        return report

    def run_graph(self, graph: TaskGraph, shared_context: Optional[Dict[str, str]] = None):
        """Execute a pre-built graph (skips planning)."""
        return self.run(goal=graph.graph_id, graph=graph, shared_context=shared_context)

    # ------------------------------------------------------------------ #
    # Node execution
    # ------------------------------------------------------------------ #

    def _run_node(self, node: TaskNode, context: Dict[str, str]) -> NodeOutcome:
        """Run one node, retrying up to ``node.max_retries`` times."""
        outcome = NodeOutcome(node_id=node.id)
        last: Optional[RunResult] = None

        for attempt in range(1, node.max_retries + 2):
            outcome.attempt = attempt
            harness = self._build_harness(node)
            prompt = self._compose_prompt(node, context)

            self._emit(
                "node_start",
                node=node.id,
                role=node.role,
                attempt=attempt,
                instruction=node.instruction,
            )

            result = harness.run(prompt, run_id=f"{node.id}_{new_id('run')}")
            last = result
            outcome.result = result
            outcome.status = result.status
            outcome.error = result.error

            if result.status is RunStatus.SUCCEEDED:
                outcome.ended_at = time.time()
                return outcome

            logger.warning(
                "node %s attempt %d -> %s (%s)", node.id, attempt, result.status.value, result.error
            )
            if attempt <= node.max_retries:
                time.sleep(0.2 * attempt)

        outcome.ended_at = time.time()
        return outcome

    def _build_harness(self, node: TaskNode) -> AgentHarness:
        role: RoleSpec = self.roles.get(node.role)
        registry = self.tool_factory(self.sandbox)
        if role.allowed_tools:
            allowed = set(role.allowed_tools)
            for name in list(registry.names()):
                if name not in allowed:
                    # Keep the spec visible so the model learns the boundary,
                    # but re-tier it to RESTRICTED so it cannot execute.
                    tool = registry.get(name)
                    object.__setattr__(
                        tool, "permission", _restricted_level()
                    )

        return AgentHarness(
            backend=self.backend,
            registry=registry,
            sandbox=self.sandbox,
            role=role.name,
            role_prompt=role.system_prompt(),
            budget=node.budget or role.budget,
            verifier=Verifier.from_config(node.verify),
            trace_root=self.trace_root,
            approver=self.approver,
            clarifier=self.clarifier,
            temperature=role.temperature,
            on_event=self.on_event,
        )

    @staticmethod
    def _compose_prompt(node: TaskNode, context: Dict[str, str]) -> str:
        parts = [node.instruction]
        if context:
            parts.append("\nContext from upstream steps:")
            for node_id, output in context.items():
                trimmed = (output or "").strip()
                if len(trimmed) > 2000:
                    trimmed = trimmed[:2000] + "...[truncated]"
                parts.append(f"\n--- {node_id} ---\n{trimmed}")
        return "\n".join(parts)

    # ------------------------------------------------------------------ #
    # Plumbing
    # ------------------------------------------------------------------ #

    def _emit(self, kind: str, **payload: Any) -> None:
        logger.debug("orchestrator %s %s", kind, payload)
        if self.on_event:
            self.on_event({"kind": kind, "ts": time.time(), **payload})

    def _persist(self, report: OrchestrationReport) -> Path:
        self.trace_root.mkdir(parents=True, exist_ok=True)
        path = self.trace_root / f"{report.graph_id}.orchestration.json"
        try:
            path.write_text(json.dumps(report.to_dict(), indent=2, default=str), encoding="utf-8")
        except OSError as exc:  # pragma: no cover - disk/permission issues
            logger.warning("could not persist orchestration report: %s", exc)
        return path

    def close(self) -> None:
        if self._owns_sandbox:
            self.sandbox.cleanup()

    def __enter__(self) -> "Orchestrator":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()


def _restricted_level():
    from jarvisx.tools.tool_kernel import PermissionLevel

    return PermissionLevel.RESTRICTED
