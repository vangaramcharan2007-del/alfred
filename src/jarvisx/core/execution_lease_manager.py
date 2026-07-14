import logging
import time
from jarvisx.core.split_brain_detector import SplitBrainDetector

class ExecutionLeaseManager:
    """Grants and revokes execution leases to ensure single_writer_multiple_observers."""
    def __init__(self, detector: SplitBrainDetector):
        self.detector = detector
        # task_id -> {'node_id': str, 'expires_at': float}
        self.leases = {}
        self.lease_duration = 30 # seconds
        
    def acquire_lease(self, task_id: str, node_id: str) -> bool:
        now = time.time()
        current_lease = self.leases.get(task_id)
        
        # If there's an active lease for someone else, deny
        if current_lease and current_lease['expires_at'] > now and current_lease['node_id'] != node_id:
            logging.warning(f"[LeaseManager] Node {node_id} denied lease for {task_id} (Held by {current_lease['node_id']})")
            return False
            
        # Grant or renew lease
        self.leases[task_id] = {'node_id': node_id, 'expires_at': now + self.lease_duration}
        self.detector.verify_single_writer(task_id, node_id)
        logging.info(f"[LeaseManager] Lease granted to {node_id} for task {task_id}")
        return True
        
    def revoke_lease(self, task_id: str):
        if task_id in self.leases:
            owner = self.leases[task_id]['node_id']
            del self.leases[task_id]
            self.detector.active_tasks.pop(task_id, None)
            logging.info(f"[LeaseManager] Lease revoked for {task_id} (Previously held by {owner})")
