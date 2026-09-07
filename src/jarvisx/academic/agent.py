"""Operational Agent wrapper for Jarvis X Academic & Homework Sentinel.

Integrates AcademicSentinelDaemon into the canonical OperationalAgent hierarchy (Layer 3),
exposing standardized telemetry, permission scopes, and execution contracts for Alfred
and the Unified Agent Fleet.
"""

from __future__ import annotations
import logging
import time
from typing import Any, Dict, List, Optional

from jarvisx.agents.base import OperationalAgent
from jarvisx.academic.models import StudentProfile, TaskStatus
from jarvisx.academic.sentinel_daemon import AcademicSentinelDaemon

logger = logging.getLogger("jarvisx.academic.agent")


class AcademicSentinelAgent(OperationalAgent):
    """Canonical Operational Agent for Academic, Homework, and Portal Automation."""

    def __init__(
        self,
        profile: Optional[StudentProfile] = None,
        db_path: str = "var/db/academic_sentinel.db",
        enable_voice: bool = True,
        enable_toast: bool = True,
    ):
        super().__init__(
            name="AcademicSentinelAgent",
            purpose="Autonomous multi-channel academic sentinel for SRM eCurricula, GCR, Teams, WhatsApp, NPTEL, and STEP Java.",
            capabilities=[
                "academic_sentinel",
                "homework_solving",
                "srm_ecurricula_automation",
                "nptel_swayam_mcq_solver",
                "srm_step_java_solver",
                "omnichannel_academic_monitor",
                "document_compilation",
                "assignment_submission",
            ],
            permissions=["read_filesystem", "write_filesystem", "network_requests", "send_alerts"],
            hspw_multiplier=2.5,
        )
        self.daemon = AcademicSentinelDaemon(
            db_path=db_path,
            enable_voice=enable_voice,
            enable_toast=enable_toast,
            profile=profile,
        )

    def _execute_task(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Executes academic cycles, queries, or targeted problem sets."""
        action = task.get("action", "cycle")
        if action in ("cycle", "scan", "sweep", "execute"):
            simulated = task.get("simulated_events") or kwargs.get("simulated_events")
            cycle_res = self.daemon.execute_cycle(simulated_events=simulated)
            return {
                "status": "completed",
                "action": action,
                "summary": cycle_res,
                "tasks_solved": cycle_res.get("tasks_solved", 0),
                "tasks_submitted": cycle_res.get("tasks_submitted", 0),
            }
        elif action in ("status", "query"):
            st_dict = self.get_status()
            st_dict["status"] = "completed"
            return st_dict
        elif action == "solve":
            task_obj = task.get("task_obj")
            if task_obj:
                solved = self.daemon.solver.solve_task(task_obj)
                compiled = self.daemon.compiler.compile_task(solved)
                self.daemon.persistence.save_task(compiled)
                return {
                    "status": "completed",
                    "task_id": compiled.task_id,
                    "solution_preview": compiled.solution_content[:150] if compiled.solution_content else "",
                }
            return {"status": "completed", "result": "No task_obj provided"}

        # Default fallback to autonomous sweep cycle
        res = self.daemon.execute_cycle()
        return {"status": "completed", "summary": res}

    def execute_cycle(self, simulated_events: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Direct hook for running an autonomous academic sweep cycle."""
        return self.daemon.execute_cycle(simulated_events=simulated_events)

    def get_status(self) -> Dict[str, Any]:
        """Returns deep operational and academic state telemetry."""
        tasks = self.daemon.persistence.list_tasks()
        base_st = self.status()
        base_st.update({
            "agent_name": self.name,
            "tasks_tracked": len(tasks),
            "tasks_submitted": len([t for t in tasks if t.status == TaskStatus.SUBMITTED]),
            "tasks_pending": len([t for t in tasks if t.status != TaskStatus.SUBMITTED]),
            "student": self.daemon.profile.name,
            "reg_no": self.daemon.profile.reg_no,
            "department": self.daemon.profile.department,
            "semester": self.daemon.profile.semester,
        })
        return base_st


_global_academic_agent: Optional[AcademicSentinelAgent] = None


def get_academic_agent(
    profile: Optional[StudentProfile] = None,
    enable_voice: bool = True,
    enable_toast: bool = True,
) -> AcademicSentinelAgent:
    """Singleton getter for the AcademicSentinelAgent."""
    global _global_academic_agent
    if _global_academic_agent is None:
        _global_academic_agent = AcademicSentinelAgent(
            profile=profile,
            enable_voice=enable_voice,
            enable_toast=enable_toast,
        )
    return _global_academic_agent
