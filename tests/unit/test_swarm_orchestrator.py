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

        # The graceful fallback is a single runnable task, not a fabricated
        # decomposition. decompose() logs "running as single task" and returns
        # exactly one entry; inventing two sub-tasks from an intent the LLM
        # failed to split would mean sending the same prompt to two agents and
        # calling that parallelism.
        #
        # This used to assert len(subtasks) >= 2 and require a "role" key on
        # each task. Neither matched the source: the fallback returns one task,
        # and the keys decompose() asks the LLM for are task_id, description
        # and prompt -- there is no "role" anywhere in its prompt.
        assert len(subtasks) == 1
        assert subtasks[0]["task_id"] == "main"
        assert subtasks[0]["prompt"] == intent
        assert all("task_id" in t and "description" in t and "prompt" in t for t in subtasks)


@pytest.mark.asyncio
async def test_execute_swarm_concurrent_execution():
    """Verify concurrent execution of sub-agents and synthesis."""
    orchestrator = SwarmOrchestrator(model="qwen2.5-coder:1.5b", max_agents=3, timeout_per_agent=10.0)

    # Mock decompose and subagent responses
    async def fake_chat(model, messages):
        user_msg = messages[-1]["content"]

        # decompose() sends "Break this complex request into 2-N independent
        # sub-tasks...". This mock used to branch on "Decompose this intent",
        # a string the source has never sent, so every call fell through to
        # the default branch and the fan-out below was never exercised.
        if "Break this complex request into" in user_msg:
            return {
                "message": {
                    "content": """[
                        {"task_id": "t1", "description": "Task 1", "prompt": "Prompt 1"},
                        {"task_id": "t2", "description": "Task 2", "prompt": "Prompt 2"}
                    ]"""
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

    # Asserted against the schema execute_swarm() actually returns. The
    # previous assertions named subtasks_count, completed_count,
    # timed_out_count, failed_count, subtasks, unified_response,
    # swarms_executed and total_subtasks_executed -- none of which this
    # module has ever produced. There is also no synthesis step: the module
    # never sends a system message, so the "Lead Swarm Synthesizer" branch
    # this test used to mock was unreachable.
    assert res["status"] == "COMPLETED"
    assert res["agents_deployed"] == 2
    assert res["agents_succeeded"] == 2
    assert res["agents_timed_out"] == 0
    assert res["agents_failed"] == 0
    assert len(res["individual_results"]) == 2
    assert "Output for Prompt 1" in res["merged_response"]
    assert "Output for Prompt 2" in res["merged_response"]


@pytest.mark.asyncio
async def test_execute_swarm_timeout_handling():
    """Verify that slow sub-agents are timed out without crashing the swarm."""
    orchestrator = SwarmOrchestrator(model="qwen2.5-coder:1.5b", max_agents=2, timeout_per_agent=0.1)

    async def fake_chat_with_delay(model, messages):
        user_msg = messages[-1]["content"]

        # See the note in test_execute_swarm_concurrent_execution: this branched
        # on "Decompose this intent", which decompose() never sends, so
        # decomposition always fell back to a single task and the slow branch
        # below could never be reached. The timeout path this test exists to
        # cover was never executed.
        if "Break this complex request into" in user_msg:
            return {
                "message": {
                    "content": """[
                        {"task_id": "fast", "description": "Fast Task", "prompt": "Fast prompt"},
                        {"task_id": "slow", "description": "Slow Task", "prompt": "Slow prompt"}
                    ]"""
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

    # One agent finishes, one exceeds timeout_per_agent=0.1 -- so the swarm is
    # PARTIAL, not COMPLETED and not FAILED. _run_agent() reports per-agent
    # status in lowercase ("success"/"timeout"/"error"); the uppercase
    # COMPLETED/TIMEOUT values asserted here before do not exist in the module.
    assert res["status"] == "PARTIAL"
    assert res["agents_deployed"] == 2
    assert res["agents_succeeded"] == 1
    assert res["agents_timed_out"] == 1
    assert res["agents_failed"] == 0
    assert any(t["status"] == "timeout" and t["task_id"] == "slow" for t in res["individual_results"])
    assert any(t["status"] == "success" and t["task_id"] == "fast" for t in res["individual_results"])
    # The timed-out agent produced nothing, so it must not appear in the merge.
    assert "Fast task done" in res["merged_response"]
    assert "Too late" not in res["merged_response"]


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
