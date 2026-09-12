"""The agent harness: the loop that actually runs an agent.

One iteration is *think -> act -> observe*:

1. assemble context (role prompt, tool schemas, transcript, budget state)
2. ask the backend for the next action
3. validate, authorize and execute the requested tools in the sandbox
4. feed the observations back and repeat until the model stops, a budget is
   breached, or the loop guard trips

Everything that happens is recorded to a :class:`TraceRecorder`, and the
finished run is passed through the :class:`Verifier` before it is allowed to
report success.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from jarvisx.agentic.backends import BackendError, ModelBackend
from jarvisx.agentic.registry import AgentTool, AgentToolRegistry
from jarvisx.agentic.sandbox import SandboxedRunner
from jarvisx.agentic.trace import TraceRecorder
from jarvisx.agentic.types import (
    Budget,
    ModelMessage,
    Observation,
    RunResult,
    RunStatus,
    StepRecord,
    ToolCall,
    Usage,
    Verdict,
    new_id,
)
from jarvisx.agentic.clarifier import ClarificationGate
from jarvisx.agentic.verifier import Verifier

logger = logging.getLogger("jarvisx.agentic.harness")

Approver = Callable[[AgentTool, Dict[str, Any]], bool]

DEFAULT_SYSTEM_PROMPT = """You are {role_name}, an autonomous engineering agent inside Alfred.

You accomplish the user's goal by calling tools. You operate inside a sandboxed
workspace; nothing you do escapes it.

Rules:
- Call one or more tools per turn when you need information or need to change state.
- Read the observation of every tool call before deciding the next action.
- If a tool call fails, read the error and correct your approach. Do not repeat an identical failing call.
- Verify your work before declaring completion.
- When the goal is genuinely met, stop calling tools and reply with a concise final summary.

Available tools:
{tool_schemas}
"""


class LoopGuardTripped(RuntimeError):
    """Raised internally when the model gets stuck repeating itself."""


class AgentHarness:
    """Runs one agent task to completion with budgets, tracing and verification."""

    def __init__(
        self,
        backend: Optional[ModelBackend] = None,
        registry: Optional[AgentToolRegistry] = None,
        sandbox: Optional[SandboxedRunner] = None,
        role: str = "generalist",
        role_prompt: Optional[str] = None,
        budget: Optional[Budget] = None,
        verifier: Optional[Verifier] = None,
        trace_root: Optional[Path | str] = None,
        approver: Optional[Approver] = None,
        clarifier: Optional[ClarificationGate] = None,
        repeat_limit: int = 3,
        temperature: float = 0.2,
        on_event: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        from jarvisx.agentic.backends import AutoBackend

        self.backend: ModelBackend = backend or AutoBackend()
        self.registry = registry or AgentToolRegistry()
        self.sandbox = sandbox or SandboxedRunner()
        self.role = role
        self.role_prompt = role_prompt or DEFAULT_SYSTEM_PROMPT
        self.budget = budget or Budget()
        self.verifier = verifier or Verifier()
        self.trace_root = Path(trace_root) if trace_root else None
        self.approver = approver
        # Off by default so that adding this does not silently change the
        # behaviour of every existing caller. Opt in where a wrong guess would
        # actually cost the user something.
        self.clarifier = clarifier
        self.repeat_limit = repeat_limit
        self.temperature = temperature
        self.on_event = on_event

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self, task: str, run_id: Optional[str] = None) -> RunResult:
        """Execute `task` and return a verified :class:`RunResult`."""
        rid = run_id or new_id("run")
        trace = TraceRecorder(rid, root=self.trace_root, on_event=self.on_event)
        result = RunResult(
            run_id=rid,
            task=task,
            role=self.role,
            status=RunStatus.RUNNING,
            budget=self.budget,
        )

        trace.emit(
            "run_start",
            task=task,
            role=self.role,
            backend=self.backend.name,
            tools=self.registry.names(),
            budget=self.budget.__dict__,
        )

        # Consequential-ambiguity gate. Runs before any tool is touched, so an
        # unanchored instruction costs one question instead of a whole run of
        # confident work aimed at a guess.
        if self.clarifier is not None:
            clarification = self.clarifier.inspect(task)
            if clarification.needed:
                trace.emit(
                    "clarification_needed",
                    # Not `kind=`: TraceRecorder.emit() already takes `kind` as
                    # its positional event name, so reusing it here raises
                    # "got multiple values for argument 'kind'".
                    ambiguity=clarification.kind,
                    question=clarification.question,
                    reason=clarification.reason,
                    unresolved=clarification.unresolved,
                )
                result.status = RunStatus.NEEDS_INPUT
                result.clarification = clarification
                result.output = clarification.question
                result.ended_at = time.time()
                return result

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": task},
        ]
        tool_schemas = self.registry.openai_schemas() or None
        seen_calls: Dict[str, int] = {}
        started = time.perf_counter()

        try:
            while True:
                result.usage.wall_seconds = time.perf_counter() - started
                breach = self.budget.violation(result.usage)
                if breach:
                    result.status = RunStatus.BUDGET_EXCEEDED
                    result.error = f"budget exhausted: {breach}"
                    trace.emit("budget_exceeded", breach=breach)
                    break

                step_started = time.perf_counter()
                try:
                    message = self.backend.complete(
                        messages, tools=tool_schemas, temperature=self.temperature
                    )
                except BackendError as exc:
                    result.status = RunStatus.FAILED
                    result.error = f"backend error: {exc}"
                    trace.emit("backend_error", error=str(exc))
                    break

                step = StepRecord(
                    index=result.usage.steps + 1,
                    thought=message.content or "",
                    tool_calls=list(message.tool_calls),
                    prompt_tokens=message.prompt_tokens,
                    completion_tokens=message.completion_tokens,
                    model=message.model or self.backend.name,
                    duration_ms=(time.perf_counter() - step_started) * 1000,
                )
                result.usage.steps += 1
                result.usage.prompt_tokens += message.prompt_tokens
                result.usage.completion_tokens += message.completion_tokens

                trace.emit(
                    "step",
                    index=step.index,
                    thought=step.thought,
                    tool_calls=[c.to_dict() for c in step.tool_calls],
                    model=step.model,
                    duration_ms=round(step.duration_ms, 2),
                )

                # No tool calls -> the model is answering. Done.
                if not message.wants_tools:
                    messages.append({"role": "assistant", "content": message.content or ""})
                    result.output = message.content or ""
                    step.duration_ms = (time.perf_counter() - step_started) * 1000
                    result.steps.append(step)
                    trace.emit("final", output=result.output[:2000])
                    result.status = RunStatus.SUCCEEDED
                    break

                # Record the assistant turn in the transcript, tool-call style.
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {
                                    "name": call.name,
                                    "arguments": json.dumps(call.arguments),
                                },
                            }
                            for call in message.tool_calls
                        ],
                    }
                )

                for call in message.tool_calls:
                    result.usage.tool_calls += 1
                    fingerprint = _fingerprint(call)
                    seen_calls[fingerprint] = seen_calls.get(fingerprint, 0) + 1

                    trace.emit(
                        "tool_call",
                        step=step.index,
                        name=call.name,
                        arguments=call.arguments,
                        repeat=seen_calls[fingerprint],
                    )

                    if seen_calls[fingerprint] > self.repeat_limit:
                        observation = Observation(
                            tool=call.name,
                            call_id=call.id,
                            ok=False,
                            error=(
                                f"loop guard: identical call to '{call.name}' repeated "
                                f"{seen_calls[fingerprint]} times"
                            ),
                        )
                        step.observations.append(observation)
                        messages.append(_tool_message(call, observation))
                        result.status = RunStatus.FAILED
                        result.error = observation.error
                        trace.emit("loop_guard", name=call.name)
                        break

                    observation = self.registry.invoke(call, approve=self.approver)
                    step.observations.append(observation)
                    messages.append(_tool_message(call, observation))
                    trace.emit(
                        "observation",
                        step=step.index,
                        tool=observation.tool,
                        ok=observation.ok,
                        denied=observation.denied,
                        error=observation.error,
                        duration_ms=round(observation.duration_ms, 2),
                    )

                    if observation.ok and _is_final(observation):
                        result.output = str(
                            (observation.output or {}).get("summary", observation.output)
                        )
                        result.status = RunStatus.SUCCEEDED
                        trace.emit("final", output=result.output[:2000], via="final_answer")

                step.duration_ms = (time.perf_counter() - step_started) * 1000
                result.steps.append(step)

                if result.status is RunStatus.SUCCEEDED:
                    break
                if result.status is RunStatus.FAILED:
                    break
            else:  # pragma: no cover - while True always breaks
                pass

        except Exception as exc:  # noqa: BLE001 - a harness must never raise
            logger.exception("harness crashed")
            result.status = RunStatus.FAILED
            result.error = f"{type(exc).__name__}: {exc}"
            trace.emit("crash", error=result.error)

        result.usage.wall_seconds = time.perf_counter() - started
        result.ended_at = time.time()

        # Verification gate: only a SUCCEEDED run may keep that status.
        if result.status is RunStatus.SUCCEEDED:
            result.verdict = self.verifier.verify(result, self.sandbox)
            if not result.verdict.passed:
                result.status = RunStatus.FAILED
                result.error = f"verification failed: {result.verdict.rationale}"
        else:
            result.verdict = Verdict(passed=False, score=0.0, rationale=result.error or "")

        trace.emit(
            "run_end",
            status=result.status.value,
            steps=result.usage.steps,
            tool_calls=result.usage.tool_calls,
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            wall_seconds=round(result.usage.wall_seconds, 3),
            verified=bool(result.verdict and result.verdict.passed),
            error=result.error,
            trace_path=str(trace.path),
        )
        return result

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _system_prompt(self) -> str:
        # Deliberately not str.format(): persona text and tool descriptions may
        # legitimately contain braces (JSON examples), which would blow up.
        return (
            self.role_prompt.replace("{role_name}", self.role)
            .replace("{tool_schemas}", _render_tools(self.registry))
        )


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _render_tools(registry: AgentToolRegistry) -> str:
    schemas = registry.flat_schemas()
    if not schemas:
        return "(no tools registered)"
    lines = []
    for schema in schemas:
        params = schema["parameters"].get("properties", {})
        required = set(schema["parameters"].get("required", []))
        rendered = ", ".join(
            f"{name}: {spec.get('type', 'string')}"
            + ("*" if name in required else "")
            for name, spec in params.items()
        )
        lines.append(
            f"- {schema['name']} [{schema['permission']}] — {schema['description']}"
        )
        if rendered:
            lines.append(f"    args: {rendered}   (* = required)")
    return "\n".join(lines)


def _tool_message(call: ToolCall, observation: Observation) -> Dict[str, Any]:
    """OpenAI-style tool result message."""
    return {
        "role": "tool",
        "tool_call_id": call.id,
        "name": call.name,
        "content": observation.render(),
    }


def _fingerprint(call: ToolCall) -> str:
    raw = json.dumps({"n": call.name, "a": call.arguments}, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _is_final(observation: Observation) -> bool:
    return isinstance(observation.output, dict) and bool(observation.output.get("final"))
