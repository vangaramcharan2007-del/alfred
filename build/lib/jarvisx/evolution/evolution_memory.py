from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class EvolutionLogRecord:
    upgrade_id: str
    reason: str
    changes_made: List[str]
    success: bool
    lessons_learned: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "upgrade_id": self.upgrade_id,
            "reason": self.reason,
            "changes_made": self.changes_made,
            "success": self.success,
            "lessons_learned": self.lessons_learned,
            "timestamp": self.timestamp,
        }


class EvolutionMemory:
    def __init__(self) -> None:
        self.log_history: List[EvolutionLogRecord] = []

    def record_evolution_event(
        self,
        upgrade_id: str,
        reason: str,
        changes_made: List[str],
        success: bool,
        lessons_learned: str,
    ) -> EvolutionLogRecord:
        rec = EvolutionLogRecord(
            upgrade_id=upgrade_id,
            reason=reason,
            changes_made=changes_made,
            success=success,
            lessons_learned=lessons_learned,
        )
        self.log_history.append(rec)
        return rec

    def get_history(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.log_history]
