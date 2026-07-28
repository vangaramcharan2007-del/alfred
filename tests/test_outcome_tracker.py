import pytest
from jarvisx.cognition.outcome_tracker import OutcomeTracker
from jarvisx.cognition.metrics import metrics

def test_outcome_tracker_record():
    tracker = OutcomeTracker(metrics)
    initial = len(tracker.outcomes)
    tracker.record_outcome("test task", "agent1", True, 1.5)
    assert len(tracker.outcomes) == initial + 1
    assert tracker.outcomes[-1]["success"] is True
