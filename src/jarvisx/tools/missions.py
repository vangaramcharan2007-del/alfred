from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import re
from typing import Callable, Optional
from uuid import uuid4

from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult
from jarvisx.tools.memory import LocalMemoryTool


MISSION_SCHEMA = "jarvisx.mission_event.v1"
MISSION_MARKER = "JARVISX_MISSION_EVENT"
MISSION_TYPES = {
    "main_quest": {"xp": 100, "priority": 70},
    "side_quest": {"xp": 40, "priority": 40},
    "boss_fight": {"xp": 250, "priority": 80},
    "daily_mission": {"xp": 20, "priority": 90},
    "recovery_mission": {"xp": 15, "priority": 100},
}


@dataclass(frozen=True)
class MissionStats:
    total_xp: int
    completed_missions: int
    current_streak: int
    inactive_days: Optional[int]

    def to_dict(self) -> dict[str, object]:
        return {
            "total_xp": self.total_xp,
            "completed_missions": self.completed_missions,
            "current_streak": self.current_streak,
            "inactive_days": self.inactive_days,
        }


class MissionTool(BaseTool):
    name = "mission"

    def __init__(
        self,
        *,
        memory_tool: LocalMemoryTool,
        logger: Optional[StructuredLogger] = None,
        now: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.memory_tool = memory_tool
        self.logger = logger or StructuredLogger()
        self._now = now or (lambda: datetime.now(timezone.utc))

    def create_mission(
        self,
        title: str,
        mission_type: str = "side_quest",
        *,
        description: str = "",
        xp: Optional[int] = None,
        progress_target: int = 1,
        trace_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> ToolResult:
        normalized_type = mission_type.strip().lower()
        if normalized_type not in MISSION_TYPES:
            return ToolResult(
                success=False,
                message=f"Unsupported mission type: {mission_type}.",
                data={"supported_mission_types": sorted(MISSION_TYPES)},
            )
        clean_title = title.strip()
        if not clean_title:
            return ToolResult(success=False, message="Mission title was empty.")

        mission = {
            "id": uuid4().hex,
            "title": clean_title,
            "type": normalized_type,
            "description": description.strip(),
            "xp": int(xp if xp is not None else MISSION_TYPES[normalized_type]["xp"]),
            "priority": int(MISSION_TYPES[normalized_type]["priority"]),
            "progress_current": 0,
            "progress_target": max(1, int(progress_target)),
            "status": "active",
            "created_at": created_at or self._timestamp(),
            "completed_at": None,
        }
        event = {
            "schema": MISSION_SCHEMA,
            "event_id": uuid4().hex,
            "event_type": "mission_created",
            "occurred_at": mission["created_at"],
            "mission": mission,
        }
        result = self._persist_event(event, trace_id=trace_id)
        if not result.success:
            return result
        self.logger.write(
            "info",
            "mission.created",
            trace_id=trace_id,
            mission_id=mission["id"],
            mission_type=normalized_type,
        )
        return ToolResult(
            success=True,
            message="Mission created.",
            data={"mission": mission, "memory": result.data},
        )

    def complete_mission(
        self,
        mission_id: str,
        *,
        progress: int = 1,
        trace_id: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> ToolResult:
        state_result = self._load_state(trace_id=trace_id)
        if not state_result.success:
            return state_result
        missions = state_result.data["missions"]
        mission = missions.get(mission_id)
        if not mission:
            self.logger.write(
                "warning",
                "mission.lookup.failed",
                trace_id=trace_id,
                mission_id=mission_id,
                reason="not_found",
            )
            return ToolResult(success=False, message=f"Mission not found: {mission_id}.")
        if mission["status"] == "completed":
            return ToolResult(success=False, message=f"Mission already completed: {mission_id}.")

        progress_delta = max(1, int(progress))
        new_progress = min(
            int(mission["progress_target"]),
            int(mission["progress_current"]) + progress_delta,
        )
        completed = new_progress >= int(mission["progress_target"])
        occurred_at = completed_at or self._timestamp()
        xp_awarded = int(mission["xp"]) if completed else 0
        event = {
            "schema": MISSION_SCHEMA,
            "event_id": uuid4().hex,
            "event_type": "mission_completed" if completed else "mission_progressed",
            "occurred_at": occurred_at,
            "mission_id": mission_id,
            "progress_delta": progress_delta,
            "progress_current": new_progress,
            "xp_awarded": xp_awarded,
        }
        result = self._persist_event(event, trace_id=trace_id)
        if not result.success:
            return result
        reloaded = self._load_state(trace_id=trace_id)
        updated_mission = reloaded.data["missions"][mission_id]
        self.logger.write(
            "info",
            "mission.completed" if completed else "mission.progressed",
            trace_id=trace_id,
            mission_id=mission_id,
            xp_awarded=xp_awarded,
        )
        return ToolResult(
            success=True,
            message="Mission completed." if completed else "Mission progress updated.",
            data={
                "mission": updated_mission,
                "xp_awarded": xp_awarded,
                "stats": reloaded.data["stats"].to_dict(),
                "memory": result.data,
            },
        )

    def list_active_missions(self, *, trace_id: Optional[str] = None) -> ToolResult:
        state_result = self._load_state(trace_id=trace_id)
        if not state_result.success:
            return state_result
        active = [
            mission
            for mission in state_result.data["missions"].values()
            if mission["status"] == "active"
        ]
        active.sort(key=lambda mission: (-int(mission["priority"]), mission["created_at"]))
        return ToolResult(
            success=True,
            message=f"Found {len(active)} active mission(s).",
            data={"missions": active, "stats": state_result.data["stats"].to_dict()},
        )

    def get_next_mission(self, *, trace_id: Optional[str] = None) -> ToolResult:
        active_result = self.list_active_missions(trace_id=trace_id)
        if not active_result.success:
            return active_result
        missions = active_result.data["missions"]
        next_mission = missions[0] if missions else None
        return ToolResult(
            success=True,
            message="Next mission selected." if next_mission else "No active missions.",
            data={"mission": next_mission, "stats": active_result.data["stats"]},
        )

    def generate_recovery_mission(
        self,
        *,
        inactive_days: Optional[int] = None,
        trace_id: Optional[str] = None,
    ) -> ToolResult:
        state_result = self._load_state(trace_id=trace_id)
        if not state_result.success:
            return state_result
        stats: MissionStats = state_result.data["stats"]
        days = inactive_days if inactive_days is not None else stats.inactive_days
        normalized_days = max(0, int(days or 0))
        title = "Recovery: restart with one small win"
        description = (
            f"After {normalized_days} inactive day(s), choose a 10-minute action that restores momentum."
        )
        return self.create_mission(
            title,
            "recovery_mission",
            description=description,
            xp=15,
            progress_target=1,
            trace_id=trace_id,
        )

    def health(self) -> HealthStatus:
        return self.memory_tool.health()

    def _load_state(self, *, trace_id: Optional[str] = None) -> ToolResult:
        memories = self.memory_tool.list_memories("project", trace_id=trace_id)
        if not memories.success:
            return memories
        events = []
        for record in memories.data.get("records", []):
            content = str(record.get("content", ""))
            events.extend(_extract_events(content))
        events.sort(key=lambda event: str(event.get("occurred_at", "")))

        missions: dict[str, dict[str, object]] = {}
        completed_dates: list[date] = []
        total_xp = 0
        completed_missions = 0
        for event in events:
            event_type = event.get("event_type")
            if event_type == "mission_created":
                mission = dict(event["mission"])
                mission["progress_percent"] = _progress_percent(mission)
                missions[str(mission["id"])] = mission
                continue
            mission_id = str(event.get("mission_id", ""))
            mission = missions.get(mission_id)
            if not mission:
                continue
            mission["progress_current"] = int(event.get("progress_current", 0))
            mission["progress_percent"] = _progress_percent(mission)
            if event_type == "mission_completed":
                mission["status"] = "completed"
                mission["completed_at"] = str(event.get("occurred_at"))
                total_xp += int(event.get("xp_awarded", 0))
                completed_missions += 1
                completed_dates.append(_date_from_iso(str(event.get("occurred_at"))))

        stats = MissionStats(
            total_xp=total_xp,
            completed_missions=completed_missions,
            current_streak=_current_streak(completed_dates, self._today()),
            inactive_days=_inactive_days(completed_dates, self._today()),
        )
        return ToolResult(
            success=True,
            message="Mission state loaded.",
            data={"missions": missions, "events": events, "stats": stats},
        )

    def _persist_event(self, event: dict[str, object], *, trace_id: Optional[str]) -> ToolResult:
        body = (
            f"{MISSION_MARKER}\n\n"
            "```json\n"
            f"{json.dumps(event, sort_keys=True)}\n"
            "```\n"
        )
        result = self.memory_tool.save_memory(body, "project", trace_id=trace_id)
        if not result.success:
            self.logger.write(
                "error",
                "mission.persist.failed",
                trace_id=trace_id,
                event_type=event.get("event_type"),
                reason=result.message,
            )
        return result

    def _timestamp(self) -> str:
        return self._now().astimezone(timezone.utc).isoformat()

    def _today(self) -> date:
        return self._now().astimezone(timezone.utc).date()


def _extract_events(content: str) -> list[dict[str, object]]:
    if MISSION_MARKER not in content:
        return []
    events: list[dict[str, object]] = []
    for match in re.finditer(r"```json\s*(\{.*?\})\s*```", content, flags=re.DOTALL):
        try:
            event = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if event.get("schema") == MISSION_SCHEMA:
            events.append(event)
    return events


def _progress_percent(mission: dict[str, object]) -> int:
    target = max(1, int(mission.get("progress_target", 1)))
    current = min(target, int(mission.get("progress_current", 0)))
    return int((current / target) * 100)


def _date_from_iso(value: str) -> date:
    return datetime.fromisoformat(value).astimezone(timezone.utc).date()


def _current_streak(completed_dates: list[date], today: date) -> int:
    if not completed_dates:
        return 0
    unique_dates = sorted(set(completed_dates))
    last = unique_dates[-1]
    if (today - last).days > 1:
        return 0
    streak = 1
    cursor = last
    for completed_day in reversed(unique_dates[:-1]):
        if (cursor - completed_day).days == 1:
            streak += 1
            cursor = completed_day
        elif completed_day == cursor:
            continue
        else:
            break
    return streak


def _inactive_days(completed_dates: list[date], today: date) -> Optional[int]:
    if not completed_dates:
        return None
    return max(0, (today - max(completed_dates)).days)
