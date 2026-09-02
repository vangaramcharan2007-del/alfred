"""Autonomous Mission Executor for Jarvis X (Layer 3 - Execution).

Connects planning intelligence with real OS and automation execution.
Transitions missions cleanly across states: CREATED, READY, RUNNING, BLOCKED, COMPLETED, FAILED.
"""

import time
from typing import Any, Dict, List, Optional

from jarvisx.missions.mission import Mission
from jarvisx.automation.capability_registry import CapabilityRealityRegistry


class MissionExecutorEngine:
    """Zero-fluff production autonomous mission execution loop engine."""

    def __init__(self, capability_registry: Optional[CapabilityRealityRegistry] = None):
        self.capability_registry = capability_registry or CapabilityRealityRegistry()

    def execute_mission(self, mission: Mission, os_kernel: Any, user_confirmed: bool = False) -> Dict[str, Any]:
        """Execute a Mission object through state transitions and physical kernel handlers."""
        start_time = time.time()
        mission.status = "READY"

        # 1. Check capability availability
        capability_name = mission.user_request or mission.title or mission.capability
        cap_verify = self.capability_registry.verify_capability(capability_name)
        if not cap_verify["verified"] and cap_verify["capability"]["execution_type"] == "UNKNOWN":
            mission.status = "BLOCKED"
            return {
                "status": "BLOCKED",
                "mission_id": mission.id,
                "reason": f"Capability '{capability_name}' is UNKNOWN or blocked by registry.",
                "duration": round(time.time() - start_time, 3),
            }

        # 2. Check dependencies
        deps = mission.context.get("dependencies", [])
        if deps:
            active_goals = getattr(os_kernel, "goal_tracker", None)
            if active_goals:
                incomplete = [d for d in deps if isinstance(d, str) and " incomplete" in d.lower()]
                if incomplete:
                    mission.status = "BLOCKED"
                    return {
                        "status": "BLOCKED",
                        "mission_id": mission.id,
                        "reason": f"Prerequisite dependencies incomplete: {incomplete}",
                        "duration": round(time.time() - start_time, 3),
                    }

        # 3. Check safety & user confirmation
        safety_guard = getattr(os_kernel, "proactive_safety", None)
        if safety_guard:
            sug_dict = {"title": mission.title, "suggestion": mission.user_request, "confidence": 0.85}
            eval_res = safety_guard.evaluate_proactive_safety(sug_dict, user_confirmed=user_confirmed)
            if not eval_res["permitted"]:
                mission.status = "BLOCKED"
                return {
                    "status": "BLOCKED",
                    "mission_id": mission.id,
                    "reason": eval_res["reason"],
                    "duration": round(time.time() - start_time, 3),
                }

        # 4. Transition state to RUNNING and execute via Kernel
        mission.status = "RUNNING"
        try:
            exec_res = os_kernel.execute_objective(mission.user_request or mission.title)
            duration = round(time.time() - start_time, 3)

            if exec_res.get("status") in ("completed", "nominal", "SUCCESS", "REPLANNED", "REGISTERED"):
                mission.status = "COMPLETED"
                mission.result = exec_res
                return {
                    "status": "COMPLETED",
                    "mission_id": mission.id,
                    "result": exec_res,
                    "duration": duration,
                }
            else:
                mission.status = "FAILED"
                mission.result = exec_res
                return {
                    "status": "FAILED",
                    "mission_id": mission.id,
                    "reason": exec_res.get("reason", "Execution returned non-success status"),
                    "duration": duration,
                }
        except Exception as e:
            duration = round(time.time() - start_time, 3)
            mission.status = "FAILED"
            return {
                "status": "FAILED",
                "mission_id": mission.id,
                "reason": str(e),
                "duration": duration,
            }
