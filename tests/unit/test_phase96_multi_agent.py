"""Unit Tests for Phase 96: Multi-Agent Operating System."""

import pytest
import time
from pathlib import Path
from jarvisx.multi_agent.models import AgentMessage, AgentRole, MessageType, SubTask
from jarvisx.multi_agent.agent_bus import AgentCommunicationBus
from jarvisx.multi_agent.alfred_master import AlfredMasterCoordinator
from jarvisx.multi_agent.research_agent import ResearchAgent
from jarvisx.multi_agent.coding_agent import CodingAgent
from jarvisx.multi_agent.friday_tactical import FridayTacticalAgent
from jarvisx.multi_agent.multi_agent_orchestrator import MultiAgentOrchestrator
from jarvisx.proactive.proactive_memory import ProactiveMemory


def test_agent_bus_pub_sub_and_replay():
    db_file = "var/test_agents/test_bus.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    bus = AgentCommunicationBus(db_file)
    received = []

    bus.subscribe("CODER", lambda msg: received.append(msg))

    msg = AgentMessage(
        id="m1",
        sender="ALFRED",
        recipient="CODER",
        msg_type=MessageType.TASK_REQUEST,
        topic="CODE_GEN",
        payload={"task_id": "t1"},
        timestamp=time.time()
    )
    bus.publish(msg)

    assert len(received) == 1
    assert received[0].topic == "CODE_GEN"

    # Test Message Replay
    replay_count = bus.replay_messages()
    assert replay_count >= 1
    assert len(received) == 2


def test_agent_capability_matching_and_permission_scopes():
    bus = AgentCommunicationBus("var/test_agents/test_cap_bus.db")
    researcher = ResearchAgent(bus)
    coder = CodingAgent(bus)
    friday = FridayTacticalAgent(bus)
    alfred = AlfredMasterCoordinator(bus)

    assert researcher.capability.permission_scope == "read_only"
    assert coder.capability.permission_scope == "project_dir"
    assert friday.capability.permission_scope == "system_exec"
    assert alfred.capability.permission_scope == "coordination"


def test_initiative_feedback_loop_phase95_5():
    db_file = "var/test_agents/test_feedback.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = ProactiveMemory(db_file)
    res = mem.record_initiative_outcome(
        initiative_id="java_revision_001",
        outcome="SUCCESS",
        before_mastery=38.0,
        after_mastery=62.0,
        confidence_accuracy=0.95
    )

    assert res["improvement_delta"] == 24.0
    assert res["outcome"] == "SUCCESS"

    outcomes = mem.list_initiative_outcomes()
    assert len(outcomes) == 1
    assert outcomes[0]["improvement_delta"] == 24.0


def test_multi_agent_team_mission_execution():
    orchestrator = MultiAgentOrchestrator()
    res = orchestrator.run_team_mission(
        objective="Build a FastAPI weather microservice with unit tests",
        project_name="test_weather_service"
    )

    assert res.status == "COMPLETED"
    assert len(res.subtasks) == 3
    assert len(res.artifacts) >= 2
    assert Path(res.artifacts[0]).exists()
    assert Path(res.artifacts[1]).exists()


def test_team_status_and_explainability():
    orchestrator = MultiAgentOrchestrator()
    status = orchestrator.get_team_status()
    assert status["agent_count"] == 4

    logs = orchestrator.explain_mission()
    assert isinstance(logs, list)
