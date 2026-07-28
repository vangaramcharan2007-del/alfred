import time
from typing import Dict, Any, List, Optional
from jarvisx.core.logging import StructuredLogger

class TaskManager:
    """
    Source of truth for task state in the distributed mesh.
    """
    STATES = {"SUBMITTED", "ACCEPTED", "RUNNING", "PAUSED", "COMPLETED", "FAILED", "CANCELLED"}

    def __init__(self, logger: StructuredLogger | None = None):
        self.logger = logger or StructuredLogger()
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, task_id: str, node: str, agent: str, trace_id: str) -> None:
        """Initialize a new task in SUBMITTED state."""
        self._tasks[task_id] = {
            "task_id": task_id,
            "status": "SUBMITTED",
            "node": node,
            "agent": agent,
            "trace_id": trace_id,
            "progress": 0,
            "created_at": time.time(),
            "updated_at": time.time(),
            "message": "",
            "result": None,
            "error": None
        }
        self.logger.write("info", "task_manager.task_created", task_id=task_id)

    def update_status(self, task_id: str, status: str, **kwargs) -> None:
        """Update a task's status and metadata based on incoming events."""
        if task_id not in self._tasks:
            self.logger.write("warning", "task_manager.task_not_found", task_id=task_id)
            return

        status = status.upper()
        if status not in self.STATES:
            self.logger.write("error", "task_manager.invalid_status", status=status)
            return

        task = self._tasks[task_id]
        task["status"] = status
        task["updated_at"] = time.time()
        
        for key, value in kwargs.items():
            task[key] = value
            
        self.logger.write("info", "task_manager.status_updated", task_id=task_id, status=status)

    def cancel_task(self, task_id: str) -> None:
        self.update_status(task_id, "CANCELLED")

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)

    def list_active_tasks(self) -> List[Dict[str, Any]]:
        """Return tasks that are not in terminal states."""
        terminals = {"COMPLETED", "FAILED", "CANCELLED"}
        return [t for t in self._tasks.values() if t["status"] not in terminals]
