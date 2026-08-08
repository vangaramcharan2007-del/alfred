"""Syllabus Tracker & Weak Area Detection for Phase 94 Personal OS Layer."""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.personal_os.models import Evidence, Subject, TopicMastery
from jarvisx.personal_os.life_memory import LifeMemory


class SyllabusTracker:
    """Manages the curriculum hierarchy and computes topic mastery with evidence backing."""

    def __init__(self, memory: Optional[LifeMemory] = None):
        self.memory = memory or LifeMemory()
        self._ensure_default_curriculum()

    def _ensure_default_curriculum(self) -> None:
        if not self.memory.list_topics():
            now = time.time()
            defaults = [
                TopicMastery(
                    subject="Java & OOP",
                    unit="Unit 3: Polymorphism & Interfaces",
                    topic="Dynamic Method Dispatch",
                    mastery_score=38.0,
                    last_revision_days_ago=9,
                    confidence=0.40,
                    evidence=[
                        Evidence("failed_quiz", "Scored 1/5 on polymorphism edge cases quiz", 0.40, now),
                        Evidence("no_revision", "No study activity recorded for 9 days", 0.30, now),
                    ]
                ),
                TopicMastery(
                    subject="Operating Systems",
                    unit="Unit 2: Process Synchronization",
                    topic="Semaphores & Mutex Locks",
                    mastery_score=42.0,
                    last_revision_days_ago=11,
                    confidence=0.45,
                    evidence=[
                        Evidence("user_confusion", "Marked deadlock synchronization as difficult", 0.35, now),
                        Evidence("no_revision", "11 days since last revision block", 0.30, now),
                    ]
                ),
                TopicMastery(
                    subject="Data Structures",
                    unit="Unit 4: Trees & Graphs",
                    topic="AVL Tree Rotations",
                    mastery_score=78.0,
                    last_revision_days_ago=2,
                    confidence=0.85,
                    evidence=[
                        Evidence("quiz_pass", "Scored 5/5 on tree rotation problem set", 0.50, now)
                    ]
                ),
            ]
            for t in defaults:
                self.memory.save_topic_mastery(t)

    def record_revision(self, subject: str, unit: str, topic_name: str, new_mastery: float, evidence: Optional[Evidence] = None) -> TopicMastery:
        ev_list = [evidence] if evidence else []
        topic = TopicMastery(
            subject=subject,
            unit=unit,
            topic=topic_name,
            mastery_score=new_mastery,
            last_revision_days_ago=0,
            confidence=round(new_mastery / 100.0, 2),
            evidence=ev_list
        )
        self.memory.save_topic_mastery(topic)
        return topic

    def get_weak_areas(self, threshold: float = 50.0) -> List[TopicMastery]:
        """Detect topics requiring immediate revision due to low mastery score or elapsed time."""
        all_topics = self.memory.list_topics()
        weak = [t for t in all_topics if t.mastery_score < threshold or t.last_revision_days_ago >= 7]
        weak.sort(key=lambda t: t.mastery_score)
        return weak

    def get_subject_average_mastery(self, subject: Optional[str] = None) -> float:
        topics = self.memory.list_topics(subject)
        if not topics:
            return 100.0
        return sum(t.mastery_score for t in topics) / len(topics)
