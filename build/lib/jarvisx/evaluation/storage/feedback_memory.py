"""SQLite Persistent Storage for Evaluation, Feedback, and Knowledge Utility."""

from __future__ import annotations
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Dict, List, Optional
from jarvisx.evaluation.models import (
    EvidenceSource,
    EvidenceTrace,
    FailureCategory,
    FailureRecord,
    ResponseEvaluation,
    SourceUtilityRecord,
)


class FeedbackMemory:
    """Manages SQLite storage for evaluations, failures, user feedback, and source utility."""

    SCHEMA_VERSION = "1.0.0"

    def __init__(self, db_path: str = "var/db/evaluation.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluations (
                    response_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    answer_snippet TEXT,
                    grounding_score REAL NOT NULL,
                    completeness_score REAL NOT NULL,
                    clarity_score REAL NOT NULL,
                    retrieval_confidence REAL NOT NULL,
                    user_correction_penalty REAL DEFAULT 0.0,
                    final_quality_score REAL NOT NULL,
                    actor_role TEXT,
                    evidence_trace_json TEXT,
                    user_feedback TEXT,
                    is_user_accepted INTEGER,
                    created_at REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failures (
                    failure_id TEXT PRIMARY KEY,
                    response_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    cause TEXT NOT NULL,
                    user_correction TEXT NOT NULL,
                    corrective_action TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (response_id) REFERENCES evaluations(response_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_utility (
                    source_file TEXT PRIMARY KEY,
                    times_retrieved INTEGER DEFAULT 0,
                    times_successful INTEGER DEFAULT 0,
                    times_corrected INTEGER DEFAULT 0,
                    utility_score REAL DEFAULT 1.0,
                    last_updated REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            cursor.execute(
                "INSERT OR IGNORE INTO meta (key, value) VALUES (?, ?)",
                ("schema_version", self.SCHEMA_VERSION),
            )
            conn.commit()

    def save_evaluation(self, eval_record: ResponseEvaluation) -> None:
        """Persist response evaluation with serialized evidence trace."""
        trace_json = ""
        if eval_record.evidence_trace:
            trace_dict = {
                "response_id": eval_record.evidence_trace.response_id,
                "query": eval_record.evidence_trace.query,
                "grounding_ratio": eval_record.evidence_trace.grounding_ratio,
                "supported_count": eval_record.evidence_trace.supported_claims_count,
                "unknown_count": eval_record.evidence_trace.unknown_claims_count,
                "unsupported_count": eval_record.evidence_trace.unsupported_claims_count,
                "sources": [
                    {
                        "source_file": s.source_file,
                        "section": s.section_heading,
                        "confidence": s.confidence,
                        "hash": s.provenance_hash,
                    }
                    for s in eval_record.evidence_trace.sources
                ],
            }
            trace_json = json.dumps(trace_dict)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO evaluations (
                    response_id, query, answer_snippet, grounding_score,
                    completeness_score, clarity_score, retrieval_confidence,
                    user_correction_penalty, final_quality_score, actor_role,
                    evidence_trace_json, user_feedback, is_user_accepted, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                eval_record.response_id,
                eval_record.query,
                eval_record.answer_snippet[:500],
                eval_record.grounding_score,
                eval_record.completeness_score,
                eval_record.clarity_score,
                eval_record.retrieval_confidence,
                eval_record.user_correction_penalty,
                eval_record.final_quality_score,
                eval_record.actor_role,
                trace_json,
                eval_record.user_feedback,
                1 if eval_record.is_user_accepted else (0 if eval_record.is_user_accepted is False else None),
                eval_record.created_at,
            ))
            conn.commit()

    def record_feedback(
        self,
        response_id: str,
        is_accepted: bool,
        user_feedback: Optional[str] = None,
        correction_penalty: float = 0.0,
    ) -> Optional[ResponseEvaluation]:
        """Update evaluation record with user acceptance and feedback."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluations WHERE response_id = ?", (response_id,))
            row = cursor.fetchone()
            if not row:
                return None

            base_score = float(row["final_quality_score"]) + float(row["user_correction_penalty"])
            new_penalty = correction_penalty if not is_accepted else 0.0
            new_final = max(0.0, min(1.0, base_score - new_penalty))

            cursor.execute("""
                UPDATE evaluations
                SET is_user_accepted = ?, user_feedback = ?, user_correction_penalty = ?, final_quality_score = ?
                WHERE response_id = ?
            """, (1 if is_accepted else 0, user_feedback, new_penalty, new_final, response_id))
            conn.commit()

        return self.get_evaluation(response_id)

    def record_failure(self, failure: FailureRecord) -> None:
        """Log a structured failure record linking user correction to failure root cause."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO failures (
                    failure_id, response_id, category, cause, user_correction, corrective_action, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                failure.failure_id,
                failure.response_id,
                failure.category.value if hasattr(failure.category, "value") else str(failure.category),
                failure.cause,
                failure.user_correction,
                failure.corrective_action,
                failure.created_at,
            ))
            conn.commit()

    def update_source_utility(self, source_file: str, retrieved: bool = True, success: bool = True, corrected: bool = False) -> SourceUtilityRecord:
        """Update historical utility score for a source document."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM source_utility WHERE source_file = ?", (source_file,))
            row = cursor.fetchone()

            if row:
                t_ret = row["times_retrieved"] + (1 if retrieved else 0)
                t_suc = row["times_successful"] + (1 if success else 0)
                t_cor = row["times_corrected"] + (1 if corrected else 0)
            else:
                t_ret = 1 if retrieved else 0
                t_suc = 1 if success else 0
                t_cor = 1 if corrected else 0

            # Utility score formula: (successful - 0.5 * corrected) / retrieved
            score = max(0.1, min(1.0, (t_suc - (0.5 * t_cor)) / max(1, t_ret)))

            now = time.time()
            cursor.execute("""
                INSERT OR REPLACE INTO source_utility (
                    source_file, times_retrieved, times_successful, times_corrected, utility_score, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (source_file, t_ret, t_suc, t_cor, score, now))
            conn.commit()

            return SourceUtilityRecord(
                source_file=source_file,
                times_retrieved=t_ret,
                times_successful=t_suc,
                times_corrected=t_cor,
                utility_score=score,
                last_updated=now,
            )

    def get_evaluation(self, response_id: str) -> Optional[ResponseEvaluation]:
        """Fetch evaluation by response ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluations WHERE response_id = ?", (response_id,))
            row = cursor.fetchone()
            if not row:
                return None

            return self._row_to_evaluation(row)

    def get_last_evaluation(self) -> Optional[ResponseEvaluation]:
        """Fetch most recent response evaluation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluations ORDER BY created_at DESC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_evaluation(row)

    def list_recent_evaluations(self, limit: int = 20) -> List[ResponseEvaluation]:
        """List recent response evaluations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluations ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_evaluation(r) for r in rows]

    def list_failures(self, limit: int = 50) -> List[FailureRecord]:
        """List logged failures."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM failures ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [
                FailureRecord(
                    failure_id=r["failure_id"],
                    response_id=r["response_id"],
                    category=FailureCategory(r["category"]),
                    cause=r["cause"],
                    user_correction=r["user_correction"],
                    corrective_action=r["corrective_action"],
                    created_at=float(r["created_at"]),
                )
                for r in rows
            ]

    def get_all_source_utilities(self) -> List[SourceUtilityRecord]:
        """Get utility records for all sources."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM source_utility ORDER BY utility_score DESC")
            rows = cursor.fetchall()
            return [
                SourceUtilityRecord(
                    source_file=r["source_file"],
                    times_retrieved=r["times_retrieved"],
                    times_successful=r["times_successful"],
                    times_corrected=r["times_corrected"],
                    utility_score=float(r["utility_score"]),
                    last_updated=float(r["last_updated"]),
                )
                for r in rows
            ]

    def _row_to_evaluation(self, row: sqlite3.Row) -> ResponseEvaluation:
        return ResponseEvaluation(
            response_id=row["response_id"],
            query=row["query"],
            answer_snippet=row["answer_snippet"],
            grounding_score=float(row["grounding_score"]),
            completeness_score=float(row["completeness_score"]),
            clarity_score=float(row["clarity_score"]),
            retrieval_confidence=float(row["retrieval_confidence"]),
            user_correction_penalty=float(row["user_correction_penalty"]),
            final_quality_score=float(row["final_quality_score"]),
            actor_role=row["actor_role"] or "AlfredMaster",
            user_feedback=row["user_feedback"],
            is_user_accepted=True if row["is_user_accepted"] == 1 else (False if row["is_user_accepted"] == 0 else None),
            created_at=float(row["created_at"]),
        )
