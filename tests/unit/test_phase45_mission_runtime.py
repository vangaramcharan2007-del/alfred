"""Unit and mock integration tests for Phase 45: Mission Runtime.

Verifies end-to-end task execution loops, simulated agent workforce interaction via
AgentContract, fault recovery retries without infinite loops, and formatted reporting.
"""

import pytest
from typing import Any, Dict, List

from jarvisx.architecture import AgentContract
from jarvisx.runtime import (
    MissionRuntime,
    MissionState,
    MissionStatus,
    AgentDispatcher,
    RecoveryManager,
)


class MockResearchAgent(AgentContract):
    def __init__(self):
        super().__init__(
            name="research_agent",
            purpose="Analyze specifications and requirements",
            capabilities=["search", "requirements", "analysis"],
        )

    def execute(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        return {"status": "completed", "output": "Requirements successfully compiled."}

    def status(self) -> Dict[str, Any]:
        return {"state": "idle", "health": "100%"}

    def report(self) -> str:
        return f"{self.name}: Ready for research tasks."


class MockCodingAgent(AgentContract):
    def __init__(self):
        super().__init__(
            name="coding_agent",
            purpose="Implement architecture and feature code",
            capabilities=["coding", "refactoring", "scaffolding"],
        )

    def execute(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        return {"status": "completed", "output": "Code implementation cleanly finalized."}

    def status(self) -> Dict[str, Any]:
        return {"state": "idle", "health": "100%"}

    def report(self) -> str:
        return f"{self.name}: Ready for implementation tasks."


class MockTestingAgent(AgentContract):
    def __init__(self):
        super().__init__(
            name="testing_agent",
            purpose="Execute test suites and verify correctness",
            capabilities=["pytest", "lint", "verification"],
        )
        self.fail_count = 0
        self.trigger_failures = False

    def execute(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        if self.trigger_failures and self.fail_count < 2:
            self.fail_count += 1
            return {"status": "error", "error": "Missing dependency: numpy (Test build failed)"}
        return {"status": "completed", "output": "All verification tests passed."}

    def status(self) -> Dict[str, Any]:
        return {"state": "idle", "health": "100%"}

    def report(self) -> str:
        return f"{self.name}: Ready for testing tasks."


@pytest.fixture
def configured_runtime() -> MissionRuntime:
    dispatcher = AgentDispatcher()
    dispatcher.register_agent(MockResearchAgent())
    dispatcher.register_agent(MockCodingAgent())
    dispatcher.register_agent(MockTestingAgent())
    return MissionRuntime(dispatcher=dispatcher)


def test_weather_app_mission_success(configured_runtime: MissionRuntime):
    """Verify exact Phase 45 Success Criteria execution and status output."""
    tasks = [
        {"description": "Requirements analyzed", "agent": "research_agent"},
        {"description": "Architecture planned", "agent": "coding_agent"},
        {"description": "Implementation completed", "agent": "coding_agent"},
        {"description": "Tests passed", "agent": "testing_agent"},
    ]

    mission = configured_runtime.create("Weather App", tasks=tasks)
    assert mission.status == MissionStatus.PLANNING
    assert len(mission.tasks) == 4

    configured_runtime.execute(mission)
    assert mission.status == MissionStatus.COMPLETED
    assert len(mission.completed_tasks) == 4
    assert len(mission.failed_tasks) == 0

    report = configured_runtime.get_report(
        mission_id=mission.id,
        duration_minutes=42,
        changes_count=15,
        review_item="API key configuration",
    )

    expected_snippet = """ALFRED MISSION REPORT

Mission:
Weather App

Tasks:
✓ Requirements analyzed
✓ Architecture planned
✓ Implementation completed
✓ Tests passed

Duration:
42 minutes

Changes:
15 files modified

Human review required:
API key configuration"""
    assert report.strip() == expected_snippet.strip()


def test_automated_recovery_and_bounded_retry():
    """Verify RecoveryManager handles task failures up to 3 attempts without infinite loop."""
    dispatcher = AgentDispatcher()
    testing_agent = MockTestingAgent()
    testing_agent.trigger_failures = True  # Will fail twice before succeeding
    dispatcher.register_agent(testing_agent)

    recovery = RecoveryManager(max_retries=3)
    runtime = MissionRuntime(dispatcher=dispatcher, recovery=recovery)

    mission = runtime.create("Verify resilient pipeline", tasks=[{"description": "Run tests", "agent": "testing_agent"}])
    runtime.execute(mission)

    # Task should succeed on attempt 3
    assert mission.status == MissionStatus.COMPLETED
    assert testing_agent.fail_count == 2
    task_result = mission.tasks[0]
    assert task_result.status == "completed"
    assert task_result.retry_count == 2
    assert len(recovery.recovery_logs[task_result.task_id]) == 2


def test_escalation_after_max_retries():
    """Verify that persistent failures beyond max_retries cleanly escalate without infinite looping."""
    class AlwaysFailingAgent(AgentContract):
        def __init__(self):
            super().__init__(name="failing_agent", purpose="Fail constantly", capabilities=["fail"])

        def execute(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
            return {"status": "error", "error": "Fatal unresolvable segmentation fault"}

        def status(self) -> Dict[str, Any]:
            return {"state": "failed"}

        def report(self) -> str:
            return "Failed."

    dispatcher = AgentDispatcher()
    dispatcher.register_agent(AlwaysFailingAgent())
    recovery = RecoveryManager(max_retries=3)
    runtime = MissionRuntime(dispatcher=dispatcher, recovery=recovery)

    mission = runtime.create("Unresolvable task test", tasks=[{"description": "Compile core kernel", "agent": "failing_agent"}])
    runtime.execute(mission, max_iterations=20)

    # Must terminate as FAILED after 3 attempts
    assert mission.status == MissionStatus.FAILED
    task = mission.tasks[0]
    assert task.status == "failed"
    assert task.retry_count == 4  # Attempt 1 (initial) + 3 retries = attempt 4 triggers escalation
    assert "Escalate" in str(task.error) or len(recovery.recovery_logs[task.task_id]) == 4
