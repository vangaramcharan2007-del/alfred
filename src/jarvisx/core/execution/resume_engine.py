"""Resume Engine — recovers and resumes objectives on startup."""
import logging
from typing import List
from contextlib import closing

from jarvisx.core.execution.persistent_queue import PersistentQueue
from jarvisx.core.execution.objective_state_machine import ObjectiveStatus
from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent

logger = logging.getLogger(__name__)

class ResumeEngine:
    """Detects unfinished objectives and requeues them on startup."""
    
    def __init__(self, queue: PersistentQueue, event_bus: EventBus):
        self.queue = queue
        self.event_bus = event_bus

    def resume_unfinished_objectives(self):
        """Finds any RUNNING or QUEUED objectives and ensures they are in a state to be picked up by the BackgroundWorker."""
        # On startup, any RUNNING objective was interrupted by a crash.
        # We need to set them back to QUEUED so the BackgroundWorker will pick them up again.
        interrupted = self.queue.get_all_by_status([ObjectiveStatus.RUNNING])
        
        for obj in interrupted:
            logger.info(f"Detected interrupted objective: {obj['objective_id']}. Requeueing.")
            # Move from RUNNING -> FAILED -> QUEUED (according to state machine rules)
            # Actually, the state machine allows RUNNING -> FAILED -> RUNNING
            # But the worker expects to pick up QUEUED objectives.
            # State machine transition: RUNNING -> FAILED -> RUNNING isn't QUEUED.
            # But wait, our state machine doesn't allow FAILED -> QUEUED.
            # It allows FAILED -> RUNNING.
            # To cleanly put it in QUEUED, we might need a bypass for ResumeEngine,
            # or just change status bypassing the state machine for startup recovery,
            # or add a transition FAILED -> QUEUED.
            # Alternatively, Resume Engine directly feeds them to the worker, but the worker polls the DB.
            # Let's bypass internal state machine checks specifically for crash recovery (it's essentially a rollback).
            
            # Safe way using internal update (bypassing the strict state machine if we just update the DB):
            # However, PersistentQueue.update_status enforces it.
            # If we set it to FAILED, then we can transition to RUNNING when we start it.
            # For simplicity, we just reset the DB status to QUEUED manually so the worker's standard `dequeue` works.
            import sqlite3
            with closing(sqlite3.connect(self.queue.db_path)) as conn, conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE objectives SET status = ? WHERE objective_id = ?", (ObjectiveStatus.QUEUED.value, obj['objective_id']))
                conn.commit()
            
            self.event_bus.publish(ExecutionEvent.OBJECTIVE_RESTARTED, {"objective_id": obj['objective_id']})
            
        queued = self.queue.get_all_by_status([ObjectiveStatus.QUEUED])
        logger.info(f"[Resume] Found {len(queued)} objectives waiting to run.")
        
        # Paused objectives remain paused.
