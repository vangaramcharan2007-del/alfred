"""Objective Scheduler — handles delayed and recurring objective execution."""
import threading
import time
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from jarvisx.core.execution.persistent_queue import PersistentQueue, Priority

logger = logging.getLogger(__name__)

class ScheduledObjective:
    def __init__(self, run_at: float, objective_id: str, objective_text: str, objective_data: Dict[str, Any], priority: Priority = Priority.NORMAL):
        self.run_at = run_at
        self.objective_id = objective_id
        self.objective_text = objective_text
        self.objective_data = objective_data
        self.priority = priority


class ObjectiveScheduler:
    """Schedules objectives to be executed at a later time."""
    
    def __init__(self, queue: PersistentQueue):
        self.queue = queue
        self._scheduled: List[ScheduledObjective] = []
        self._lock = threading.Lock()
        
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        """Start the scheduler thread."""
        if self._thread and self._thread.is_alive():
            return
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="ObjectiveScheduler")
        self._thread.start()

    def stop(self):
        """Stop the scheduler."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def get_queue_length(self) -> int:
        """Return the number of scheduled objectives pending execution."""
        with self._lock:
            return len(self._scheduled)

    def schedule_delay(self, delay_seconds: float, objective_id: str, objective_text: str, objective_data: Dict[str, Any], priority: Priority = Priority.NORMAL):
        """Schedule an objective to run after a specific delay."""
        run_at = time.time() + delay_seconds
        self.schedule_at(run_at, objective_id, objective_text, objective_data, priority)

    def schedule_at(self, run_at_timestamp: float, objective_id: str, objective_text: str, objective_data: Dict[str, Any], priority: Priority = Priority.NORMAL):
        """Schedule an objective to run at a specific Unix timestamp."""
        obj = ScheduledObjective(run_at_timestamp, objective_id, objective_text, objective_data, priority)
        with self._lock:
            self._scheduled.append(obj)
            # Sort by run_at ascending
            self._scheduled.sort(key=lambda x: x.run_at)
        logger.info(f"Scheduled objective {objective_id} for {datetime.fromtimestamp(run_at_timestamp)}")

    def _run_loop(self):
        """Main loop that moves scheduled objectives into the persistent queue."""
        while not self._stop_event.is_set():
            now = time.time()
            to_enqueue = []
            
            with self._lock:
                # Find all objectives that should run now
                while self._scheduled and self._scheduled[0].run_at <= now:
                    to_enqueue.append(self._scheduled.pop(0))
                    
            for obj in to_enqueue:
                logger.info(f"Enqueuing scheduled objective: {obj.objective_id}")
                self.queue.enqueue(obj.objective_id, obj.objective_text, obj.objective_data, obj.priority)
                
            time.sleep(0.5)
