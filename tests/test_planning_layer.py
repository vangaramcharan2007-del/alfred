import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from jarvisx.core.planning.dependency_graph import DependencyGraph
from jarvisx.core.planning.plan_validator import PlanValidator
from jarvisx.core.planning.progress_tracker import ProgressTracker
from jarvisx.core.planning.execution_monitor import ExecutionMonitor
from jarvisx.core.planning.objective_manager import ObjectiveManager
from jarvisx.core.providers.provider_router import ProviderRouter

@pytest.fixture
def mock_router():
    router = ProviderRouter(fallback_manager=None)
    router.route_with_failover = AsyncMock()
    return router

def test_dependency_graph_cycle():
    tasks = [
        {"id": "A", "depends_on": ["B"]},
        {"id": "B", "depends_on": ["A"]}
    ]
    graph = DependencyGraph(tasks)
    assert graph.detect_cycles() is True

def test_dependency_graph_valid():
    tasks = [
        {"id": "A", "depends_on": []},
        {"id": "B", "depends_on": ["A"]},
        {"id": "C", "depends_on": ["A"]}
    ]
    graph = DependencyGraph(tasks)
    assert graph.detect_cycles() is False
    
    executable = graph.get_executable_tasks(set())
    assert len(executable) == 1
    assert executable[0]["id"] == "A"
    
    executable = graph.get_executable_tasks({"A"})
    assert len(executable) == 2
    assert {"B", "C"} == {t["id"] for t in executable}

def test_plan_validator():
    valid_plan = [
        {
            "id": "t1", 
            "description": "Create", 
            "tool": "file_ops", 
            "method": "create_file", 
            "args": {"filepath": "test.txt", "content": ""},
            "depends_on": []
        }
    ]
    is_valid, err = PlanValidator.validate(valid_plan)
    assert is_valid is True
    
    invalid_plan = [{"id": "t1"}] # missing keys
    is_valid, err = PlanValidator.validate(invalid_plan)
    assert is_valid is False

@pytest.mark.asyncio
async def test_execution_monitor():
    monitor = ExecutionMonitor()
    
    # Test valid method
    task = {
        "id": "t1", 
        "tool": "file_ops", 
        "method": "create_file", 
        "args": {"filepath": "temp_test_planning.txt", "content": "hello"}
    }
    res = await monitor.execute_task(task)
    assert res["success"] is True
    
    # cleanup
    del_task = {
        "id": "t2",
        "tool": "file_ops",
        "method": "delete_file",
        "args": {"filepath": "temp_test_planning.txt"}
    }
    await monitor.execute_task(del_task)

@pytest.mark.asyncio
async def test_objective_manager_success(mock_router):
    manager = ObjectiveManager(mock_router)
    
    # Mock the LLM returning a valid JSON plan
    mock_router.route_with_failover.return_value = '''
    [
        {
            "id": "task_1",
            "description": "Mock file creation",
            "tool": "file_ops",
            "method": "create_file",
            "args": {"filepath": "test_mock.txt", "content": "mock"},
            "confidence": 0.99,
            "depends_on": []
        },
        {
            "id": "task_2",
            "description": "Mock file deletion",
            "tool": "file_ops",
            "method": "delete_file",
            "args": {"filepath": "test_mock.txt"},
            "confidence": 0.99,
            "depends_on": ["task_1"]
        }
    ]
    '''
    
    result = await manager.execute_objective("Test objective")
    assert result["success"] is True
    assert result["tracker"]["state"] == "COMPLETED"
    assert "task_1" in result["tracker"]["completed_tasks"]
    assert "task_2" in result["tracker"]["completed_tasks"]
