import time
from typing import Dict, Any, List

class ProgressTracker:
    """Tracks the state and progress of an objective."""
    
    VALID_STATES = {"PENDING", "RUNNING", "FAILED", "COMPLETED", "RETRYING", "CANCELLED"}
    
    def __init__(self):
        self.state = "PENDING"
        self.completed_tasks = set()
        self.failed_tasks = set()
        self.retries = 0
        self.start_time = None
        self.end_time = None

    def start(self):
        self.state = "RUNNING"
        self.start_time = time.time()

    def mark_completed(self, task_id: str):
        self.completed_tasks.add(task_id)
        if task_id in self.failed_tasks:
            self.failed_tasks.remove(task_id)

    def mark_failed(self, task_id: str):
        self.failed_tasks.add(task_id)
        self.state = "FAILED"
        
    def increment_retry(self):
        self.retries += 1
        self.state = "RETRYING"

    def complete_objective(self):
        self.state = "COMPLETED"
        self.end_time = time.time()

    def cancel_objective(self):
        self.state = "CANCELLED"
        self.end_time = time.time()

    @property
    def elapsed_time(self) -> float:
        if not self.start_time:
            return 0.0
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def get_status(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "completed_tasks": list(self.completed_tasks),
            "failed_tasks": list(self.failed_tasks),
            "retries": self.retries,
            "elapsed_time": round(self.elapsed_time, 2)
        }
