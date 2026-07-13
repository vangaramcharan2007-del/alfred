import json
from datetime import datetime, timezone
from typing import Optional

from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult
from jarvisx.tools.operational_db import OperationalDatabase


class XPTool(BaseTool):
    name = "xp"

    def __init__(self, op_db: OperationalDatabase, logger: Optional[StructuredLogger] = None):
        self.op_db = op_db
        self.logger = logger or StructuredLogger()

    def _get_xp_state(self, trace_id: Optional[str] = None) -> dict[str, int]:
        state = self.op_db.get("xp_state")
        if state:
            return state
        return {"xp": 0, "level": 1, "credits": 0, "streak": 0}

    def _save_xp_state(self, state: dict[str, int], trace_id: Optional[str] = None) -> ToolResult:
        self.op_db.set("xp_state", state)
        return ToolResult(success=True, message="XP state saved.")

    def award_xp(self, mission_type: str, trace_id: Optional[str] = None) -> ToolResult:
        state = self._get_xp_state(trace_id=trace_id)
        
        # XP Reward table
        rewards = {
            "daily_mission": 10,
            "side_quest": 25,
            "main_quest": 100,
            "boss_fight": 500
        }
        
        gained = rewards.get(mission_type, 5)
        state["xp"] += gained
        
        # Simple level calculation: Level = (XP / 100) + 1
        new_level = (state["xp"] // 100) + 1
        leveled_up = new_level > state["level"]
        
        if leveled_up:
            state["level"] = new_level
            state["credits"] += 50 * (new_level - 1)  # Reward credits on level up
            
        self._save_xp_state(state, trace_id=trace_id)
        
        self.logger.write("info", "xp.awarded", xp=gained, mission_type=mission_type, leveled_up=leveled_up)
        
        return ToolResult(
            success=True,
            message=f"Awarded {gained} XP.",
            data={"gained": gained, "new_total": state["xp"], "level": state["level"], "leveled_up": leveled_up, "credits": state["credits"]}
        )

    def get_stats(self, trace_id: Optional[str] = None) -> ToolResult:
        state = self._get_xp_state(trace_id=trace_id)
        return ToolResult(
            success=True,
            message="XP stats retrieved.",
            data=state
        )

    def health(self) -> HealthStatus:
        return self.op_db.health()
