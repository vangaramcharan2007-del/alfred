from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProfile:
    name: str
    purpose: str
    offline: bool
    notes: str
    tier: str = "tier_1_fast"

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "offline": self.offline,
            "notes": self.notes,
            "tier": self.tier,
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
                tier="tier_2_reasoning",
            ),
            "coding": ModelProfile(
                name="local-coding",
                purpose="debugging and patch generation",
                offline=True,
                notes="Debug Agent suggests fixes but does not deploy without approval.",
                tier="tier_2_reasoning",
            ),
            "vision": ModelProfile(
                name="local-vision",
                purpose="image or CAD inspection",
                offline=True,
                notes="Placeholder for a local vision-capable model.",
                tier="tier_2_reasoning",
            ),
        }

    def select(self, task_class: str, message: str = "", has_image: bool = False) -> ModelProfile:
        # Determine base profile based on task_class
        if task_class in {"debug", "coding"}:
            base_profile = self._profiles["coding"]
        elif task_class in {"cad", "editing", "vision"}:
            base_profile = self._profiles["vision"]
        elif task_class in {"research", "shadowbroker", "planning"}:
            base_profile = self._profiles["reasoning"]
        elif task_class == "memory":
            base_profile = self._profiles["memory"]
        elif task_class == "device":
            base_profile = self._profiles["device"]
        else:
            base_profile = self._profiles["intent"]
            
        # Determine tier dynamically based on complexity
        tier = self._determine_tier(task_class, message, has_image)
        
        # Return a new ModelProfile with the determined tier
        return ModelProfile(
            name=base_profile.name,
            purpose=base_profile.purpose,
            offline=base_profile.offline,
            notes=base_profile.notes,
            tier=tier,
        )

    def _determine_tier(self, task_class: str, message: str, has_image: bool) -> str:
        if has_image:
            return "tier_2_reasoning"
            
        complex_classes = {"coding", "reasoning", "planning", "debug", "shadowbroker", "cad", "editing"}
        if task_class in complex_classes:
            return "tier_2_reasoning"
            
        words = message.strip().split()
        if len(words) > 15:
            return "tier_2_reasoning"
            
        return "tier_1_fast"
