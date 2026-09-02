from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.evolution.evolution_state import EvolutionState

class EvolutionController:
    def __init__(self, state: Optional[EvolutionState] = None):
        self.state = state or EvolutionState()

    def start_upgrade(self, proposal_id: str, title: str, risk_level: str = "LOW") -> Dict[str, Any]:
        upgrade = {
            "proposal_id": proposal_id,
            "title": title,
            "status": "in_progress",
            "start_time": time.time(),
            "risk_level": risk_level
        }
        self.state.active_upgrade = upgrade
        self.state.risk_level = risk_level
        return upgrade

    def complete_upgrade(self, proposal_id: str, result: Dict[str, Any]) -> None:
        if self.state.active_upgrade and self.state.active_upgrade["proposal_id"] == proposal_id:
            upgrade = self.state.active_upgrade
            upgrade["status"] = "completed"
            upgrade["end_time"] = time.time()
            upgrade["result"] = result
            self.state.upgrade_history.append(upgrade)
            self.state.previous_improvements.append(upgrade)
            self.state.active_upgrade = None
            self.state.risk_level = "LOW"

    def fail_upgrade(self, proposal_id: str, error: str) -> None:
        if self.state.active_upgrade and self.state.active_upgrade["proposal_id"] == proposal_id:
            upgrade = self.state.active_upgrade
            upgrade["status"] = "failed"
            upgrade["end_time"] = time.time()
            upgrade["error"] = error
            self.state.upgrade_history.append(upgrade)
            self.state.active_upgrade = None
            self.state.risk_level = "LOW"
