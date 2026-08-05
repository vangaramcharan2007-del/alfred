"""Personal Productivity & Knowledge System Layer for Jarvis X (Layer 4).

Delivers study material cataloging, academic assignment coordination, communications triage,
and intelligent lecture transcription and exam synthesis.
"""

from jarvisx.productivity.knowledge_base import PersonalKnowledgeBase, DocumentNote
from jarvisx.productivity.study_scheduler import StudyScheduler, Assignment, RevisionSession
from jarvisx.productivity.inbox_triage import InboxMessage, InboxTriageEngine
from jarvisx.productivity.lecture_synth import LectureExamSynthesizer

__all__ = [
    "PersonalKnowledgeBase",
    "DocumentNote",
    "StudyScheduler",
    "Assignment",
    "RevisionSession",
    "InboxMessage",
    "InboxTriageEngine",
    "LectureExamSynthesizer",
]
