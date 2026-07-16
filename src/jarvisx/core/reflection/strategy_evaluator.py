import logging
import uuid
from .learning_store import LearningStore

logger = logging.getLogger(__name__)

class StrategyEvaluator:
    """
    Calculates execution and planning efficiency scores.
    """
    def __init__(self, store: LearningStore):
        self.store = store

    def evaluate_objective(self, objective_id: str, estimated_hours: float, actual_hours: float, retry_count: int):
        planning_accuracy = min(estimated_hours / actual_hours, 1.0) if actual_hours > 0 else 1.0
        # A simple heuristic for execution efficiency
        execution_efficiency = max(1.0 - (retry_count * 0.1), 0.1)
        
        self.store.conn.execute(
            "INSERT INTO strategy_evaluations (id, objective_id, planning_accuracy, execution_efficiency, recovery_efficiency) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), objective_id, planning_accuracy, execution_efficiency, 1.0)
        )
        self.store.conn.commit()
