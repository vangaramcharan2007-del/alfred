import pytest
import tempfile
from pathlib import Path
from jarvisx.capabilities.goose.goose_executor import GooseExecutor

@pytest.mark.asyncio
async def test_goose_executor_mission():
    executor = GooseExecutor()
    with tempfile.TemporaryDirectory() as tmpdir:
        res = await executor.execute_mission(
            mission_type="fix_bug",
            task_description="Fix null check in user controller",
            repo_path=tmpdir,
            session_id="test_sess_001"
        )
        assert res["status"] == "completed"
        assert res["mission_type"] == "fix_bug"
        assert "sandbox_id" in res
