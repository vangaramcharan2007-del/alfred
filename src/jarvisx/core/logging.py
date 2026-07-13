from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any, Optional

from jarvisx.core.events import utc_now_iso


class StructuredLogger:
    """Small JSON-lines logger for offline-friendly traceability."""

    def __init__(self, *, path: Optional[Path] = None, echo: bool = False, buffer_size: int = 100) -> None:
        self.path = path
        self.echo = echo
        self._buffer: deque[dict[str, Any]] = deque(maxlen=buffer_size)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        level: str,
        message: str,
        *,
        trace_id: Optional[str] = None,
        **fields: Any,
    ) -> dict[str, Any]:
        record = {
            "timestamp": utc_now_iso(),
            "level": level,
            "message": message,
            "trace_id": trace_id,
            **fields,
        }
        self._buffer.append(record)
        line = json.dumps(record, sort_keys=True)
        if self.path:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        if self.echo:
            print(line)
        return record

    def recent(self, n: int = 50) -> list[dict[str, Any]]:
        """Return the most recent *n* log entries from the in-memory buffer."""
        entries = list(self._buffer)
        return entries[-n:]

