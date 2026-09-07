"""Unit tests for AcademicSentinelAgent integration into UnifiedAgentFleet and MetaOrchestrator."""

import pytest
from jarvisx.orchestration.unified_agent_fleet import UnifiedAgentFleet
from jarvisx.orchestration.meta_orchestrator import MetaOrchestrator
from jarvisx.agents.registry import AgentRegistry
from jarvisx.academic.agent import AcademicSentinelAgent, get_academic_agent


def test_fleet_has_academic_sentinel():
    """Verify AcademicSentinelAgent is registered in the UnifiedAgentFleet singleton."""
    fleet = UnifiedAgentFleet.get_instance()
    agent = fleet.get_agent("AcademicSentinelAgent")
    assert agent is not None
    assert isinstance(agent, AcademicSentinelAgent)
    assert "academic_sentinel" in agent.capabilities
    assert "homework_solving" in agent.capabilities
    assert "srm_ecurricula_automation" in agent.capabilities
    assert "srm_step_java_solver" in agent.capabilities


def test_fleet_homework_agent_alias():
    """Verify 'HomeworkAgent' alias resolves to the AcademicSentinelAgent."""
    fleet = UnifiedAgentFleet.get_instance()
    agent = fleet.get_agent("HomeworkAgent")
    assert agent is not None
    assert isinstance(agent, AcademicSentinelAgent)


def test_agent_status_telemetry():
    """Verify operational status reports student info and active metrics."""
    agent = AcademicSentinelAgent(enable_voice=False, enable_toast=False)
    st = agent.get_status()
    assert st["agent_name"] == "AcademicSentinelAgent"
    assert st["student"] == "RAM CHARAN VANGA"
    assert st["reg_no"] == "RA2511027010164"
    assert "BIG DATA ANALYTICS" in st["department"]
    assert "tasks_tracked" in st
    assert "tasks_submitted" in st


def test_fleet_dispatch_status():
    """Verify async dispatch through UnifiedAgentFleet returns valid status."""
    import asyncio
    fleet = UnifiedAgentFleet.get_instance()
    res = asyncio.run(fleet.dispatch_task_async("AcademicSentinelAgent", {"action": "status"}))
    assert res["status"] == "completed"
    assert res["agent"] == "AcademicSentinelAgent"
    assert res["real_agent_invoked"] is True
    result_data = res["result"]
    assert result_data["student"] == "RAM CHARAN VANGA"
    assert result_data["reg_no"] == "RA2511027010164"


def test_meta_orchestrator_requirements_analysis():
    """Verify MetaOrchestrator classifies academic tasks to Academic_Sentinel role."""
    orchestrator = MetaOrchestrator.get_instance()
    roles1 = orchestrator._analyze_requirements("Submit my homework for CS201")
    assert "Academic_Sentinel" in roles1

    roles2 = orchestrator._analyze_requirements("Solve the NPTEL week 4 assignment and upload to portal")
    assert "Academic_Sentinel" in roles2

    roles3 = orchestrator._analyze_requirements("Check SRM STEP Java lab exercises on ecurricula")
    assert "Academic_Sentinel" in roles3


def test_meta_orchestrator_task_orchestration():
    """Verify MetaOrchestrator orchestrates and executes an academic task."""
    orchestrator = MetaOrchestrator.get_instance()
    res = orchestrator.orchestrate_task("Solve homework problem on ecurricula")
    assert res["status"] == "success"
    assert "Academic_Sentinel" in res["agents_provisioned"]
    assert any("Academic_Sentinel completed" in log for log in res["execution_logs"])


def test_agent_registry_integration():
    """Verify Alfred's central AgentRegistry can register and discover AcademicSentinelAgent."""
    registry = AgentRegistry()
    agent = AcademicSentinelAgent(enable_voice=False, enable_toast=False)
    registry.register(agent)
    
    assert registry.get_agent("AcademicSentinelAgent") is agent
    matched = registry.discover("srm_step_java_solver")
    assert "AcademicSentinelAgent" in matched
    matched_all = registry.discover()
    assert "AcademicSentinelAgent" in matched_all
