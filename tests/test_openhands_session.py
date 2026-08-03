import pytest
from jarvisx.capabilities.openhands.openhands_session import OpenHandsSessionManager

def test_openhands_session_manager():
    mgr = OpenHandsSessionManager()
    session = mgr.start_session("EnterpriseMicroservice")

    assert session.session_id.startswith("oh_sess_")
    assert session.is_active is True

    mgr.record_task_history(session.session_id, {"action": "refactor", "status": "success"})
    assert len(session.history) == 1

    assert mgr.pause_session(session.session_id) is True
    assert session.is_paused is True

    assert mgr.resume_session(session.session_id) is True
    assert session.is_paused is False

    assert mgr.terminate_session(session.session_id) is True
    assert session.is_active is False
