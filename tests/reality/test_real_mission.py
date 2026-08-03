import pytest
from jarvisx.runtime.runtime import JarvisRuntime

@pytest.mark.asyncio
@pytest.mark.parametrize("task_title", [
    "Create a calculator CLI",
    "Fix a broken Python project",
    "Analyze an unknown repository",
    "Generate documentation",
    "Refactor a module"
])
async def test_real_mission_execution(task_title):
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    res = await runtime.process_task(task_title)
    assert res["status"] == "COMPLETED"

    result = res["mission_result"]["result"]
    assert len(result["files_changed"]) > 0
    assert result["test_result"]["exit_code"] == 0
    assert result["git_result"]["status"] == "COMMITTED"

    await runtime.stop()
