from __future__ import annotations
from typing import Dict, Any, List, Optional
from friday.persistence import FridayPersistenceManager

class FridayScheduleManager:
    """
    Manages daily schedule, timetable, classes, and study sessions for Friday.
    """
    def __init__(self, persistence: Optional[FridayPersistenceManager] = None):
        self.persistence = persistence or FridayPersistenceManager()

    def get_todays_schedule(self) -> List[Dict[str, Any]]:
        return self.persistence.get_schedule()
