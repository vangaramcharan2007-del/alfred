"""Academic Sentinel Autonomous Controller & Daemon Loop.

Orchestrates the continuous academic loop across all channels:
1. Continuous Channel Ingestion (Email, GCR, Teams, WhatsApp, eCurricula, NPTEL, STEP Java)
2. Task Normalization & Priority Ranking
3. Autonomous Solution & Document Compilation
4. Multi-modal Alerting (Voice + Desktop Toasts)
5. Portal Submissions & Staging
6. Persistent Ledger Tracking
"""

from __future__ import annotations
import logging
import time
from typing import Any, Dict, List, Optional

from jarvisx.academic.models import (
    AcademicTask,
    AlertEvent,
    ChannelSource,
    StudentProfile,
    TaskPriority,
    TaskStatus,
)
from jarvisx.academic.channel_hub import ChannelHub
from jarvisx.academic.normalizer import AssignmentNormalizer
from jarvisx.academic.solver_engine import AcademicSolverEngine
from jarvisx.academic.document_compiler import AcademicDocumentCompiler
from jarvisx.academic.alert_dispatcher import AcademicAlertDispatcher
from jarvisx.academic.submission_engine import AcademicSubmissionEngine
from jarvisx.academic.persistence import AcademicPersistenceManager

logger = logging.getLogger("jarvisx.academic.sentinel_daemon")


class AcademicSentinelDaemon:
    """Autonomous Sentinel controlling the full academic homework and assessment lifecycle."""

    def __init__(
        self,
        db_path: str = "var/db/academic_sentinel.db",
        enable_voice: bool = True,
        enable_toast: bool = True,
        profile: Optional[StudentProfile] = None,
    ):
        self.profile = profile or StudentProfile()
        self.persistence = AcademicPersistenceManager(db_path)
        self.channel_hub = ChannelHub(self.profile)
        self.normalizer = AssignmentNormalizer()
        self.solver = AcademicSolverEngine()
        self.compiler = AcademicDocumentCompiler(profile=self.profile)
        self.alerter = AcademicAlertDispatcher(enable_voice=enable_voice, enable_toast=enable_toast)
        self.submission_engine = AcademicSubmissionEngine(profile=self.profile)
        
        # Expose 5 Core Resilience Subsystems
        self.session_vault = self.channel_hub.session_vault
        self.resilient_scraper = self.channel_hub.resilient_scraper
        self.multimodal_anchor = self.channel_hub.multimodal_anchor
        self.stylometry_engine = self.solver.stylometry
        self.resilience_ctrl = self.submission_engine.resilience_ctrl

    def execute_cycle(self, simulated_events: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Runs a complete autonomous academic sweep cycle with full resilience enforcement."""
        cycle_start = time.time()
        logger.info("=== STARTING RESILIENT ACADEMIC SENTINEL CYCLE ===")

        # 1. Ingest from all channels
        raw_tasks = self.channel_hub.poll_all_channels(simulated_events)
        newly_discovered: List[AcademicTask] = []
        
        for task in raw_tasks:
            existing = self.persistence.get_task(task.task_id)
            if not existing:
                self.persistence.save_task(task)
                newly_discovered.append(task)
                # Alert discovery
                self.alerter.dispatch_task_alert(task, is_solved=False)
            elif existing.status != TaskStatus.SUBMITTED:
                newly_discovered.append(existing)

        # 2. Autonomous Solve & Document Compile
        solved_tasks: List[AcademicTask] = []
        for task in newly_discovered:
            if task.status in (TaskStatus.DISCOVERED, TaskStatus.PARSED):
                task = self.solver.solve_task(task)
                task = self.compiler.compile_task(task)
                self.persistence.save_task(task)
                solved_tasks.append(task)

        # 3. Autonomous Submission / Staging
        submitted_tasks: List[AcademicTask] = []
        for task in solved_tasks:
            task = self.submission_engine.process_submission(task)
            self.persistence.save_task(task)
            submitted_tasks.append(task)
            # Alert completion
            self.alerter.dispatch_task_alert(task, is_solved=True)

        cycle_summary = {
            "timestamp": time.time(),
            "duration_seconds": round(time.time() - cycle_start, 2),
            "channels_polled": len(ChannelSource),
            "tasks_ingested": len(raw_tasks),
            "tasks_solved": len(solved_tasks),
            "tasks_submitted": len(submitted_tasks),
            "alerts_dispatched": len(self.alerter.dispatched_history),
            "resilience_telemetry": {
                "active_sessions": len(self.session_vault._sessions),
                "cached_routes": len(self.resilient_scraper._route_cache),
                "stylometry_active": True,
                "two_phase_staging": True,
                "next_sweep_delay_s": round(self.resilience_ctrl.get_next_sweep_delay(), 1),
            },
            "active_tasks": [t.to_dict() for t in submitted_tasks],
        }

        logger.info(f"=== CYCLE COMPLETE: {len(submitted_tasks)} tasks processed ===")
        return cycle_summary
