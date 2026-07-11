from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SystemState:
    last_trace_id: Optional[str] = None
    last_intent: Optional[str] = None
    values: dict[str, Any] = field(default_factory=dict)
