import logging
import time
from jarvisx.core.split_brain_detector import SplitBrainDetector
from jarvisx.core.worker_registry import WorkerRegistry
from jarvisx.core.execution_lease_manager import ExecutionLeaseManager
from jarvisx.core.heartbeat_monitor import HeartbeatMonitor

logging.basicConfig(level=logging.INFO, format='%(message)s')

def simulate():
    print("\n--- Jarvis X GENESIS: Distributed Execution Simulation ---")
    
    detector = SplitBrainDetector()
    registry = WorkerRegistry()
    lease_mgr = ExecutionLeaseManager(detector)
    monitor = HeartbeatMonitor(registry, lease_mgr)
    
    # 1. Register Nodes
    print("\n[System] Registering nodes...")
    registry.register_node("laptop_01", ["CPU", "GPU"])
    registry.register_node("cloud_worker_01", ["CPU", "GPU", "HIGH_BANDWIDTH"])
    
    # 2. Laptop starts a task
    print("\n[Laptop] Acquiring execution lease for task_alpha...")
    success = lease_mgr.acquire_lease("task_alpha", "laptop_01")
    
    # 3. Cloud worker attempts to steal the lease (Split Brain Prevention)
    print("\n[Cloud] Attempting to concurrently execute task_alpha...")
    lease_mgr.acquire_lease("task_alpha", "cloud_worker_01")
    
    # 4. Laptop Battery Dies (Misses heartbeats)
    print("\n[Network] Laptop disconnects abruptly (Simulating 20 seconds passing)...")
    registry.nodes["laptop_01"]["last_seen"] -= 20
    monitor.check_heartbeats()
    
    # 5. Cloud worker takes over
    print("\n[Cloud] Noticing dropped lease, cloud worker re-attempts acquisition...")
    success = lease_mgr.acquire_lease("task_alpha", "cloud_worker_01")
    
    if success:
        print("\n[System] SUCCESS: Execution ownership migrated to cloud without split-brain.")

if __name__ == "__main__":
    simulate()
