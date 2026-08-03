import pytest
from jarvisx.runtime.runtime import JarvisRuntime

@pytest.mark.asyncio
async def test_golden_mission_1_python_rest_api():
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    res = await runtime.process_task("Create a Python REST API")
    assert res["status"] == "COMPLETED"

    result = res["mission_result"]["result"]
    files = result["files_changed"]
    assert "app.py" in files
    assert "test_app.py" in files
    assert "README.md" in files

    assert result["test_result"]["exit_code"] == 0
    assert result["git_result"]["status"] == "COMMITTED"

    await runtime.stop()
