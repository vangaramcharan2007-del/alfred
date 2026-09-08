"""Structured, replayable execution traces.

Every harness step is appended as one JSON line to
``<root>/<run_id>.jsonl``.  That gives a durable, greppable, machine-readable
record of *why* an agent did what it did — which is the difference between an
orchestrator you can debug and one you can only guess about.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional

logger = logging.getLogger("jarvisx.agentic.trace")

DEFAULT_TRACE_ROOT = Path("var") / "agentic" / "runs"


class TraceRecorder:
    """Append-only JSONL trace writer with an in-process event hook."""

    def __init__(
        self,
        run_id: str,
        root: Optional[Path | str] = None,
        on_event: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.run_id = run_id
        self.root = Path(root) if root else DEFAULT_TRACE_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / f"{run_id}.jsonl"
        self._lock = threading.Lock()
        self._on_event = on_event
        self._events: List[Dict[str, Any]] = []
        self._seq = 0

    def emit(self, kind: str, **payload: Any) -> Dict[str, Any]:
        """Record one event, persist it, and fan it out to listeners."""
        with self._lock:
            self._seq += 1
            event = {
                "seq": self._seq,
                "ts": time.time(),
                "run_id": self.run_id,
                "kind": kind,
                **payload,
            }
            self._events.append(event)
            try:
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(event, default=str) + "\n")
            except OSError as exc:  # pragma: no cover - disk full / perms
                logger.warning("trace write failed: %s", exc)
        if self._on_event:
            try:
                self._on_event(event)
            except Exception as exc:  # noqa: BLE001 - listeners must not break runs
                logger.warning("trace listener raised: %s", exc)
        return event

    @property
    def events(self) -> List[Dict[str, Any]]:
        return list(self._events)

    # -- replay ------------------------------------------------------------ #

    @staticmethod
    def read(path: Path | str) -> List[Dict[str, Any]]:
        """Load a trace file back into memory."""
        return list(TraceRecorder.iter_file(path))

    @staticmethod
    def iter_file(path: Path | str) -> Iterator[Dict[str, Any]]:
        """Stream events from a trace file, skipping corrupt lines."""
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    @staticmethod
    def summarize(path: Path | str) -> Dict[str, Any]:
        """Reduce a trace file to counts plus the terminal event."""
        counts: Dict[str, int] = {}
        last: Dict[str, Any] = {}
        first_ts = None
        last_ts = None
        for event in TraceRecorder.iter_file(path):
            counts[event.get("kind", "?")] = counts.get(event.get("kind", "?"), 0) + 1
            first_ts = first_ts or event.get("ts")
            last_ts = event.get("ts")
            last = event
        duration = (last_ts - first_ts) if first_ts and last_ts else 0.0
        return {
            "path": str(path),
            "events": sum(counts.values()),
            "by_kind": counts,
            "duration_seconds": round(duration, 3),
            "final": last,
        }


def render_trace(path: Path | str) -> str:
    """Human-readable rendering of a trace, for the CLI and demos."""
    lines: List[str] = []
    for event in TraceRecorder.iter_file(path):
        kind = event.get("kind", "?")
        stamp = time.strftime("%H:%M:%S", time.localtime(event.get("ts", 0)))
        if kind == "step":
            thought = (event.get("thought") or "").strip().replace("\n", " ")
            if len(thought) > 100:
                thought = thought[:100] + "..."
            lines.append(f"{stamp} step {event.get('index')}  {thought}")
            for call in event.get("tool_calls", []):
                lines.append(f"{stamp}   -> {call.get('name')} {call.get('arguments')}")
            for obs in event.get("observations", []):
                marker = "ok" if obs.get("ok") else ("DENIED" if obs.get("denied") else "ERR")
                lines.append(f"{stamp}   <- [{marker}] {obs.get('tool')}")
        elif kind == "run_end":
            lines.append(
                f"{stamp} {kind}: {event.get('status')} "
                f"steps={event.get('steps')} tool_calls={event.get('tool_calls')}"
            )
        else:
            lines.append(f"{stamp} {kind}")
    return "\n".join(lines)
