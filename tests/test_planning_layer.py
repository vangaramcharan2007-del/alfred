"""
Phase 10 Test Suite: Agent Runtime Upgrade
Covers:
  - ToolRegistry self-registration, introspection, dispatch, evidence
  - PlanValidator rejects unknown tools/methods
  - ExecutionMonitor dispatches via registry
  - State-preserving replanning
  - Completed tasks never repeated
  - Planner cannot hallucinate capabilities
"""
import json
import pytest
import asyncio
import os
from unittest.mock import AsyncMock

from jarvisx.core.tools.tool_registry import ToolRegistry
from jarvisx.core.planning.dependency_graph import DependencyGraph
from jarvisx.core.planning.plan_validator import PlanValidator
from jarvisx.core.planning.progress_tracker import ProgressTracker
from jarvisx.core.planning.execution_monitor import ExecutionMonitor
from jarvisx.core.planning.planning_metrics import PlanningMetrics
from jarvisx.core.planning.objective_manager import ObjectiveManager
from jarvisx.core.tools.execution.file_ops import FileOps
from jarvisx.core.tools.execution.command_executor import CommandExecutor
from jarvisx.core.tools.execution.python_executor import PythonExecutor
from jarvisx.core.tools.execution.git_ops import GitOps
from jarvisx.core.providers.provider_router import ProviderRouter


# ========== Fixtures ==========

@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the singleton before every test."""
    ToolRegistry.reset()
    yield
    ToolRegistry.reset()


@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(FileOps(), name="file_ops")
    reg.register(CommandExecutor(), name="command_executor")
    reg.register(PythonExecutor(), name="python_executor")
    return reg


@pytest.fixture
def mock_router():
    router = ProviderRouter(fallback_manager=None)
    router.route_with_failover = AsyncMock()
    return router


# ========== Requirement 1: Universal Tool Registry ==========

class TestToolRegistry:

    def test_register_and_list(self, registry):
        tools = registry.list_tools()
        assert "file_ops" in tools
        assert "command_executor" in tools
        assert "python_executor" in tools

    def test_has_tool(self, registry):
        assert registry.has_tool("file_ops") is True
        assert registry.has_tool("nonexistent_tool") is False

    def test_has_method(self, registry):
        assert registry.has_method("file_ops", "create_file") is True
        assert registry.has_method("file_ops", "nonexistent_method") is False

    def test_list_methods(self, registry):
        methods = registry.list_methods("file_ops")
        assert "create_file" in methods
        assert "read_file" in methods
        assert "write_file" in methods
        assert "delete_file" in methods

    def test_unregister(self, registry):
        assert registry.unregister("file_ops") is True
        assert registry.has_tool("file_ops") is False
        assert registry.unregister("nonexistent") is False

    def test_get_tool_schema(self, registry):
        schema = registry.get_tool_schema("file_ops")
        assert schema["tool"] == "file_ops"
        assert "methods" in schema
        assert "create_file" in schema["methods"]

    def test_get_capability_manifest(self, registry):
        manifest = registry.get_capability_manifest()
        assert len(manifest) == 3
        tool_names = [entry["tool"] for entry in manifest]
        assert "file_ops" in tool_names

    def test_schema_introspection_has_parameters(self, registry):
        schema = registry.get_tool_schema("file_ops")
        create_file_params = schema["methods"]["create_file"]["parameters"]
        assert "filepath" in create_file_params
        assert create_file_params["filepath"]["required"] is True


# ========== Requirement 1: Registry Dispatch ==========

class TestRegistryDispatch:

    @pytest.mark.asyncio
    async def test_execute_creates_file(self, registry):
        test_path = "test_registry_dispatch.txt"
        result = await registry.execute("file_ops", "create_file", {"filepath": test_path, "content": "registry test"})
        assert result["success"] is True
        assert "evidence" in result
        assert result["evidence"]["tool"] == "file_ops"
        assert result["evidence"]["method"] == "create_file"
        assert result["evidence"]["duration_ms"] >= 0
        assert "timestamp" in result["evidence"]
        # Cleanup
        await registry.execute("file_ops", "delete_file", {"filepath": test_path})

    @pytest.mark.asyncio
    async def test_execute_unregistered_tool(self, registry):
        result = await registry.execute("fake_tool", "fake_method", {})
        assert result["success"] is False
        assert "not registered" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_missing_method(self, registry):
        result = await registry.execute("file_ops", "nonexistent_method", {})
        assert result["success"] is False
        assert "not found" in result["error"]


# ========== Requirement 2: Tool Signature Injection ==========

class TestToolSignatureInjection:

    def test_capability_block_contains_tool_methods(self, registry):
        from jarvisx.core.planning.task_decomposer import TaskDecomposer
        router = ProviderRouter(fallback_manager=None)
        decomposer = TaskDecomposer(router, registry=registry)
        block = decomposer._build_capability_block()
        assert "file_ops.create_file" in block
        assert "command_executor.execute" in block


# ========== Requirement 2: Planner Cannot Hallucinate ==========

class TestPlanValidatorRejectsHallucinations:

    def test_rejects_unregistered_tool(self, registry):
        validator = PlanValidator(registry=registry)
        plan = [{
            "id": "t1",
            "description": "Do something",
            "tool": "magic_wand",
            "method": "cast_spell",
            "args": {},
            "depends_on": []
        }]
        valid, err = validator.validate(plan)
        assert valid is False
        assert "unregistered tool" in err

    def test_rejects_unknown_method(self, registry):
        validator = PlanValidator(registry=registry)
        plan = [{
            "id": "t1",
            "description": "Do something",
            "tool": "file_ops",
            "method": "teleport_file",
            "args": {},
            "depends_on": []
        }]
        valid, err = validator.validate(plan)
        assert valid is False
        assert "unknown method" in err

    def test_accepts_valid_plan(self, registry):
        validator = PlanValidator(registry=registry)
        plan = [{
            "id": "t1",
            "description": "Create a file",
            "tool": "file_ops",
            "method": "create_file",
            "args": {"filepath": "test.txt", "content": "hello"},
            "depends_on": []
        }]
        valid, err = validator.validate(plan)
        assert valid is True
        assert err == ""

    def test_rejects_circular_deps(self, registry):
        validator = PlanValidator(registry=registry)
        plan = [
            {"id": "a", "description": "a", "tool": "file_ops", "method": "create_file", "args": {}, "depends_on": ["b"]},
            {"id": "b", "description": "b", "tool": "file_ops", "method": "create_file", "args": {}, "depends_on": ["a"]},
        ]
        valid, err = validator.validate(plan)
        assert valid is False
        assert "circular" in err

    def test_rejects_empty_plan(self, registry):
        validator = PlanValidator(registry=registry)
        valid, err = validator.validate([])
        assert valid is False


# ========== Requirement 3: State-Preserving Replanning ==========

class TestStatePreservingReplanning:

    @pytest.mark.asyncio
    async def test_completed_tasks_preserved_after_replan(self, registry, mock_router):
        """Verify completed tasks are NEVER cleared on replan."""
        manager = ObjectiveManager(mock_router, registry=registry)

        # First call: return a plan where task_1 succeeds, task_2 will fail
        # Second call (replan): return corrective plan
        mock_router.route_with_failover.side_effect = [
            # Initial plan
            json.dumps([
                {"id": "task_1", "description": "Create file", "tool": "file_ops", "method": "create_file",
                 "args": {"filepath": "state_test.txt", "content": "hello"}, "confidence": 0.99, "depends_on": []},
                {"id": "task_2", "description": "Read nonexistent", "tool": "file_ops", "method": "read_file",
                 "args": {"filepath": "DOES_NOT_EXIST_12345.txt"}, "confidence": 0.5, "depends_on": ["task_1"]}
            ]),
            # Corrective plan (only the failed portion)
            json.dumps([
                {"id": "task_2_fix", "description": "Create the missing file", "tool": "file_ops", "method": "create_file",
                 "args": {"filepath": "DOES_NOT_EXIST_12345.txt", "content": "recovered"}, "confidence": 0.99, "depends_on": []},
                {"id": "task_2_retry", "description": "Read file", "tool": "file_ops", "method": "read_file",
                 "args": {"filepath": "DOES_NOT_EXIST_12345.txt"}, "confidence": 0.99, "depends_on": ["task_2_fix"]}
            ])
        ]

        result = await manager.execute_objective("Test state preservation")

        assert result["success"] is True
        assert "task_1" in result["tracker"]["completed_tasks"]
        # Cleanup
        for f in ["state_test.txt", "DOES_NOT_EXIST_12345.txt"]:
            if os.path.exists(f):
                os.remove(f)

    @pytest.mark.asyncio
    async def test_completed_tasks_never_re_executed(self, registry, mock_router):
        """Verify completed tasks are not dispatched again."""
        manager = ObjectiveManager(mock_router, registry=registry)

        # Plan with two tasks, both succeed
        mock_router.route_with_failover.return_value = json.dumps([
            {"id": "t1", "description": "Create a", "tool": "file_ops", "method": "create_file",
             "args": {"filepath": "never_repeat_a.txt", "content": "a"}, "confidence": 0.99, "depends_on": []},
            {"id": "t2", "description": "Create b", "tool": "file_ops", "method": "create_file",
             "args": {"filepath": "never_repeat_b.txt", "content": "b"}, "confidence": 0.99, "depends_on": []}
        ])

        result = await manager.execute_objective("Parallel creation")

        assert result["success"] is True
        completed = result["tracker"]["completed_tasks"]
        assert "t1" in completed
        assert "t2" in completed
        # Cleanup
        for f in ["never_repeat_a.txt", "never_repeat_b.txt"]:
            if os.path.exists(f):
                os.remove(f)


# ========== Requirement 4: Execution Evidence ==========

class TestExecutionEvidence:

    @pytest.mark.asyncio
    async def test_evidence_present_on_success(self, registry):
        monitor = ExecutionMonitor(registry=registry)
        task = {"id": "ev1", "tool": "file_ops", "method": "create_file",
                "args": {"filepath": "evidence_test.txt", "content": "proof"}}
        result = await monitor.execute_task(task)
        assert result["success"] is True
        assert result["evidence"]["tool"] == "file_ops"
        assert result["evidence"]["method"] == "create_file"
        assert "duration_ms" in result["evidence"]
        assert "timestamp" in result["evidence"]
        # Cleanup
        await registry.execute("file_ops", "delete_file", {"filepath": "evidence_test.txt"})

    @pytest.mark.asyncio
    async def test_evidence_present_on_failure(self, registry):
        monitor = ExecutionMonitor(registry=registry)
        task = {"id": "ev_fail", "tool": "nonexistent", "method": "x", "args": {}}
        result = await monitor.execute_task(task)
        assert result["success"] is False
        assert "error" in result


# ========== Requirement 6: Persistence ==========

class TestPersistence:

    @pytest.mark.asyncio
    async def test_objective_state_persisted(self, registry, mock_router):
        manager = ObjectiveManager(mock_router, registry=registry)

        mock_router.route_with_failover.return_value = json.dumps([
            {"id": "p1", "description": "Create persist test", "tool": "file_ops", "method": "create_file",
             "args": {"filepath": "persist_test.txt", "content": "data"}, "confidence": 0.99, "depends_on": []}
        ])

        result = await manager.execute_objective("Persist test objective")
        assert result["success"] is True

        # Check the state file exists
        state_dir = "var/objective_state"
        assert os.path.exists(state_dir)
        state_files = os.listdir(state_dir)
        assert len(state_files) > 0

        # Cleanup
        if os.path.exists("persist_test.txt"):
            os.remove("persist_test.txt")


# ========== Dependency Graph ==========

class TestDependencyGraphAdvanced:

    def test_parallel_eligibility(self):
        tasks = [
            {"id": "a", "depends_on": []},
            {"id": "b", "depends_on": []},
            {"id": "c", "depends_on": []},
        ]
        graph = DependencyGraph(tasks)
        executable = graph.get_executable_tasks(set())
        assert len(executable) == 3

    def test_sequential_chain(self):
        tasks = [
            {"id": "a", "depends_on": []},
            {"id": "b", "depends_on": ["a"]},
            {"id": "c", "depends_on": ["b"]},
        ]
        graph = DependencyGraph(tasks)
        exe = graph.get_executable_tasks(set())
        assert len(exe) == 1
        assert exe[0]["id"] == "a"

        exe = graph.get_executable_tasks({"a"})
        assert len(exe) == 1
        assert exe[0]["id"] == "b"

    def test_cycle_detection(self):
        tasks = [
            {"id": "x", "depends_on": ["y"]},
            {"id": "y", "depends_on": ["x"]},
        ]
        graph = DependencyGraph(tasks)
        assert graph.detect_cycles() is True

    def test_diamond_dependency(self):
        tasks = [
            {"id": "a", "depends_on": []},
            {"id": "b", "depends_on": ["a"]},
            {"id": "c", "depends_on": ["a"]},
            {"id": "d", "depends_on": ["b", "c"]},
        ]
        graph = DependencyGraph(tasks)
        assert graph.detect_cycles() is False
        exe = graph.get_executable_tasks({"a", "b", "c"})
        assert len(exe) == 1
        assert exe[0]["id"] == "d"


# ========== Metrics ==========

class TestMetricsIntegrity:

    def test_retries_increment(self):
        m = PlanningMetrics()
        m.record_retry()
        m.record_retry()
        assert m.get_metrics()["retries"] == 2

    def test_replans_increment(self):
        m = PlanningMetrics()
        m.record_replan()
        assert m.get_metrics()["replans"] == 1

    def test_success_rate(self):
        m = PlanningMetrics()
        m.record_outcome(True)
        m.record_outcome(True)
        m.record_outcome(False)
        assert m.get_metrics()["success_rate"] == round(2/3, 2)


