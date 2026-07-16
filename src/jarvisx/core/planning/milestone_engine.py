import uuid
import logging
from typing import List, Dict, Any
from .objective_store import ObjectiveStore

logger = logging.getLogger(__name__)

class MilestoneEngine:
    """
    Manages milestone progression within an objective.
    """
    def __init__(self, store: ObjectiveStore):
        self.store = store

    def create_milestone(self, objective_id: str, name: str) -> str:
        m_id = str(uuid.uuid4())
        self.store.execute_transaction([
            ("INSERT INTO milestones (id, objective_id, name) VALUES (?, ?, ?)",
             (m_id, objective_id, name))
        ])
        return m_id

    def complete_milestone(self, milestone_id: str):
        self.store.execute_transaction([
            ("UPDATE milestones SET status = 'completed' WHERE id = ?", (milestone_id,))
        ])

    def show_milestones(self, objective_id: str) -> List[Dict[str, Any]]:
        cursor = self.store.conn.execute(
            "SELECT * FROM milestones WHERE objective_id = ?", 
            (objective_id,)
        )
        return [dict(r) for r in cursor.fetchall()]

    def next_milestone(self, objective_id: str) -> Dict[str, Any]:
        """Returns the first uncompleted milestone."""
        cursor = self.store.conn.execute(
            "SELECT * FROM milestones WHERE objective_id = ? AND status != 'completed' ORDER BY rowid ASC LIMIT 1", 
            (objective_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
