from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class EvolutionState:
    current_version: str = "1.0.0"
    previous_improvements: List[Dict[str, Any]] = field(default_factory=list)
    active_upgrade: Optional[Dict[str, Any]] = None
    upgrade_history: List[Dict[str, Any]] = field(default_factory=list)
    risk_level: str = "LOW"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_version": self.current_version,
            "previous_improvements_count": len(self.previous_improvements),
            "active_upgrade": self.active_upgrade,
            "upgrade_history_count": len(self.upgrade_history),
            "risk_level": self.risk_level
        }
