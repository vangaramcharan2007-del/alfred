import logging
from typing import Dict, Any, List
from .objective_store import ObjectiveStore
from .milestone_engine import MilestoneEngine

logger = logging.getLogger(__name__)

class ProgressMonitor:
    """
    Calculates completion percentages, blocked dependencies, and formats status summaries.
    """
    def __init__(self, store: ObjectiveStore):
        self.store = store

    def get_progress_report(self, objective_id: str) -> str:
        # Fetch all milestones
        cursor = self.store.conn.execute("SELECT name, status FROM milestones WHERE objective_id = ?", (objective_id,))
        milestones = cursor.fetchall()
        
        if not milestones:
            return "No milestones found for this objective."
            
        completed = [m["name"] for m in milestones if m["status"] == "completed"]
        remaining = [m["name"] for m in milestones if m["status"] != "completed"]
        
        total = len(milestones)
        percent = int((len(completed) / total) * 100) if total > 0 else 0
        
        report = f"Objective Progress: {percent}% complete\n\n"
        if completed:
            report += "Completed:\n- " + "\n- ".join(completed) + "\n\n"
        if remaining:
            report += "Remaining:\n- " + "\n- ".join(remaining)
            
        return report

    def get_active_workers(self) -> int:
        cursor = self.store.conn.execute("SELECT count(*) as c FROM worker_assignments")
        row = cursor.fetchone()
        return row["c"] if row else 0
