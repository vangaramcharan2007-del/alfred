import tempfile
from jarvisx.capabilities.openhands.openhands_workspace import OpenHandsWorkspaceManager

def test_openhands_workspace_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = OpenHandsWorkspaceManager(base_workspace_dir=tmpdir)
        ws = mgr.create_workspace(persistent=False)

        assert ws.workspace_id.startswith("oh_ws_")
        assert ws.is_active is True

        repo_ws = mgr.open_repository(tmpdir)
        assert repo_ws is not None

        assert mgr.reset_workspace(ws.workspace_id) is True
        assert mgr.close_workspace(ws.workspace_id) is True
        assert mgr.cleanup(ws.workspace_id) is True
