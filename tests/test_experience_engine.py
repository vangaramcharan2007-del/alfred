import pytest
from jarvisx.learning.experience_engine import ExperienceEngine
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


@pytest.fixture
def engine():
    provider = SQLiteMemoryProvider()
    memory = CognitiveMemory(provider)
    return ExperienceEngine(memory)


def test_capture_experience(engine):
    task_result = {
        "type": "creative_task",
        "action": "video_editing",
        "result": "success",
        "agent": "editing_agent",
        "preferences_detected": ["cinematic style", "slow transitions"],
    }
    exp = engine.capture_experience(task_result)
    assert exp["type"] == "creative_task"
    assert exp["action"] == "video_editing"
    assert exp["agent"] == "editing_agent"
    assert "cinematic style" in exp["preferences_detected"]
    assert "timestamp" in exp


def test_summarize_experience(engine):
    exp = {
        "agent": "editing_agent",
        "action": "video_editing",
        "result": "success",
        "preferences_detected": ["cinematic style"],
    }
    summary = engine.summarize_experience(exp)
    assert "editing_agent" in summary
    assert "video_editing" in summary
    assert "cinematic style" in summary


def test_extract_patterns(engine):
    experiences = [
        {"preferences_detected": ["cinematic style", "slow transitions"]},
        {"preferences_detected": ["cinematic style"]},
        {"preferences_detected": ["fast cuts"]},
    ]
    patterns = engine.extract_patterns(experiences)
    repeated = [p for p in patterns if p["pattern_type"] == "repeated_preference"]
    assert any(p["value"] == "cinematic style" for p in repeated)


@pytest.mark.asyncio
async def test_store_experience(engine):
    exp = {
        "agent": "editing_agent",
        "action": "video_editing",
        "result": "success",
        "preferences_detected": [],
    }
    mem_id = await engine.store_experience(exp)
    assert mem_id.startswith("mem_episodic_")
