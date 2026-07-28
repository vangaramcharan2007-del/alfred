import pytest
import time
from jarvisx.agents.agent_monitor import AgentMonitor

def test_agent_monitor_heartbeat():
    monitor = AgentMonitor()
    monitor.register_heartbeat("friday", node="local", gpu_available=True)
    
    health = monitor.get_agent_health("friday")
    assert health is not None
    assert health["status"] == "online"
    assert health["gpu"] == "available"
    assert health["node"] == "local"

def test_agent_monitor_success_rate():
    monitor = AgentMonitor()
    monitor.record_success("edith", 120)
    monitor.record_success("edith", 150)
    monitor.record_failure("edith", 200)
    
    health = monitor.get_agent_health("edith")
    # 2 successes out of 3 total = 66%
    assert health["success_rate"] == 66
    assert health["latency"] == "200ms"

def test_agent_offline_detection():
    monitor = AgentMonitor()
    monitor.register_heartbeat("vision")
    
    # Manually backdate the heartbeat to simulate timeout
    internal_health = monitor._get_or_create("vision")
    internal_health._last_heartbeat = time.time() - 350
    
    health = monitor.get_agent_health("vision")
    assert health["status"] == "offline"
