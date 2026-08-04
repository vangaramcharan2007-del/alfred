"""
Phase 51 Unit Test Suite — Unified Brain & Personal Intelligence Systems.
Tests Command Center, Morning Briefing, Coding Session, Study Mode, Knowledge Graph, Vision Agent, Interrupt Manager, and Proactive Engine.
"""
import pytest
import asyncio
from pathlib import Path
from jarvisx.core.command_center import PersonalCommandCenter
from jarvisx.cognition.morning_briefing import MorningBriefingGenerator
from jarvisx.cognition.coding_session import CodingSessionEngine
from friday.study_mode import StudyModeEngine
from jarvisx.memory.knowledge_graph import PersonalKnowledgeGraph
from jarvisx.automation.computer_vision_agent import ComputerVisionAgent
from jarvisx.automation.interrupt_manager import SmartInterruptManager
from jarvisx.automation.proactive_tasks import ProactiveTaskEngine
from jarvisx.interface.cli import JarvisCLI


@pytest.mark.asyncio
async def test_personal_command_center(tmp_path):
    pcc = PersonalCommandCenter(db_dir=str(tmp_path))
    pcc.set_mode("FOCUS")
    assert pcc.active_context["current_mode"] == "FOCUS"

    res = await pcc.query_brain("Linear Algebra")
    assert res["status"] == "SUCCESS"
    assert "query" in res


def test_morning_briefing_generator():
    mbg = MorningBriefingGenerator()
    res = mbg.generate_briefing()
    assert res["status"] == "SUCCESS"
    assert "briefing_text" in res
    assert "ACADEMICS" in res["briefing_text"]
    assert "ENGINEERING" in res["briefing_text"]


def test_coding_session_engine(tmp_path):
    cse = CodingSessionEngine()
    res = cse.start_coding_session(cwd=str(tmp_path))
    assert res["status"] == "SUCCESS"
    assert "test_status" in res


def test_study_mode_engine():
    sme = StudyModeEngine()
    res = sme.start_study_mode(target_subject="Linear Algebra", duration_minutes=30)
    assert res["status"] == "SUCCESS"
    assert res["subject"] == "Linear Algebra"
    assert res["duration_minutes"] == 30


def test_personal_knowledge_graph(tmp_path):
    db_file = tmp_path / "kg.db"
    pkg = PersonalKnowledgeGraph(db_path=str(db_file))
    
    pkg.add_node("node_1", "Concept", "Eigenvectors", {"difficulty": "Medium"})
    pkg.add_edge("project_jarvis", "includes", "node_1")

    res = pkg.query_relationship("Linear Algebra")
    assert res["status"] == "SUCCESS"
    assert "answer" in res


def test_computer_vision_agent():
    agent = ComputerVisionAgent()
    res = agent.run_observe_reason_act_verify_loop("take screenshot")
    assert res["status"] in ("SUCCESS", "PARTIAL")
    assert res["action_executed"] == "screen.capture"


def test_smart_interrupt_manager():
    sim = SmartInterruptManager()
    sim.set_focus_mode(True)

    # Normal priority suppressed in focus mode
    res1 = sim.dispatch_notification("Update", "Minor log info", priority="NORMAL")
    assert res1["status"] == "SUPPRESSED"

    # Important/Critical delivered despite focus mode
    res2 = sim.dispatch_notification("Security", "Risk Gate Triggered", priority="CRITICAL")
    assert res2["status"] == "DELIVERED"


def test_proactive_task_engine(tmp_path):
    pte = ProactiveTaskEngine()
    res = pte.prepare_assignment_workspace("Unit Testing Project", "Software Engineering", "2026-08-10")
    assert res["status"] == "SUCCESS"
    assert Path(res["workspace_dir"]).exists()


@pytest.mark.asyncio
async def test_jarvis_cli_phase51_commands():
    cli = JarvisCLI()
    res_morning = await cli.handle_command_async("morning")
    assert res_morning["status"] == "SUCCESS"

    res_brain = await cli.handle_command_async("brain Linear")
    assert res_brain["status"] == "SUCCESS"

    res_graph = await cli.handle_command_async("graph fastapi")
    assert res_graph["status"] == "SUCCESS"
