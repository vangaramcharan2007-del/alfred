import pytest
import os
import shutil
import json
import asyncio
from jarvisx.core.skills.skill_registry import SkillRegistry
from jarvisx.core.skills.skill import BaseSkill
from jarvisx.core.workflows.workflow_manager import WorkflowManager

class MockSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "Test Skill"
        
    @property
    def description(self) -> str:
        return "A mock skill for testing"
        
    @property
    def required_tools(self) -> list:
        return []
        
    async def execute(self, task: str, context: dict = None) -> str:
        return f"Executed {task}"

def test_skill_registration():
    registry = SkillRegistry()
    registry.clear()
    
    skill = MockSkill()
    registry.register(skill)
    
    assert registry.get_skill("Test Skill") == skill
    
    capabilities = registry.list_capabilities()
    assert "Test Skill" in capabilities
    assert "mock skill" in capabilities

def test_workflow_storage():
    test_workspace = "test_workspace"
    if os.path.exists(test_workspace):
        shutil.rmtree(test_workspace)
        
    manager = WorkflowManager(workspace_path=test_workspace)
    
    steps = ["Step 1", "Step 2", "Step 3"]
    manager.save_workflow("Test Workflow", steps, {"goal": "Test"})
    
    workflows = manager.list_workflows()
    assert "Test Workflow" in workflows
    
    loaded = manager.get_workflow("Test Workflow")
    assert loaded["steps"] == steps
    assert loaded["metadata"]["goal"] == "Test"
    
    shutil.rmtree(test_workspace)

@pytest.mark.asyncio
async def test_skill_execution():
    from jarvisx.core.skills.skill_executor import SkillExecutor
    
    registry = SkillRegistry()
    registry.clear()
    registry.register(MockSkill())
    
    executor = SkillExecutor()
    result = await executor.execute_skill("Test Skill", "do something")
    
    assert result == "Executed do something"
