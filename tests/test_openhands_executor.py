import pytest
import tempfile
from jarvisx.capabilities.openhands.openhands_executor import OpenHandsExecutor

@pytest.mark.asyncio
async def test_openhands_executor_mission():
    executor = OpenHandsExecutor()
    with tempfile.TemporaryDirectory() as tmpdir:
        res = await executor.execute_mission(
            mission_type="implement_feature",
            task_description="Build OpenAPI doc generator",
            repo_path=tmpdir,
            session_id="oh_sess_001"
        )
        assert res["status"] == "completed"
        assert res["mission_type"] == "implement_feature"
        assert "sandbox_id" in res
