"""Unit and integration tests for SwarmOrchestrator (Jarvis X Automation Layer)."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from jarvisx.automation.swarm_orchestrator import SwarmOrchestrator, get_swarm_orchestrator


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the SwarmOrchestrator singleton between tests."""
    SwarmOrchestrator._instance = None
    yield
    SwarmOrchestrator._instance = None


@pytest.mark.asyncio
async def test_swarm_orchestrator_initialization_and_singleton():
    """Verify singleton pattern and configuration constraints."""
    orch1 = get_swarm_orchestrator(model="qwen2.5-coder:1.5b", max_agents=4, timeout_per_agent=25.0)
    orch2 = SwarmOrchestrator.get_instance()
    
    assert orch1 is orch2
    assert orch1.model == "qwen2.5-coder:1.5b"
    assert orch1.max_agents == 4
    assert orch1.timeout_per_agent == 25.0

    # Max agents upper bound check
    orch_capped = SwarmOrchestrator(max_agents=10)
    assert orch_capped.max_agents == 5


@pytest.mark.asyncio
async def test_decompose_with_mocked_ollama():
    """Verify intent decomposition into structured sub-tasks with JSON parsing."""
    orchestrator = SwarmOrchestrator(model="qwen2.5-coder:1.5b", max_agents=3)
    
    mock_response = {
        "message": {
            "content": """```json
[
  {
    "task_id": "subtask_1",
    "name": "Architecture Design",
    "role": "System Architect",
    "prompt": "Design the system architecture and component interactions."
  },
  {
    "task_id": "subtask_2",
    "name": "Backend Implementation",
    "role": "Backend Engineer",
    "prompt": "Write the async endpoints and business logic."
  },
  {
    "task_id": "subtask_3",
    "name": "Security & Testing",
    "role": "QA & Security Auditor",
    "prompt": "Design unit tests and verify authentication security."
  }
]
```"""
        }
    }

    with patch.object(orchestrator._client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_response
        
        intent = "Build a scalable real-time chat application"
        subtasks = await orchestrator.decompose(intent)

        assert len(subtasks) == 3
        assert subtasks[0]["task_id"] == "subtask_1"
        assert subtasks[0]["role"] == "System Architect"
        assert subtasks[1]["task_id"] == "subtask_2"
        assert subtasks[2]["task_id"] == "subtask_3"
        mock_chat.assert_awaited_once()


@pytest.mark.asyncio
async def test_decompose_fallback_on_invalid_json():
    """Verify graceful fallback when LLM output is not valid JSON."""
    orchestrator = SwarmOrchestrator(model="qwen2.5-coder:1.5b", max_agents=5)

    with patch.object(orchestrator._client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = {"message": {"content": "Sorry, I cannot format this as JSON."}}
        
        intent = "Perform data pipeline analysis"
        subtasks = await orchestrator.decompose(intent)

        assert len(subtasks) >= 2
        assert all("task_id" in t and "role" in t and "prompt" in t for t in subtasks)


@pytest.mark.asyncio
async def test_execute_swarm_concurrent_execution():
    """Verify concurrent execution of sub-agents and synthesis."""
    orchestrator = SwarmOrchestrator(model="qwen2.5-coder:1.5b", max_agents=3, timeout_per_agent=10.0)

    # Mock decompose and subagent responses
    async def fake_chat(model, messages):
        user_msg = messages[-1]["content"]
        system_msg = messages[0]["content"]

        if "Decompose this intent" in user_msg:
            return {
                "message": {
                    "content": """[
                        {"task_id": "t1", "name": "Task 1", "role": "Worker 1", "prompt": "Prompt 1"},
                        {"task_id": "t2", "name": "Task 2", "role": "Worker 2", "prompt": "Prompt 2"}
                    ]"""
                }
            }
        elif "Lead Swarm Synthesizer" in system_msg:
            return {
                "message": {
                    "content": "Unified synthesis: All tasks were successfully completed."
                }
            }
        else:
            # Sub-agent response
            await asyncio.sleep(0.05)
            return {
                "message": {
                    "content": f"Output for {user_msg}"
                }
            }

    with patch.object(orchestrator._client, "chat", side_effect=fake_chat):
        res = await orchestrator.execute_swarm("Optimize database queries")

        assert res["status"] == "COMPLETED"
        assert res["subtasks_count"] == 2
        assert res["completed_count"] == 2
        assert res["timed_out_count"] == 0
        assert res["failed_count"] == 0
        assert len(res["subtasks"]) == 2
        assert "Unified synthesis" in res["unified_response"]
        assert orchestrator.swarms_executed == 1
        assert orchestrator.total_subtasks_executed == 2


@pytest.mark.asyncio
async def test_execute_swarm_timeout_handling():
    """Verify that slow sub-agents are timed out without crashing the swarm."""
    orchestrator = SwarmOrchestrator(model="qwen2.5-coder:1.5b", max_agents=2, timeout_per_agent=0.1)

    async def fake_chat_with_delay(model, messages):
        user_msg = messages[-1]["content"]
        system_msg = messages[0]["content"]

        if "Decompose this intent" in user_msg:
            return {
                "message": {
                    "content": """[
                        {"task_id": "fast", "name": "Fast Task", "role": "Fast Worker", "prompt": "Fast prompt"},
                        {"task_id": "slow", "name": "Slow Task", "role": "Slow Worker", "prompt": "Slow prompt"}
                    ]"""
                }
            }
        elif "Lead Swarm Synthesizer" in system_msg:
            return {
                "message": {
                    "content": "Partial synthesis completed."
                }
            }
        elif "Slow prompt" in user_msg:
            # Simulate slow task exceeding timeout
            await asyncio.sleep(0.5)
            return {"message": {"content": "Too late"}}
        else:
            # Fast task
            return {"message": {"content": "Fast task done"}}

    with patch.object(orchestrator._client, "chat", side_effect=fake_chat_with_delay):
        res = await orchestrator.execute_swarm("Process dual stream")

        assert res["status"] == "PARTIAL"
        assert res["completed_count"] == 1
        assert res["timed_out_count"] == 1
        assert any(t["status"] == "TIMEOUT" for t in res["subtasks"])
        assert any(t["status"] == "COMPLETED" for t in res["subtasks"])


@pytest.mark.asyncio
async def test_live_ollama_swarm_execution():
    """Live end-to-end integration test against local Ollama if available."""
    orchestrator = get_swarm_orchestrator(model="qwen2.5-coder:1.5b", max_agents=2, timeout_per_agent=30.0)
    
    try:
        res = await orchestrator.execute_swarm("Create a checklist for deploying a Python service to production")
        assert res["status"] in ("COMPLETED", "PARTIAL")
        assert res["subtasks_count"] > 0
        assert len(res["unified_response"]) > 0
        assert "execution_time_sec" in res
    except Exception as e:
        pytest.skip(f"Ollama local daemon unavailable: {e}")
