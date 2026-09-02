from __future__ import annotations
from typing import Dict, Any, List, Optional
from friday.persistence import FridayPersistenceManager

class FridayHabitTracker:
    """
    Tracks daily study habits, streak counts, and consistency metrics.
    """
    def __init__(self, persistence: Optional[FridayPersistenceManager] = None):
        self.persistence = persistence or FridayPersistenceManager()

    def get_habits(self) -> List[Dict[str, Any]]:
        return self.persistence.get_habits()
