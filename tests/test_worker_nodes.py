import pytest
import asyncio
from jarvisx.nodes.worker_node import WorkerNode
from jarvisx.network.agent_protocol import TaskRequest

def test_worker_node_registration():
    node = WorkerNode(node_id="gaming_laptop", name="Friend PC", hardware_info={"gpu": "RTX 4070"})
    node.register_agent("editing_agent")
    
    assert "editing_agent" in node.available_agents
    assert node.status == "online"
    assert node.hardware_info["gpu"] == "RTX 4070"

def test_heartbeat_updates():
    node = WorkerNode(node_id="gaming_laptop", name="Friend PC", hardware_info={})
    node.network_latency = 50
    node.heartbeat(latency=120)
    
    assert node.network_latency == 120
    assert node.status == "online"

@pytest.mark.asyncio
async def test_async_task_submission():
    node = WorkerNode(node_id="test_node", name="Test", hardware_info={})
    req = TaskRequest(
        task_id="t_123",
        trace_id="tr_1",
        agent_id="editing_agent",
        required_capabilities=["video_editing"],
        payload={}
    )
    
    job_id = await node.execute_task(req)
    assert job_id.startswith("job_")
    
    # Wait for mock execution to complete
    await asyncio.sleep(0.2)
    
    response = await node.poll_job(job_id)
    assert response is not None
    assert response.status == "completed"
    assert response.result["executed_on"] == "test_node"
