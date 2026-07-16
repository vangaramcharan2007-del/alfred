import logging
import json
from .learning_store import LearningStore

logger = logging.getLogger(__name__)

class PatternDetector:
    """
    Scans the learning database to find frequent failures and dependency bottlenecks.
    """
    def __init__(self, store: LearningStore):
        self.store = store

    def detect_frequent_failures(self) -> list:
        lessons = self.store.get_lessons(category="execution_lessons", limit=100)
        failure_counts = {}
        for lesson in lessons:
            data = json.loads(lesson["lesson_data"])
            primary = data.get("primary_failure")
            if primary:
                failure_counts[primary] = failure_counts.get(primary, 0) + 1
                
        # Return failures that happened more than once
        return [reason for reason, count in failure_counts.items() if count > 1]
