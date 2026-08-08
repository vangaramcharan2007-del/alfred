"""Proactive Memory & SQLite Persistent Store with Schema Versioning for Phase 95."""

from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.proactive.models import (
    InitiativeDecision,
    InitiativeType,
    RiskSignal,
    SignalType,
    TrajectoryForecast,
)


class ProactiveMemory:
    """Dedicated persistent SQLite store for events, risk signals, predictions, and initiatives."""

    def __init__(self, db_path: str = "var/db/proactive.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_meta (
                    version TEXT PRIMARY KEY,
                    upgraded_at REAL
                )
            """)
            cur.execute("INSERT OR IGNORE INTO schema_meta (version, upgraded_at) VALUES ('v1.0', ?)", (time.time(),))

            cur.execute("""
                CREATE TABLE IF NOT EXISTS life_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT,
                    payload_json TEXT,
                    timestamp REAL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS risk_signals (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    source TEXT,
                    severity REAL,
                    confidence REAL,
                    reason_json TEXT,
                    timestamp REAL,
                    is_suppressed INTEGER
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT,
                    current_mastery REAL,
                    days_to_target INTEGER,
                    forecast_score REAL,
                    required_hours REAL,
                    cgpa_impact REAL,
                    timestamp REAL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS initiatives (
                    id TEXT PRIMARY KEY,
                    action_type TEXT,
                    title TEXT,
                    target_subject TEXT,
                    mission_goal TEXT,
                    confidence REAL,
                    reason TEXT,
                    dispatched INTEGER,
                    timestamp REAL
                )
            """)
            conn.commit()

    def save_event(self, event_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO life_events (id, event_type, payload_json, timestamp)
                VALUES (?, ?, ?, ?)
            """, (event_id, event_type, json.dumps(payload), time.time()))
            conn.commit()

    def save_risk_signal(self, signal: RiskSignal) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO risk_signals (id, type, source, severity, confidence, reason_json, timestamp, is_suppressed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.id,
                signal.type.value,
                signal.source,
                signal.severity,
                signal.confidence,
                json.dumps(signal.reason),
                signal.timestamp,
                1 if signal.is_suppressed else 0,
            ))
            conn.commit()

    def list_risk_signals(self) -> List[RiskSignal]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, type, source, severity, confidence, reason_json, timestamp, is_suppressed FROM risk_signals")
            rows = cur.fetchall()
            return [
                RiskSignal(
                    id=r[0],
                    type=SignalType(r[1]),
                    source=r[2],
                    severity=r[3],
                    confidence=r[4],
                    reason=json.loads(r[5]),
                    timestamp=r[6],
                    is_suppressed=bool(r[7]),
                )
                for r in rows
            ]

    def save_prediction(self, pred: TrajectoryForecast) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO predictions (subject, current_mastery, days_to_target, forecast_score, required_hours, cgpa_impact, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pred.subject_or_goal,
                pred.current_mastery_pct,
                pred.days_to_target,
                pred.forecasted_score_pct,
                pred.required_hours_per_week,
                pred.cgpa_impact_delta,
                time.time(),
            ))
            conn.commit()

    def save_initiative(self, init: InitiativeDecision) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO initiatives (id, action_type, title, target_subject, mission_goal, confidence, reason, dispatched, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                init.id,
                init.action_type.value,
                init.title,
                init.target_subject,
                init.mission_goal,
                init.confidence,
                init.reason,
                1 if init.dispatched else 0,
                time.time(),
            ))
            conn.commit()

    def list_initiatives(self) -> List[InitiativeDecision]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, action_type, title, target_subject, mission_goal, confidence, reason, dispatched FROM initiatives")
            return [
                InitiativeDecision(
                    id=r[0],
                    action_type=InitiativeType(r[1]),
                    title=r[2],
                    target_subject=r[3],
                    mission_goal=r[4],
                    confidence=r[5],
                    reason=r[6],
                    dispatched=bool(r[7]),
                )
                for r in cur.fetchall()
            ]
