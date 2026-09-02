from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvisx.core.health import HealthStatus


@dataclass(frozen=True)
class ToolResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"success": self.success, "message": self.message, "data": self.data}


class BaseTool:
    name = "base"

    def health(self) -> HealthStatus:
        return HealthStatus.ok(f"{self.name} ready")
