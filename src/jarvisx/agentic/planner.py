"""Planners: goal -> :class:`TaskGraph`.

Two implementations:

``LLMPlanner``       asks a model for a JSON plan, then validates and repairs it
``HeuristicPlanner`` deterministic rule-based decomposition, no network needed

``AutoPlanner`` tries the model first and falls back to heuristics when the
model is unavailable or returns something unusable — so planning never fails
outright.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Sequence

from jarvisx.agentic.backends import BackendError, ModelBackend
from jarvisx.agentic.graph import GraphError, TaskGraph
from jarvisx.agentic.roles import RoleRegistry
from jarvisx.agentic.types import Budget, TaskNode, new_id

logger = logging.getLogger("jarvisx.agentic.planner")

PLAN_SYSTEM_PROMPT = """You are Alfred's technical planner.

Decompose the user's goal into a minimal DAG of independent, verifiable steps.
Each step is executed by a separate agent in a sandboxed workspace.

Respond with ONLY a JSON object of this exact shape, no prose, no code fences:
{
  "steps": [
    {
      "id": "short_snake_case_id",
      "instruction": "exactly what this agent must accomplish",
      "role": "one of: {roles}",
      "depends_on": ["id_of_prerequisite_step"],
      "verify": [{"type": "nonempty_output"}]
    }
  ]
}

Rules:
- Use between 1 and 6 steps. Fewer is better.
- Only add depends_on when a step genuinely needs another step's output.
- verify types available: {check_types}
- Do not invent tools or roles that are not listed.
"""

VALID_CHECK_TYPES = (
    "python_assert",
    "tests_pass",
    "file_exists",
    "output_contains",
    "nonempty_output",
    "json_output",
)


class Planner:
    """Interface for goal decomposition."""

    def plan(self, goal: str) -> TaskGraph:
        raise NotImplementedError


class LLMPlanner(Planner):
    """Asks a model for a JSON plan and validates it into a real graph."""

    def __init__(
        self,
        backend: Optional[ModelBackend] = None,
        roles: Optional[RoleRegistry] = None,
        default_budget: Optional[Budget] = None,
    ):
        if backend is None:
            from jarvisx.agentic.backends import AutoBackend

            backend = AutoBackend()
        self.backend = backend
        self.roles = roles or RoleRegistry()
        self.default_budget = default_budget or Budget()

    def plan(self, goal: str) -> TaskGraph:
        prompt = PLAN_SYSTEM_PROMPT.replace(
            "{roles}", ", ".join(self.roles.names())
        ).replace("{check_types}", ", ".join(VALID_CHECK_TYPES))

        message = self.backend.complete(
            [
                {"role": "system", "content": prompt},
                {"role": "user", "content": goal},
            ],
            tools=None,
            temperature=0.1,
        )
        payload = extract_json(message.content)
        if payload is None:
            raise ValueError(f"planner returned no parseable JSON: {message.content[:200]!r}")

        nodes = self._to_nodes(payload, goal)
        if not nodes:
            raise ValueError("planner returned an empty step list")
        return TaskGraph(nodes)

    def _to_nodes(self, payload: Dict[str, Any], goal: str) -> List[TaskNode]:
        raw_steps = payload.get("steps")
        if not isinstance(raw_steps, list):
            raise ValueError(f"plan JSON must contain a 'steps' array, got {type(raw_steps).__name__}")

        known_roles = set(self.roles.names())
        nodes: List[TaskNode] = []
        seen: set[str] = set()
        for index, raw in enumerate(raw_steps):
            if not isinstance(raw, dict):
                continue
            node_id = str(raw.get("id") or f"step_{index + 1}").strip()
            if node_id in seen:
                node_id = f"{node_id}_{index + 1}"
            seen.add(node_id)

            role = str(raw.get("role") or "generalist").strip()
            if role not in known_roles:
                logger.info("planner picked unknown role %r; using generalist", role)
                role = "generalist"

            verify = [
                check
                for check in (raw.get("verify") or [])
                if isinstance(check, dict) and check.get("type") in VALID_CHECK_TYPES
            ] or [{"type": "nonempty_output"}]

            nodes.append(
                TaskNode(
                    id=node_id,
                    instruction=str(raw.get("instruction") or goal).strip(),
                    role=role,
                    depends_on=[str(d) for d in (raw.get("depends_on") or [])],
                    budget=self.default_budget,
                    verify=verify,
                )
            )

        # Drop dangling dependencies rather than failing the whole plan.
        valid_ids = {n.id for n in nodes}
        for node in nodes:
            dropped = [d for d in node.depends_on if d not in valid_ids]
            if dropped:
                logger.warning("node %s: dropping unknown deps %s", node.id, dropped)
                node.depends_on = [d for d in node.depends_on if d in valid_ids]
        return nodes


class HeuristicPlanner(Planner):
    """Rule-based decomposition that needs no model at all."""

    def __init__(self, roles: Optional[RoleRegistry] = None, default_budget: Optional[Budget] = None):
        self.roles = roles or RoleRegistry()
        self.default_budget = default_budget or Budget()

    def plan(self, goal: str) -> TaskGraph:
        return TaskGraph(self.decompose(goal))

    def decompose(self, goal: str) -> List[TaskNode]:
        text = goal.lower()

        # Precedence matters: the review/research verbs are more specific than
        # the implementation verbs, and they frequently co-occur with words
        # like "code". "Review this code" must plan a review, not a build.
        if any(word in text for word in ("review", "audit", "assess", "critique")):
            return [
                TaskNode(
                    id="review",
                    instruction=goal,
                    role="reviewer",
                    budget=self.default_budget,
                    verify=[{"type": "nonempty_output"}],
                )
            ]

        if any(
            word in text
            for word in ("research", "investigate", "compare", "explain", "summar")
        ):
            return [
                TaskNode(
                    id="research",
                    instruction=goal,
                    role="researcher",
                    budget=self.default_budget,
                    verify=[{"type": "nonempty_output"}],
                )
            ]

        if any(
            word in text
            for word in ("implement", "write", "build", "create", "code", "function")
        ):
            return [
                TaskNode(
                    id="implement",
                    instruction=goal,
                    role="coder",
                    budget=self.default_budget,
                    verify=[{"type": "file_exists", "path": "generated_solution.py"}],
                ),
                TaskNode(
                    id="verify",
                    instruction=f"Verify this deliverable and report concrete evidence: {goal}",
                    role="tester",
                    depends_on=["implement"],
                    budget=self.default_budget,
                    verify=[{"type": "nonempty_output"}],
                ),
            ]

        return [
            TaskNode(
                id="execute",
                instruction=goal,
                role="generalist",
                budget=self.default_budget,
                verify=[{"type": "nonempty_output"}],
            )
        ]


class AutoPlanner(Planner):
    """Model-first planner with a deterministic safety net."""

    def __init__(
        self,
        backend: Optional[ModelBackend] = None,
        roles: Optional[RoleRegistry] = None,
        default_budget: Optional[Budget] = None,
    ):
        self.roles = roles or RoleRegistry()
        self.default_budget = default_budget or Budget()
        self._backend = backend
        self.llm = LLMPlanner(backend, self.roles, self.default_budget)
        self.heuristic = HeuristicPlanner(self.roles, self.default_budget)
        self.last_strategy = "unplanned"

    def plan(self, goal: str) -> TaskGraph:
        try:
            graph = self.llm.plan(goal)
            graph.waves()  # validate before accepting
            self.last_strategy = "llm"
            return graph
        except (BackendError, ValueError, GraphError, KeyError) as exc:
            logger.info("LLM planning fell back to heuristics: %s", exc)
        graph = self.heuristic.plan(goal)
        self.last_strategy = "heuristic"
        return graph


# --------------------------------------------------------------------------- #
# JSON extraction
# --------------------------------------------------------------------------- #

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Pull the first JSON object out of a model response.

    Tolerates code fences, leading prose and trailing commentary.
    """
    if not text:
        return None
    candidates: List[str] = []

    fenced = _FENCE_RE.findall(text)
    candidates.extend(fenced)
    candidates.append(text)

    for candidate in candidates:
        candidate = candidate.strip()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        start = candidate.find("{")
        end = candidate.rfind("}")
        if 0 <= start < end:
            try:
                parsed = json.loads(candidate[start : end + 1])
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
    return None
