"""Persistent Memory Store for Phase 97 Self Improvement Loop."""

from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.self_improvement.models import (
    ErrorClass,
    FailureRootCause,
    PerformanceMetric,
    SandboxRun,
    SuccessPattern,
    UpgradeProposal,
    UpgradeStatus,
)


class SelfImprovementMemory:
    """Dedicated SQLite Store for Self-Improvement metrics, failure root-causes, and upgrade proposals."""

    def __init__(self, db_path: str = "var/db/self_improvement.db"):
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
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    agent_name TEXT PRIMARY KEY,
                    total_tasks INTEGER,
                    successes INTEGER,
                    failures INTEGER,
                    success_rate REAL,
                    avg_duration_sec REAL,
                    confidence_score REAL,
                    trend TEXT,
                    updated_at REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS failure_reports (
                    failure_id TEXT PRIMARY KEY,
                    error_class TEXT,
                    failed_agent TEXT,
                    root_cause_category TEXT,
                    proposed_fix TEXT,
                    confidence REAL,
                    recurrence_count INTEGER,
                    timestamp REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS success_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    task_type TEXT,
                    strategy_template_json TEXT,
                    success_rate REAL,
                    sample_count INTEGER,
                    updated_at REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS upgrade_proposals (
                    proposal_id TEXT PRIMARY KEY,
                    target_component TEXT,
                    change_type TEXT,
                    patch_diff TEXT,
                    validation_score REAL,
                    status TEXT,
                    rollback_plan TEXT,
                    created_at REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS sandbox_runs (
                    run_id TEXT PRIMARY KEY,
                    proposal_id TEXT,
                    tests_passed INTEGER,
                    total_tests INTEGER,
                    regression_detected INTEGER,
                    duration_sec REAL,
                    status TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()

    def save_metric(self, metric: PerformanceMetric) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO agent_metrics
                (agent_name, total_tasks, successes, failures, success_rate, avg_duration_sec, confidence_score, trend, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.agent_name,
                metric.total_tasks,
                metric.successes,
                metric.failures,
                metric.success_rate,
                metric.avg_duration_sec,
                metric.confidence_score,
                metric.trend,
                time.time(),
            ))
            conn.commit()

    def list_metrics(self) -> List[PerformanceMetric]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT agent_name, total_tasks, successes, failures, success_rate, avg_duration_sec, confidence_score, trend FROM agent_metrics")
            return [
                PerformanceMetric(
                    agent_name=r[0],
                    total_tasks=r[1],
                    successes=r[2],
                    failures=r[3],
                    success_rate=r[4],
                    avg_duration_sec=r[5],
                    confidence_score=r[6],
                    trend=r[7],
                )
                for r in cur.fetchall()
            ]

    def record_failure(self, failure: FailureRootCause) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO failure_reports
                (failure_id, error_class, failed_agent, root_cause_category, proposed_fix, confidence, recurrence_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                failure.failure_id,
                failure.error_class.value,
                failure.failed_agent,
                failure.root_cause_category,
                failure.proposed_fix,
                failure.confidence,
                failure.recurrence_count,
                failure.timestamp,
            ))
            conn.commit()

    def list_failures(self) -> List[FailureRootCause]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT failure_id, error_class, failed_agent, root_cause_category, proposed_fix, confidence, recurrence_count, timestamp FROM failure_reports ORDER BY timestamp DESC")
            return [
                FailureRootCause(
                    failure_id=r[0],
                    error_class=ErrorClass(r[1]),
                    failed_agent=r[2],
                    root_cause_category=r[3],
                    proposed_fix=r[4],
                    confidence=r[5],
                    recurrence_count=r[6],
                    timestamp=r[7],
                )
                for r in cur.fetchall()
            ]

    def save_pattern(self, pattern: SuccessPattern) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO success_patterns
                (pattern_id, task_type, strategy_template_json, success_rate, sample_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_id,
                pattern.task_type,
                json.dumps(pattern.strategy_template),
                pattern.success_rate,
                pattern.sample_count,
                time.time(),
            ))
            conn.commit()

    def list_patterns(self) -> List[SuccessPattern]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT pattern_id, task_type, strategy_template_json, success_rate, sample_count FROM success_patterns")
            return [
                SuccessPattern(
                    pattern_id=r[0],
                    task_type=r[1],
                    strategy_template=json.loads(r[2]),
                    success_rate=r[3],
                    sample_count=r[4],
                )
                for r in cur.fetchall()
            ]

    def save_proposal(self, proposal: UpgradeProposal) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO upgrade_proposals
                (proposal_id, target_component, change_type, patch_diff, validation_score, status, rollback_plan, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proposal.proposal_id,
                proposal.target_component,
                proposal.change_type,
                proposal.patch_diff,
                proposal.validation_score,
                proposal.status.value,
                proposal.rollback_plan,
                proposal.created_at,
            ))
            conn.commit()

    def list_proposals(self) -> List[UpgradeProposal]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT proposal_id, target_component, change_type, patch_diff, validation_score, status, rollback_plan, created_at FROM upgrade_proposals ORDER BY created_at DESC")
            return [
                UpgradeProposal(
                    proposal_id=r[0],
                    target_component=r[1],
                    change_type=r[2],
                    patch_diff=r[3],
                    validation_score=r[4],
                    status=UpgradeStatus(r[5]),
                    rollback_plan=r[6],
                    created_at=r[7],
                )
                for r in cur.fetchall()
            ]

    def record_sandbox_run(self, run: SandboxRun) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO sandbox_runs
                (run_id, proposal_id, tests_passed, total_tests, regression_detected, duration_sec, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.run_id,
                run.proposal_id,
                run.tests_passed,
                run.total_tests,
                1 if run.regression_detected else 0,
                run.duration_sec,
                run.status,
                time.time(),
            ))
            conn.commit()
