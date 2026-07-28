import pytest
import asyncio
from jarvisx.network.gateway import AgentGateway, MockTransport
from jarvisx.network.agent_protocol import Envelope

@pytest.mark.asyncio
async def test_gateway_connection():
    transport = MockTransport()
    gateway = AgentGateway(transport)
    
    await gateway.connect_node("node1", "conn1")
    status = gateway.get_connection_status("node1")
    
    assert status is not None
    assert status["status"] == "connected"
    assert status["connection_id"] == "conn1"
    
    await gateway.disconnect_node("node1")
    status = gateway.get_connection_status("node1")
    assert status["status"] == "disconnected"

@pytest.mark.asyncio
async def test_gateway_messaging():
    transport = MockTransport()
    gateway = AgentGateway(transport)
    
    tx = asyncio.Queue()
    rx = asyncio.Queue()
    transport.register_queues("node1", tx, rx)
    
    await gateway.connect_node("node1", "conn1")
    
    msg = Envelope(
        message_id="1",
        trace_id="tr1",
        timestamp="123",
        type="test.msg",
        payload={"data": "hello"}
    )
    
    await gateway.send_message("node1", msg)
    
    # Simulate node receiving
    received = await tx.get()
    assert received.type == "test.msg"
    
    # Simulate node responding
    resp_msg = Envelope(
        message_id="2",
        trace_id="tr1",
        timestamp="124",
        type="test.resp",
        payload={"ack": True}
    )
    await rx.put(resp_msg)
    
    # Gateway receives
    gw_received = await gateway.receive_message("node1")
    assert gw_received is not None
    assert gw_received.type == "test.resp"
