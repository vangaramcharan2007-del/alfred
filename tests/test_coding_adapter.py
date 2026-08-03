import pytest
import tempfile
from pathlib import Path
from jarvisx.capabilities.coding.coding_adapter import CodingAdapter
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel

@pytest.mark.asyncio
async def test_coding_adapter_lifecycle_and_execution():
    pm = PermissionManager()
    pm.request_permission("coding_agent", PermissionLevel.READ)
    pm.request_permission("coding_agent", PermissionLevel.WRITE)
    pm.request_permission("coding_agent", PermissionLevel.EXECUTE)

    adapter = CodingAdapter(permission_manager=pm)
    await adapter.initialize()
    assert await adapter.health_check() is True

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mini FastAPI setup
        main_file = Path(tmpdir) / "main.py"
        main_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")

        inputs = {
            "repository": tmpdir,
            "task_description": "Add a calculator API endpoint to this FastAPI project",
            "test_command": "python -c \"print('1 passed')\""
        }

        result = await adapter.execute(inputs)
        assert result["status"] == "success"
        assert result["repository_context"]["framework"] == "FastAPI"
        assert len(result["plan"]["steps"]) > 0
        assert len(result["code_changes"]) > 0
        assert result["test_results"]["passed"] is True
        assert result["review"]["approved"] is True
        assert result["metrics"]["coding_tasks_completed"] == 1

    await adapter.shutdown()
    assert await adapter.health_check() is False
