from __future__ import annotations
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class ProductionLogger:
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path or "logs/jarvis.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

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
        line = json.dumps(entry)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        return entry

_global_logger: Optional[ProductionLogger] = None

def get_production_logger() -> ProductionLogger:
    global _global_logger
    if _global_logger is None:
        _global_logger = ProductionLogger()
    return _global_logger
