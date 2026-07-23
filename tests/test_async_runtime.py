import asyncio
import pytest

from jarvisx.runtime import create_default_runtime

@pytest.mark.asyncio
async def test_alfred_process_is_awaited_correctly():
    runtime = create_default_runtime()
    
    # Check that it returns an awaitable coroutine
    coro = runtime.alfred.process("hello alfred", trace_id="test-trace")
    assert asyncio.iscoroutine(coro)
    
    # Properly await it
    response = await coro
    assert response.handled is True
    assert response.message is not None
