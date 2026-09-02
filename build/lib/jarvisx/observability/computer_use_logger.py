"""Structured Observability and Computer-Use Audit Logger for Jarvis X: GENESIS.

Logs every desktop actuation with latency, error isolation, and credential redaction.
"""

from __future__ import annotations
import os
import json
import time
import re
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


SENSITIVE_PATTERNS = [
    re.compile(r'AIza[0-9A-Za-z-_]{10,60}'),
    re.compile(r'sk-[0-9A-Za-z-_]{10,80}'),
    re.compile(r'password\s*[:=]\s*[^\s]+', re.IGNORECASE),
    re.compile(r'bearer\s+[0-9A-Za-z-_.]+', re.IGNORECASE),
]


def redact_sensitive(text: str) -> str:
    """Scrub passwords, secrets, and API keys from logs."""
    if not isinstance(text, str):
        return text
    clean = text
    for pattern in SENSITIVE_PATTERNS:
        clean = pattern.sub("[REDACTED_SECRET]", clean)
    return clean


class ComputerUseLogger:
    """Structured JSON audit logger for UACC and desktop actions."""

    def __init__(self, log_path: str = "var/logs/computer_use.log"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_action(
        self,
        task_id: str,
        tool: str,
        action: str,
        success: bool,
        latency_ms: float,
        agent_id: str = "Alfred-Genesis",
        params: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """Append an audit record to the computer-use logfile."""
        clean_params = {}
        if params:
            for k, v in params.items():
                if isinstance(v, str):
                    clean_params[k] = redact_sensitive(v)
                else:
                    clean_params[k] = v

        entry = {
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_id,
            "agent_id": agent_id,
            "tool": tool,
            "action": action,
            "params": clean_params,
            "success": success,
            "latency_ms": latency_ms,
            "error": redact_sensitive(str(error)) if error else None
        }

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass


_GLOBAL_COMPUTER_USE_LOGGER: Optional[ComputerUseLogger] = None


def get_computer_use_logger() -> ComputerUseLogger:
    global _GLOBAL_COMPUTER_USE_LOGGER
    if _GLOBAL_COMPUTER_USE_LOGGER is None:
        _GLOBAL_COMPUTER_USE_LOGGER = ComputerUseLogger()
    return _GLOBAL_COMPUTER_USE_LOGGER
