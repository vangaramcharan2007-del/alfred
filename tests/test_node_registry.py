import pytest
import time
from jarvisx.nodes.node_registry import NodeRegistry
from jarvisx.nodes.worker_node import WorkerNode

def test_node_scoring_and_selection():
    registry = NodeRegistry()
    
    local_node = WorkerNode(node_id="local_laptop", name="Local", hardware_info={"gpu": False})
    local_node.network_latency = 10
    local_node.register_agent("editing_agent")
    
    gaming_node = WorkerNode(node_id="gaming_laptop", name="Gaming", hardware_info={"gpu": True})
    gaming_node.network_latency = 50
    gaming_node.register_agent("editing_agent")
    
    registry.register_node(local_node)
    registry.register_node(gaming_node)
    
    # Require GPU
    results = registry.find_best_node("editing_agent", required_hardware={"gpu": True})
    
    assert len(results) == 2
    assert results[0]["node"] == "gaming_laptop" # GPU match + decent latency
    assert results[1]["node"] == "local_laptop"  # No GPU -> massive penalty

def test_offline_node_rejection():
    registry = NodeRegistry()
    
    dead_node = WorkerNode(node_id="dead_laptop", name="Dead", hardware_info={})
    dead_node.register_agent("editing_agent")
    # Simulate a node that hasn't heartbeated in 10 minutes
    dead_node._last_heartbeat = time.time() - 600
    
    registry.register_node(dead_node)
    
    results = registry.find_best_node("editing_agent")
    assert len(results) == 0 # Offline node is ignored
