import pytest
from jarvisx.memory.shared_memory import SharedMemory, MockSQLiteProvider

@pytest.mark.asyncio
async def test_unit_shared_memory_operations():
    provider = MockSQLiteProvider()
    memory = SharedMemory(provider=provider)

    success = await memory.store_memory("key_1", {"fact": "unit_test_memory"})
    assert success is True

    val = await memory.retrieve_memory("key_1")
    assert val == {"fact": "unit_test_memory"}

    search_res = await memory.search_context("unit_test")
    assert len(search_res) >= 1
