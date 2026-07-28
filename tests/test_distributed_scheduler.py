import pytest
from jarvisx.core.distributed_scheduler import DistributedScheduler
from jarvisx.agents.capability_registry import CapabilityRegistry, AgentManifest
from jarvisx.nodes.node_registry import NodeRegistry
from jarvisx.nodes.worker_node import WorkerNode

@pytest.mark.asyncio
async def test_scheduler_best_node_selection():
    cap_reg = CapabilityRegistry()
    # Mocking manifest to ensure editing_agent exists
    cap_reg.register_agent(AgentManifest(id="editing_agent", name="Editor", role="Video Editor", capabilities=["video_editing"], status="active"))
    
    node_reg = NodeRegistry()
    local = WorkerNode(node_id="local_laptop", name="Local", hardware_info={"gpu": False})
    local.register_agent("editing_agent")
    gaming = WorkerNode(node_id="gaming_laptop", name="Gaming", hardware_info={"gpu": True})
    gaming.register_agent("editing_agent")
    
    node_reg.register_node(local)
    node_reg.register_node(gaming)
    
    scheduler = DistributedScheduler(cap_reg, node_reg)
    
    # Task requires video_editing and a GPU
    job_id = await scheduler.dispatch(
        trace_id="tr_1",
        required_capabilities=["video_editing"],
        payload={"video": "4k.mp4"},
        required_hardware={"gpu": True}
    )
    
    assert job_id is not None
    assert job_id.startswith("job_")
    
    # Since gaming laptop has GPU, it should receive the task
    assert len(gaming._active_jobs) > 0
    assert len(local._active_jobs) == 0
