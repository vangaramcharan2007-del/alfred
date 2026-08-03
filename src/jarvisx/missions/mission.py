from __future__ import annotations
import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class Mission:
    mission_id: str = field(default_factory=lambda: f"mission_{uuid.uuid4().hex[:8]}")
    title: str = ""
    user_request: str = ""
    intent: str = "engineering"
    capability: str = "coding.agent"
    provider: str = "goose"
    status: str = "PENDING"  # PENDING, PLANNING, EXECUTING, REVIEWING, COMPLETED, FAILED
    steps: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "title": self.title,
            "user_request": self.user_request,
            "intent": self.intent,
            "capability": self.capability,
            "provider": self.provider,
            "status": self.status,
            "steps": self.steps,
            "result": self.result,
            "created_at": self.created_at
        }
