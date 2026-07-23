import asyncio
import pytest
from jarvisx.runtime import create_default_runtime

@pytest.mark.asyncio
async def test_greeting_agent():
    runtime = create_default_runtime()
    
    response = await runtime.alfred.process("hello alfred", trace_id="trace-greet")
    assert response.handled is True
    assert response.agent_id == "chat"
    assert "Hello" in response.message
    
    response2 = await runtime.alfred.process("goodbye", trace_id="trace-bye")
    assert response2.handled is True
    assert response2.agent_id == "chat"
    assert "Goodbye" in response2.message
