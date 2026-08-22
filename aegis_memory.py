"""
AEGIS Memory Core - Persistent Encapsulated SQLite Database Layer with Clinical EHR
Stores physiological vital logs, Eye Aspect Ratio (EAR) fatigue events,
conversation context, and full Electronic Health Record (EHR) Patient Profiles.
"""

import sqlite3
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone


class AegisMemory:
    """
    Encapsulated Persistent Memory Layer for AEGIS.
    Tracks vitals, optical rPPG signals, conversational context,
    and clinical patient EHR records in SQLite.
    """

    def __init__(self, db_path: str = "aegis_core.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_tables()
        self._initialize_default_profile()

    def _initialize_tables(self) -> None:
        """Initialize database schema with WAL mode for fast concurrent operations."""
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vitals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                heart_rate REAL,
                eye_aspect_ratio REAL,
                fatigue_flag BOOLEAN,
                rppg_signal REAL DEFAULT 0.0
            );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT,
                content TEXT
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_uid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                age INTEGER DEFAULT 24,
                gender TEXT DEFAULT 'Male',
                blood_type TEXT DEFAULT 'O+',
                allergies TEXT DEFAULT 'Ibuprofen, NSAIDs',
                active_medications TEXT DEFAULT 'None',
                chronic_conditions TEXT DEFAULT 'Mild Asthmatic Tendency',
                emergency_contact TEXT DEFAULT 'Dr. Callaghan',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS allergy_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                allergen TEXT NOT NULL,
                reaction_type TEXT DEFAULT 'Severe Hypersensitivity / Anaphylaxis',
                severity TEXT DEFAULT 'HIGH RISK'
            );
        """)
        self.conn.commit()

    def _initialize_default_profile(self) -> None:
        """Ensure default EHR patient record exists on startup."""
        self.cursor.execute("SELECT COUNT(*) FROM patient_profile WHERE patient_uid = 'PAT-RAM-2026';")
        count = self.cursor.fetchone()[0]
        if count == 0:
            self.cursor.execute("""
                INSERT INTO patient_profile (
                    patient_uid, name, age, gender, blood_type,
                    allergies, active_medications, chronic_conditions, emergency_contact
                ) VALUES (
                    'PAT-RAM-2026', 'Ramcharan', 24, 'Male', 'O+',
                    'Ibuprofen, NSAIDs', 'None', 'Mild Asthmatic Tendency', 'Dr. Callaghan'
                );
            """)

            # Seed documented allergy records
            self.cursor.execute("""
                INSERT OR IGNORE INTO allergy_records (allergen, reaction_type, severity)
                VALUES 
                ('Ibuprofen', 'Severe Hypersensitivity / Bronchospasm', 'HIGH RISK'),
                ('NSAIDs', 'Cross-reactive Platelet & Bronchial Spasm', 'HIGH RISK'),
                ('Aspirin', 'Respiratory / Urticarial Reaction', 'HIGH RISK');
            """)
            self.conn.commit()

    def get_patient_profile(self, patient_uid: str = "PAT-RAM-2026") -> Dict[str, Any]:
        """
        Retrieve patient's full Electronic Health Record (EHR).
        """
        self.cursor.execute("""
            SELECT patient_uid, name, age, gender, blood_type,
                   allergies, active_medications, chronic_conditions, emergency_contact
            FROM patient_profile
            WHERE patient_uid = ?
            LIMIT 1;
        """, (patient_uid,))
        row = self.cursor.fetchone()
        if not row:
            return {
                "patient_uid": "PAT-RAM-2026",
                "name": "Ramcharan",
                "age": 24,
                "gender": "Male",
                "blood_type": "O+",
                "allergies": "Ibuprofen, NSAIDs",
                "allergies_list": ["ibuprofen", "nsaids", "aspirin"],
                "active_medications": "None",
                "chronic_conditions": "Mild Asthmatic Tendency",
                "emergency_contact": "Dr. Callaghan"
            }

        allergies_str = row[5] or ""
        allergies_list = [a.strip().lower() for a in allergies_str.split(",") if a.strip()]

        return {
            "patient_uid": row[0],
            "name": row[1],
            "age": int(row[2]),
            "gender": row[3],
            "blood_type": row[4],
            "allergies": allergies_str,
            "allergies_list": allergies_list,
            "active_medications": row[6] or "None",
            "chronic_conditions": row[7] or "None",
            "emergency_contact": row[8] or "None"
        }

    def update_patient_profile(
        self,
        name: Optional[str] = None,
        age: Optional[int] = None,
        allergies: Optional[str] = None,
        active_medications: Optional[str] = None,
        chronic_conditions: Optional[str] = None,
        patient_uid: str = "PAT-RAM-2026"
    ) -> Dict[str, Any]:
        """
        Update fields in patient's EHR profile.
        """
        current = self.get_patient_profile(patient_uid)
        new_name = name if name is not None else current["name"]
        new_age = age if age is not None else current["age"]
        new_allergies = allergies if allergies is not None else current["allergies"]
        new_meds = active_medications if active_medications is not None else current["active_medications"]
        new_conditions = chronic_conditions if chronic_conditions is not None else current["chronic_conditions"]

        self.cursor.execute("""
            UPDATE patient_profile
            SET name = ?, age = ?, allergies = ?, active_medications = ?,
                chronic_conditions = ?, updated_at = CURRENT_TIMESTAMP
            WHERE patient_uid = ?;
        """, (new_name, new_age, new_allergies, new_meds, new_conditions, patient_uid))
        self.conn.commit()
        return self.get_patient_profile(patient_uid)

    def log_vitals(
        self,
        hr: float,
        ear: float,
        is_fatigued: bool,
        rppg_signal: float = 0.0
    ) -> int:
        """Log an instantaneous biometric snapshot into persistent storage."""
        self.cursor.execute(
            """
            INSERT INTO vitals_log (heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal)
            VALUES (?, ?, ?, ?)
            """,
            (float(hr), float(ear), int(is_fatigued), float(rppg_signal))
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_recent_baseline(self, limit: int = 50) -> List[Tuple[float, float, int, float]]:
        """Fetch recent vital snapshots to calculate rolling averages."""
        self.cursor.execute(
            """
            SELECT heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal
            FROM vitals_log
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        return self.cursor.fetchall()

    def get_latest_vital(self) -> Optional[Dict[str, Any]]:
        """Retrieve the single most recent vital log entry."""
        self.cursor.execute(
            """
            SELECT timestamp, heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal
            FROM vitals_log
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "timestamp": row[0],
            "heart_rate": float(row[1]),
            "eye_aspect_ratio": float(row[2]),
            "fatigue_flag": bool(row[3]),
            "rppg_signal": float(row[4])
        }

    def add_conversation(self, role: str, content: str) -> None:
        """Append a conversational turn into persistent memory context."""
        self.cursor.execute(
            "INSERT INTO memory_context (role, content) VALUES (?, ?)",
            (role, content)
        )
        self.conn.commit()

    def get_conversation_context(self, limit: int = 10) -> List[Dict[str, str]]:
        """Fetch the most recent dialogue context formatted for LLM prompts."""
        self.cursor.execute(
            """
            SELECT role, content
            FROM memory_context
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = self.cursor.fetchall()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def clear_memory(self) -> None:
        """Clear logs (used for testing)."""
        self.cursor.execute("DELETE FROM vitals_log;")
        self.cursor.execute("DELETE FROM memory_context;")
        self.conn.commit()

    def close(self) -> None:
        """Close SQLite connection."""
        self.conn.close()
