from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class FailureReport:
    what_failed: str
    why: str
    agent_id: Optional[str]
    tool_name: Optional[str]
    proposed_fix: str
    trace_id: Optional[str] = None

    @classmethod
    def from_exception(
        cls,
        exc: BaseException,
        *,
        agent_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        proposed_fix: str = "Inspect the trace logs, isolate the failing component, and add a focused test.",
        trace_id: Optional[str] = None,
    ) -> "FailureReport":
        return cls(
            what_failed=exc.__class__.__name__,
            why=str(exc) or repr(exc),
            agent_id=agent_id,
            tool_name=tool_name,
            proposed_fix=proposed_fix,
            trace_id=trace_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "what_failed": self.what_failed,
            "why": self.why,
            "agent_id": self.agent_id,
            "tool_name": self.tool_name,
            "proposed_fix": self.proposed_fix,
            "trace_id": self.trace_id,
        }
