import pytest
from jarvisx.capabilities.goose.goose_session import GooseSessionManager

def test_goose_session_manager():
    mgr = GooseSessionManager()
    session = mgr.create_session("TestEnterpriseApp")

    assert session.session_id.startswith("goose_sess_")
    assert session.is_active is True

    mgr.record_task_history(session.session_id, {"action": "refactor_code", "status": "success"})
    assert len(session.history) == 1
    assert session.metrics["tasks_executed"] == 1

    active = mgr.list_active_sessions()
    assert len(active) == 1

    term = mgr.terminate_session(session.session_id)
    assert term is True
    assert len(mgr.list_active_sessions()) == 0
