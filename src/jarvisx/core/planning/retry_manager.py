import uuid
import logging
from .objective_store import ObjectiveStore

logger = logging.getLogger(__name__)

class RetryManager:
    """
    Enforces retry strategies for failed tasks.
    """
    def __init__(self, store: ObjectiveStore):
        self.store = store

    def log_failure(self, task_id: str, reason: str, strategy: str = "linear"):
        self.store.execute_transaction([
            ("INSERT INTO retry_history (id, task_id, failure_reason, retry_strategy) VALUES (?, ?, ?, ?)",
             (str(uuid.uuid4()), task_id, reason, strategy)),
            ("UPDATE tasks SET status = 'failed' WHERE id = ?", (task_id,))
        ])
        logger.warning(f"Task {task_id} failed: {reason}. Strategy: {strategy}")

    def get_retry_count(self, task_id: str) -> int:
        cursor = self.store.conn.execute("SELECT count(*) as c FROM retry_history WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        return row["c"] if row else 0
