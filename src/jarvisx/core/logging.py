from __future__ import annotations

import json
import logging
import logging.handlers
import os
import gzip
import shutil
from collections import deque
from pathlib import Path
from typing import Any, Optional

from jarvisx.core.events import utc_now_iso

def _compress_rotator(source: str, dest: str) -> None:
    with open(source, 'rb') as f_in:
        with gzip.open(dest + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(source)

def _compress_namer(name: str) -> str:
    return name

class StructuredLogger:
    """Small JSON-lines logger for offline-friendly traceability."""

    def __init__(self, *, path: Optional[Path] = None, echo: bool = False, buffer_size: int = 100) -> None:
        self.path = path
        self.echo = echo
        self._buffer: deque[dict[str, Any]] = deque(maxlen=buffer_size)
        
        self._logger = logging.getLogger("jarvis_structured_logger")
        self._logger.setLevel(logging.INFO)
        # Prevent duplicate logs if instantiated multiple times
        self._logger.handlers.clear()
        
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # 10 MB = 10 * 1024 * 1024 bytes
            handler = logging.handlers.RotatingFileHandler(
                str(self.path), maxBytes=10*1024*1024, backupCount=10, encoding="utf-8"
            )
            handler.rotator = _compress_rotator
            handler.namer = _compress_namer
            # We just want to write the raw message string, which will be the JSON
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)

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
            self._logger.info(line)
        if self.echo:
            print(line)
        return record

    def recent(self, n: int = 50) -> list[dict[str, Any]]:
        """Return the most recent *n* log entries from the in-memory buffer."""
        entries = list(self._buffer)
        return entries[-n:]
        
    def close(self) -> None:
        """Flushes and closes the file handlers."""
        for handler in self._logger.handlers:
            handler.close()

