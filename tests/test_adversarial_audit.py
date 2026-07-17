import asyncio
import json
import os
import shutil
import time
import pytest
from unittest.mock import AsyncMock

from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.tools.tool_registry import ToolRegistry
from jarvisx.core.planning.objective_manager import ObjectiveManager
from jarvisx.core.planning.dependency_graph import DependencyGraph
from jarvisx.core.planning.plan_validator import PlanValidator
from jarvisx.core.planning.task_decomposer import TaskDecomposer


@pytest.fixture(autouse=True)
def reset_registry():
    ToolRegistry.reset()
    yield
    ToolRegistry.reset()
    if os.path.exists("var/objective_state"):
        shutil.rmtree("var/objective_state")


@pytest.fixture
def registry():
    return ToolRegistry.get_instance()


@pytest.fixture
def mock_router():
    router = ProviderRouter(fallback_manager=None)
    router.route_with_failover = AsyncMock()
    return router


class TestAdversarialAudit:

    def test_dependency_graph_structures(self):
        # 1. Circular dependency
        tasks_cycle = [
            {"id": "a", "depends_on": ["b"]},
            {"id": "b", "depends_on": ["a"]}
        ]
        assert DependencyGraph(tasks_cycle).detect_cycles() is True

        # 2. Self dependency
        tasks_self = [
            {"id": "a", "depends_on": ["a"]}
        ]
        assert DependencyGraph(tasks_self).detect_cycles() is True

        # 3. Diamond dependency
        tasks_diamond = [
            {"id": "root", "depends_on": []},
            {"id": "left", "depends_on": ["root"]},
            {"id": "right", "depends_on": ["root"]},
            {"id": "merge", "depends_on": ["left", "right"]}
        ]
        graph = DependencyGraph(tasks_diamond)
        assert graph.detect_cycles() is False
        exec_1 = graph.get_executable_tasks(set())
        assert len(exec_1) == 1 and exec_1[0]["id"] == "root"
        exec_2 = graph.get_executable_tasks({"root"})
        assert len(exec_2) == 2 and {t["id"] for t in exec_2} == {"left", "right"}
        exec_3 = graph.get_executable_tasks({"root", "left", "right"})
        assert len(exec_3) == 1 and exec_3[0]["id"] == "merge"

    @pytest.mark.asyncio
    async def test_hallucination_attack(self, registry):
        # Tools registered: none
        validator = PlanValidator(registry=registry)
        
        # Attack: hallucinated VisionTool
        attack_plan = [{
            "id": "t1",
            "description": "Take screenshot",
            "tool": "VisionTool",
            "method": "capture_desktop",
            "args": {},
            "depends_on": []
        }]
        
        valid, err = validator.validate(attack_plan)
        assert valid is False
        assert "unregistered tool:" in err.lower() or "unregistered tool" in err.lower()

    @pytest.mark.asyncio
    async def test_state_preserving_replanning_and_evidence(self, registry, mock_router):
        # Register a fake tool for testing execution
        class FakeTool:
            def success_method(self, **kwargs):
                return {"success": True, "evidence": {"tool": "fake", "method": "success_method", "duration_ms": 10, "timestamp": time.time()}}
            def fail_method(self, **kwargs):
                return {"success": False, "error": "Forced failure"}
                
        registry.register(FakeTool(), name="fake_tool")

        manager = ObjectiveManager(mock_router, registry=registry)

        # First call: return a plan with 4 steps. Step 3 will fail.
        mock_router.route_with_failover.side_effect = [
            # Initial Plan
            json.dumps([
                {"id": "step1", "description": "1", "tool": "fake_tool", "method": "success_method", "args": {}, "depends_on": []},
                {"id": "step2", "description": "2", "tool": "fake_tool", "method": "success_method", "args": {}, "depends_on": ["step1"]},
                {"id": "step3", "description": "3", "tool": "fake_tool", "method": "fail_method", "args": {}, "depends_on": ["step2"]},
                {"id": "step4", "description": "4", "tool": "fake_tool", "method": "success_method", "args": {}, "depends_on": ["step3"]}
            ]),
            # Corrective Plan (after step 3 fails). Assume LLM figures out how to fix it by using success_method.
            json.dumps([
                {"id": "step3_fixed", "description": "3 fixed", "tool": "fake_tool", "method": "success_method", "args": {}, "depends_on": []},
                {"id": "step4", "description": "4", "tool": "fake_tool", "method": "success_method", "args": {}, "depends_on": ["step3_fixed"]}
            ])
        ]

        result = await manager.execute_objective("Test objective")
        
        assert result["success"] is True
        tracker_status = result["tracker"]
        completed = tracker_status["completed_tasks"]
        
        # Verify step 1 and 2 were preserved and not rerun (if they were rerun, the flow wouldn't make sense, but we can verify completed_tasks)
        assert "step1" in completed
        assert "step2" in completed
        assert "step3_fixed" in completed
        assert "step4" in completed
        assert "step3" not in completed # It failed and was discarded from plan
        
        # Verify evidence format
        evidence = result["evidence"]
        assert "step1" in evidence
        assert "duration_ms" in evidence["step1"]
        assert evidence["step1"]["tool"] == "fake"

    @pytest.mark.asyncio
    async def test_persistence_validation(self, registry, mock_router):
        class DummyTool:
            def do_work(self, **kwargs):
                return {"success": True, "evidence": {"tool": "dummy", "method": "do_work", "duration_ms": 5, "timestamp": time.time()}}
        registry.register(DummyTool(), name="dummy_tool")

        manager = ObjectiveManager(mock_router, registry=registry)
        mock_router.route_with_failover.return_value = json.dumps([
            {"id": "persist_step1", "description": "persist", "tool": "dummy_tool", "method": "do_work", "args": {}, "depends_on": []}
        ])

        result = await manager.execute_objective("Persistence objective")
        assert result["success"] is True
        
        # Check that persistence file exists
        files = os.listdir("var/objective_state")
        assert len(files) == 1
        with open(os.path.join("var/objective_state", files[0]), "r") as f:
            data = json.load(f)
            
        assert data["objective"] == "Persistence objective"
        assert "tracker" in data
        assert "persist_step1" in data["tracker"]["completed_tasks"]
        assert "evidence" in data
        assert "persist_step1" in data["evidence"]
