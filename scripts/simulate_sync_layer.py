import logging
import time
from jarvisx.core.sync_engine import SyncEngine
from jarvisx.core.checkpoint_manager import CheckpointManager
from jarvisx.core.conflict_resolver import ConflictResolver

logging.basicConfig(level=logging.INFO, format='%(message)s')

def simulate():
    print("\n--- Jarvis X GENESIS: Antigravity Sync Simulation ---")
    sync_engine = SyncEngine()
    checkpoint_mgr = CheckpointManager(sync_engine)
    resolver = ConflictResolver()
    
    print("\n[Laptop] User starts long running research task...")
    task_state = {"progress": 10, "source": "active_device"}
    cp_payload = checkpoint_mgr.create_checkpoint("exec_001", task_state)
    
    print("\n[Network] Syncing to cloud...")
    sync_engine.push_cloud()
    
    print("\n[Network] Laptop disconnects (Offline Mode).")
    sync_engine.cloud_connected = False
    
    print("\n[Laptop] Swarm continues working offline...")
    task_state["progress"] = 30
    checkpoint_mgr.create_checkpoint("exec_001", task_state)
    sync_engine.push_cloud() # Will fail and queue
    
    print("\n[Cloud] Meanwhile, a cloud worker tries to push an older cached state...")
    cloud_state = {"progress": 25, "source": "cloud_worker"}
    
    print("\n[Network] Laptop reconnects...")
    sync_engine.cloud_connected = True
    
    print("\n[Network] Resolving conflict between local queue and cloud incoming...")
    final_state = resolver.resolve_state(task_state, cloud_state)
    
    print("\n[Network] Flushing offline queue to cloud...")
    sync_engine.push_cloud()
    
    print(f"\n[System] Final task progress verified at {final_state['progress']}%")

if __name__ == "__main__":
    simulate()
