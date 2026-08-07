"""Structured Execution Trace for Phase 91 Autonomous Mission Brain."""

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, Any, List


class ExecutionTraceRecorder:
    """Records step-by-step telemetry, action parameters, tool outcomes, and timestamps."""

    def __init__(self, trace_file_path: str):
        self.trace_file_path = trace_file_path
        self.entries: List[Dict[str, Any]] = []

    def record_step(
        self,
        step_index: int,
        action_name: str,
        tool: str,
        parameters: Dict[str, Any],
        result_status: str,
        duration_sec: float,
        artifacts: List[str],
        notes: str = ""
    ) -> Dict[str, Any]:
        """Append an execution step record and persist to execution_trace.json."""
        entry = {
            "step": step_index,
            "action": action_name,
            "tool": tool,
            "parameters": {k: str(v) if not isinstance(v, (int, float, bool, dict, list)) else v for k, v in parameters.items()},
            "result": result_status,
            "duration_sec": duration_sec,
            "artifacts": artifacts,
            "notes": notes,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.entries.append(entry)
        self.flush()
        return entry

    def flush(self) -> None:
        """Write current trace to disk."""
        p = Path(self.trace_file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.entries, indent=2), encoding="utf-8")

    def get_entries(self) -> List[Dict[str, Any]]:
        return self.entries
