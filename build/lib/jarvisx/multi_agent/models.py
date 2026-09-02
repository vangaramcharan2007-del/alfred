"""Data Models for Phase 96 Multi-Agent Operating System."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentRole(str, Enum):
    COORDINATOR = "COORDINATOR"  # Alfred
    TACTICAL = "TACTICAL"        # Friday
    RESEARCHER = "RESEARCHER"    # Knowledge & Discovery
    CODER = "CODER"              # Software Engineering


class MessageType(str, Enum):
    TASK_REQUEST = "TASK_REQUEST"
    TASK_RESULT = "TASK_RESULT"
    STATUS_UPDATE = "STATUS_UPDATE"
    ERROR_REPORT = "ERROR_REPORT"
    BROADCAST = "BROADCAST"


@dataclass
class AgentMessage:
    id: str
    sender: str
    recipient: str
    msg_type: MessageType
    topic: str
    payload: Dict[str, Any]
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "msg_type": self.msg_type.value,
            "topic": self.topic,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


@dataclass
class AgentCapability:
    name: str
    role: AgentRole
    skills: List[str]
    permission_scope: str  # read_only, project_dir, system_exec, coordination

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role.value,
            "skills": self.skills,
            "permission_scope": self.permission_scope,
        }


@dataclass
class SubTask:
    id: str
    title: str
    agent_role: AgentRole
    parameters: Dict[str, Any]
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "agent_role": self.agent_role.value,
            "parameters": self.parameters,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class TeamMissionResult:
    mission_id: str
    objective: str
    subtasks: List[SubTask]
    artifacts: List[str]
    status: str  # COMPLETED, PARTIAL, FAILED
    duration_sec: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "objective": self.objective,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "artifacts": self.artifacts,
            "status": self.status,
            "duration_sec": self.duration_sec,
        }
