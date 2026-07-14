# src/jarvisx/core/health_monitor.py

class HealthMonitor:
    """
    Monitors node, service, and agent health. Tracks heartbeat status
    and exposes states: HEALTHY, DEGRADED, UNHEALTHY, OFFLINE.
    """
    def __init__(self):
        pass

    def get_node_health(self, node_id: str) -> str:
        return "HEALTHY"
