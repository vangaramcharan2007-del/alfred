from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Event:
    type: str
    source: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    target: Optional[str] = None
    trace_id: str = field(default_factory=lambda: uuid4().hex)
    correlation_id: Optional[str] = None
    id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: str = field(default_factory=utc_now_iso)

    def child(
        self,
        *,
        event_type: str,
        source: str,
        target: Optional[str] = None,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> "Event":
        return Event(
            type=event_type,
            source=source,
            target=target,
            payload=payload or {},
            trace_id=self.trace_id,
            correlation_id=self.id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "target": self.target,
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "payload": dict(self.payload),
        }
