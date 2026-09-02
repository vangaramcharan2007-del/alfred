"""Goal Decomposer for Phase 91 Autonomous Mission Brain."""

from __future__ import annotations
import json
from typing import Dict, Any, List, Optional
from jarvisx.llm.llm_router import LLMRouter


class GoalDecomposer:
    """Decomposes high-level user goals into structured milestones and requirements."""

    def __init__(self, router: Optional[LLMRouter] = None):
        self.router = router or LLMRouter()

    def decompose(self, goal: str) -> Dict[str, Any]:
        """Decompose natural language goal into execution milestones."""
        g = goal.lower().strip()

        # Deterministic Archetype Detection
        if "calculator" in g:
            return {
                "mission_name": "python_calculator",
                "goal": goal,
                "domain": "software_engineering",
                "milestones": [
                    {"id": "m1", "title": "Generate Calculator Source Module", "type": "code_creation", "target": "src/calculator.py"},
                    {"id": "m2", "title": "Generate Unit Tests", "type": "test_creation", "target": "tests/test_calculator.py"},
                    {"id": "m3", "title": "Generate Project Documentation", "type": "doc_creation", "target": "README.md"},
                    {"id": "m4", "title": "Generate Mission Summary Report", "type": "report_creation", "target": "mission_report.md"}
                ]
            }

        elif "java" in g and "exam" in g or "exam" in g:
            return {
                "mission_name": "java_exam_prep",
                "goal": goal,
                "domain": "academic_preparation",
                "milestones": [
                    {"id": "m1", "title": "Generate Comprehensive Java Crash Notes", "type": "notes_creation", "target": "java_crash_notes.md"},
                    {"id": "m2", "title": "Generate Interactive Practice Quiz", "type": "quiz_creation", "target": "java_practice_quiz.json"},
                    {"id": "m3", "title": "Generate Study Revision Schedule", "type": "schedule_creation", "target": "study_revision_schedule.md"},
                    {"id": "m4", "title": "Generate Mission Summary Report", "type": "report_creation", "target": "mission_report.md"}
                ]
            }

        elif "organize" in g or "papers" in g or "research" in g:
            return {
                "mission_name": "research_papers_organization",
                "goal": goal,
                "domain": "file_organization",
                "milestones": [
                    {"id": "m1", "title": "Categorize & Organize Research Documents", "type": "file_organization", "target": "documents"},
                    {"id": "m2", "title": "Generate Research Topic Summaries", "type": "notes_creation", "target": "research_summary.md"},
                    {"id": "m3", "title": "Generate Mission Summary Report", "type": "report_creation", "target": "mission_report.md"}
                ]
            }

        # Dynamic Generalized Fallback
        slug = g.replace("jarvis", "").replace("create", "").replace("prepare", "").replace(" ", "_").strip("_")[:30] or "custom_mission"
        return {
            "mission_name": slug,
            "goal": goal,
            "domain": "general_automation",
            "milestones": [
                {"id": "m1", "title": "Execute Primary Goal Work", "type": "work_execution", "target": "output_deliverables"},
                {"id": "m2", "title": "Generate Mission Summary Report", "type": "report_creation", "target": "mission_report.md"}
            ]
        }
