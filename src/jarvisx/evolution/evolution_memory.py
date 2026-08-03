from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.meta.meta_memory import MetaMemory

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
            "timestamp": self.timestamp
        }

class EvolutionMemory:
    def __init__(self, meta_memory: Optional[MetaMemory] = None):
        self.meta_memory = meta_memory or MetaMemory()
        self.log_history: List[EvolutionLogRecord] = []

    def record_evolution_event(
        self,
        upgrade_id: str,
        reason: str,
        changes_made: List[str],
        success: bool,
        lessons_learned: str
    ) -> EvolutionLogRecord:
        rec = EvolutionLogRecord(
            upgrade_id=upgrade_id,
            reason=reason,
            changes_made=changes_made,
            success=success,
            lessons_learned=lessons_learned
        )
        self.log_history.append(rec)
        self.meta_memory.record_evolution_step(
            milestone=f"Upgrade '{upgrade_id}' {'succeeded' if success else 'failed'}",
            capability_count=1,
            confidence=0.98 if success else 0.85
        )
        return rec

    def get_history(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.log_history]
