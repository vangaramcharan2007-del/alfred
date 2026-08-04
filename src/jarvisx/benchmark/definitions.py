"""
Mission definitions for Alfred Autonomous Mission Benchmark.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Optional


@dataclass
class MissionDefinition:
    mission_id: str
    title: str
    description: str
    category: str
    steps: List[str] = field(default_factory=list)


def get_all_missions() -> List[MissionDefinition]:
    return [
        MissionDefinition(
            mission_id="M001",
            title="Create a simple Python application",
            description="Analyze workspace, plan tasks, create files, execute code, run pytest, and report result.",
            category="software_development",
            steps=[
                "Analyze workspace environment",
                "Plan application module structure",
                "Create app.py and test_app.py files",
                "Execute Python application",
                "Run pytest test suite",
                "Generate final execution report"
            ]
        ),
        MissionDefinition(
            mission_id="M002",
            title="Debug a broken Python project",
            description="Detect failure in broken project, analyze traceback, modify code, and verify fix.",
            category="debugging_recovery",
            steps=[
                "Initialize broken project sandbox",
                "Run script to capture traceback",
                "Analyze error root cause",
                "Apply bug fix to codebase",
                "Re-run verification test suite"
            ]
        ),
        MissionDefinition(
            mission_id="M003",
            title="Research and summarize a technical topic",
            description="Use available knowledge/tools to research a topic and store summary in Cognitive Memory.",
            category="knowledge_research",
            steps=[
                "Receive technical query topic",
                "Synthesize structured research response",
                "Store summary into Cognitive Memory / SQLite",
                "Verify memory persistence index"
            ]
        ),
        MissionDefinition(
            mission_id="M004",
            title="Create a personal study plan",
            description="Use Friday academic engine to calculate 10 CGPA strategy and generate actionable schedule.",
            category="academic_planning",
            steps=[
                "Load student course credit profile",
                "Calculate 10 CGPA subject priority weights",
                "Generate daily focus study timetable",
                "Log academic targets to Friday DB"
            ]
        ),
        MissionDefinition(
            mission_id="M005",
            title="Automate a safe desktop workflow",
            description="Use automation layer to organize workspace files with explicit Production Safety Gate approval.",
            category="desktop_automation",
            steps=[
                "Identify target workspace directory",
                "Classify action risk level in ProductionSafetyGate",
                "Format and request user approval [Y/N]",
                "Execute safe desktop action"
            ]
        )
    ]
