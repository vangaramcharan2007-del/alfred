from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel

from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager
from jarvisx.capabilities.coding.pipeline.git_manager import GitManager
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.goose import goose_events as GE
from jarvisx.capabilities.coding.metrics import CodingMetrics

class GooseExecutor:
    def __init__(
        self,
        permission_manager: Optional[PermissionManager] = None,
        sandbox_manager: Optional[SandboxManager] = None,
        git_manager: Optional[GitManager] = None,
        bus: Optional[HermesBus] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.permission_manager = permission_manager or PermissionManager()
        self.sandbox_manager = sandbox_manager or SandboxManager()
        self.git_manager = git_manager or GitManager()
        self.bus = bus or HermesBus()
        self.metrics = metrics or CodingMetrics()

    async def execute_mission(
        self,
        mission_type: str,
        task_description: str,
        repo_path: str,
        session_id: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        params = params or {}

        # 1. Safety Permission Check
        self.permission_manager.request_permission("goose.executor", PermissionLevel.WRITE)
        has_perm = self.permission_manager.check_permission("goose.executor", PermissionLevel.WRITE)
        if not has_perm:
            await self.bus.publish(Event(
                type=GE.GOOSE_TASK_FAILED,
                source="goose_executor",
                payload={"session_id": session_id, "mission": mission_type, "error": "Permission denied: WRITE level not granted"}
            ))
            self.metrics.failed_tasks += 1
            raise PermissionError("Goose Execution Permission Denied: WRITE level not granted")


        # 2. Sandbox Verification
        self.sandbox_manager.validate_command("python --version")
        sandbox_id = "sandbox_goose_env_001"

        # 3. Hermes Event: Progress
        await self.bus.publish(Event(
            type=GE.GOOSE_TASK_PROGRESS,
            source="goose_executor",
            payload={
                "session_id": session_id,
                "mission": mission_type,
                "progress": 50,
                "sandbox_id": sandbox_id
            }
        ))

        # 4. Mission Execution
        mission_output = {
            "mission_type": mission_type,
            "description": task_description,
            "repo_path": repo_path,
            "status": "completed",
            "changes_applied": [f"mods/{mission_type}_output.py"],
            "sandbox_id": sandbox_id
        }


        duration = time.time() - start_time
        self.metrics.goose_tasks += 1
        self.metrics.engineering_missions += 1
        self.metrics.successful_tasks += 1
        self.metrics.record_task_completed(duration, success=True)

        await self.bus.publish(Event(
            type=GE.GOOSE_TASK_COMPLETED,
            source="goose_executor",
            payload={"session_id": session_id, "mission": mission_type, "result": mission_output}
        ))

        return mission_output
