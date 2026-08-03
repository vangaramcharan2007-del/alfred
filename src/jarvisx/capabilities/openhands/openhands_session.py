from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class OpenHandsSession:
    session_id: str
    project: str
    start_time: float = field(default_factory=time.time)
    is_active: bool = True
    is_paused: bool = False
    history: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=lambda: {"tasks_executed": 0, "total_duration": 0.0})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "project": self.project,
            "start_time": self.start_time,
            "is_active": self.is_active,
            "is_paused": self.is_paused,
            "history_count": len(self.history),
            "metrics": self.metrics
        }

class OpenHandsSessionManager:
    def __init__(self):
        self.sessions: Dict[str, OpenHandsSession] = {}

    def start_session(self, project_name: str) -> OpenHandsSession:
        sid = f"oh_sess_{uuid.uuid4().hex[:8]}"
        session = OpenHandsSession(session_id=sid, project=project_name)
        self.sessions[sid] = session
        return session

    def resume_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.is_active = True
            session.is_paused = False
            return True
        return False

    def pause_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.is_paused = True
            return True
        return False

    def cancel_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            session.metrics["cancelled"] = True
            return True
        return False

    def terminate_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            session.metrics["total_duration"] = time.time() - session.start_time
            return True
        return False

    def record_task_history(self, session_id: str, task_record: Dict[str, Any]) -> None:
        session = self.sessions.get(session_id)
        if session:
            session.history.append(task_record)
            session.metrics["tasks_executed"] += 1

    def get_session(self, session_id: str) -> Optional[OpenHandsSession]:
        return self.sessions.get(session_id)

    def list_active_sessions(self) -> List[OpenHandsSession]:
        return [s for s in self.sessions.values() if s.is_active and not s.is_paused]
