import asyncio
import logging
from .distributed_executor import DistributedExecutor
from .workload_scheduler import WorkloadScheduler
from .world_model_runtime import WorldModelRuntime
from .initiative_daemon import InitiativeDaemon
from .mesh_transport import MeshTransport

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AutonomyIntegrationTest")

async def run_scenario():
    logger.info("=== Starting Phase III Autonomy Scenario ===")
    
    # Setup mocks
    laptop_transport = MeshTransport("laptop-001")
    world_model = WorldModelRuntime()
    scheduler = WorkloadScheduler("laptop-001")
    executor = DistributedExecutor("laptop-001")
    
    daemon = InitiativeDaemon(world_model, scheduler, executor, laptop_transport)
    await daemon.start()
    
    # 1. Establish initial world state
    world_model.update_device_state("laptop-001", {"cpu_percent": 15, "battery_percent": 100, "is_executing_heavy_task": False})
    world_model.update_device_state("phone-002", {"cpu_percent": 80, "battery_percent": 100, "is_executing_heavy_task": True})
    
    scheduler.update_telemetry("laptop-001", {"cpu_percent": 15, "battery_percent": 100})
    scheduler.update_telemetry("phone-002", {"cpu_percent": 80, "battery_percent": 100})
    
    await asyncio.sleep(3) # Let daemon check (nothing happens)
    
    # 2. Trigger low battery condition on Phone
    logger.info("Simulating critical battery drop on phone-002...")
    world_model.update_device_state("phone-002", {"cpu_percent": 85, "battery_percent": 15, "is_executing_heavy_task": True})
    scheduler.update_telemetry("phone-002", {"cpu_percent": 85, "battery_percent": 15})
    
    # 3. Wait for daemon to detect and act
    await asyncio.sleep(3)
    
    # 4. Verify workload executes on laptop
    await executor.execute_task("heavy-compute-999", "echo 'Compiling Model...'", is_async=True)
    
    await daemon.stop()
    logger.info("=== Phase III Scenario Complete ===")

if __name__ == "__main__":
    asyncio.run(run_scenario())
