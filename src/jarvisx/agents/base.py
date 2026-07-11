from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from jarvisx.core.events import Event
from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool


@dataclass(frozen=True)
class AgentResponse:
    agent_id: str
    handled: bool
    message: str
    trace_id: str
    data: dict[str, Any] = field(default_factory=dict)
    model: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "handled": self.handled,
            "message": self.message,
            "trace_id": self.trace_id,
            "data": self.data,
            "model": self.model,
        }


class BaseAgent:
    agent_id = "base"
    role = "Base agent"
    expertise: tuple[str, ...] = ()
    tone = "clear"
    personality = "focused"
    capabilities: tuple[str, ...] = ()

    def __init__(
        self,
        *,
        tools: Optional[Mapping[str, BaseTool]] = None,
        logger: Optional[StructuredLogger] = None,
    ) -> None:
        self.tools = dict(tools or {})
        self.logger = logger or StructuredLogger()

    async def handle(self, event: Event) -> AgentResponse:
        raise NotImplementedError

    def health(self) -> HealthStatus:
        return HealthStatus.ok(f"{self.agent_id} ready")

    def describe(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "expertise": list(self.expertise),
            "tone": self.tone,
            "personality": self.personality,
            "capabilities": list(self.capabilities),
            "tools": sorted(self.tools.keys()),
        }

    def _response(
        self,
        event: Event,
        *,
        handled: bool,
        message: str,
        data: Optional[dict[str, Any]] = None,
    ) -> AgentResponse:
        self.logger.write(
            "info",
            "agent.response",
            trace_id=event.trace_id,
            agent_id=self.agent_id,
            handled=handled,
        )
        return AgentResponse(
            agent_id=self.agent_id,
            handled=handled,
            message=message,
            trace_id=event.trace_id,
            data=data or {},
            model=event.payload.get("model") if isinstance(event.payload, Mapping) else None,
        )
