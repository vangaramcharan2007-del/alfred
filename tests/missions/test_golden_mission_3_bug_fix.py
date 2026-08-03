import pytest
from jarvisx.runtime.runtime import JarvisRuntime

@pytest.mark.asyncio
async def test_golden_mission_3_fix_real_bug():
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    res = await runtime.process_task("Fix a real bug in division module")
    assert res["status"] == "COMPLETED"

    result = res["mission_result"]["result"]
    files = result["files_changed"]
    assert "bug_module.py" in files
    assert "test_bug_module.py" in files

    assert result["test_result"]["exit_code"] == 0
    assert result["git_result"]["status"] == "COMMITTED"

    await runtime.stop()
