from __future__ import annotations
from typing import Dict, Any, List, Optional
from friday.persistence import FridayPersistenceManager

class FridayNotesAndGoals:
    """
    Manages personal notes, daily motivation quotes, and long-term academic/career goals.
    """
    def __init__(self, persistence: Optional[FridayPersistenceManager] = None):
        self.persistence = persistence or FridayPersistenceManager()

    def get_notes_and_goals(self) -> List[Dict[str, Any]]:
        return self.persistence.get_notes_and_goals()
