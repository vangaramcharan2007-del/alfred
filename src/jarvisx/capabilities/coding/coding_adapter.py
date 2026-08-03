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
                    version=data.get("version", "1.0.0"),
                    api_version=data.get("api_version", "v1"),
                    description=data.get("description", "Advanced Coding Agent Capability"),
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
                    version="1.0.0",
                    api_version="v1",
                    description="Advanced Coding Agent Capability",
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
        start_time = time.time()
        
        repo_path = inputs.get("repository", ".")
        task_desc = inputs.get("task_description", "Generic coding task")
        test_command = inputs.get("test_command", None)
        code_edits = inputs.get("code_edits", [])  # Optional pre-defined edits list

        # Step 1: Hermes Event - Task Requested
        await self.bus.publish(Event(
            type="coding.task.started",
            source="coding_adapter",
            payload={"repo": repo_path, "task": task_desc}
        ))

        # Step 2: Repository Analysis
        repo_context = self.analyzer.analyze(repo_path)

        # Step 3: Task Planning (Planner Agent)
        plan = self.planner.plan_task(task_desc, repo_context)
        await self.bus.publish(Event(
            type="coding.plan.created",
            source="task_planner",
            payload=plan.to_dict()
        ))

        # Step 4: Code Execution (Developer Agent)
        file_changes = []
        if code_edits:
            for edit in code_edits:
                rec = self.executor.write_file(
                    repo_root=repo_path,
                    relative_path=edit["file"],
                    content=edit["content"],
                    capability_name=self.manifest.name
                )
                file_changes.append(rec)
        else:
            # Generate default change according to plan
            for step in plan.steps:
                if step.target_file and step.action_type in ["create", "modify"]:
                    default_content = f"# Auto-generated code for {step.title}\n# Task: {task_desc}\n\ndef calculator_handler(op: str, a: float, b: float):\n    if op == 'add': return a + b\n    if op == 'sub': return a - b\n    if op == 'mul': return a * b\n    if op == 'div': return a / b if b != 0 else 'error'\n    return None\n"
                    rec = self.executor.write_file(
                        repo_root=repo_path,
                        relative_path=step.target_file,
                        content=default_content,
                        capability_name=self.manifest.name
                    )
                    file_changes.append(rec)
                    break

        await self.bus.publish(Event(
            type="coding.code.modified",
            source="code_executor",
            payload={"changes_count": len(file_changes)}
        ))

        # Step 5: Test Execution (Tester Agent)
        test_result = await self.test_runner.run_tests(
            repo_path=repo_path,
            test_command=test_command
        )
        self.metrics.record_test_run(test_result.passed)

        await self.bus.publish(Event(
            type="coding.tests.completed",
            source="test_runner",
            payload={"passed": test_result.passed}
        ))

        # Step 6: Code Review (Reviewer Agent)
        review_result = self.reviewer.review_changes(file_changes)
        self.metrics.record_review()

        await self.bus.publish(Event(
            type="coding.review.completed",
            source="code_reviewer",
            payload=review_result.to_dict()
        ))

        duration = time.time() - start_time
        success = test_result.passed and review_result.approved
        self.metrics.record_task_completed(duration_seconds=duration, success=success)

        return {
            "status": "success" if success else "completed_with_issues",
            "repository_context": repo_context.to_dict(),
            "plan": plan.to_dict(),
            "code_changes": [
                {
                    "file_path": fc.file_path,
                    "action": fc.action,
                    "content_after": fc.content_after
                } for fc in file_changes
            ],
            "test_results": {
                "passed": test_result.passed,
                "total_tests": test_result.total_tests,
                "passed_count": test_result.passed_count,
                "failed_count": test_result.failed_count,
                "command": test_result.command
            },
            "review": review_result.to_dict(),
            "metrics": self.metrics.to_dict()
        }
