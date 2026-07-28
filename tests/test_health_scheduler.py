import pytest
from jarvisx.core.distributed_scheduler import DistributedScheduler
from jarvisx.agents.capability_registry import CapabilityRegistry
from jarvisx.nodes.node_registry import NodeRegistry

def test_health_based_scheduling():
    scheduler = DistributedScheduler(CapabilityRegistry(), NodeRegistry())
    
    node_a = {
        "node": "node_a",
        "gpu": "available",
        "status": "online",
        "success_rate": 95,
        "latency": "10ms"
    }
    
    node_b = {
        "node": "node_b",
        "gpu": "available",
        "status": "online",
        "success_rate": 50,
        "latency": "100ms"
    }
    
    telemetry = [node_a, node_b]
    
    # Select best node should prefer node_a due to better health/latency
    best_node = scheduler.select_best_node("agent1", [], telemetry)
    assert best_node == "node_a"
    
    # If node A is offline, should pick B
    node_a["status"] = "offline"
    best_node = scheduler.select_best_node("agent1", [], telemetry)
    assert best_node == "node_b"
