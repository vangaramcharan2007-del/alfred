import pytest
from jarvisx.memory.shared_memory import SharedMemory, MockSQLiteProvider

@pytest.mark.asyncio
async def test_shared_memory():
    provider = MockSQLiteProvider()
    memory = SharedMemory(provider)
    
    await memory.store_memory("key1", "value1")
    val = await memory.retrieve_memory("key1")
    assert val == "value1"
    
    await memory.sync_memory("node2", {"key2": "value2"})
    val2 = await memory.retrieve_memory("key2")
    assert val2 == "value2"
    
    results = await memory.search_context("value")
    assert len(results) == 2
