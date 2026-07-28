import pytest
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider

@pytest.mark.asyncio
async def test_cognitive_memory():
    provider = SQLiteMemoryProvider()
    mem = CognitiveMemory(provider)
    
    ep_id = await mem.store_experience("User edited a travel video")
    assert ep_id.startswith("mem_episodic_")
    
    sem_id = await mem.extract_knowledge("User prefers cinematic edits", "video editing", confidence=0.92)
    assert sem_id.startswith("mem_semantic_")
    
    proc_id = await mem.build_relationships("Render Workflow", ["Edit", "Render"])
    assert proc_id.startswith("mem_procedural_")
    
    # Context retrieval
    results = await mem.retrieve_context("cinematic")
    assert len(results) == 1
    assert results[0]["data"]["type"] == "semantic"
    assert results[0]["data"]["fact"] == "User prefers cinematic edits"
    
    await mem.forget_memory(ep_id)
    results2 = await mem.retrieve_context("travel")
    assert len(results2) == 0
