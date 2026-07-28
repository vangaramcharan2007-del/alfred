import pytest
from jarvisx.agents.adaptation_manager import AdaptationManager
from jarvisx.learning.knowledge_graph import KnowledgeGraph
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


@pytest.fixture
def adaptation_system():
    provider = SQLiteMemoryProvider()
    memory = CognitiveMemory(provider)
    graph = KnowledgeGraph()
    manager = AdaptationManager(memory, graph)
    return manager, graph, memory


@pytest.mark.asyncio
async def test_adapt_agent(adaptation_system):
    manager, graph, _ = adaptation_system
    # Seed graph with some learned relationships
    graph.add_relationship("user", "cinematic style", "prefers", 0.9)
    graph.add_relationship("editing_agent", "video_editing", "performed", 1.0)

    profile = await manager.adapt_agent("editing_agent")
    assert profile["agent_id"] == "editing_agent"
    assert "preferences" in profile
    assert profile["adaptation_score"] >= 0


@pytest.mark.asyncio
async def test_update_preferences(adaptation_system):
    manager, _, _ = adaptation_system
    success = await manager.update_preferences("editing_agent", "style", "cinematic")
    assert success is True
    ctx = manager.get_agent_context("editing_agent")
    assert ctx["preferences"]["style"] == "cinematic"


@pytest.mark.asyncio
async def test_apply_feedback(adaptation_system):
    manager, _, _ = adaptation_system
    feedback = {"type": "preference", "preference": "slow pacing", "confidence": 0.85}
    success = await manager.apply_feedback("editing_agent", feedback)
    assert success is True
    ctx = manager.get_agent_context("editing_agent")
    assert "slow pacing" in ctx["learned_behaviors"]
    assert ctx["adaptation_score"] > 0


@pytest.mark.asyncio
async def test_evaluate_agent(adaptation_system):
    manager, _, _ = adaptation_system
    await manager.update_preferences("editing_agent", "style", "cinematic")
    result = await manager.evaluate_agent("editing_agent")
    assert result["agent_id"] == "editing_agent"
    assert result["total_preferences"] >= 1


def test_get_agent_context_default(adaptation_system):
    manager, _, _ = adaptation_system
    ctx = manager.get_agent_context("nonexistent_agent")
    assert ctx["agent_id"] == "nonexistent_agent"
    assert ctx["adaptation_score"] == 0.0
    assert ctx["preferences"] == {}
