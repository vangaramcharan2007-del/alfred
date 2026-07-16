import uuid
import logging
from typing import List, Dict, Any
from .objective_store import ObjectiveStore

logger = logging.getLogger(__name__)

class GoalManager:
    """
    CRUD Interface for Objectives, Visions, and Tasks.
    """
    def __init__(self, store: ObjectiveStore):
        self.store = store

    def create_objective(self, name: str, priority="normal", obj_type="engineering") -> str:
        obj_id = str(uuid.uuid4())
        self.store.execute_transaction([
            ("INSERT INTO objectives (id, name, priority, objective_type) VALUES (?, ?, ?, ?)",
             (obj_id, name, priority, obj_type))
        ])
        logger.info(f"Created objective: {name} ({obj_id})")
        return obj_id

    def set_objective_status(self, objective_id: str, status: str):
        valid = {'created', 'planning', 'ready', 'running', 'blocked', 'paused', 'completed', 'failed', 'cancelled', 'archived'}
        if status not in valid:
            raise ValueError(f"Invalid objective status: {status}")
        self.store.execute_transaction([
            ("UPDATE objectives SET status = ? WHERE id = ?", (status, objective_id))
        ])

    def pause_objective(self, objective_id: str):
        self.set_objective_status(objective_id, "paused")

    def resume_objective(self, objective_id: str):
        self.set_objective_status(objective_id, "running")

    def cancel_objective(self, objective_id: str):
        self.set_objective_status(objective_id, "cancelled")

    def archive_objective(self, objective_id: str):
        self.set_objective_status(objective_id, "archived")

    def list_active_objectives(self) -> List[Dict[str, Any]]:
        return self.store.list_active_objectives()
