"""Notification Policy Engine — controls what Alfred tells the user and when."""
from enum import Enum
from typing import Optional


class NotificationLevel(str, Enum):
    SILENT = "SILENT"
    INFORMATIONAL = "INFORMATIONAL"
    IMPORTANT = "IMPORTANT"
    CRITICAL = "CRITICAL"


# Pre-defined classification of internal events
_EVENT_CLASSIFICATION = {
    # SILENT — never surface to the user
    "memory_indexing":      NotificationLevel.SILENT,
    "cache_cleanup":        NotificationLevel.SILENT,
    "internal_retry":       NotificationLevel.SILENT,
    "internal_planning":    NotificationLevel.SILENT,
    "agent_communication":  NotificationLevel.SILENT,
    "heartbeat":            NotificationLevel.SILENT,

    # INFORMATIONAL — show when convenient
    "task_completion":      NotificationLevel.INFORMATIONAL,
    "suggestion":           NotificationLevel.INFORMATIONAL,
    "recommendation":       NotificationLevel.INFORMATIONAL,
    "objective_progress":   NotificationLevel.INFORMATIONAL,

    # IMPORTANT — actively notify
    "repeated_failure":     NotificationLevel.IMPORTANT,
    "missing_permission":   NotificationLevel.IMPORTANT,
    "incomplete_objective": NotificationLevel.IMPORTANT,
    "capability_gap":       NotificationLevel.IMPORTANT,

    # CRITICAL — always interrupt
    "low_disk_space":       NotificationLevel.CRITICAL,
    "hardware_issue":       NotificationLevel.CRITICAL,
    "backup_failure":       NotificationLevel.CRITICAL,
    "security_issue":       NotificationLevel.CRITICAL,
}


class NotificationPolicy:
    """Determines whether an internal event should be surfaced to the user."""

    def __init__(self, minimum_level: NotificationLevel = NotificationLevel.INFORMATIONAL):
        self.minimum_level = minimum_level
        self._level_rank = {
            NotificationLevel.SILENT: 0,
            NotificationLevel.INFORMATIONAL: 1,
            NotificationLevel.IMPORTANT: 2,
            NotificationLevel.CRITICAL: 3,
        }

    def classify(self, event_type: str) -> NotificationLevel:
        """Return the notification level for a given internal event type."""
        return _EVENT_CLASSIFICATION.get(event_type, NotificationLevel.SILENT)

    def should_notify(self, event_type: str) -> bool:
        """Return True if this event type is at or above the minimum level."""
        level = self.classify(event_type)
        return self._level_rank[level] >= self._level_rank[self.minimum_level]

    def set_minimum_level(self, level: NotificationLevel):
        self.minimum_level = level
