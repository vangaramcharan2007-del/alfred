import pytest
from jarvisx.learning.feedback_engine import FeedbackEngine
from jarvisx.learning.knowledge_graph import KnowledgeGraph
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


@pytest.fixture
def feedback_system():
    provider = SQLiteMemoryProvider()
    memory = CognitiveMemory(provider)
    graph = KnowledgeGraph()
    engine = FeedbackEngine(memory, graph)
    return engine, graph, memory


def test_classify_correction(feedback_system):
    engine, _, _ = feedback_system
    assert engine.classify_feedback("No, make it shorter") == "correction"
    assert engine.classify_feedback("That's wrong") == "correction"
    assert engine.classify_feedback("Not what I wanted") == "correction"


def test_classify_preference(feedback_system):
    engine, _, _ = feedback_system
    assert engine.classify_feedback("I prefer shorter responses") == "preference"
    assert engine.classify_feedback("I like examples") == "preference"
    assert engine.classify_feedback("I want more detail") == "preference"


def test_classify_positive(feedback_system):
    engine, _, _ = feedback_system
    assert engine.classify_feedback("That's great!") == "positive"
    assert engine.classify_feedback("Perfect, thanks") == "positive"


def test_classify_negative(feedback_system):
    engine, _, _ = feedback_system
    assert engine.classify_feedback("That's terrible") == "negative"
    assert engine.classify_feedback("This is awful") == "negative"


def test_classify_unknown(feedback_system):
    engine, _, _ = feedback_system
    assert engine.classify_feedback("Tell me about quantum physics") == "unknown"


@pytest.mark.asyncio
async def test_capture_feedback(feedback_system):
    engine, _, _ = feedback_system
    result = await engine.capture_feedback("I prefer cinematic editing")
    assert result["type"] == "preference"
    assert result["confidence"] > 0
    assert result["raw"] == "I prefer cinematic editing"


@pytest.mark.asyncio
async def test_update_memory(feedback_system):
    engine, graph, _ = feedback_system
    feedback = {
        "type": "preference",
        "preference": "cinematic editing",
        "confidence": 0.85,
        "raw": "I prefer cinematic editing",
    }
    mem_id = await engine.update_memory(feedback)
    assert mem_id.startswith("mem_semantic_")

    # Verify graph was updated
    user_prefs = graph.find_related("user", relation_type="prefers")
    assert "cinematic editing" in user_prefs
