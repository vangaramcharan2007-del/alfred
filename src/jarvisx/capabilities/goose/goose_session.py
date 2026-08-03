from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class GooseSession:
    session_id: str
    project_name: str
    created_at: float = field(default_factory=time.time)
    is_active: bool = True
    history: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "project_name": self.project_name,
            "created_at": round(self.created_at, 3),
            "is_active": self.is_active,
            "history": self.history,
            "metrics": self.metrics
        }

class GooseSessionManager:
    def __init__(self):
        self.sessions: Dict[str, GooseSession] = {}

    def create_session(self, project_name: str) -> GooseSession:
        sid = f"goose_sess_{uuid.uuid4().hex[:8]}"
        session = GooseSession(session_id=sid, project_name=project_name, is_active=True)
        self.sessions[sid] = session
        return session

    def resume_session(self, session_id: str) -> Optional[GooseSession]:
        session = self.sessions.get(session_id)
        if session:
            session.is_active = True
        return session

    def terminate_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            return True
        return False

    def get_session(self, session_id: str) -> Optional[GooseSession]:
        return self.sessions.get(session_id)

    def list_active_sessions(self) -> List[GooseSession]:
        return [s for s in self.sessions.values() if s.is_active]

    def record_task_history(self, session_id: str, task: Dict[str, Any]) -> None:
        session = self.get_session(session_id)
        if session:
            session.history.append(task)
            completed_tasks = len(session.history)
            session.metrics["tasks_executed"] = completed_tasks
