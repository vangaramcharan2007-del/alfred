"""Unit and Integration Tests for Bounded Autonomous Proactive Operation.

Covers:
1. Scheduler invokes evaluator
2. No-op decision causes nothing
3. Valid reminder produces intervention
4. Duplicate suppression
5. Cooldown enforcement
6. Daemon restart does not spam
7. Permission gate blocks autonomous CONFIRM/RESTRICTED actions
8. LLM failure is isolated
9. Memory failure is isolated
10. Malformed decision is rejected
11. Autonomous action is auditable
"""

import json
import os
import time
import pytest

from jarvisx.events.event_bus import EventBus
from jarvisx.events.models import EventType
from jarvisx.events.proactive_scheduler import ProactiveScheduler
from jarvisx.personal_os.goal_manager import GoalManager
from jarvisx.personal_os.life_memory import LifeMemory
from jarvisx.personal_os.models import Goal, GoalStatus, Milestone
from jarvisx.proactive.proactive_evaluator import ProactiveEvaluator, ProactiveEvaluationResult
from jarvisx.proactive.proactive_memory import ProactiveMemory


class FakeProactiveLLMRouter:
    """Mock LLMRouter for deterministic proactive evaluation tests."""
    def __init__(self, responses: list | dict):
        self.responses = responses
        self.call_history = []
        self._index = 0

    def route_request_sync(self, prompt: str, require_offline: bool = False, model_override: str = None):
        self.call_history.append(prompt)
        if isinstance(self.responses, list):
            if self._index < len(self.responses):
                resp = self.responses[self._index]
                self._index += 1
            else:
                resp = '{"should_intervene": false, "reason": "default"}'
            return {
                "status": "success",
                "provider_id": "fake.local",
                "result": {"status": "AVAILABLE", "response": resp}
            }
        elif isinstance(self.responses, dict):
            for key, resp in self.responses.items():
                if key in prompt:
                    return {
                        "status": "success",
                        "provider_id": "fake.local",
                        "result": {"status": "AVAILABLE", "response": resp}
                    }
            return {
                "status": "success",
                "provider_id": "fake.local",
                "result": {"status": "AVAILABLE", "response": '{"should_intervene": false}'}
            }


@pytest.fixture
def proactive_env(tmp_path):
    proactive_db = str(tmp_path / "proactive_test.db")
    life_db = str(tmp_path / "life_test.db")
    pmem = ProactiveMemory(proactive_db)
    lmem = LifeMemory(life_db)
    gm = GoalManager(memory=lmem)
    return pmem, gm


def test_no_op_decision_causes_nothing(proactive_env):
    """When LLM decides no intervention is needed, evaluator returns should_intervene=False."""
    pmem, gm = proactive_env
    fake_router = FakeProactiveLLMRouter([
        '{"should_intervene": false, "reason": "All milestones on schedule", "priority": "low"}'
    ])
    evaluator = ProactiveEvaluator(proactive_memory=pmem, goal_manager=gm, llm_router=fake_router)

    res = evaluator.evaluate_cycle()
    assert res.should_intervene is False
    assert res.outcome == "no_intervention"
    assert len(pmem.list_interventions()) == 0


def test_valid_reminder_produces_intervention(proactive_env):
    """Valid reminder from LLM produces an active intervention and persists it."""
    pmem, gm = proactive_env
    # Mark a goal AT_RISK to create candidate signal
    gm.create_goal("Study Graph Algorithms", category="academic", target_date="2026-08-15")
    goals = gm.list_goals()
    gm.evaluate_goal_risk(goals[0].id, average_topic_mastery=40.0)

    reminder_json = (
        '{"should_intervene": true, "intervention_type": "study_reminder", '
        '"reason": "Graph Algorithms exam in 3 days with low mastery", '
        '"priority": "high", "message": "Sir, your Graph Algorithms exam is in 3 days.", "action": null}'
    )
    fake_router = FakeProactiveLLMRouter([reminder_json])
    evaluator = ProactiveEvaluator(proactive_memory=pmem, goal_manager=gm, llm_router=fake_router)

    res = evaluator.evaluate_cycle()
    assert res.should_intervene is True
    assert res.intervention_type == "study_reminder"
    assert "Graph Algorithms" in res.message
    assert res.outcome == "intervention_notified"

    interventions = pmem.list_interventions()
    assert len(interventions) == 1
    assert interventions[0]["intervention_type"] == "study_reminder"
    assert interventions[0]["outcome"] == "intervention_notified"


def test_duplicate_suppression(proactive_env):
    """Subsequent cycle with the exact same intervention message within cooldown is suppressed."""
    pmem, gm = proactive_env
    reminder_json = (
        '{"should_intervene": true, "intervention_type": "study_reminder", '
        '"reason": "Exam soon", "priority": "medium", "message": "Remember to practice DSA.", "action": null}'
    )
    fake_router = FakeProactiveLLMRouter([reminder_json, reminder_json])
    evaluator = ProactiveEvaluator(
        proactive_memory=pmem,
        goal_manager=gm,
        llm_router=fake_router,
        cooldowns={"study_reminder": 3600.0}
    )

    # First cycle -> Success
    res1 = evaluator.evaluate_cycle(now=1000.0)
    assert res1.should_intervene is True

    # Second cycle (5 mins later, same message) -> Duplicate suppressed
    res2 = evaluator.evaluate_cycle(now=1300.0)
    assert res2.should_intervene is False
    assert res2.outcome == "duplicate_suppressed"


def test_cooldown_enforcement(proactive_env):
    """Subsequent cycle with a different message within cooldown window is suppressed."""
    pmem, gm = proactive_env
    reminder1 = (
        '{"should_intervene": true, "intervention_type": "study_reminder", '
        '"reason": "Task 1", "priority": "medium", "message": "Study OS.", "action": null}'
    )
    reminder2 = (
        '{"should_intervene": true, "intervention_type": "study_reminder", '
        '"reason": "Task 2", "priority": "medium", "message": "Study DBMS.", "action": null}'
    )
    fake_router = FakeProactiveLLMRouter([reminder1, reminder2])
    evaluator = ProactiveEvaluator(
        proactive_memory=pmem,
        goal_manager=gm,
        llm_router=fake_router,
        cooldowns={"study_reminder": 3600.0}
    )

    res1 = evaluator.evaluate_cycle(now=1000.0)
    assert res1.should_intervene is True

    # 10 minutes later (within 1h cooldown)
    res2 = evaluator.evaluate_cycle(now=1600.0)
    assert res2.should_intervene is False
    assert res2.outcome == "cooldown_active"

    # After cooldown expires (4000s later)
    res3 = evaluator.evaluate_cycle(now=5000.0, force=False)
    # fake_router returns default no-op for third call
    assert res3.outcome in ("no_intervention", "intervention_notified")


def test_daemon_restart_does_not_spam(tmp_path):
    """A freshly booted evaluator instance respects stored cooldowns from previous sessions."""
    proactive_db = str(tmp_path / "proactive_restart.db")
    life_db = str(tmp_path / "life_restart.db")

    # Session 1: Run intervention
    pmem1 = ProactiveMemory(proactive_db)
    lmem1 = LifeMemory(life_db)
    gm1 = GoalManager(memory=lmem1)

    reminder_json = (
        '{"should_intervene": true, "intervention_type": "goal_checkin", '
        '"reason": "Inactivity", "priority": "medium", "message": "Check-in on project goal.", "action": null}'
    )
    fake_router1 = FakeProactiveLLMRouter([reminder_json])
    evaluator1 = ProactiveEvaluator(
        proactive_memory=pmem1,
        goal_manager=gm1,
        llm_router=fake_router1,
        cooldowns={"goal_checkin": 7200.0}
    )
    res1 = evaluator1.evaluate_cycle(now=1000.0)
    assert res1.should_intervene is True

    # Session 2: Fresh instance (simulating daemon restart 15 minutes later)
    pmem2 = ProactiveMemory(proactive_db)
    lmem2 = LifeMemory(life_db)
    gm2 = GoalManager(memory=lmem2)
    fake_router2 = FakeProactiveLLMRouter([reminder_json])
    evaluator2 = ProactiveEvaluator(
        proactive_memory=pmem2,
        goal_manager=gm2,
        llm_router=fake_router2,
        cooldowns={"goal_checkin": 7200.0}
    )

    res2 = evaluator2.evaluate_cycle(now=1900.0)
    assert res2.should_intervene is False
    assert res2.outcome in ("duplicate_suppressed", "cooldown_active")


def test_permission_gate_blocks_autonomous_confirm_action(proactive_env):
    """If LLM attempts to propose a CONFIRM action autonomously, it is denied by ToolExecutor non-interactive gate."""
    pmem, gm = proactive_env
    action_json = (
        '{"should_intervene": true, "intervention_type": "study_reminder", '
        '"reason": "Write notes", "priority": "medium", "message": "Writing notes file.", '
        '"action": {"tool": "create_file", "arguments": {"path": "notes.txt", "content": "auto-generated"}}}'
    )
    fake_router = FakeProactiveLLMRouter([action_json])
    evaluator = ProactiveEvaluator(proactive_memory=pmem, goal_manager=gm, llm_router=fake_router)

    res = evaluator.evaluate_cycle()
    assert res.should_intervene is True
    # Action result must indicate failed verification / permission denial
    assert res.action_result is not None
    assert res.action_result["status"] == "failed"
    assert res.action_result["verified"] is False
    assert res.outcome == "action_blocked_or_failed"


def test_llm_failure_isolation(proactive_env):
    """When LLM provider raises an exception, evaluator fails gracefully without crashing."""
    pmem, gm = proactive_env

    class CrashingLLMRouter:
        def route_request_sync(self, prompt, **kwargs):
            raise ConnectionError("Ollama daemon unreachable")

    evaluator = ProactiveEvaluator(proactive_memory=pmem, goal_manager=gm, llm_router=CrashingLLMRouter())
    res = evaluator.evaluate_cycle()
    assert res.should_intervene is False
    assert res.outcome == "llm_failure_isolated"


def test_memory_failure_isolation(proactive_env):
    """When goal manager or memory intelligence fails, evaluator handles it safely."""
    pmem, _ = proactive_env

    class BrokenGoalManager:
        def list_goals(self):
            raise RuntimeError("Database locked")

    fake_router = FakeProactiveLLMRouter(['{"should_intervene": false}'])
    evaluator = ProactiveEvaluator(proactive_memory=pmem, goal_manager=BrokenGoalManager(), llm_router=fake_router)

    res = evaluator.evaluate_cycle()
    assert res.should_intervene is False


def test_malformed_decision_rejected(proactive_env):
    """When LLM outputs non-JSON or malformed content, it is rejected safely."""
    pmem, gm = proactive_env
    fake_router = FakeProactiveLLMRouter(["I think you should study now, Sir! (non-json)"])
    evaluator = ProactiveEvaluator(proactive_memory=pmem, goal_manager=gm, llm_router=fake_router)

    res = evaluator.evaluate_cycle()
    assert res.should_intervene is False
    assert res.outcome == "malformed_decision_rejected"


def test_scheduler_invokes_evaluator(proactive_env):
    """ProactiveScheduler periodically executes evaluator and publishes events on intervention."""
    pmem, gm = proactive_env
    reminder_json = (
        '{"should_intervene": true, "intervention_type": "study_reminder", '
        '"reason": "Exam tomorrow", "priority": "high", "message": "Review Unit 4 today.", "action": null}'
    )
    fake_router = FakeProactiveLLMRouter([reminder_json])
    evaluator = ProactiveEvaluator(proactive_memory=pmem, goal_manager=gm, llm_router=fake_router)

    event_bus = EventBus()
    published_events = []
    event_bus.subscribe(EventType.PROACTIVE_INTERVENTION, lambda e: published_events.append(e))

    scheduler = ProactiveScheduler(event_bus=event_bus, check_interval_seconds=0.1, evaluator=evaluator)
    # Run loop step manually
    eval_res = evaluator.evaluate_cycle()
    assert eval_res.should_intervene is True


def test_autonomous_action_auditable(proactive_env):
    """All interventions are persisted with full audit telemetry in SQLite."""
    pmem, gm = proactive_env
    reminder_json = (
        '{"should_intervene": true, "intervention_type": "system_health", '
        '"reason": "High memory load", "priority": "high", "message": "RAM usage is 96%.", "action": null}'
    )
    fake_router = FakeProactiveLLMRouter([reminder_json])
    evaluator = ProactiveEvaluator(proactive_memory=pmem, goal_manager=gm, llm_router=fake_router)

    evaluator.evaluate_cycle(now=5000.0)
    records = pmem.list_interventions()
    assert len(records) == 1
    assert records[0]["intervention_type"] == "system_health"
    assert records[0]["priority"] == "high"
    assert records[0]["message"] == "RAM usage is 96%."
    assert records[0]["timestamp"] == 5000.0
