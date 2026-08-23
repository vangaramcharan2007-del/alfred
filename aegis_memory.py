"""
AEGIS Memory Core - Persistent Encapsulated SQLite Database Layer with Clinical EHR
Stores physiological vital logs, Eye Aspect Ratio (EAR) fatigue events,
conversation context, multi-patient EHR profiles, and Store-and-Forward FHIR Sync Queue.
"""

import sqlite3
import json
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone


class AegisMemory:
    """
    Encapsulated Persistent Memory Layer for AEGIS.
    Tracks vitals, optical rPPG signals, conversational context,
    multi-patient EHR records, and offline Store-and-Forward hospital sync queues in SQLite.
    """

    def __init__(self, db_path: str = "aegis_core.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_tables()
        self._initialize_default_profiles()

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
                location TEXT DEFAULT 'Village PHC Unit 1',
                emergency_contact TEXT DEFAULT 'Dr. Callaghan',
                is_active BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Migration safety for existing SQLite DB files
        try:
            self.cursor.execute("ALTER TABLE patient_profile ADD COLUMN location TEXT DEFAULT 'Village PHC Unit 1';")
        except Exception:
            pass
        try:
            self.cursor.execute("ALTER TABLE patient_profile ADD COLUMN is_active BOOLEAN DEFAULT 0;")
        except Exception:
            pass

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS allergy_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                allergen TEXT NOT NULL,
                reaction_type TEXT DEFAULT 'Severe Hypersensitivity / Anaphylaxis',
                severity TEXT DEFAULT 'HIGH RISK'
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fhir_sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_uid TEXT NOT NULL,
                bundle_id TEXT NOT NULL,
                bundle_type TEXT DEFAULT 'document',
                payload_json TEXT NOT NULL,
                status TEXT DEFAULT 'QUEUED_OFFLINE',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced_at DATETIME
            );
        """)
        self.conn.commit()

    def _initialize_default_profiles(self) -> None:
        """Seed default hospital & village patient profiles on startup."""
        patients = [
            (
                'PAT-RAM-2026', 'Ramcharan', 24, 'Male', 'O+',
                'Ibuprofen, NSAIDs', 'None', 'Mild Asthmatic Tendency',
                'District General Clinic - Bed 01', 'Dr. Callaghan', 1
            ),
            (
                'PAT-SOM-102', 'Somu', 48, 'Male', 'B+',
                'Penicillin, Amoxicillin', 'Amlodipine 5mg', 'Hypertension, Acute Febrile Onset',
                'Warangal Rural PHC Sub-Centre', 'Dr. Rao', 0
            ),
            (
                'PAT-GIR-304', 'Giri', 22, 'Female', 'A+',
                'Sulfa Drugs', 'Ferrous Sulfate', 'Dysmenorrhea, Mild Anemia',
                'Karimnagar Mobile Health Camp', 'Nurse Anitha', 0
            )
        ]

        for p in patients:
            self.cursor.execute("""
                INSERT OR IGNORE INTO patient_profile (
                    patient_uid, name, age, gender, blood_type,
                    allergies, active_medications, chronic_conditions,
                    location, emergency_contact, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, p)

        # Seed initial pending FHIR bundles in sync queue
        self.cursor.execute("SELECT COUNT(*) FROM fhir_sync_queue;")
        if self.cursor.fetchone()[0] == 0:
            demo_bundles = [
                ("PAT-RAM-2026", "BUNDLE-FHIR-RAM-01", json.dumps({"resourceType": "Bundle", "type": "document", "total": 7, "patient": "Ramcharan"})),
                ("PAT-SOM-102", "BUNDLE-FHIR-SOM-02", json.dumps({"resourceType": "Bundle", "type": "document", "total": 5, "patient": "Somu", "condition": "Fever"}))
            ]
            for uid, bid, p_json in demo_bundles:
                self.cursor.execute("""
                    INSERT INTO fhir_sync_queue (patient_uid, bundle_id, payload_json, status)
                    VALUES (?, ?, ?, 'QUEUED_OFFLINE');
                """, (uid, bid, p_json))

        self.conn.commit()

    def list_all_patients(self) -> List[Dict[str, Any]]:
        """Retrieve all registered patients in the offline clinic."""
        self.cursor.execute("""
            SELECT patient_uid, name, age, gender, blood_type, allergies,
                   active_medications, chronic_conditions, location, is_active
            FROM patient_profile
            ORDER BY id ASC;
        """)
        rows = self.cursor.fetchall()
        return [
            {
                "patient_uid": r[0],
                "name": r[1],
                "age": r[2],
                "gender": r[3],
                "blood_type": r[4],
                "allergies": r[5],
                "active_medications": r[6],
                "chronic_conditions": r[7],
                "location": r[8],
                "is_active": bool(r[9])
            }
            for r in rows
        ]

    def set_active_patient(self, patient_uid: str) -> Dict[str, Any]:
        """Switch the current active patient in the examination workstation."""
        self.cursor.execute("UPDATE patient_profile SET is_active = 0;")
        self.cursor.execute("UPDATE patient_profile SET is_active = 1 WHERE patient_uid = ?;", (patient_uid,))
        self.conn.commit()
        return self.get_patient_profile(patient_uid)

    def get_patient_profile(self, patient_uid: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve patient EHR profile."""
        if patient_uid:
            self.cursor.execute("""
                SELECT patient_uid, name, age, gender, blood_type,
                       allergies, active_medications, chronic_conditions, emergency_contact, location
                FROM patient_profile WHERE patient_uid = ?;
            """, (patient_uid,))
        else:
            self.cursor.execute("""
                SELECT patient_uid, name, age, gender, blood_type,
                       allergies, active_medications, chronic_conditions, emergency_contact, location
                FROM patient_profile WHERE is_active = 1 LIMIT 1;
            """)
        
        row = self.cursor.fetchone()
        if not row:
            self.cursor.execute("""
                SELECT patient_uid, name, age, gender, blood_type,
                       allergies, active_medications, chronic_conditions, emergency_contact, location
                FROM patient_profile LIMIT 1;
            """)
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
                "emergency_contact": "Dr. Callaghan",
                "location": "District General Clinic"
            }

        allergies_str = row[5] or ""
        allergies_list = [a.strip().lower() for a in allergies_str.split(",") if a.strip()]

        return {
            "patient_uid": row[0],
            "name": row[1],
            "age": row[2],
            "gender": row[3],
            "blood_type": row[4],
            "allergies": allergies_str,
            "allergies_list": allergies_list,
            "active_medications": row[6] or "None",
            "chronic_conditions": row[7] or "None",
            "emergency_contact": row[8] or "Dr. Callaghan",
            "location": row[9] or "Village PHC"
        }

    def update_patient_profile(
        self,
        name: Optional[str] = None,
        age: Optional[int] = None,
        allergies: Optional[str] = None,
        active_medications: Optional[str] = None,
        chronic_conditions: Optional[str] = None,
        patient_uid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update fields in the active patient profile."""
        current = self.get_patient_profile(patient_uid)
        target_uid = current["patient_uid"]

        new_name = name if name is not None else current["name"]
        new_age = age if age is not None else current["age"]
        new_allergies = allergies if allergies is not None else current["allergies"]
        new_meds = active_medications if active_medications is not None else current["active_medications"]
        new_conditions = chronic_conditions if chronic_conditions is not None else current["chronic_conditions"]

        self.cursor.execute("""
            UPDATE patient_profile
            SET name = ?, age = ?, allergies = ?, active_medications = ?, chronic_conditions = ?, updated_at = CURRENT_TIMESTAMP
            WHERE patient_uid = ?;
        """, (new_name, new_age, new_allergies, new_meds, new_conditions, target_uid))
        self.conn.commit()

        return self.get_patient_profile(target_uid)

    def queue_fhir_bundle(self, patient_uid: str, bundle_dict: Dict[str, Any]) -> str:
        """Queue an HL7/FHIR v4.0.1 Document Bundle into local store-and-forward queue."""
        bundle_id = bundle_dict.get("id", f"BUNDLE-{int(datetime.now(timezone.utc).timestamp())}")
        payload_json = json.dumps(bundle_dict)
        self.cursor.execute("""
            INSERT INTO fhir_sync_queue (patient_uid, bundle_id, payload_json, status)
            VALUES (?, ?, ?, 'QUEUED_OFFLINE');
        """, (patient_uid, bundle_id, payload_json))
        self.conn.commit()
        return bundle_id

    def get_sync_queue_status(self) -> Dict[str, Any]:
        """Retrieve offline Store-and-Forward sync queue statistics."""
        self.cursor.execute("SELECT COUNT(*) FROM fhir_sync_queue WHERE status = 'QUEUED_OFFLINE';")
        pending_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM fhir_sync_queue WHERE status = 'SYNCED_TO_DISTRICT_HOSPITAL';")
        synced_count = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT id, patient_uid, bundle_id, status, created_at, synced_at
            FROM fhir_sync_queue
            ORDER BY id DESC LIMIT 10;
        """)
        rows = self.cursor.fetchall()
        recent_records = [
            {
                "id": r[0],
                "patient_uid": r[1],
                "bundle_id": r[2],
                "status": r[3],
                "created_at": r[4],
                "synced_at": r[5]
            }
            for r in rows
        ]

        return {
            "pending_offline_count": pending_count,
            "synced_hospital_count": synced_count,
            "total_bundles": pending_count + synced_count,
            "sync_mode": "OFFLINE_STORE_AND_FORWARD",
            "recent_bundles": recent_records
        }

    def trigger_sync_batch(self) -> Dict[str, Any]:
        """Simulate opportunistic delta sync to district hospital / ABDM gateway."""
        now_iso = datetime.now(timezone.utc).isoformat()
        self.cursor.execute("""
            UPDATE fhir_sync_queue
            SET status = 'SYNCED_TO_DISTRICT_HOSPITAL', synced_at = ?
            WHERE status = 'QUEUED_OFFLINE';
        """, (now_iso,))
        synced_count = self.cursor.rowcount
        self.conn.commit()
        return {
            "status": "success",
            "synced_bundles_count": synced_count,
            "sync_target": "District Hospital Central EHR / ABDM Gateway",
            "timestamp": now_iso
        }

    def insert_vital(
        self,
        heart_rate: float,
        eye_aspect_ratio: float,
        fatigue_flag: bool,
        rppg_signal: float = 0.0
    ) -> int:
        """Insert a vital sample into vitals_log."""
        self.cursor.execute("""
            INSERT INTO vitals_log (heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal)
            VALUES (?, ?, ?, ?);
        """, (heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_latest_vital(self) -> Optional[Dict[str, Any]]:
        """Fetch the most recent vital record."""
        self.cursor.execute("""
            SELECT heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal, timestamp
            FROM vitals_log
            ORDER BY id DESC LIMIT 1;
        """)
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "heart_rate": row[0],
            "eye_aspect_ratio": row[1],
            "fatigue_flag": bool(r[2]),
            "rppg_signal": row[3],
            "timestamp": row[4]
        }

    def get_recent_baseline(self, limit: int = 20) -> List[Tuple[float, float, bool, float]]:
        """Fetch recent records for rolling baseline averages."""
        self.cursor.execute("""
            SELECT heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal
            FROM vitals_log
            ORDER BY id DESC LIMIT ?;
        """, (limit,))
        return self.cursor.fetchall()

    def add_conversation(self, role: str, content: str) -> None:
        """Record conversation turn."""
        self.cursor.execute("""
            INSERT INTO memory_context (role, content)
            VALUES (?, ?);
        """, (role, content))
        self.conn.commit()

    def get_conversation_context(self, limit: int = 10) -> List[Dict[str, str]]:
        """Fetch recent conversation turns."""
        self.cursor.execute("""
            SELECT role, content FROM memory_context
            ORDER BY id DESC LIMIT ?;
        """, (limit,))
        rows = self.cursor.fetchall()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def clear_memory(self) -> None:
        """Clear vitals_log and memory_context."""
        self.cursor.execute("DELETE FROM vitals_log;")
        self.cursor.execute("DELETE FROM memory_context;")
        self.conn.commit()

    def close(self) -> None:
        """Close connection cleanly."""
        try:
            self.conn.close()
        except Exception:
            pass
