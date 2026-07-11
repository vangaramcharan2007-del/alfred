from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from jarvisx.core.events import utc_now_iso


class StructuredLogger:
    """Small JSON-lines logger for offline-friendly traceability."""

    def __init__(self, *, path: Optional[Path] = None, echo: bool = False) -> None:
        self.path = path
        self.echo = echo
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
        line = json.dumps(record, sort_keys=True)
        if self.path:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        if self.echo:
            print(line)
        return record
