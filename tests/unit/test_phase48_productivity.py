"""Unit and verification tests for Phase 48: Personal Productivity & Knowledge System.

Verifies document note cataloging, semantic searching, academic assignment tracking,
spaced revision timetable synthesis, and empirical HSPW computation.
"""

import pytest
from jarvisx.productivity import PersonalKnowledgeBase, StudyScheduler
from jarvisx.agents import ProductivityAgent, AgentRegistry
from jarvisx.architecture import get_layer_for_module


def test_knowledge_base_indexing_and_search():
    """Verify PersonalKnowledgeBase stores notes, synthesizes abstracts, and returns searches."""
    kb = PersonalKnowledgeBase()

    n1 = kb.add_note("OS Schedulers", "Preemptive vs cooperative multitasking details.\nRound robin.", course="Operating Systems", tags=["cpu", "kernel"])
    n2 = kb.add_note("Graph Theory", "Adjacency matrix representation of graphs.", course="Algorithms", tags=["math", "graphs"])

    assert len(kb.documents) == 2
    assert "Preemptive vs cooperative" in n1.summary

    # Search by tag
    kernel_matches = kb.search(query="kernel")
    assert len(kernel_matches) == 1
    assert kernel_matches[0].title == "OS Schedulers"

    # Search by course
    os_res = kb.get_course_summary("Operating Systems")
    assert os_res["total_notes"] == 1
    assert "cpu" in os_res["topics"]
    assert kb._hours_saved >= 0.25


def test_study_scheduler_deadlines_and_revision_plans():
    """Verify StudyScheduler schedules deadlines and generates spaced-repetition revision blocks."""
    sch = StudyScheduler()

    a1 = sch.add_assignment("Distributed Systems Project 1", "Systems", "Oct 15", priority="High")
    sch.add_assignment("Math Problem Set", "Calculus", "Oct 12", priority="Medium")

    topics = ["RPC primitives", "Raft consensus", "Byzantine faults", "Vector clocks"]
    plan = sch.generate_revision_plan("Systems", topics, days_until_exam=5)

    assert len(plan) == 4
    assert sch._hours_saved >= 0.8

    dash = sch.get_weekly_dashboard()
    assert dash["status"] == "nominal"
    assert dash["pending_count"] == 2
    assert "ALFRED PERSONAL PRODUCTIVITY DASHBOARD" in dash["output"]
    assert "Active Revision Schedules:" in dash["output"]

    # Verify task completion updates dashboard
    sch.complete_assignment(a1.id)
    dash_post = sch.get_weekly_dashboard()
    assert dash_post["pending_count"] == 1


def test_productivity_agent_workforce_execution():
    """Verify ProductivityAgent performs college workflow tasks and reports HSPW metrics."""
    agent = ProductivityAgent(name="college_assistant")

    # Add a note
    res_note = agent.execute({"action": "add_note", "title": "Memory paging", "course": "OS", "tags": ["memory"]})
    assert res_note["status"] == "completed"

    # Schedule revision
    res_rev = agent.execute({"action": "schedule_revision", "course": "OS", "topics": ["Paging", "Virtual Memory"], "days_until_exam": 4})
    assert res_rev["sessions_created"] == 2

    # View dashboard
    res_dash = agent.execute({"action": "dashboard"})
    assert "ALFRED PERSONAL PRODUCTIVITY DASHBOARD" in res_dash["output"]

    metrics = agent.metrics()
    assert metrics["tasks_completed"] == 3
    # 3 completed tasks * 0.8 HSPW multiplier = 2.4 hrs saved by this agent instance
    assert metrics["hours_saved"] == 2.4


def test_architecture_layer_registration():
    """Verify jarvisx.productivity is recognized cleanly under Layer 4 (capabilities)."""
    assert get_layer_for_module("jarvisx.productivity.knowledge_base") == "capabilities"
    assert get_layer_for_module("jarvisx.productivity") == "capabilities"
