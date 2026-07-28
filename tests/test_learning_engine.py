import pytest
from jarvisx.learning.learning_engine import LearningEngine
from jarvisx.learning.experience_engine import ExperienceEngine
from jarvisx.learning.knowledge_extractor import KnowledgeExtractor
from jarvisx.learning.knowledge_graph import KnowledgeGraph
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


@pytest.fixture
def learning_system():
    provider = SQLiteMemoryProvider()
    memory = CognitiveMemory(provider)
    graph = KnowledgeGraph()
    exp_engine = ExperienceEngine(memory)
    extractor = KnowledgeExtractor(memory)
    engine = LearningEngine(exp_engine, extractor, graph, memory)
    return engine, graph, memory


@pytest.mark.asyncio
async def test_learn_pipeline(learning_system):
    engine, graph, memory = learning_system
    task_result = {
        "type": "creative_task",
        "action": "video_editing",
        "result": "success",
        "agent": "editing_agent",
        "preferences_detected": ["cinematic style", "slow transitions"],
    }
    result = await engine.learn(task_result)

    assert result["facts_stored"] > 0
    assert len(result["entities"]) > 0
    assert len(result["relationships"]) > 0

    # Verify graph was updated
    user_rels = graph.query_relationships("user")
    assert len(user_rels) > 0


@pytest.mark.asyncio
async def test_apply_learning(learning_system):
    engine, graph, memory = learning_system

    # First learn something
    await engine.learn({
        "type": "creative_task",
        "action": "video_editing",
        "result": "success",
        "agent": "editing_agent",
        "preferences_detected": ["cinematic style"],
    })

    # Then apply it
    context = await engine.apply_learning("editing_agent", "video_editing")
    assert "preferences" in context
    assert "strategies" in context


@pytest.mark.asyncio
async def test_evaluate_outcome(learning_system):
    engine, graph, memory = learning_system
    result = await engine.evaluate_outcome("task_1", "success")
    assert "updated_facts" in result
    assert "new_confidence" in result


@pytest.mark.asyncio
async def test_update_strategy(learning_system):
    engine, graph, memory = learning_system
    success = await engine.update_strategy("editing_agent", {
        "description": "Use cinematic pacing for travel videos",
        "confidence": 0.9,
    })
    assert success is True
