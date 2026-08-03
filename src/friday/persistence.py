from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

class FridayPersistenceManager:
    """
    SQLite persistence for Friday personal assistant: schedules, 10 CGPA plans, assignments, habits, health, notes & goals.
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "var/db/friday.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

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
                    current_score REAL DEFAULT 0.0
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
                    type TEXT NOT NULL, -- 'note' or 'goal'
                    content TEXT NOT NULL,
                    target_date TEXT
                )
            """)

            # Seed default 10 CGPA plan & schedule if empty
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM schedule")
            if cur.fetchone()[0] == 0:
                conn.executemany("INSERT INTO schedule (time_slot, activity, category) VALUES (?, ?, ?)", [
                    ("09:00 AM - 10:30 AM", "Advanced Algorithms & Data Structures", "class"),
                    ("11:00 AM - 12:30 PM", "Software Engineering Architecture", "class"),
                    ("02:00 PM - 04:00 PM", "Deep Learning & AI Research Lab", "study"),
                    ("05:00 PM - 06:30 PM", "Jarvis X & System Programming", "project"),
                    ("08:00 PM - 09:30 PM", "10 CGPA Revision & Assignment Review", "academic")
                ])
                conn.executemany("INSERT INTO cgpa_plan (subject, target_grade, credits, current_score) VALUES (?, ?, ?, ?)", [
                    ("Data Structures & Algorithms", "O (10.0)", 4, 95.0),
                    ("Software Engineering", "O (10.0)", 3, 94.0),
                    ("Machine Learning", "O (10.0)", 4, 96.0),
                    ("Operating Systems", "O (10.0)", 3, 92.0)
                ])
                conn.executemany("INSERT INTO assignments (title, subject, due_date, status) VALUES (?, ?, ?, ?)", [
                    ("Algorithm Complexity Analysis Report", "Data Structures & Algorithms", "Tomorrow", "IN_PROGRESS"),
                    ("Software Design Patterns Implementation", "Software Engineering", "In 3 Days", "PENDING")
                ])
                conn.executemany("INSERT INTO habits (habit_name, streak_count, last_completed) VALUES (?, ?, ?)", [
                    ("Daily Coding / System Architecture", 14, "Today"),
                    ("10 CGPA Revision (2 hrs)", 10, "Today"),
                    ("Hydration & Fitness Break", 8, "Today")
                ])
                conn.executemany("INSERT INTO notes_goals (type, content, target_date) VALUES (?, ?, ?)", [
                    ("goal", "Achieve 10 CGPA in current semester", "Semester End"),
                    ("goal", "Build Jarvis X & Friday into production-ready daily assistants", "Q3 2026"),
                    ("note", "Focus on clean architecture and evidence-based performance", "Ongoing")
                ])
            conn.commit()

    def get_schedule(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM schedule ORDER BY id").fetchall()
            return [dict(r) for r in rows]

    def get_cgpa_plan(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM cgpa_plan ORDER BY id").fetchall()
            return [dict(r) for r in rows]

    def get_assignments(self) -> List[Dict[str, Any]]:

        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM assignments ORDER BY id").fetchall()
            return [dict(r) for r in rows]

    def get_habits(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM habits ORDER BY id").fetchall()
            return [dict(r) for r in rows]

    def get_notes_and_goals(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM notes_goals ORDER BY id").fetchall()
            return [dict(r) for r in rows]

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

