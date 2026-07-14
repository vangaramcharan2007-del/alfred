import logging

class SplitBrainDetector:
    """Detects if multiple execution nodes claim ownership over the same task."""
    def __init__(self):
        # Maps task_id -> active node_id
        self.active_tasks = {}

    def verify_single_writer(self, task_id: str, claiming_node_id: str) -> bool:
        current_owner = self.active_tasks.get(task_id)
        if current_owner and current_owner != claiming_node_id:
            logging.critical(f"[SplitBrain] VIOLATION: {claiming_node_id} attempted to write to {task_id}, but {current_owner} holds the lease!")
            return False
        
        self.active_tasks[task_id] = claiming_node_id
        return True
