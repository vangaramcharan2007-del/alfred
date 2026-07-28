import pytest
from jarvisx.cognition.decision_record import DecisionRecord

def test_decision_record_creation():
    record = DecisionRecord(
        task="Do this",
        selected_agent="friday",
        alternatives=["edith"],
        reasons=["capability"],
        confidence=0.9
    )
    assert record.task == "Do this"
    assert record.selected_agent == "friday"
    assert len(record.alternatives) == 1
