"""Life Memory Persistent SQLite Store for Phase 94 Personal OS Layer."""

from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.personal_os.models import (
    DailyPriority,
    Evidence,
    Goal,
    GoalStatus,
    HabitLog,
    Milestone,
    TopicMastery,
)


class LifeMemory:
    """Dedicated persistent SQLite database for structured life facts, goals, syllabus, and habits."""

    def __init__(self, db_path: str = "var/db/personal_os.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    category TEXT,
                    target_date TEXT,
                    progress_pct REAL,
                    status TEXT,
                    risk_reason TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS milestones (
                    id TEXT PRIMARY KEY,
                    goal_id TEXT,
                    title TEXT,
                    deadline TEXT,
                    completed INTEGER
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    subject TEXT,
                    unit TEXT,
                    topic TEXT,
                    mastery_score REAL,
                    last_revision_days_ago INTEGER,
                    confidence REAL,
                    PRIMARY KEY (subject, unit, topic)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT,
                    topic TEXT,
                    type TEXT,
                    description TEXT,
                    weight REAL,
                    timestamp REAL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    habit TEXT,
                    duration_hours REAL,
                    category TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS priorities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    task TEXT,
                    score REAL,
                    breakdown_json TEXT,
                    explanation TEXT,
                    mission_goal TEXT
                )
            """)
            conn.commit()

    def save_goal(self, goal: Goal) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO goals (id, title, category, target_date, progress_pct, status, risk_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                goal.id,
                goal.title,
                goal.category,
                goal.target_date,
                goal.progress_pct,
                goal.status.value,
                goal.risk_reason,
            ))
            for m in goal.milestones:
                cur.execute("""
                    INSERT OR REPLACE INTO milestones (id, goal_id, title, deadline, completed)
                    VALUES (?, ?, ?, ?, ?)
                """, (m.id, goal.id, m.title, m.deadline, 1 if m.completed else 0))
            conn.commit()

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, title, category, target_date, progress_pct, status, risk_reason FROM goals WHERE id = ?", (goal_id,))
            row = cur.fetchone()
            if not row:
                return None
            cur.execute("SELECT id, title, deadline, completed FROM milestones WHERE goal_id = ?", (goal_id,))
            milestones = [Milestone(id=m[0], title=m[1], deadline=m[2], completed=bool(m[3])) for m in cur.fetchall()]
            return Goal(
                id=row[0],
                title=row[1],
                category=row[2],
                target_date=row[3],
                progress_pct=row[4],
                status=GoalStatus(row[5]),
                risk_reason=row[6],
                milestones=milestones,
            )

    def list_goals(self) -> List[Goal]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM goals")
            return [self.get_goal(r[0]) for r in cur.fetchall() if self.get_goal(r[0])]

    def save_topic_mastery(self, topic: TopicMastery) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO topics (subject, unit, topic, mastery_score, last_revision_days_ago, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                topic.subject,
                topic.unit,
                topic.topic,
                topic.mastery_score,
                topic.last_revision_days_ago,
                topic.confidence,
            ))
            for ev in topic.evidence:
                cur.execute("""
                    INSERT INTO evidence (subject, topic, type, description, weight, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (topic.subject, topic.topic, ev.type, ev.description, ev.weight, ev.timestamp))
            conn.commit()

    def list_topics(self, subject: Optional[str] = None) -> List[TopicMastery]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            if subject:
                cur.execute("SELECT subject, unit, topic, mastery_score, last_revision_days_ago, confidence FROM topics WHERE subject = ?", (subject,))
            else:
                cur.execute("SELECT subject, unit, topic, mastery_score, last_revision_days_ago, confidence FROM topics")
            rows = cur.fetchall()
            results = []
            for r in rows:
                cur.execute("SELECT type, description, weight, timestamp FROM evidence WHERE subject = ? AND topic = ?", (r[0], r[2]))
                ev_list = [Evidence(type=e[0], description=e[1], weight=e[2], timestamp=e[3]) for e in cur.fetchall()]
                results.append(TopicMastery(
                    subject=r[0],
                    unit=r[1],
                    topic=r[2],
                    mastery_score=r[3],
                    last_revision_days_ago=r[4],
                    confidence=r[5],
                    evidence=ev_list,
                ))
            return results

    def save_habit(self, log: HabitLog) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO habits (date, habit, duration_hours, category)
                VALUES (?, ?, ?, ?)
            """, (log.date, log.habit, log.duration_hours, log.category))
            conn.commit()

    def list_habits(self, limit: int = 30) -> List[HabitLog]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT date, habit, duration_hours, category FROM habits ORDER BY id DESC LIMIT ?", (limit,))
            return [HabitLog(date=r[0], habit=r[1], duration_hours=r[2], category=r[3]) for r in cur.fetchall()]

    def save_daily_priorities(self, priorities: List[DailyPriority], date_str: str) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            for p in priorities:
                cur.execute("""
                    INSERT INTO priorities (date, task, score, breakdown_json, explanation, mission_goal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (date_str, p.task, p.score, json.dumps(p.breakdown), p.explanation, p.generated_mission_goal))
            conn.commit()
