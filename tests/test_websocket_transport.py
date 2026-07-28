import pytest
import asyncio
from jarvisx.network.transports.websocket_transport import WebSocketTransport
from jarvisx.network.event_bus import DistributedEventBus
from jarvisx.network.agent_protocol import Envelope

@pytest.mark.asyncio
async def test_websocket_lifecycle():
    bus = DistributedEventBus()
    transport = WebSocketTransport(event_bus=bus)
    
    events = []
    
    async def track(payload):
        events.append(payload)
        
    bus.subscribe("agent.connection.connected", track)
    bus.subscribe("agent.connection.disconnected", track)
    bus.subscribe("agent.connection.reconnecting", track)
    
    await transport.connect("node_1", "conn_1")
    assert transport.connections["node_1"]["status"] == "connected"
    
    msg = Envelope(
        message_id="msg_1",
        trace_id="trace_1",
        timestamp="100",
        type="test.ping",
        payload={}
    )
    
    await transport.send("node_1", msg)
    received = await transport.receive("node_1")
    assert received is not None
    assert received.type == "test.ping"
    
    await transport.reconnect("node_1")
    assert transport.connections["node_1"]["status"] == "connected"
    
    await transport.disconnect("node_1")
    assert transport.connections["node_1"]["status"] == "disconnected"
    
    await asyncio.sleep(0.1) # allow async event handlers to process
    assert len(events) >= 3 # connected, reconnecting, connected, disconnected
