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
    context: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    created_at: float = field(default_factory=time.time)

    @property
    def id(self) -> str:
        return self.mission_id

    @id.setter
    def id(self, value: str) -> None:
        self.mission_id = value

    @property
    def goal(self) -> str:
        return self.user_request or self.title

    @goal.setter
    def goal(self, value: str) -> None:
        self.user_request = value
        if not self.title:
            self.title = value

    @property
    def tasks(self) -> List[str]:
        return self.steps

    @tasks.setter
    def tasks(self, value: List[str]) -> None:
        self.steps = value

    @property
    def state(self) -> str:
        return self.status

    @state.setter
    def state(self, value: str) -> None:
        self.status = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "id": self.id,
            "title": self.title,
            "user_request": self.user_request,
            "goal": self.goal,
            "intent": self.intent,
            "capability": self.capability,
            "provider": self.provider,
            "status": self.status,
            "state": self.state,
            "steps": self.steps,
            "tasks": self.tasks,
            "context": self.context,
            "evidence": self.evidence,
            "result": self.result,
            "created_at": self.created_at
        }
