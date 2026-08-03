from __future__ import annotations
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class ProductionLogger:
    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = Path(log_dir or "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / "jarvis.log"
        self.runtime_jsonl = self.log_dir / "runtime.jsonl"
        self.missions_jsonl = self.log_dir / "missions.jsonl"
        self.errors_jsonl = self.log_dir / "errors.jsonl"

    def log_event(
        self,
        category: str,  # mission, provider, model, decision, error
        event_name: str,
        payload: Dict[str, Any],
        level: str = "INFO"
    ) -> Dict[str, Any]:
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "category": category,
            "event": event_name,
            "level": level,
            "payload": payload
        }
        line = json.dumps(entry) + "\n"

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)

        if category == "mission":
            with open(self.missions_jsonl, "a", encoding="utf-8") as f:
                f.write(line)
        elif level in ("ERROR", "WARNING", "CRITICAL") or category == "error":
            with open(self.errors_jsonl, "a", encoding="utf-8") as f:
                f.write(line)
        else:
            with open(self.runtime_jsonl, "a", encoding="utf-8") as f:
                f.write(line)

        return entry


_global_logger: Optional[ProductionLogger] = None

def get_production_logger() -> ProductionLogger:
    global _global_logger
    if _global_logger is None:
        _global_logger = ProductionLogger()
    return _global_logger
