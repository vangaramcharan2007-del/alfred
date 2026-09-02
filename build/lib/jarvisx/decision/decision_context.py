from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class DecisionContext:
    task_description: str = ""
    intent: str = "engineering"
    available_capabilities: List[str] = field(default_factory=list)
    available_providers: List[str] = field(default_factory=list)
    available_models: List[str] = field(default_factory=list)
    require_offline: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_description": self.task_description,
            "intent": self.intent,
            "available_capabilities": self.available_capabilities,
            "available_providers": self.available_providers,
            "available_models": self.available_models,
            "require_offline": self.require_offline
        }
