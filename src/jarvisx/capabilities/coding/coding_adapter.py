from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from jarvisx.capabilities.capability_adapter import CapabilityAdapter
from jarvisx.capabilities.capability_manifest import CapabilityManifest
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event

from jarvisx.capabilities.coding.metrics import CodingMetrics
from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager
from jarvisx.capabilities.coding.pipeline.repository_analyzer import RepositoryAnalyzer
from jarvisx.capabilities.coding.pipeline.task_planner import TaskPlanner
from jarvisx.capabilities.coding.pipeline.code_executor import CodeExecutor
from jarvisx.capabilities.coding.pipeline.test_runner import TestRunner
from jarvisx.capabilities.coding.pipeline.code_reviewer import CodeReviewer
from jarvisx.capabilities.coding.pipeline.git_manager import GitManager

from jarvisx.capabilities.coding.autonomous_loop import AutonomousLoop, AutonomousLoopReport

class CodingAdapter(CapabilityAdapter):
    def __init__(
        self,
        manifest: Optional[CapabilityManifest] = None,
        bus: Optional[HermesBus] = None,
        permission_manager: Optional[PermissionManager] = None
    ):
        if manifest is None:
            manifest_path = Path(__file__).resolve().parent.parent / "manifests" / "coding_agent.json"
            if manifest_path.exists():
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest = CapabilityManifest(
                    name=data.get("name", "coding_agent"),
                    version=data.get("version", "1.1.0"),
                    api_version=data.get("api_version", "v1"),
                    description=data.get("description", "Advanced Autonomous Coding Agent Capability"),
                    category=data.get("category", "coding"),
                    inputs=data.get("inputs", {}),
                    outputs=data.get("outputs", {}),
                    requirements=data.get("requirements", {}),
                    permissions=data.get("permissions", ["READ", "WRITE", "EXECUTE"]),
                    confidence=data.get("confidence", 0.95)
                )
            else:
                manifest = CapabilityManifest(
                    name="coding_agent",
                    version="1.1.0",
                    api_version="v1",
                    description="Advanced Autonomous Coding Agent Capability",
                    category="coding",
                    inputs={"repository": "string", "task_description": "string"},
                    outputs={"code_changes": "array", "test_results": "object", "review": "object"},
                    permissions=["READ", "WRITE", "EXECUTE"]
                )

        super().__init__(manifest)
        self.bus = bus or HermesBus()
        self.permission_manager = permission_manager or PermissionManager()
        self.metrics = CodingMetrics()
        
        # Initialize pipeline modules
        self.sandbox = SandboxManager()
        self.analyzer = RepositoryAnalyzer()
        self.planner = TaskPlanner()
        self.executor = CodeExecutor(permission_manager=self.permission_manager)
        self.test_runner = TestRunner(sandbox_manager=self.sandbox)
        self.reviewer = CodeReviewer()
        self.git_manager = GitManager(sandbox_manager=self.sandbox, permission_manager=self.permission_manager)
        
        self.autonomous_loop = AutonomousLoop(
            max_attempts=3,
            bus=self.bus,
            permission_manager=self.permission_manager,
            metrics=self.metrics
        )
        
        self.initialized = False

    async def initialize(self) -> None:
        # Request default permissions in permission manager
        for perm_str in self.manifest.permissions:
            try:
                perm_enum = PermissionLevel(perm_str)
                self.permission_manager.request_permission(self.manifest.name, perm_enum)
            except Exception:
                pass
        self.initialized = True

    async def health_check(self) -> bool:
        return self.initialized

    async def shutdown(self) -> None:
        self.initialized = False

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        repo_path = inputs.get("repository", ".")
        task_desc = inputs.get("task_description", "Generic coding task")
        test_command = inputs.get("test_command", None)
        code_edits = inputs.get("code_edits", []) or inputs.get("initial_code_edits", [])  # Optional pre-defined edits list

        max_attempts = inputs.get("max_attempts", 3)

        loop = AutonomousLoop(
            max_attempts=max_attempts,
            bus=self.bus,
            permission_manager=self.permission_manager,
            metrics=self.metrics
        )

        report = await loop.run(
            repo_path=repo_path,
            task_description=task_desc,
            test_command=test_command,
            initial_code_edits=code_edits,
            capability_name=self.manifest.name
        )

        repo_context = self.analyzer.analyze(repo_path)
        plan = self.planner.plan_task(task_desc, repo_context)

        return {
            "status": report.status,
            "repository_context": repo_context.to_dict(),
            "plan": plan.to_dict(),
            "code_changes": [
                {
                    "file_path": att["file"],
                    "action": att.get("action", "modified")
                }
                for a in report.history.attempts
                for att in a.changes_made
            ],
            "test_results": report.test_results,
            "review": report.review,
            "metrics": report.metrics,
            "history": report.history.to_dict()
        }

