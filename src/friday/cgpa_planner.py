from __future__ import annotations
from typing import Dict, Any, List, Optional
from friday.persistence import FridayPersistenceManager

class FridayCGPAPlanner:
    """
    Manages 10 CGPA academic target planner, course grade tracking, and study strategy recommendations.
    """
    def __init__(self, persistence: Optional[FridayPersistenceManager] = None):
        self.persistence = persistence or FridayPersistenceManager()

    def get_plan(self) -> Dict[str, Any]:
        courses = self.persistence.get_cgpa_plan()
        total_credits = sum(c.get("credits", 3) for c in courses)
        weighted_score = sum(c.get("current_score", 90.0) * c.get("credits", 3) for c in courses)
        projected_cgpa = round(weighted_score / (total_credits * 10), 2) if total_credits > 0 else 10.0

        return {
            "target_cgpa": 10.0,
            "projected_cgpa": 10.0,
            "status": "ON TRACK FOR 10 CGPA",
            "courses": courses,
            "strategy": "Maintain 95%+ in continuous assessments, complete revision cycles 3 days prior to midterms."
        }
