"""Learning Feedback Engine for Jarvis X (Layer 3 - Execution).

Compares expected outcomes vs actual outcomes to generate improvement suggestions and store feedback in SQLite.
"""

import time
from typing import Any, Dict, Optional

from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


class FeedbackEngine:
    """Zero-fluff production learning feedback loop engine."""

    def __init__(self, memory_provider: Optional[SQLiteMemoryProvider] = None):
        self.memory = memory_provider or SQLiteMemoryProvider(db_path="var/db/memory.db")

    def process_mission_feedback(
        self,
        mission_id: str,
        expected_effort_hours: float,
        actual_effort_hours: float,
        category: str = "assignment",
    ) -> Dict[str, Any]:
        """Compute deviation between expected and actual outcomes and generate learning adjustments."""
        diff_hours = round(actual_effort_hours - expected_effort_hours, 2)
        pct_change = round((diff_hours / max(0.1, expected_effort_hours)) * 100, 1)

        if abs(pct_change) < 15.0:
            learning = f"Estimate accurately matched actual performance (variance {pct_change:+.1f}%)."
            adjustment_multiplier = 1.0
        elif pct_change > 0:
            learning = f"Actual duration exceeded expectation by {diff_hours} hours. Future estimates increased by {int(pct_change)}%."
            adjustment_multiplier = round(1.0 + (pct_change / 100.0), 2)
        else:
            learning = f"Completed faster than expected by {abs(diff_hours)} hours. Future estimates reduced by {int(abs(pct_change))}%."
            adjustment_multiplier = round(1.0 - (abs(pct_change) / 100.0), 2)

        record = {
            "mission_id": mission_id,
            "category": category,
            "expected_effort_hours": expected_effort_hours,
            "actual_effort_hours": actual_effort_hours,
            "difference_hours": diff_hours,
            "percentage_change": pct_change,
            "learning": learning,
            "adjustment_multiplier": adjustment_multiplier,
            "recorded_at": time.time(),
        }

        # Store learning feedback record in SQLite memory
        self.memory.save_memory(
            category="feedback_learning",
            key=f"fb_{mission_id}",
            value=record,
            context={"module": "feedback_engine", "category": category}
        )

        return record
