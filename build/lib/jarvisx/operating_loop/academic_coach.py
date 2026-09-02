"""Academic & Engineering Coach Engine for Phase 105.

Supports dynamic learning profiles (BTech CSE, Medical, Law, Research, etc.),
topic mastery matrices, and prioritized mission synthesis.
"""

from __future__ import annotations
import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from jarvisx.operating_loop.models import (
    LearningProfile,
    StudyMission,
    TopicMastery,
)

logger = logging.getLogger("jarvisx.academic_coach")


class AcademicCoachEngine:
    """Manages syllabus tracking, dynamic topic mastery, and generates prioritized study missions."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "var/db/operating_loop.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.profile = self._load_or_create_profile()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_profiles (
                    id TEXT PRIMARY KEY,
                    degree TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    primary_goal TEXT NOT NULL,
                    learning_style TEXT NOT NULL,
                    active_streak_days INTEGER NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS topic_mastery (
                    topic_name TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    mastery_level REAL NOT NULL,
                    confidence REAL NOT NULL,
                    exam_proximity_days INTEGER,
                    past_failures_count INTEGER NOT NULL,
                    subtopics_json TEXT NOT NULL,
                    last_practiced_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS study_missions (
                    mission_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    estimated_minutes INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    tasks_json TEXT NOT NULL,
                    completed INTEGER NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    def _load_or_create_profile(self) -> LearningProfile:
        with self._get_connection() as conn:
            p_row = conn.execute("SELECT * FROM learning_profiles WHERE id = 'default'").fetchone()
            t_rows = conn.execute("SELECT * FROM topic_mastery").fetchall()

            topics: Dict[str, TopicMastery] = {}
            for row in t_rows:
                subtopics = json.loads(row["subtopics_json"]) if row["subtopics_json"] else []
                topics[row["topic_name"]] = TopicMastery(
                    topic_name=row["topic_name"],
                    domain=row["domain"],
                    mastery_level=row["mastery_level"],
                    confidence=row["confidence"],
                    exam_proximity_days=row["exam_proximity_days"],
                    past_failures_count=row["past_failures_count"],
                    subtopics=subtopics,
                    last_practiced_at=row["last_practiced_at"],
                )

            if p_row:
                return LearningProfile(
                    degree=p_row["degree"],
                    domain=p_row["domain"],
                    primary_goal=p_row["primary_goal"],
                    learning_style=p_row["learning_style"],
                    topics=topics,
                    active_streak_days=p_row["active_streak_days"],
                )

        # Default initialization for BTech CSE
        default_topics = {
            "Arrays & Strings": TopicMastery("Arrays & Strings", "DSA", 0.85, 0.90, None, 0, ["Two Pointers", "Sliding Window"]),
            "Binary Trees & BST": TopicMastery("Binary Trees & BST", "DSA", 0.60, 0.80, None, 1, ["DFS/BFS Traversals", "LCA"]),
            "Graph Algorithms": TopicMastery("Graph Algorithms", "DSA", 0.25, 0.70, None, 3, ["Dijkstra", "Topological Sort", "Union-Find"]),
            "Dynamic Programming": TopicMastery("Dynamic Programming", "DSA", 0.30, 0.75, None, 4, ["0/1 Knapsack", "LCS", "LIS"]),
            "Virtual Memory & Paging": TopicMastery("Virtual Memory & Paging", "Operating Systems", 0.45, 0.80, 12, 2, ["Page Replacement", "TLB Misses"]),
            "Process Synchronization": TopicMastery("Process Synchronization", "Operating Systems", 0.70, 0.85, 12, 0, ["Semaphores", "Mutexes", "Dining Philosophers"]),
            "Database Normalization": TopicMastery("Database Normalization", "DBMS", 0.75, 0.85, 18, 0, ["1NF", "2NF", "3NF", "BCNF"]),
            "Deadlocks & Concurrency": TopicMastery("Deadlocks & Concurrency", "DBMS", 0.35, 0.75, 18, 2, ["2PL", "Deadlock Detection", "Timestamp Ordering"]),
            "TCP/IP & Subnetting": TopicMastery("TCP/IP & Subnetting", "Computer Networks", 0.65, 0.80, 24, 1, ["CIDR", "Flow Control", "Congestion Avoidance"]),
        }
        profile = LearningProfile(
            degree="BTech",
            domain="Computer Science & Engineering (BDA)",
            primary_goal="Targeting 10 CGPA & Master DSA",
            learning_style="Hands-on coding, spaced-repetition retrieval, and problem solving",
            topics=default_topics,
            active_streak_days=5,
        )
        self.save_profile(profile)
        return profile

    def save_profile(self, profile: Optional[LearningProfile] = None):
        p = profile or self.profile
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO learning_profiles (
                    id, degree, domain, primary_goal, learning_style, active_streak_days, updated_at
                ) VALUES ('default', ?, ?, ?, ?, ?, ?)
                """,
                (p.degree, p.domain, p.primary_goal, p.learning_style, p.active_streak_days, time.time()),
            )
            for t in p.topics.values():
                conn.execute(
                    """
                    INSERT OR REPLACE INTO topic_mastery (
                        topic_name, domain, mastery_level, confidence, exam_proximity_days,
                        past_failures_count, subtopics_json, last_practiced_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        t.topic_name,
                        t.domain,
                        t.mastery_level,
                        t.confidence,
                        t.exam_proximity_days,
                        t.past_failures_count,
                        json.dumps(t.subtopics),
                        t.last_practiced_at,
                    ),
                )
            conn.commit()

    def update_topic_mastery(
        self,
        topic_name: str,
        mastery_delta: float,
        domain: str = "General",
        past_failure_delta: int = 0,
    ) -> TopicMastery:
        """Update or insert topic mastery score with bounds clamping (0.0 to 1.0)."""
        if topic_name in self.profile.topics:
            t = self.profile.topics[topic_name]
            t.mastery_level = max(0.0, min(1.0, round(t.mastery_level + mastery_delta, 3)))
            t.past_failures_count = max(0, t.past_failures_count + past_failure_delta)
            t.last_practiced_at = time.time()
        else:
            t = TopicMastery(
                topic_name=topic_name,
                domain=domain,
                mastery_level=max(0.0, min(1.0, round(0.5 + mastery_delta, 3))),
                last_practiced_at=time.time(),
            )
            self.profile.topics[topic_name] = t

        self.save_profile()
        return t

    def get_highest_priority_topics(self, limit: int = 3) -> List[TopicMastery]:
        """Rank topics dynamically by computed priority formula."""
        ranked = sorted(
            self.profile.topics.values(),
            key=lambda t: t.calculate_priority_score(),
            reverse=True,
        )
        return ranked[:limit]

    def generate_daily_study_missions(self, max_missions: int = 3) -> List[StudyMission]:
        """Generate focused, actionable study missions based on weakness + exam proximity."""
        top_topics = self.get_highest_priority_topics(limit=max_missions)
        missions: List[StudyMission] = []

        for topic in top_topics:
            sub = topic.subtopics[0] if topic.subtopics else "Core Concepts"
            reason = (
                f"High priority (Mastery: {int(topic.mastery_level * 100)}%"
                + (f", Exam in {topic.exam_proximity_days}d" if topic.exam_proximity_days else "")
                + (f", {topic.past_failures_count} past mistakes" if topic.past_failures_count > 0 else "")
                + ")"
            )

            tasks = [
                f"Review active recall notes on {topic.topic_name} ({sub})",
                f"Solve 2 practice problems / LeetCode challenges on {topic.topic_name}",
                f"Implement code verification snippet and record insights in Obsidian",
            ]

            mission = StudyMission(
                title=f"[*] {topic.domain}: {topic.topic_name} Focus Sprint",
                topic=topic.topic_name,
                estimated_minutes=45,
                reason=reason,
                tasks=tasks,
            )
            missions.append(mission)
            self._save_mission(mission)

        return missions

    def _save_mission(self, mission: StudyMission):
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO study_missions (
                    mission_id, title, topic, estimated_minutes, reason, tasks_json, completed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mission.mission_id,
                    mission.title,
                    mission.topic,
                    mission.estimated_minutes,
                    mission.reason,
                    json.dumps(mission.tasks),
                    1 if mission.completed else 0,
                    mission.created_at,
                ),
            )
            conn.commit()

    def get_recent_missions(self, limit: int = 5) -> List[StudyMission]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM study_missions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            missions = []
            for r in rows:
                missions.append(
                    StudyMission(
                        mission_id=r["mission_id"],
                        title=r["title"],
                        topic=r["topic"],
                        estimated_minutes=r["estimated_minutes"],
                        reason=r["reason"],
                        tasks=json.loads(r["tasks_json"]),
                        completed=bool(r["completed"]),
                        created_at=r["created_at"],
                    )
                )
            return missions
