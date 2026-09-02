from __future__ import annotations
from typing import Dict, Any, List, Optional

class MissionRouter:
    INTENT_TO_CAPABILITY = {
        "engineering": "coding.agent",
        "debugging": "coding.agent",
        "architecture": "architecture.agent",
        "review": "coding.agent",
        "analysis": "meta.engine",
        "testing": "coding.agent",
        "deployment": "github.engineering",
        "optimization": "coding.agent",
        "refactoring": "coding.agent",
        "evolution": "evolution.engine",
    }

    INTENT_TO_PROVIDER = {
        "engineering": "goose",
        "debugging": "goose",
        "architecture": "local",
        "review": "openhands",
        "analysis": "local",
        "testing": "goose",
        "deployment": "github",
        "optimization": "goose",
        "refactoring": "openhands",
        "evolution": "local",
    }

    def route(self, intent: str) -> Dict[str, Any]:
        return {
            "capability": self.INTENT_TO_CAPABILITY.get(intent, "coding.agent"),
            "preferred_provider": self.INTENT_TO_PROVIDER.get(intent, "goose"),
            "intent": intent
        }
