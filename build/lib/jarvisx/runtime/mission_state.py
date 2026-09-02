"""Mission State Engine for Jarvis X.

Encapsulates the lifecycle, execution progress, checkpoints, and assigned workers
for active tasks supervised by Alfred.
"""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional
import uuid


class MissionStatus(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"


@dataclass
class TaskItem:
    task_id: str
    description: str
    assigned_agent: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    created_at: float = field(default_factory=time.time)


@dataclass
class MissionState:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective: str = ""
    status: MissionStatus = MissionStatus.CREATED
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    tasks: List[TaskItem] = field(default_factory=list)
    current_task_idx: int = 0
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    assigned_agents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def transition(self, new_status: MissionStatus) -> None:
        self.status = new_status
        self.updated_at = time.time()
        self.checkpoints.append(
            {
                "timestamp": self.updated_at,
                "status": new_status.value,
                "current_task_idx": self.current_task_idx,
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
            }
        )

    def get_current_task(self) -> Optional[TaskItem]:
        if 0 <= self.current_task_idx < len(self.tasks):
            return self.tasks[self.current_task_idx]
        return None
