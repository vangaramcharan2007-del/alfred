import asyncio
import pytest
from jarvisx.runtime import create_default_runtime

@pytest.mark.asyncio
async def test_clarification_engine(monkeypatch):
    runtime = create_default_runtime()
    
    # Send ambiguous command which normally wouldn't match. We'll mock classify to return low confidence.
    original_classify = runtime.alfred.classifier.classify
    def mock_classify(message):
        if message == "play something":
            from jarvisx.agents.alfred import Intent
            return Intent("unknown", "planner", "unknown", 0.35, "Mock low confidence")
        return original_classify(message)
        
    monkeypatch.setattr(runtime.alfred.classifier, "classify", mock_classify)
    
    # Send ambiguous command
    response1 = await runtime.alfred.process("play something", trace_id="trace-1")
    assert response1.handled is True
    assert "I have two possible interpretations" in response1.message
    assert runtime.alfred.pending_action == "play something"
    
    # Send clarification
    response2 = await runtime.alfred.process("desktop", trace_id="trace-2")
    # It should have re-processed 'play something (desktop)' 
    assert response2.handled is True
    assert runtime.alfred.pending_action is None
