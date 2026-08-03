from __future__ import annotations
import time
from typing import Dict, Any, List, Optional

class MissionHistory:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def record(self, mission_id: str, status: str, details: Dict[str, Any]) -> None:
        self.records.append({
            "mission_id": mission_id,
            "status": status,
            "details": details,
            "timestamp": time.time()
        })

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.records)
