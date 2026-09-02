from __future__ import annotations

import json
import logging
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
        
        self._logger = logging.getLogger(f"jarvis_structured_logger.{id(self)}")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False
        
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
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as log_file:
                log_file.write(line + "\n")
        if self.echo:
            print(line)
        return record

    def recent(self, n: int = 50) -> list[dict[str, Any]]:
        """Return the most recent *n* log entries from the in-memory buffer."""
        entries = list(self._buffer)
        return entries[-n:]
        
    def close(self) -> None:
        """Flushes and closes the file handlers."""
        for handler in list(self._logger.handlers):
            handler.flush()
            handler.close()
            self._logger.removeHandler(handler)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
