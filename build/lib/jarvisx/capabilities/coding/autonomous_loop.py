from __future__ import annotations
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.permission_manager import PermissionManager
from jarvisx.capabilities.coding.metrics import CodingMetrics
from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager
from jarvisx.capabilities.coding.pipeline.repository_analyzer import RepositoryAnalyzer
from jarvisx.capabilities.coding.pipeline.task_planner import TaskPlanner
from jarvisx.capabilities.coding.pipeline.code_executor import CodeExecutor
from jarvisx.capabilities.coding.pipeline.test_runner import TestRunner
from jarvisx.capabilities.coding.pipeline.code_reviewer import CodeReviewer
from jarvisx.capabilities.coding.pipeline.git_manager import GitManager
from jarvisx.capabilities.coding.execution_history import ExecutionHistory
from jarvisx.capabilities.coding.error_analyzer import ErrorAnalyzer
from jarvisx.capabilities.coding.repair_planner import RepairPlanner

@dataclass
class AutonomousLoopReport:
    status: str  # "success", "repaired_and_passed", "failed_max_retries", "completed_with_issues"
    total_attempts: int
    history: ExecutionHistory
    test_results: Dict[str, Any]
    review: Dict[str, Any]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "total_attempts": self.total_attempts,
            "history": self.history.to_dict(),
            "test_results": self.test_results,
            "review": self.review,
            "metrics": self.metrics
        }

class AutonomousLoop:
    def __init__(
        self,
        max_attempts: int = 3,
        bus: Optional[HermesBus] = None,
        permission_manager: Optional[PermissionManager] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.max_attempts = max_attempts
        self.bus = bus or HermesBus()
        self.permission_manager = permission_manager or PermissionManager()
        self.metrics = metrics or CodingMetrics()

        self.sandbox = SandboxManager()
        self.analyzer = RepositoryAnalyzer()
        self.planner = TaskPlanner()
        self.executor = CodeExecutor(permission_manager=self.permission_manager)
        self.test_runner = TestRunner(sandbox_manager=self.sandbox)
        self.reviewer = CodeReviewer()
        self.git_manager = GitManager(sandbox_manager=self.sandbox, permission_manager=self.permission_manager)
        self.error_analyzer = ErrorAnalyzer()
        self.repair_planner = RepairPlanner()

    async def run(
        self,
        repo_path: str,
        task_description: str,
        test_command: Optional[str] = None,
        initial_code_edits: Optional[List[Dict[str, str]]] = None,
        capability_name: str = "coding_agent"
    ) -> AutonomousLoopReport:
        history = ExecutionHistory(mission_id=f"mission_{int(time.time())}")
        start_time = time.time()

        # Step 1: Hermes Event - Mission Started
        await self.bus.publish(Event(
            type="coding.task.started",
            source="autonomous_loop",
            payload={"repo": repo_path, "task": task_description, "max_attempts": self.max_attempts}
        ))

        # Step 2: Repository Context & Planning
        repo_context = self.analyzer.analyze(repo_path)
        plan = self.planner.plan_task(task_description, repo_context)

        await self.bus.publish(Event(
            type="coding.plan.created",
            source="task_planner",
            payload=plan.to_dict()
        ))

        # Step 3: Apply Initial Edits
        file_changes = []
        if initial_code_edits:
            for edit in initial_code_edits:
                rec = self.executor.write_file(
                    repo_root=repo_path,
                    relative_path=edit["file"],
                    content=edit["content"],
                    capability_name=capability_name
                )
                file_changes.append(rec)
        else:
            for step in plan.steps:
                if step.target_file and step.action_type in ["create", "modify"]:
                    target_p = Path(repo_path) / step.target_file
                    existing_str = target_p.read_text(encoding="utf-8", errors="ignore") if target_p.exists() else ""
                    if "# Auto-generated code" not in existing_str:
                        default_content = existing_str + f"\n# Auto-generated code for {step.title}\n# Task: {task_description}\n"
                        rec = self.executor.write_file(
                            repo_root=repo_path,
                            relative_path=step.target_file,
                            content=default_content,
                            capability_name=capability_name
                        )
                        file_changes.append(rec)
                    break



        await self.bus.publish(Event(
            type="coding.code.modified",
            source="code_executor",
            payload={"changes_count": len(file_changes)}
        ))

        # Step 4: Autonomous Loop Execution (Test -> Fail -> Analyze -> Repair -> Re-test)
        attempt_num = 1
        current_test_res = None
        successful_repair = False

        while attempt_num <= self.max_attempts:
            attempt_start = time.time()
            current_test_res = await self.test_runner.run_tests(
                repo_path=repo_path,
                test_command=test_command
            )
            self.metrics.record_test_run(current_test_res.passed)

            await self.bus.publish(Event(
                type="coding.tests.completed",
                source="test_runner",
                payload={"attempt": attempt_num, "passed": current_test_res.passed}
            ))

            if current_test_res.passed:
                history.record_attempt(
                    attempt_number=attempt_num,
                    changes_made=[{"file": fc.file_path, "action": fc.action} for fc in file_changes],
                    tests_executed=True,
                    test_passed=True,
                    duration_seconds=time.time() - attempt_start
                )
                if attempt_num > 1:
                    successful_repair = True
                    self.metrics.record_auto_repair(success=True)
                break

            # Tests Failed: Begin Debugging & Self-Repair Protocol
            failures = [f"Exit Code {current_test_res.exit_code}: {current_test_res.stderr or current_test_res.stdout}"]
            
            # Analyze error traceback
            debug_context = self.error_analyzer.analyze_traceback(
                stderr_output=current_test_res.stderr,
                stdout_output=current_test_res.stdout
            )

            await self.bus.publish(Event(
                type="coding.repair.started",
                source="error_analyzer",
                payload={"attempt": attempt_num, "debugging_context": debug_context.to_dict()}
            ))

            if attempt_num >= self.max_attempts:
                # Reached maximum allowed repair attempts
                history.record_attempt(
                    attempt_number=attempt_num,
                    changes_made=[{"file": fc.file_path, "action": fc.action} for fc in file_changes],
                    tests_executed=True,
                    test_passed=False,
                    failures=failures,
                    duration_seconds=time.time() - attempt_start
                )
                self.metrics.record_auto_repair(success=False)
                break

            # Generate and apply repair plan
            repair_plan = self.repair_planner.create_repair_plan(repo_path, debug_context)
            repair_rec = self.repair_planner.apply_repair_plan(
                repo_path=repo_path,
                repair_plan=repair_plan,
                executor=self.executor,
                capability_name=capability_name
            )
            file_changes.append(repair_rec)

            await self.bus.publish(Event(
                type="coding.repair.applied",
                source="repair_planner",
                payload={"attempt": attempt_num, "repair_plan": repair_plan.to_dict()}
            ))

            history.record_attempt(
                attempt_number=attempt_num,
                changes_made=[{"file": repair_rec.file_path, "action": repair_rec.action}],
                tests_executed=True,
                test_passed=False,
                failures=failures,
                successful_fixes=[repair_plan.proposed_fix_description],
                duration_seconds=time.time() - attempt_start
            )

            attempt_num += 1

        # Step 5: Final Review & Status Determination
        review_result = self.reviewer.review_changes(file_changes)
        self.metrics.record_review()

        await self.bus.publish(Event(
            type="coding.review.completed",
            source="code_reviewer",
            payload=review_result.to_dict()
        ))

        total_duration = time.time() - start_time
        final_passed = current_test_res.passed if current_test_res else False
        overall_success = final_passed and review_result.approved
        self.metrics.record_task_completed(duration_seconds=total_duration, success=overall_success)

        if successful_repair and overall_success:
            status_str = "repaired_and_passed"
            await self.bus.publish(Event(
                type="coding.repair.passed",
                source="autonomous_loop",
                payload={"attempts": len(history.attempts)}
            ))
        elif overall_success:
            status_str = "success"
        elif not final_passed:
            status_str = "failed_max_retries"
        else:
            status_str = "completed_with_issues"

        await self.bus.publish(Event(
            type="coding.loop.completed",
            source="autonomous_loop",
            payload={"status": status_str, "total_attempts": len(history.attempts)}
        ))

        return AutonomousLoopReport(
            status=status_str,
            total_attempts=len(history.attempts),
            history=history,
            test_results={
                "passed": final_passed,
                "command": current_test_res.command if current_test_res else test_command,
                "stdout": current_test_res.stdout if current_test_res else "",
                "stderr": current_test_res.stderr if current_test_res else ""
            },
            review=review_result.to_dict(),
            metrics=self.metrics.to_dict()
        )
