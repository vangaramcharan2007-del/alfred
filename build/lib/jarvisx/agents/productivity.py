"""Operational Productivity Agent for Jarvis X.

Specialized workforce agent managing college note catalogs, assignment deadlines,
and spaced-repetition revision plans.
"""

from typing import Any, Dict, Optional
from jarvisx.agents.base import OperationalAgent
from jarvisx.productivity import PersonalKnowledgeBase, StudyScheduler


class ProductivityAgent(OperationalAgent):
    """Production worker organizing personal study workflows and note catalogs."""

    __test__ = False

    def __init__(
        self,
        name: str = "productivity_agent",
        hspw_multiplier: float = 0.8,
        kb: Optional[PersonalKnowledgeBase] = None,
        scheduler: Optional[StudyScheduler] = None,
    ):
        super().__init__(
            name=name,
            purpose="Organize study notes, track deadlines, and generate exam revision timetables",
            capabilities=["note_organization", "deadline_tracking", "revision_planning", "project_milestones"],
            permissions=["read_filesystem", "write_filesystem", "memory_access"],
            hspw_multiplier=hspw_multiplier,
        )
        self.kb = kb or PersonalKnowledgeBase()
        self.scheduler = scheduler or StudyScheduler()

    def _execute_task(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        action = (task.get("action") or task.get("parameters", {}).get("action", "dashboard")).lower()

        if action == "add_note":
            title = task.get("title", "Untitled Note")
            content = task.get("content", "")
            course = task.get("course", "General")
            tags = task.get("tags", [])
            note = self.kb.add_note(title, content, course, tags)
            return {
                "status": "completed",
                "action": "add_note",
                "note_id": note.id,
                "output": f"✓ Cataloged note '{note.title}' under {course}",
            }

        elif action == "schedule_revision":
            course = task.get("course", "General Study")
            topics = task.get("topics", ["Overview", "Chapter 1", "Practice Problems"])
            days = task.get("days_until_exam", 7)
            sessions = self.scheduler.generate_revision_plan(course, topics, days)
            return {
                "status": "completed",
                "action": "schedule_revision",
                "course": course,
                "sessions_created": len(sessions),
                "output": f"✓ Synthesized {len(sessions)}-session revision plan for {course}",
            }

        elif action == "add_assignment":
            title = task.get("title", "Project Milestone")
            course = task.get("course", "General")
            due_date = task.get("due_date", "Friday")
            prio = task.get("priority", "Medium")
            item = self.scheduler.add_assignment(title, course, due_date, prio)
            return {
                "status": "completed",
                "action": "add_assignment",
                "assignment_id": item.id,
                "output": f"✓ Registered priority [{prio}] assignment '{item.title}' for {course}",
            }

        else:
            dashboard = self.scheduler.get_weekly_dashboard()
            return {
                "status": "completed",
                "action": "dashboard",
                "pending_count": dashboard.get("pending_count", 0),
                "output": dashboard["output"],
            }
