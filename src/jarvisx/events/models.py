"""Event Models & Schemas for the Jarvis X Event Nervous System."""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    SYSTEM_BOOT = "SYSTEM_BOOT"
    DEADLINE_APPROACHING = "DEADLINE_APPROACHING"
    HABIT_MISSED = "HABIT_MISSED"
    MEMORY_DECAY_CYCLE = "MEMORY_DECAY_CYCLE"
    KNOWLEDGE_UPDATED = "KNOWLEDGE_UPDATED"
    MISSION_COMPLETED = "MISSION_COMPLETED"
    VOICE_TRIGGER = "VOICE_TRIGGER"
    HEARTBEAT_TICK = "HEARTBEAT_TICK"
    CUSTOM = "CUSTOM"


@dataclass
class SystemEvent:
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    priority: int = 5  # 1 (lowest) to 10 (highest/critical)
    origin: str = "System"  # System, User, Sensor, Voice, Scheduler
    timestamp: float = field(default_factory=time.time)
    handled: bool = False
    handler_result: Optional[Dict[str, Any]] = None
