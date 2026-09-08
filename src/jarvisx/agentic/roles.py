"""Agent role registry.

A role is a named bundle of *persona + budget + tool allow-list*.  The
scheduler assigns roles to graph nodes; the harness materializes them.  This
is what turns "one big agent" into a workforce you can reason about.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from jarvisx.agentic.types import Budget


@dataclass(frozen=True)
class RoleSpec:
    """A reusable agent persona with its own resource envelope."""

    name: str
    title: str
    focus: str
    budget: Budget = field(default_factory=Budget)
    allowed_tools: Optional[tuple] = None  # None = every registered tool
    temperature: float = 0.2

    def system_prompt(self, tool_schemas: str = "(tools injected at runtime)") -> str:
        """Render the persona prompt. Uses concatenation, not ``str.format``,
        so braces inside persona text can never break the render."""
        return (
            f"You are {self.title}, Alfred's {self.name} agent.\n"
            f"Your focus: {self.focus}\n\n"
            "You work inside a sandboxed workspace. Call tools to gather evidence and "
            "make changes, read every observation before acting, verify your work, and "
            "stop as soon as the goal is met.\n\n"
            "Available tools:\n" + tool_schemas + "\n"
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "title": self.title,
            "focus": self.focus,
            "budget": {
                "max_steps": self.budget.max_steps,
                "max_tool_calls": self.budget.max_tool_calls,
                "max_seconds": self.budget.max_seconds,
                "max_tokens": self.budget.max_tokens,
            },
            "allowed_tools": list(self.allowed_tools) if self.allowed_tools else None,
            "temperature": self.temperature,
        }


_DEFAULT_ROLES: List[RoleSpec] = [
    RoleSpec(
        name="generalist",
        title="Staff Engineer",
        focus="delivering the requested outcome end to end with clean, working code",
        budget=Budget(max_steps=8, max_tool_calls=20, max_seconds=120.0),
    ),
    RoleSpec(
        name="planner",
        title="Technical Planner",
        focus="decomposing goals into small, independently verifiable steps",
        budget=Budget(max_steps=4, max_tool_calls=6, max_seconds=60.0),
        temperature=0.1,
    ),
    RoleSpec(
        name="coder",
        title="Implementation Engineer",
        focus="writing correct, minimal, tested code",
        budget=Budget(max_steps=10, max_tool_calls=24, max_seconds=180.0),
        allowed_tools=("write_file", "read_file", "python_exec", "list_files", "final_answer"),
    ),
    RoleSpec(
        name="tester",
        title="Verification Engineer",
        focus="proving behaviour with executable tests and reporting real results",
        budget=Budget(max_steps=8, max_tool_calls=16, max_seconds=150.0),
        allowed_tools=("write_file", "read_file", "run_tests", "python_exec", "final_answer"),
    ),
    RoleSpec(
        name="reviewer",
        title="Code Reviewer",
        focus="finding defects, edge cases and security problems in produced code",
        budget=Budget(max_steps=6, max_tool_calls=12, max_seconds=120.0),
        allowed_tools=("read_file", "list_files", "python_exec", "final_answer"),
        temperature=0.0,
    ),
    RoleSpec(
        name="researcher",
        title="Research Analyst",
        focus="gathering and summarising the facts needed to make a decision",
        budget=Budget(max_steps=6, max_tool_calls=12, max_seconds=120.0),
        allowed_tools=("read_file", "list_files", "python_exec", "final_answer"),
    ),
]


class RoleRegistry:
    """Lookup table from role name to :class:`RoleSpec`."""

    def __init__(self, roles: Optional[Iterable[RoleSpec]] = None):
        self._roles: Dict[str, RoleSpec] = {}
        for role in roles if roles is not None else _DEFAULT_ROLES:
            self._roles[role.name] = role

    def register(self, role: RoleSpec) -> None:
        self._roles[role.name] = role

    def get(self, name: str) -> RoleSpec:
        """Return the role, falling back to the generalist for unknown names."""
        return self._roles.get(name, self._roles.get("generalist") or RoleSpec(
            name=name, title="Agent", focus="completing the assigned task"
        ))

    def names(self) -> List[str]:
        return sorted(self._roles)

    def __contains__(self, name: object) -> bool:
        return name in self._roles

    def __len__(self) -> int:
        return len(self._roles)

    def describe(self) -> str:
        return "\n".join(
            f"- {r.name}: {r.title} — {r.focus}" for r in self._roles.values()
        )
