"""Unit tests for compound intent decomposition and multi-task orchestration in DynamicOrchestrator."""

from unittest.mock import MagicMock, patch
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator


def test_multitask_decomposition_two_tasks():
    orch = DynamicOrchestrator()
    tasks = orch._decompose_multitask("open mail and sent to vansh hi")
    assert len(tasks) == 2
    assert tasks[0] == "open mail"
    assert "sent to vansh hi" in tasks[1]


def test_multitask_decomposition_five_tasks():
    orch = DynamicOrchestrator()
    prompt = (
        "explain array implemntation using an example in vscode type the code infront of my eyes "
        "also book tickets to spiderman bnd in the best seats and stop at payment page "
        "and also open youtube and play esuresh "
        "also say hi in to vansh in whatsapp"
    )
    tasks = orch._decompose_multitask(prompt)
    assert len(tasks) >= 4
    assert any("array" in t for t in tasks)
    assert any("ticket" in t or "spiderman" in t for t in tasks)
    assert any("youtube" in t or "play" in t for t in tasks)
    assert any("whatsapp" in t or "vansh" in t for t in tasks)


def test_multitask_execution_runs_all_subtasks():
    orch = DynamicOrchestrator()
    with patch.object(orch, "_execute_single_voice_command") as mock_exec:
        mock_exec.side_effect = [
            {"action": "launch", "response": "Opening mail for you now, Sir."},
            {"action": "call_text", "response": "Dispatched communication request for 'vansh hi', Sir."}
        ]
        res = orch.execute_voice_command("open mail and sent to vansh hi", persona="ALFRED")
        assert res["action"] == "multitask"
        assert len(res["sub_tasks"]) == 2
        assert "Multitasking 2 tasks" in res["response"]
        assert "1. Opening mail" in res["response"]
        assert "2. Dispatched communication" in res["response"]
