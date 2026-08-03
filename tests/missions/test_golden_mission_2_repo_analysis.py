import pytest
from jarvisx.runtime.runtime import JarvisRuntime

@pytest.mark.asyncio
async def test_golden_mission_2_repository_analysis():
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    res = await runtime.process_task("Analyze an existing repository")
    assert res["status"] == "COMPLETED"

    result = res["mission_result"]["result"]
    files = result["files_changed"]
    assert "ARCHITECTURE_REPORT.md" in files
    assert result["git_result"]["status"] == "COMMITTED"

    await runtime.stop()
