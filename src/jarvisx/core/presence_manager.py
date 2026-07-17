"""Presence Manager — tracks all internal activity and exposes a single Alfred-facing summary."""
import time
from typing import Dict, Any, List, Optional
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class PresenceManager:
    """Tracks active objectives, running agents, background jobs, and health.
    Generates summaries suitable for Alfred to speak aloud."""

    _instance: Optional["PresenceManager"] = None

    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._objectives: Dict[str, Dict[str, Any]] = {}
        self._background_jobs: Dict[str, Dict[str, Any]] = {}
        self._health = HealthStatus.HEALTHY
        self._activity_log: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "PresenceManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # --- Agent tracking ---

    def register_agent(self, agent_name: str):
        self._agents[agent_name] = {
            "registered_at": time.time(),
            "status": "running",
        }
        self._log("agent_start", agent_name)

    def unregister_agent(self, agent_name: str):
        if agent_name in self._agents:
            self._agents[agent_name]["status"] = "stopped"
        self._log("agent_stop", agent_name)

    # --- Objective tracking ---

    def register_objective(self, objective: Dict[str, Any]):
        obj_id = objective.get("objective_id", objective.get("id", "unknown"))
        self._objectives[obj_id] = {
            "title": objective.get("title", "Untitled"),
            "progress": objective.get("progress", 0),
            "status": "active",
            "registered_at": time.time(),
        }
        self._log("objective_start", objective.get("title", obj_id))

    def update_objective_progress(self, objective_id: str, progress: int):
        if objective_id in self._objectives:
            self._objectives[objective_id]["progress"] = progress

    def complete_objective(self, objective_id: str):
        if objective_id in self._objectives:
            self._objectives[objective_id]["status"] = "completed"
            self._objectives[objective_id]["progress"] = 100
        self._log("objective_complete", objective_id)

    # --- Background jobs ---

    def register_background_job(self, job_name: str):
        self._background_jobs[job_name] = {
            "started_at": time.time(),
            "status": "running",
        }

    def complete_background_job(self, job_name: str):
        if job_name in self._background_jobs:
            self._background_jobs[job_name]["status"] = "completed"

    # --- Health ---

    def set_health(self, status: HealthStatus):
        self._health = status

    # --- Summaries ---

    def get_active_summary(self) -> str:
        """Generate a human-readable summary of what Alfred is doing."""
        active_objs = [
            o for o in self._objectives.values() if o["status"] == "active"
        ]
        running_jobs = [
            name for name, j in self._background_jobs.items() if j["status"] == "running"
        ]

        parts = []
        if active_objs:
            for obj in active_objs:
                parts.append(f"{obj['title']} ({obj['progress']}%)")
        if running_jobs:
            parts.append(f"Background: {', '.join(running_jobs)}")

        if not parts:
            return "All tasks complete. Standing by."

        return " | ".join(parts)

    def get_diagnostics_snapshot(self) -> Dict[str, Any]:
        """Full internal state for the diagnostics console."""
        return {
            "active_objectives": {
                oid: o for oid, o in self._objectives.items() if o["status"] == "active"
            },
            "completed_objectives": {
                oid: o for oid, o in self._objectives.items() if o["status"] == "completed"
            },
            "running_agents": [
                name for name, a in self._agents.items() if a["status"] == "running"
            ],
            "background_jobs": {
                name: j for name, j in self._background_jobs.items() if j["status"] == "running"
            },
            "health": self._health.value,
        }

    def get_running_agent_names(self) -> List[str]:
        return [name for name, a in self._agents.items() if a["status"] == "running"]

    # --- Internal ---

    def _log(self, event_type: str, detail: str):
        self._activity_log.append({
            "type": event_type,
            "detail": detail,
            "timestamp": time.time(),
        })
