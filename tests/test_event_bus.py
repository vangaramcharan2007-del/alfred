import pytest
import asyncio
from jarvisx.network.event_bus import DistributedEventBus

@pytest.mark.asyncio
async def test_event_bus():
    bus = DistributedEventBus()
    
    received = []
    
    async def handler(payload):
        received.append(payload)
        
    bus.subscribe("test.event", handler)
    
    await bus.publish("test.event", {"data": 123})
    
    # Wait for async task to run
    await asyncio.sleep(0.1)
    
    assert len(received) == 1
    assert received[0]["data"] == 123
    
    bus.unsubscribe("test.event", handler)
    
    await bus.publish("test.event", {"data": 456})
    await asyncio.sleep(0.1)
    
    # Should not have received a second event
    assert len(received) == 1
