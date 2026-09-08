"""Core data contracts for the Alfred Agentic Harness Orchestration layer.

Every object that crosses a layer boundary (backend -> harness -> scheduler ->
control plane -> trace store) is defined here so the whole stack speaks one
vocabulary.  Nothing in this module imports from the rest of the package, which
keeps it import-safe and dependency-free (standard library only).
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


def new_id(prefix: str) -> str:
    """Short, sortable, collision-resistant identifier."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    BUDGET_EXCEEDED = "budget_exceeded"
    DENIED = "denied"


TERMINAL_STATUSES = frozenset(
    {
        RunStatus.SUCCEEDED,
        RunStatus.FAILED,
        RunStatus.SKIPPED,
        RunStatus.CANCELLED,
        RunStatus.BUDGET_EXCEEDED,
        RunStatus.DENIED,
    }
)

#: Anything that ran but did not achieve its goal. A node in one of these
#: states must never let an orchestration report claim success.
_FAILURE_STATUSES = frozenset(
    {
        RunStatus.FAILED,
        RunStatus.CANCELLED,
        RunStatus.BUDGET_EXCEEDED,
        RunStatus.DENIED,
    }
)


# --------------------------------------------------------------------------- #
# Model layer
# --------------------------------------------------------------------------- #


@dataclass
class ToolCall:
    """A single tool invocation requested by the model."""

    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: new_id("call"))

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "arguments": self.arguments}


@dataclass
class ModelMessage:
    """Normalized model response, provider-agnostic."""

    content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def wants_tools(self) -> bool:
        return bool(self.tool_calls)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "tool_calls": [c.to_dict() for c in self.tool_calls],
            "finish_reason": self.finish_reason,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }


@dataclass
class Usage:
    """Cumulative resource accounting for a run."""

    steps: int = 0
    tool_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    wall_seconds: float = 0.0

    def merge(self, other: "Usage") -> None:
        self.steps += other.steps
        self.tool_calls += other.tool_calls
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.wall_seconds += other.wall_seconds

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Budget:
    """Hard ceilings for one harness run. Exceeding any of them stops the loop."""

    max_steps: int = 8
    max_tool_calls: int = 24
    max_seconds: float = 120.0
    max_tokens: int = 64_000

    def violation(self, usage: Usage) -> Optional[str]:
        """Return the name of the first ceiling `usage` has breached, else None."""
        if usage.steps >= self.max_steps:
            return f"max_steps ({self.max_steps})"
        if usage.tool_calls >= self.max_tool_calls:
            return f"max_tool_calls ({self.max_tool_calls})"
        if usage.wall_seconds >= self.max_seconds:
            return f"max_seconds ({self.max_seconds:.1f}s)"
        total_tokens = usage.prompt_tokens + usage.completion_tokens
        if total_tokens >= self.max_tokens:
            return f"max_tokens ({self.max_tokens})"
        return None


# --------------------------------------------------------------------------- #
# Harness layer
# --------------------------------------------------------------------------- #


@dataclass
class Observation:
    """Result of one executed tool call, fed back into the model context."""

    tool: str
    call_id: str
    ok: bool
    output: Any = None
    error: Optional[str] = None
    denied: bool = False
    duration_ms: float = 0.0

    def render(self, max_chars: int = 4000) -> str:
        """Flatten into a compact string for the model transcript."""
        if self.denied:
            body = f"DENIED: {self.error or 'blocked by policy'}"
        elif not self.ok:
            body = f"ERROR: {self.error or 'unknown failure'}"
        else:
            body = self.output if isinstance(self.output, str) else json.dumps(
                self.output, default=str
            )
        if len(body) > max_chars:
            body = body[:max_chars] + f"...[truncated {len(body) - max_chars} chars]"
        return f"[{self.tool}] {body}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StepRecord:
    """One iteration of the harness loop: think -> act -> observe."""

    index: int
    thought: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    observations: List[Observation] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "thought": self.thought,
            "tool_calls": [c.to_dict() for c in self.tool_calls],
            "observations": [o.to_dict() for o in self.observations],
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "model": self.model,
            "duration_ms": self.duration_ms,
        }


@dataclass
class Verdict:
    """Outcome of the verification gate applied to a run."""

    passed: bool
    score: float = 0.0
    checks: List[Dict[str, Any]] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunResult:
    """Final artifact of one harness execution."""

    run_id: str
    task: str
    role: str = "generalist"
    status: RunStatus = RunStatus.PENDING
    output: str = ""
    steps: List[StepRecord] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)
    verdict: Optional[Verdict] = None
    budget: Optional[Budget] = None
    error: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None

    @property
    def ok(self) -> bool:
        return self.status == RunStatus.SUCCEEDED

    @property
    def duration_seconds(self) -> float:
        end = self.ended_at if self.ended_at is not None else time.time()
        return round(end - self.started_at, 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task": self.task,
            "role": self.role,
            "status": self.status.value,
            "output": self.output,
            "steps": [s.to_dict() for s in self.steps],
            "usage": self.usage.to_dict(),
            "verdict": self.verdict.to_dict() if self.verdict else None,
            "budget": asdict(self.budget) if self.budget else None,
            "error": self.error,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_seconds": self.duration_seconds,
        }


# --------------------------------------------------------------------------- #
# Orchestration layer
# --------------------------------------------------------------------------- #


@dataclass
class TaskNode:
    """A unit of work in the task graph."""

    id: str
    instruction: str
    role: str = "generalist"
    depends_on: List[str] = field(default_factory=list)
    budget: Budget = field(default_factory=Budget)
    verify: List[Dict[str, Any]] = field(default_factory=list)
    max_retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "instruction": self.instruction,
            "role": self.role,
            "depends_on": list(self.depends_on),
            "budget": asdict(self.budget),
            "verify": self.verify,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
        }


@dataclass
class NodeOutcome:
    """Per-node result recorded by the scheduler."""

    node_id: str
    attempt: int = 1
    status: RunStatus = RunStatus.PENDING
    result: Optional[RunResult] = None
    error: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "attempt": self.attempt,
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "error": self.error,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }


@dataclass
class OrchestrationReport:
    """Aggregate outcome of a full goal -> graph -> execution cycle."""

    goal: str
    graph_id: str
    nodes: List[TaskNode] = field(default_factory=list)
    outcomes: Dict[str, NodeOutcome] = field(default_factory=dict)
    usage: Usage = field(default_factory=Usage)
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None

    @property
    def succeeded(self) -> List[str]:
        return [k for k, v in self.outcomes.items() if v.status == RunStatus.SUCCEEDED]

    @property
    def failed(self) -> List[str]:
        """Nodes that ran and did not succeed (error, budget, denial, cancel)."""
        return [
            k
            for k, v in self.outcomes.items()
            if v.status in _FAILURE_STATUSES
        ]

    @property
    def skipped(self) -> List[str]:
        return [k for k, v in self.outcomes.items() if v.status == RunStatus.SKIPPED]

    @property
    def ok(self) -> bool:
        """True only when every node in the graph actually succeeded."""
        return bool(self.outcomes) and all(
            v.status == RunStatus.SUCCEEDED for v in self.outcomes.values()
        )

    def final_output(self) -> str:
        """Concatenate node outputs in graph order for a human-readable summary."""
        parts: List[str] = []
        for node in self.nodes:
            outcome = self.outcomes.get(node.id)
            if outcome and outcome.result and outcome.result.output:
                parts.append(f"## {node.id} ({node.role})\n{outcome.result.output}")
        return "\n\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        end = self.ended_at if self.ended_at is not None else time.time()
        return {
            "goal": self.goal,
            "graph_id": self.graph_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "outcomes": {k: v.to_dict() for k, v in self.outcomes.items()},
            "usage": self.usage.to_dict(),
            "started_at": self.started_at,
            "ended_at": end,
            "duration_seconds": round(end - self.started_at, 3),
            "succeeded": self.succeeded,
            "failed": self.failed,
            "skipped": self.skipped,
            "ok": self.ok,
        }
