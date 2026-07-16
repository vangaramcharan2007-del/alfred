import logging
from ..workforce_db import WorkforceDatabase

logger = logging.getLogger(__name__)

class TaskMemory:
    """
    Interfaces with the WorkforceDatabase to read active/completed tasks
    and determine the progress of ongoing engineering projects.
    """
    def __init__(self, db_path="var/workforce.db"):
        self.db = WorkforceDatabase(db_path=db_path)

    def get_active_tasks(self) -> list:
        cursor = self.db.conn.execute(
            "SELECT task_id, status, assigned_agent, started_at FROM workforce_tasks WHERE status NOT IN ('COMPLETED', 'FAILED') ORDER BY started_at DESC"
        )
        return [{"task_id": r[0], "status": r[1], "assigned_agent": r[2], "started_at": r[3]} for r in cursor.fetchall()]

    def get_completed_tasks_recently(self, limit=5) -> list:
        cursor = self.db.conn.execute(
            "SELECT task_id, status, assigned_agent, completed_at FROM workforce_tasks WHERE status = 'COMPLETED' ORDER BY completed_at DESC LIMIT ?",
            (limit,)
        )
        return [{"task_id": r[0], "status": r[1], "assigned_agent": r[2], "completed_at": r[3]} for r in cursor.fetchall()]

    def get_project_state(self) -> dict:
        """Heuristics to define what the system is currently working on."""
        active = self.get_active_tasks()
        completed = self.get_completed_tasks_recently()
        
        return {
            "active": active,
            "recently_completed": completed
        }
