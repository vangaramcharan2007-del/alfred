from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProfile:
    name: str
    purpose: str
    offline: bool
    notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "offline": self.offline,
            "notes": self.notes,
        }


class ModelRouter:
    """Selects the smallest capable model profile for a task class."""

    def __init__(self) -> None:
        self._profiles = {
            "intent": ModelProfile(
                name="small-local-intent",
                purpose="intent classification",
                offline=True,
                notes="Rule-based in this scaffold; replace with a local classifier later.",
            ),
            "device": ModelProfile(
                name="small-local-control",
                purpose="device command parsing",
                offline=True,
                notes="Use for direct app and notification tasks.",
            ),
            "memory": ModelProfile(
                name="small-local-memory",
                purpose="memory retrieval and storage",
                offline=True,
                notes="Use local text search before semantic retrieval is available.",
            ),
            "reasoning": ModelProfile(
                name="local-reasoning",
                purpose="multi-step reasoning",
                offline=True,
                notes="Placeholder for a larger local reasoning model.",
            ),
            "coding": ModelProfile(
                name="local-coding",
                purpose="debugging and patch generation",
                offline=True,
                notes="Debug Agent suggests fixes but does not deploy without approval.",
            ),
            "vision": ModelProfile(
                name="local-vision",
                purpose="image or CAD inspection",
                offline=True,
                notes="Placeholder for a local vision-capable model.",
            ),
        }

    def select(self, task_class: str) -> ModelProfile:
        if task_class in {"debug", "coding"}:
            return self._profiles["coding"]
        if task_class in {"cad", "editing", "vision"}:
            return self._profiles["vision"]
        if task_class in {"research", "shadowbroker", "planning"}:
            return self._profiles["reasoning"]
        if task_class == "memory":
            return self._profiles["memory"]
        if task_class == "device":
            return self._profiles["device"]
        return self._profiles["intent"]
