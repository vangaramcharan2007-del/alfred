"""Personal Productivity & Knowledge System Layer for Jarvis X.

Delivers study material cataloging, academic assignment coordination, and intelligent
revision timetables.
"""

from jarvisx.productivity.knowledge_base import PersonalKnowledgeBase, DocumentNote
from jarvisx.productivity.study_scheduler import StudyScheduler, Assignment, RevisionSession

__all__ = [
    "PersonalKnowledgeBase",
    "DocumentNote",
    "StudyScheduler",
    "Assignment",
    "RevisionSession",
]
