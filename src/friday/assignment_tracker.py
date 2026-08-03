from __future__ import annotations
from typing import Dict, Any, List, Optional
from friday.persistence import FridayPersistenceManager

class FridayAssignmentTracker:
    """
    Tracks academic assignments, due dates, submission status, and priority deadlines.
    """
    def __init__(self, persistence: Optional[FridayPersistenceManager] = None):
        self.persistence = persistence or FridayPersistenceManager()

    def get_pending_assignments(self) -> List[Dict[str, Any]]:
        return self.persistence.get_assignments()
