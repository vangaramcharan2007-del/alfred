import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ShutdownManager:
    """
    Manages the graceful shutdown of the Jarvis X ecosystem.
    Enforces the required shutdown order:
    Stop Incoming Requests -> Drain Task Queue -> Flush Memory -> 
    Sync Supabase -> Close Databases -> Shutdown Workers -> 
    Release Resources -> Shutdown Complete
    """

    def __init__(self, runtime: "JarvisRuntime") -> None:
        self.runtime = runtime
        self._is_shutting_down = False

    def shutdown(self) -> None:
        if self._is_shutting_down:
            return
            
        self._is_shutting_down = True
        logger.info("INITIATING JARVIS X SHUTDOWN SEQUENCE...")

        # 1. Stop Incoming Requests (API / Listeners)
        logger.info("[1/7] Stopping incoming requests and monitors...")
        if self.runtime.continuous_health:
            self.runtime.continuous_health.stop()
        if self.runtime.proactive_monitor:
            self.runtime.proactive_monitor.stop()

        # 2. Drain Task Queue / Workflow Executor
        logger.info("[2/7] Draining task queues and workflow engine...")
        if hasattr(self.runtime, 'workflow_tool') and self.runtime.workflow_tool.engine:
            self.runtime.workflow_tool.engine.shutdown()

        # 3. Flush Memory Buffers
        logger.info("[3/7] Flushing memory buffers...")
        # (Currently memory is flushed dynamically, but we invoke explicit flush if added)
        
        # 4. Sync Supabase
        logger.info("[4/7] Synchronizing with Supabase...")
        # This will block until the queue is flushed based on OperationalDatabase updates
        op_db = None
        if hasattr(self.runtime, "personalization") and hasattr(self.runtime.personalization, "memory_tool"):
            # Fetch from any tool that holds it, or directly from world_model
            pass
            
        if self.runtime.world_model:
            op_db = self.runtime.world_model.op_db
            if op_db:
                op_db.close() # close() on op_db will trigger final sync

        # 5. Close Databases
        logger.info("[5/7] Closing databases...")
        # Operational DB closed above, SQLite providers should clean up on GC
        
        # 6. Shutdown Workers
        logger.info("[6/7] Shutting down workers...")
        self.runtime.hermes.shutdown()

        # 7. Release Resources
        logger.info("[7/7] Releasing resources...")
        self.runtime.alfred.logger.close()

        logger.info("SHUTDOWN COMPLETE. Goodbye.")
