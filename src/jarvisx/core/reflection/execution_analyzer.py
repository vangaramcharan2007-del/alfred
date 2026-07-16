import logging
from .learning_store import LearningStore

logger = logging.getLogger(__name__)

class ExecutionAnalyzer:
    """
    Analyzes post-mortem execution data to identify bottlenecks and failure reasons.
    """
    def __init__(self, store: LearningStore):
        self.store = store

    def analyze_objective(self, objective_id: str, estimated_hours: float, actual_hours: float, failure_reasons: list):
        """
        Parses raw execution data and logs a structured lesson.
        """
        lesson_data = {
            "estimated_duration": estimated_hours,
            "actual_duration": actual_hours,
            "variance": actual_hours - estimated_hours,
            "primary_failure": failure_reasons[0] if failure_reasons else None,
            "all_failures": failure_reasons
        }
        
        self.store.log_lesson(
            category="execution_lessons", 
            context_id=objective_id, 
            data=lesson_data
        )
        logger.info(f"Execution analyzed and stored for {objective_id}")
