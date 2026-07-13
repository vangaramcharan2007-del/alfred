import asyncio
from pathlib import Path
from jarvisx.runtime import create_default_runtime

async def simulate_sync_scenario():
    print("Starting Synchronization Validation Scenario...")
    runtime = create_default_runtime()
    
    print("1. Creating local un-synchronized state...")
    runtime.world_model.save_entity("sim", "scenario", {"simulated_offline": True, "test_value": 42})
    
    print("2. Forcing Operational Database Sync...")
    try:
        # We manually trigger the sync queue
        runtime.world_model.op_db._sync_queue.put({"action": "sync"})
        print("  [OK] OpDB Sync triggered successfully.")
    except Exception as e:
        print(f"  [ERROR] OpDB Sync failed: {e}")
        
    print("3. Validating Hermes synchronization...")
    try:
        await runtime.hermes.publish("test_event", {"payload": "test"})
        print("  [OK] Hermes event published successfully.")
    except Exception as e:
        print(f"  [ERROR] Hermes publish failed: {e}")

    # Give the sync worker a moment to process the queue
    await asyncio.sleep(2)
    
    print("4. Shutting down gracefully to ensure state persistence...")
    runtime.shutdown()
    print("Simulation complete.")

if __name__ == "__main__":
    asyncio.run(simulate_sync_scenario())
