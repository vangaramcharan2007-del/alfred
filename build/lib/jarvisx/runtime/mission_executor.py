"""Mission Executor for Jarvis X.

Drives step-by-step task execution, invokes agent routing, coordinates recovery
cycles upon failure, and persists checkpoint transitions.
"""

from typing import Any, Dict
from jarvisx.runtime.agent_dispatcher import AgentDispatcher
from jarvisx.runtime.mission_state import MissionState, MissionStatus
from jarvisx.runtime.recovery_manager import RecoveryManager


class MissionExecutor:
    """Operational runtime engine that advances mission state across assigned agent workforce."""

    def __init__(self, dispatcher: AgentDispatcher, recovery: RecoveryManager):
        self.dispatcher = dispatcher
        self.recovery = recovery

    def execute_step(self, mission: MissionState) -> Dict[str, Any]:
        """Execute the currently active task within the mission schedule."""
        if mission.status in (MissionStatus.COMPLETED, MissionStatus.FAILED):
            return {
                "status": mission.status.value.lower(),
                "message": f"Mission already finalized with status {mission.status}",
            }

        task = mission.get_current_task()
        if not task:
            mission.transition(MissionStatus.COMPLETED)
            return {"status": "completed", "message": "All mission tasks exhausted."}

        mission.transition(MissionStatus.EXECUTING)
        agent_name = task.assigned_agent or "engineering_agent"
        task.status = "in_progress"

        result = self.dispatcher.assign(
            task_description=task.description,
            agent_name=agent_name,
            task_id=task.task_id,
        )

        if result.get("status") in ("completed", "success"):
            task.status = "completed"
            task.result = result
            mission.completed_tasks.append(task.task_id)
            mission.current_task_idx += 1
            if mission.current_task_idx >= len(mission.tasks):
                mission.transition(MissionStatus.COMPLETED)
            else:
                mission.transition(MissionStatus.EXECUTING)
            return {"status": "success", "task": task.description, "result": result}
        else:
            error_msg = str(result.get("error", "Unknown execution failure"))
            recovery_outcome = self.recovery.attempt_recovery(mission, task, error_msg)
            if recovery_outcome.get("status") == "retrying":
                task.error = f"{error_msg} (Attempting recovery: {recovery_outcome['strategy']})"
                return {
                    "status": "recovering",
                    "task": task.description,
                    "attempt": task.retry_count,
                    "strategy": recovery_outcome["strategy"],
                }
            else:
                task.status = "failed"
                task.error = error_msg
                mission.failed_tasks.append(task.task_id)
                return {
                    "status": "failed",
                    "task": task.description,
                    "error": error_msg,
                    "escalation": recovery_outcome.get("notice"),
                }
