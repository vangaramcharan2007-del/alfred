"""Background Worker — executes objectives independently of the chat interface."""
import threading
import time
import logging
from typing import Optional, Dict, Any

from jarvisx.core.execution.persistent_queue import PersistentQueue
from jarvisx.core.execution.execution_dispatcher import ExecutionDispatcher
from jarvisx.core.execution.objective_state_machine import ObjectiveStatus
from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.core.execution.checkpoint_manager import CheckpointManager

logger = logging.getLogger(__name__)

class BackgroundWorker:
    """A threaded background worker that pulls from the PersistentQueue."""

    def __init__(self, queue: PersistentQueue, dispatcher: ExecutionDispatcher, event_bus: EventBus, checkpoint_manager: CheckpointManager):
        self.queue = queue
        self.dispatcher = dispatcher
        self.event_bus = event_bus
        self.checkpoint_manager = checkpoint_manager
        
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        # We need a way to tell the executor to pause mid-objective.
        # This will be injected into the executor or context.
        self._current_objective_id: Optional[str] = None
        # Thread-safe flag for the active task
        self._task_pause_flag = False

    def start(self, start_paused: bool = False):
        """Start the background worker thread.
        
        Args:
            start_paused: If True, the worker starts in a paused state and will
                          not process objectives until resume() is called.
        """
        if self._thread and self._thread.is_alive():
            logger.warning("Background worker already running.")
            return

        self._stop_event.clear()
        # Only clear pause if not requesting a paused start AND not already set externally
        if not start_paused and not self._pause_event.is_set():
            self._pause_event.clear()
        elif start_paused:
            self._pause_event.set()

        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="BackgroundWorker")
        self._thread.start()
        
        self.event_bus.publish(ExecutionEvent.BACKGROUND_WORKER_STARTED, {})
        logger.info("[Worker] Started")

    def is_running(self) -> bool:
        """Return True if the worker thread is alive and not paused or stopped."""
        return (self._thread is not None 
                and self._thread.is_alive() 
                and not self._stop_event.is_set() 
                and not self._pause_event.is_set())

    def _run_loop(self):
        """Main execution loop for the background worker."""
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                time.sleep(1.0)
                continue
                
            # Dequeue the next objective
            try:
                objective = self.queue.dequeue()
            except Exception as e:
                logger.error(f"[Worker] Error dequeuing: {e}")
                objective = None
                
            if not objective:
                time.sleep(1.0)
                continue

            self._current_objective_id = objective["objective_id"]
            self._task_pause_flag = False
            
            logger.info(f"[Worker] Starting objective: {self._current_objective_id}")
            
            # Load checkpoint if exists
            snapshot = self.checkpoint_manager.load_checkpoint(self._current_objective_id)
            
            if snapshot:
                logger.info(f"[Resume] Continuing From Step {snapshot.current_step + 1}")
                self.event_bus.publish(ExecutionEvent.OBJECTIVE_RESUMED, {"objective_id": self._current_objective_id})

            try:
                # Dispatch the objective
                # We need to pass a callback or reference to check for pause
                # In this architecture, we pass the worker itself or a lambda to check pause
                result = self.dispatcher.task_executor.execute_objective(
                    objective["objective_data"], 
                    snapshot=snapshot,
                    pause_check_fn=lambda: self._task_pause_flag or self._pause_event.is_set() or self._stop_event.is_set()
                )
                
                # Check outcome
                if self._task_pause_flag or self._pause_event.is_set():
                    logger.info(f"[Worker] Paused objective {self._current_objective_id}")
                    self.queue.update_status(self._current_objective_id, ObjectiveStatus.PAUSED)
                    self.event_bus.publish(ExecutionEvent.OBJECTIVE_PAUSED, {"objective_id": self._current_objective_id})
                elif result.get("success", False):
                    logger.info(f"[Worker] Completed objective {self._current_objective_id}")
                    self.queue.update_status(self._current_objective_id, ObjectiveStatus.COMPLETED)
                    # Clean up checkpoint on success
                    self.checkpoint_manager.delete_checkpoint(self._current_objective_id)
                    self.event_bus.publish(ExecutionEvent.OBJECTIVE_COMPLETED, {"objective_id": self._current_objective_id})
                else:
                    logger.error(f"[Worker] Failed objective {self._current_objective_id}")
                    self.queue.update_status(self._current_objective_id, ObjectiveStatus.FAILED, last_error=str(result.get("error", "Unknown Error")))
                    self.event_bus.publish(ExecutionEvent.OBJECTIVE_FAILED, {"objective_id": self._current_objective_id})
                    
            except Exception as e:
                logger.error(f"[Worker] Exception in objective execution: {e}")
                self.queue.update_status(self._current_objective_id, ObjectiveStatus.FAILED, last_error=str(e))
                self.event_bus.publish(ExecutionEvent.OBJECTIVE_FAILED, {"objective_id": self._current_objective_id})
                
            finally:
                self._current_objective_id = None

    def stop(self):
        """Stop the background worker."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self.event_bus.publish(ExecutionEvent.BACKGROUND_WORKER_STOPPED, {})
        logger.info("[Worker] Stopped")

    def shutdown(self):
        self.stop()

    def pause(self):
        """Pause the entire worker."""
        self._pause_event.set()
        logger.info("[Worker] Paused")

    def resume(self):
        """Resume the entire worker."""
        self._pause_event.clear()
        logger.info("[Worker] Resumed")

    def pause_objective(self, objective_id: str):
        """Pause a specific objective."""
        if self._current_objective_id == objective_id:
            self._task_pause_flag = True
        else:
            # If not currently running, just update the queue
            self.queue.pause(objective_id)

    def status(self) -> str:
        if self._stop_event.is_set() or not self._thread:
            return "STOPPED"
        if self._pause_event.is_set():
            return "PAUSED"
        return "RUNNING"

    def statistics(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "active_objective": self._current_objective_id,
            "queue_length": self.queue.queue_length()
        }

    def active_objective(self) -> Optional[str]:
        return self._current_objective_id

    def queue_length(self) -> int:
        return self.queue.queue_length()
