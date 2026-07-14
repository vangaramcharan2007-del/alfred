import logging
import time
from jarvisx.core.worker_registry import WorkerRegistry
from jarvisx.core.execution_lease_manager import ExecutionLeaseManager

class HeartbeatMonitor:
    """Monitors node heartbeats and purges dead nodes to free their leases."""
    def __init__(self, registry: WorkerRegistry, lease_manager: ExecutionLeaseManager):
        self.registry = registry
        self.lease_manager = lease_manager
        self.timeout = 15 # seconds
        
    def check_heartbeats(self):
        now = time.time()
        for node_id, data in list(self.registry.nodes.items()):
            if data['status'] == 'ONLINE' and now - data['last_seen'] > self.timeout:
                logging.warning(f"[Heartbeat] Node {node_id} missed heartbeats. Marking OFFLINE.")
                self.registry.nodes[node_id]['status'] = 'OFFLINE'
                
                # Revoke all leases held by this node
                tasks_to_revoke = [tid for tid, lease in self.lease_manager.leases.items() if lease['node_id'] == node_id]
                for tid in tasks_to_revoke:
                    self.lease_manager.revoke_lease(tid)
                    
    def ping(self, node_id: str):
        if node_id in self.registry.nodes:
            self.registry.nodes[node_id]['last_seen'] = time.time()
            if self.registry.nodes[node_id]['status'] == 'OFFLINE':
                self.registry.nodes[node_id]['status'] = 'ONLINE'
                logging.info(f"[Heartbeat] Node {node_id} recovered.")
