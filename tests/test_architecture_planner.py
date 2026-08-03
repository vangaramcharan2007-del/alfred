import pytest
from jarvisx.capabilities.coding.architecture_planner import ArchitecturePlanner

def test_architecture_planner_meeting_assistant():
    planner = ArchitecturePlanner()
    arch = planner.propose_architecture("Build a real-time AI meeting assistant")

    assert arch.project_name is not None
    assert len(arch.components) >= 3
    assert "backend" in arch.technology_stack
    assert len(arch.decisions) >= 1
    assert len(arch.api_design) >= 1

def test_architecture_planner_generic():
    planner = ArchitecturePlanner()
    arch = planner.propose_architecture("Build a task management dashboard")

    assert len(arch.components) >= 2
    assert "frontend" in arch.technology_stack
