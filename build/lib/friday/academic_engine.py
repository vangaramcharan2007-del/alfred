"""
Friday Academic Engine — 10 CGPA Goal Optimizer.
Tracks subjects, credits, syllabus, assignments, attendance, exam dates, revision history.
Generates daily morning study directives and manages 1-click study sessions.
"""
from __future__ import annotations
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from friday.persistence import FridayPersistenceManager


class FridayAcademicEngine:
    """
    Core 10 CGPA Optimizer and Academic Manager for Friday.
    """

    def __init__(self, persistence: Optional[FridayPersistenceManager] = None):
        self.persistence = persistence or FridayPersistenceManager()
        self.db_path = Path("var/db/friday_academics.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    current_grade_pct REAL NOT NULL,
                    syllabus_covered_pct REAL NOT NULL,
                    attendance_pct REAL NOT NULL,
                    next_exam_date TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS study_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_code TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    notes TEXT
                )
            """)

            # Seed default courses if empty
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM subjects")
            if cur.fetchone()[0] == 0:
                defaults = [
                    ("CS301", "Operating Systems", 4, 91.5, 58.0, 94.0, "2026-08-25"),
                    ("CS302", "Advanced Algorithms", 4, 94.0, 65.0, 96.0, "2026-08-28"),
                    ("MA301", "Linear Algebra & Applications", 3, 88.0, 50.0, 90.0, "2026-08-20"),
                    ("CS304", "Database Systems", 3, 95.0, 75.0, 98.0, "2026-09-02"),
                ]
                conn.executemany(
                    "INSERT INTO subjects (code, name, credits, current_grade_pct, syllabus_covered_pct, attendance_pct, next_exam_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    defaults
                )
            conn.commit()

    def calculate_10_cgpa_strategy(self) -> Dict[str, Any]:
        """
        Calculates high-impact study recommendation prioritized by:
        Impact Score = Credits * (100 - syllabus_covered_pct) * (100 - current_grade_pct)
        """
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM subjects").fetchall()

        ranked = []
        for r in rows:
            credits = r["credits"]
            syll = r["syllabus_covered_pct"]
            grade = r["current_grade_pct"]

            # Higher impact for higher credit courses with low syllabus coverage or current grade
            gap = max(1.0, 100.0 - grade)
            uncovered = max(1.0, 100.0 - syll)
            impact_score = round(credits * (uncovered / 10.0) * (gap / 10.0), 2)

            ranked.append({
                "code": r["code"],
                "name": r["name"],
                "credits": credits,
                "current_grade": grade,
                "syllabus_covered": syll,
                "attendance": r["attendance_pct"],
                "next_exam": r["next_exam_date"],
                "impact_score": impact_score
            })

        ranked.sort(key=lambda x: x["impact_score"], reverse=True)
        top_focus = ranked[0] if ranked else None

        rec_minutes = 90 if top_focus and top_focus["credits"] >= 4 else 60
        why_text = f"Highest 10 CGPA impact opportunity ({top_focus['credits']} credits, {top_focus['current_grade']}% current score, next exam on {top_focus['next_exam']})." if top_focus else "Regular revision."

        return {
            "target_cgpa": 10.0,
            "top_focus": top_focus,
            "recommended_duration_minutes": rec_minutes,
            "why": why_text,
            "all_ranked_subjects": ranked
        }

    def generate_morning_academic_directive(self) -> Dict[str, Any]:
        strat = self.calculate_10_cgpa_strategy()
        tf = strat["top_focus"]
        assignments = self.persistence.get_assignments()

        directive_text = (
            f"Good morning Ramcharan. Here is your 10 CGPA Academic Directive:\n\n"
            f"[PRIMARY REVISION FOCUS]\n"
            f"  - Subject           : {tf['name']} ({tf['code']})\n"
            f"  - Recommended Time  : {strat['recommended_duration_minutes']} minutes\n"
            f"  - Strategic Reason  : {strat['why']}\n\n"
            f"[ACADEMIC HEALTH]\n"
            f"  - Current Score     : {tf['current_grade']}%\n"
            f"  - Syllabus Covered  : {tf['syllabus_covered']}%\n"
            f"  - Attendance        : {tf['attendance']}%\n"
            f"  - Next Exam Date    : {tf['next_exam']}\n"
            f"  - Pending Assignments: {len(assignments)} items\n"
        )
        return {
            "status": "SUCCESS",
            "subject": tf["name"],
            "duration_minutes": strat["recommended_duration_minutes"],
            "why": strat["why"],
            "directive_text": directive_text
        }
