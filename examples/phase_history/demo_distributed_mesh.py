import asyncio
import time
from jarvisx.agents.capability_registry import CapabilityRegistry, AgentManifest
from jarvisx.nodes.node_registry import NodeRegistry
from jarvisx.nodes.worker_node import WorkerNode
from jarvisx.core.distributed_scheduler import DistributedScheduler
from jarvisx.core.logging import StructuredLogger

async def run_demo():
    print("\n--- DISTRIBUTED AGENT MESH DEMO ---")
    
    # 1. Setup Registries
    cap_reg = CapabilityRegistry()
    node_reg = NodeRegistry()
    scheduler = DistributedScheduler(cap_reg, node_reg)
    
    # 2. Register Agent Capabilities
    cap_reg.register_agent(AgentManifest(
        id="editing_agent", 
        name="Editor", 
        role="Video Editor", 
        capabilities=["video_editing", "rendering"],
        status="active"
    ))
    
    # 3. Setup Mesh Nodes
    print("Initializing Mesh Nodes...")
    
    local_laptop = WorkerNode(node_id="local_laptop", name="Local MacBook", hardware_info={"gpu": False})
    local_laptop.register_agent("coding_agent")
    local_laptop.network_latency = 10
    
    gaming_laptop = WorkerNode(node_id="gaming_laptop", name="Gaming Laptop Node", hardware_info={"gpu": True})
    gaming_laptop.register_agent("editing_agent")
    gaming_laptop.network_latency = 45
    
    cloud_node = WorkerNode(node_id="cloud_gpu", name="AWS A100", hardware_info={"gpu": True})
    cloud_node.register_agent("ai_agent")
    cloud_node.network_latency = 120
    
    node_reg.register_node(local_laptop)
    node_reg.register_node(gaming_laptop)
    node_reg.register_node(cloud_node)
    
    print("\nUser: \"Render this video\"")
    print("Alfred processing task...")
    
    # Alfred determines it needs 'video_editing' and hardware 'gpu'
    required_capabilities = ["video_editing"]
    required_hardware = {"gpu": True}
    
    print("\nSearching capabilities...")
    agent_scores = cap_reg.discover_capability(required_capabilities)
    if agent_scores:
        print(f"Found: {agent_scores[0]['agent']}")
    
    print("\nSearching nodes...")
    node_scores = node_reg.find_best_node(agent_scores[0]["agent"], required_hardware)
    if node_scores:
        best = node_scores[0]
        print(f"Found: {best['node']}")
        print(f"Score: {best['score']}")
    
    print("\nDispatching task...")
    job_id = await scheduler.dispatch(
        trace_id="demo_1",
        required_capabilities=required_capabilities,
        payload={"file": "vid.mp4"},
        required_hardware=required_hardware
    )
    
    print(f"\nJob ID: {job_id}")
    print("Monitoring progress...")
    
    # Poll for completion (non-blocking)
    target_node = node_reg._nodes[node_scores[0]["node"]]
    while True:
        status = await target_node.poll_job(job_id)
        if status:
            print(f"Status received: {status.status}")
            break
        print("...")
        await asyncio.sleep(0.05)
        
    print("\nTask completed.")

if __name__ == "__main__":
    asyncio.run(run_demo())
