import pytest
from jarvisx.capabilities.coding.execution_history import ExecutionHistory

def test_execution_history_tracking():
    history = ExecutionHistory(mission_id="mission_test_123")
    assert history.mission_id == "mission_test_123"

    rec1 = history.record_attempt(
        attempt_number=1,
        changes_made=[{"file": "main.py", "action": "modified"}],
        tests_executed=True,
        test_passed=False,
        failures=["ZeroDivisionError: division by zero"],
        duration_seconds=0.5
    )

    assert rec1.attempt_number == 1
    assert rec1.test_passed is False
    assert len(rec1.failures) == 1

    rec2 = history.record_attempt(
        attempt_number=2,
        changes_made=[{"file": "main.py", "action": "modified"}],
        tests_executed=True,
        test_passed=True,
        successful_fixes=["Added zero guard check"],
        duration_seconds=0.4
    )

    assert rec2.test_passed is True
    assert history.get_successful_fixes() == ["Added zero guard check"]
    
    summary = history.to_dict()
    assert summary["total_attempts"] == 2
    assert summary["successful"] is True
