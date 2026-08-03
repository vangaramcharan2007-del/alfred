import pytest
from pathlib import Path
from jarvisx.workspace.workspace_manager import WorkspaceManager

def test_real_file_creation():
    wm = WorkspaceManager(base_dir="workspace")
    m_dir = wm.get_mission_dir("test_file_creation_id")
    assert m_dir.exists()
    assert (m_dir / "files").exists()
    assert (m_dir / "tests").exists()
    assert (m_dir / "logs").exists()
