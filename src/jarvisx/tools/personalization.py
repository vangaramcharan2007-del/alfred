from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Callable, Optional
from uuid import uuid4

from jarvisx.config.personalization import DEFAULT_PERSONALITIES, MODE_CONFIGS
from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult
from jarvisx.tools.memory import LocalMemoryTool


PERSONALIZATION_SCHEMA = "jarvisx.personalization_event.v1"
PERSONALIZATION_MARKER = "JARVISX_PERSONALIZATION_EVENT"
DEFAULT_MODE = "companion"
SAFE_PERSONALITY_FIELDS = {
    "agent_id",
    "name",
    "tone",
    "style",
    "verbosity",
    "warmth",
    "examples",
    "pacing",
    "notes",
}
FORBIDDEN_PERSONALITY_FIELDS = {
    "routing",
    "permissions",
    "execution",
    "tools",
    "model",
    "models",
    "agent_id_override",
    "system_prompt",
}


@dataclass(frozen=True)
class PersonalizationState:
    mode: str
    autonomy_level: int
    personalities: dict[str, dict[str, object]]


class PersonalizationTool(BaseTool):
    name = "personalization"

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

    def set_mode(self, mode: str, *, trace_id: Optional[str] = None) -> ToolResult:
        normalized = mode.strip().lower()
        if normalized not in MODE_CONFIGS:
            self.logger.write(
                "warning",
                "personalization.mode.invalid",
                trace_id=trace_id,
                mode=mode,
            )
            return ToolResult(
                success=False,
                message=f"Unsupported mode: {mode}.",
                data={"supported_modes": sorted(MODE_CONFIGS)},
            )
        event = self._event("mode_set", {"mode": normalized})
        result = self._persist_event(event, trace_id=trace_id)
        if not result.success:
            return result
        self.logger.write(
            "info",
            "personalization.mode.set",
            trace_id=trace_id,
            mode=normalized,
        )
        return ToolResult(
            success=True,
            message=f"Mode set to {normalized}.",
            data={"mode": self._mode_payload(normalized), "memory": result.data},
        )

    def get_mode(self) -> ToolResult:
        """Returns the current active operating mode."""
        state = self._load_state()
        return ToolResult(
            success=True, 
            data={
                "mode": state.mode,
                "autonomy_level": state.autonomy_level
            }
        )

    def set_autonomy_level(self, level: int, trace_id: Optional[str] = None) -> ToolResult:
        """Sets the computer control autonomy level (0-3)."""
        if not isinstance(level, int) or level < 0 or level > 3:
            return ToolResult(success=False, message="Autonomy level must be an integer between 0 and 3.")
        
        event = self._event("autonomy_set", {"level": level})
        result = self._persist_event(event, trace_id=trace_id)
        if not result.success:
            return result
        
        self.logger.write(
            "info",
            "personalization.autonomy_level.switch",
            trace_id=trace_id,
            new_level=level,
        )
        return ToolResult(success=True, message=f"Autonomy level set to {level}.")

    def get_autonomy_level(self) -> ToolResult:
        """Returns the current autonomy level."""
        state = self._load_state()
        return ToolResult(success=True, data={"autonomy_level": state.autonomy_level})

    def set_personality(
        self,
        agent_id: str,
        profile: dict[str, object],
        *,
        trace_id: Optional[str] = None,
    ) -> ToolResult:
        normalized_agent_id = _normalize_agent_id(agent_id)
        if not normalized_agent_id:
            return ToolResult(success=False, message="Agent id was empty.")
        forbidden = sorted(set(profile) & FORBIDDEN_PERSONALITY_FIELDS)
        if forbidden:
            self.logger.write(
                "warning",
                "personalization.personality.rejected",
                trace_id=trace_id,
                agent_id=normalized_agent_id,
                forbidden_fields=forbidden,
            )
            return ToolResult(
                success=False,
                message="Personality profiles may contain communication style fields only.",
                data={"forbidden_fields": forbidden, "safe_fields": sorted(SAFE_PERSONALITY_FIELDS)},
            )
        sanitized = {
            key: value
            for key, value in profile.items()
            if key in SAFE_PERSONALITY_FIELDS and value is not None
        }
        sanitized["agent_id"] = normalized_agent_id
        if "name" not in sanitized:
            sanitized["name"] = normalized_agent_id
        event = self._event(
            "personality_set",
            {"agent_id": normalized_agent_id, "profile": sanitized},
        )
        result = self._persist_event(event, trace_id=trace_id)
        if not result.success:
            return result
        self.logger.write(
            "info",
            "personalization.personality.set",
            trace_id=trace_id,
            agent_id=normalized_agent_id,
        )
        return ToolResult(
            success=True,
            message=f"Personality saved for {normalized_agent_id}.",
            data={"personality": sanitized, "memory": result.data},
        )

    def get_personality(self, agent_id: str, *, trace_id: Optional[str] = None) -> ToolResult:
        normalized_agent_id = _normalize_agent_id(agent_id)
        state = self._load_state(trace_id=trace_id)
        profile = state.personalities.get(
            normalized_agent_id,
            _fallback_personality(normalized_agent_id),
        )
        return ToolResult(
            success=True,
            message=f"Personality loaded for {normalized_agent_id}.",
            data={"personality": deepcopy(profile)},
        )

    def list_modes(self, *, trace_id: Optional[str] = None) -> ToolResult:
        state = self._load_state(trace_id=trace_id)
        return ToolResult(
            success=True,
            message=f"Found {len(MODE_CONFIGS)} mode(s).",
            data={"active_mode": state.mode, "modes": deepcopy(MODE_CONFIGS)},
        )

    def list_personalities(self, *, trace_id: Optional[str] = None) -> ToolResult:
        state = self._load_state(trace_id=trace_id)
        return ToolResult(
            success=True,
            message=f"Found {len(state.personalities)} personality profile(s).",
            data={"personalities": deepcopy(state.personalities)},
        )

    def get_response_config(
        self,
        agent_id: str,
        *,
        trace_id: Optional[str] = None,
    ) -> ToolResult:
        state = self._load_state(trace_id=trace_id)
        personality = state.personalities.get(
            _normalize_agent_id(agent_id),
            _fallback_personality(agent_id),
        )
        return ToolResult(
            success=True,
            message=f"Response configuration loaded for {agent_id}.",
            data={
                "mode": self._mode_payload(state.mode),
                "autonomy_level": state.autonomy_level,
                "personality": deepcopy(personality),
                "style_only": True,
                "logic_boundaries": {
                    "affects_routing": False,
                    "affects_permissions": False,
                    "affects_execution": False,
                    "affects_model_selection": False,
                },
            },
        )

    def mode_priority_bias(self, *, trace_id: Optional[str] = None) -> dict[str, int]:
        state = self._load_state(trace_id=trace_id)
        mode = MODE_CONFIGS[state.mode]
        bias = mode.get("mission_bias", {})
        if not isinstance(bias, dict):
            return {}
        return {str(key): int(value) for key, value in bias.items()}

    def health(self) -> HealthStatus:
        return self.memory_tool.health()

    def _load_state(self, *, trace_id: Optional[str] = None) -> PersonalizationState:
        personalities = deepcopy(DEFAULT_PERSONALITIES)
        mode = DEFAULT_MODE
        autonomy_level = 0
        memories = self.memory_tool.list_memories("preference", trace_id=trace_id)
        if not memories.success:
            return PersonalizationState(mode=mode, autonomy_level=autonomy_level, personalities=personalities)
        events = []
        for record in memories.data.get("records", []):
            events.extend(_extract_events(str(record.get("content", ""))))
        events.sort(key=lambda event: str(event.get("occurred_at", "")))
        for event in events:
            event_type = event.get("event_type")
            payload = event.get("payload")
            if not isinstance(payload, dict):
                continue
            if event_type == "mode_set":
                candidate = str(payload.get("mode", "")).strip().lower()
                if candidate in MODE_CONFIGS:
                    mode = candidate
            elif event_type == "autonomy_set":
                level = payload.get("level")
                if isinstance(level, int):
                    autonomy_level = level
            elif event_type == "personality_set":
                agent_id = _normalize_agent_id(str(payload.get("agent_id", "")))
                profile = payload.get("profile")
                if agent_id and isinstance(profile, dict):
                    personalities[agent_id] = {
                        key: value
                        for key, value in profile.items()
                        if key in SAFE_PERSONALITY_FIELDS
                    }
                    personalities[agent_id]["agent_id"] = agent_id
        return PersonalizationState(mode=mode, autonomy_level=autonomy_level, personalities=personalities)

    def _mode_payload(self, mode: str) -> dict[str, object]:
        return deepcopy(MODE_CONFIGS[mode])

    def _event(self, event_type: str, payload: dict[str, object]) -> dict[str, object]:
        return {
            "schema": PERSONALIZATION_SCHEMA,
            "event_id": uuid4().hex,
            "event_type": event_type,
            "occurred_at": self._timestamp(),
            "payload": payload,
        }

    def _persist_event(self, event: dict[str, object], *, trace_id: Optional[str]) -> ToolResult:
        body = (
            f"{PERSONALIZATION_MARKER}\n\n"
            "```json\n"
            f"{json.dumps(event, sort_keys=True)}\n"
            "```\n"
        )
        result = self.memory_tool.save_memory(body, "preference", trace_id=trace_id)
        if not result.success:
            self.logger.write(
                "error",
                "personalization.persist.failed",
                trace_id=trace_id,
                event_type=event.get("event_type"),
                reason=result.message,
            )
        return result

    def _timestamp(self) -> str:
        return self._now().astimezone(timezone.utc).isoformat()


def _extract_events(content: str) -> list[dict[str, object]]:
    if PERSONALIZATION_MARKER not in content:
        return []
    events: list[dict[str, object]] = []
    for match in re.finditer(r"```json\s*(\{.*?\})\s*```", content, flags=re.DOTALL):
        try:
            event = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if event.get("schema") == PERSONALIZATION_SCHEMA:
            events.append(event)
    return events


def _fallback_personality(agent_id: str) -> dict[str, object]:
    normalized_agent_id = _normalize_agent_id(agent_id) or "unknown"
    return {
        "agent_id": normalized_agent_id,
        "name": normalized_agent_id,
        "tone": "neutral",
        "style": "clear and role-appropriate",
        "verbosity": "adaptive",
        "warmth": "neutral",
        "notes": "Fallback style profile for future agents.",
    }


def _normalize_agent_id(agent_id: str) -> str:
    return agent_id.strip().lower()
