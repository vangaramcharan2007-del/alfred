"""Execution Dispatcher — routes objectives to the correct executor."""
import logging
from typing import Dict, Any

from jarvisx.core.execution.task_executor import TaskExecutor

logger = logging.getLogger(__name__)

class ExecutionDispatcher:
    """Dispatches an objective to the appropriate execution engine."""
    
    def __init__(self, task_executor: TaskExecutor):
        self.task_executor = task_executor
        
    def dispatch(self, objective_data: Dict[str, Any], snapshot=None):
        """
        Route the objective. Currently routes everything to TaskExecutor.
        In the future, this can inspect objective_type and route to Mobile/Browser/etc.
        """
        logger.info(f"Dispatching objective: {objective_data.get('objective_id')}")
        self.task_executor.execute_objective(objective_data, snapshot=snapshot)
