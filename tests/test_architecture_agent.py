import pytest
from jarvisx.capabilities.coding.architecture_agent import ArchitectureAgent

@pytest.mark.asyncio
async def test_architecture_agent_design_system():
    agent = ArchitectureAgent()
    result = await agent.design_system("Build a real-time AI meeting assistant")

    assert "project_name" in result
    assert "architecture" in result
    assert len(result["adrs"]) >= 1
    assert "component_diagram" in result["diagrams"]
    assert "data_flow_diagram" in result["diagrams"]
    assert len(result["roadmap"]) >= 3
