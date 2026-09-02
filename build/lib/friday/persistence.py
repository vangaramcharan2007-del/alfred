from __future__ import annotations
import sqlite3
import time
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional


class FridayPersistenceManager:
    """
    SQLite persistence for Friday: schedules, CGPA, assignments, habits,
    attendance, study sessions, time savings, and knowledge base.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "var/db/friday.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time_slot TEXT NOT NULL,
                    activity TEXT NOT NULL,
                    category TEXT DEFAULT 'class'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cgpa_plan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    target_grade TEXT NOT NULL,
                    credits INTEGER DEFAULT 3,
                    current_score REAL DEFAULT 0.0,
                    syllabus_pct REAL DEFAULT 0.0,
                    attendance_pct REAL DEFAULT 100.0,
                    classes_attended INTEGER DEFAULT 0,
                    classes_total INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_name TEXT NOT NULL,
                    streak_count INTEGER DEFAULT 0,
                    last_completed TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    target_date TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    minutes INTEGER NOT NULL,
                    date TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS time_savings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    minutes_saved REAL NOT NULL,
                    date TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Seed defaults if empty
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM schedule")
            if cur.fetchone()[0] == 0:
                self._seed_defaults(conn)
            conn.commit()

    def _seed_defaults(self, conn: sqlite3.Connection):
        conn.executemany(
            "INSERT INTO schedule (time_slot, activity, category) VALUES (?, ?, ?)",
            [
                ("09:00 AM - 10:30 AM", "Advanced Algorithms & Data Structures", "class"),
                ("11:00 AM - 12:30 PM", "Software Engineering Architecture", "class"),
                ("02:00 PM - 04:00 PM", "Deep Learning & AI Research Lab", "study"),
                ("05:00 PM - 06:30 PM", "Jarvis X & System Programming", "project"),
                ("08:00 PM - 09:30 PM", "10 CGPA Revision & Assignment Review", "academic"),
            ],
        )
        conn.executemany(
            "INSERT INTO cgpa_plan (subject, target_grade, credits, current_score, syllabus_pct, attendance_pct, classes_attended, classes_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("Data Structures & Algorithms", "O (10.0)", 4, 95.0, 72.0, 94.0, 47, 50),
                ("Software Engineering", "O (10.0)", 3, 94.0, 65.0, 92.0, 46, 50),
                ("Machine Learning", "O (10.0)", 4, 96.0, 80.0, 96.0, 48, 50),
                ("Operating Systems", "O (10.0)", 3, 92.0, 58.0, 90.0, 45, 50),
            ],
        )
        conn.executemany(
            "INSERT INTO assignments (title, subject, due_date, status) VALUES (?, ?, ?, ?)",
            [
                ("Algorithm Complexity Analysis Report", "Data Structures & Algorithms", "Tomorrow", "IN_PROGRESS"),
                ("Software Design Patterns Implementation", "Software Engineering", "In 3 Days", "PENDING"),
            ],
        )
        conn.executemany(
            "INSERT INTO habits (habit_name, streak_count, last_completed) VALUES (?, ?, ?)",
            [
                ("Daily Coding / System Architecture", 14, "Today"),
                ("10 CGPA Revision (2 hrs)", 10, "Today"),
                ("Hydration & Fitness Break", 8, "Today"),
            ],
        )
        conn.executemany(
            "INSERT INTO notes_goals (type, content, target_date) VALUES (?, ?, ?)",
            [
                ("goal", "Achieve 10 CGPA in current semester", "Semester End"),
                ("goal", "Build Jarvis X & Friday into production-ready daily assistants", "Q3 2026"),
                ("note", "Focus on clean architecture and evidence-based performance", "Ongoing"),
            ],
        )
        conn.executemany(
            "INSERT INTO study_sessions (subject, minutes, date) VALUES (?, ?, ?)",
            [
                ("Data Structures & Algorithms", 90, str(date.today())),
                ("Machine Learning", 45, str(date.today())),
            ],
        )
        conn.executemany(
            "INSERT INTO time_savings (action, minutes_saved, date) VALUES (?, ?, ?)",
            [
                ("Alfred workspace restore", 8.0, str(date.today())),
                ("Alfred fix-this workflow", 12.0, str(date.today())),
                ("Friday daily briefing", 5.0, str(date.today())),
            ],
        )

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------
    def get_schedule(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM schedule ORDER BY id").fetchall()]

    def get_cgpa_plan(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM cgpa_plan ORDER BY id").fetchall()]

    def get_assignments(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM assignments ORDER BY id").fetchall()]

    def get_habits(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM habits ORDER BY id").fetchall()]

    def get_notes_and_goals(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM notes_goals ORDER BY id").fetchall()]

    def get_study_sessions(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        d = target_date or str(date.today())
        with self._get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM study_sessions WHERE date = ? ORDER BY id", (d,)).fetchall()]

    def get_study_minutes_today(self) -> int:
        sessions = self.get_study_sessions()
        return sum(s["minutes"] for s in sessions)

    def get_time_savings_today(self) -> float:
        d = str(date.today())
        with self._get_connection() as conn:
            row = conn.execute("SELECT COALESCE(SUM(minutes_saved), 0) as total FROM time_savings WHERE date = ?", (d,)).fetchone()
            return float(row["total"])

    def get_time_savings_week(self) -> float:
        with self._get_connection() as conn:
            row = conn.execute("SELECT COALESCE(SUM(minutes_saved), 0) as total FROM time_savings WHERE date >= date('now', '-7 days')").fetchone()
            return float(row["total"])

    def get_time_savings_semester(self) -> float:
        with self._get_connection() as conn:
            row = conn.execute("SELECT COALESCE(SUM(minutes_saved), 0) as total FROM time_savings").fetchone()
            return float(row["total"])

    def get_knowledge_base(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if category:
                return [dict(r) for r in conn.execute("SELECT * FROM knowledge_base WHERE category = ? ORDER BY id DESC", (category,)).fetchall()]
            return [dict(r) for r in conn.execute("SELECT * FROM knowledge_base ORDER BY id DESC LIMIT 20").fetchall()]

    # ------------------------------------------------------------------
    # Writers
    # ------------------------------------------------------------------
    def add_assignment(self, title: str, subject: str, due_date: str, status: str = "PENDING") -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.execute("INSERT INTO assignments (title, subject, due_date, status) VALUES (?, ?, ?, ?)", (title, subject, due_date, status))
            conn.commit()
        return {"status": "SUCCESS", "title": title, "due_date": due_date}

    def add_schedule_event(self, time_slot: str, activity: str, category: str = "class") -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.execute("INSERT INTO schedule (time_slot, activity, category) VALUES (?, ?, ?)", (time_slot, activity, category))
            conn.commit()
        return {"status": "SUCCESS", "time_slot": time_slot, "activity": activity}

    def update_habit(self, habit_name: str, last_completed: str = "Today") -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.execute("UPDATE habits SET streak_count = streak_count + 1, last_completed = ? WHERE habit_name = ?", (last_completed, habit_name))
            conn.commit()
        return {"status": "SUCCESS", "habit_name": habit_name}

    def add_note_or_goal(self, item_type: str, content: str, target_date: Optional[str] = None) -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.execute("INSERT INTO notes_goals (type, content, target_date) VALUES (?, ?, ?)", (item_type, content, target_date or ""))
            conn.commit()
        return {"status": "SUCCESS", "type": item_type, "content": content}

    def log_study_session(self, subject: str, minutes: int) -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.execute("INSERT INTO study_sessions (subject, minutes, date) VALUES (?, ?, ?)", (subject, minutes, str(date.today())))
            conn.commit()
        return {"status": "SUCCESS", "subject": subject, "minutes": minutes}

    def log_time_saved(self, action: str, minutes_saved: float) -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.execute("INSERT INTO time_savings (action, minutes_saved, date) VALUES (?, ?, ?)", (action, minutes_saved, str(date.today())))
            conn.commit()
        return {"status": "SUCCESS", "action": action, "minutes_saved": minutes_saved}

    def add_knowledge(self, category: str, title: str, content: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.execute("INSERT INTO knowledge_base (category, title, content, created_at) VALUES (?, ?, ?, ?)",
                         (category, title, content, datetime.now().isoformat()))
            conn.commit()
        return {"status": "SUCCESS", "category": category, "title": title}
