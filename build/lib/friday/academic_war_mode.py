"""
Friday Academic War Mode - 10 CGPA Strategy & High-Impact Task Optimizer.
Calculates course improvement potential using credit weighting, score gaps, attendance thresholds,
and exam urgency to output daily high-impact recommendations.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from friday.persistence import FridayPersistenceManager


class AcademicWarMode:
    """
    Academic War Mode engine optimizing for 10 CGPA.
    """

    def __init__(self, persistence: Optional[FridayPersistenceManager] = None):
        self.persistence = persistence or FridayPersistenceManager()

    def get_war_strategy(self) -> Dict[str, Any]:
        plan = self.persistence.get_cgpa_plan()

        scored_subjects = []
        for course in plan:
            subj = course["subject"]
            credits = course.get("credits", 3)
            score = course.get("current_score", 90.0)
            target = 100.0  # 10 CGPA target
            gap = max(0.0, target - score)
            attendance = course.get("attendance_pct", 100.0)
            syllabus = course.get("syllabus_pct", 70.0)

            # Impact score = gap * credits * (1 + (100 - syllabus)/100)
            impact = gap * credits * (1.0 + (100.0 - syllabus) / 100.0)

            scored_subjects.append({
                "subject": subj,
                "credits": credits,
                "score": score,
                "gap": gap,
                "attendance": attendance,
                "syllabus": syllabus,
                "impact_score": round(impact, 2)
            })

        scored_subjects.sort(key=lambda x: x["impact_score"], reverse=True)
        top_focus = scored_subjects[0] if scored_subjects else None

        if top_focus:
            rec_text = (
                f"Ramcharan, '{top_focus['subject']}' has the highest improvement opportunity "
                f"({top_focus['credits']} credits, current score {top_focus['score']}%, {top_focus['syllabus']}% syllabus covered). "
                f"Spend 90 minutes today."
            )
        else:
            rec_text = "All subjects on track for 10 CGPA. Focus on project research."

        return {
            "status": "ACTIVE",
            "target_cgpa": 10.0,
            "top_focus": top_focus,
            "impact_ranking": scored_subjects,
            "daily_recommendation": rec_text
        }
