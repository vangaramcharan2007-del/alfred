import pytest
from pathlib import Path
from jarvisx.runtime.runtime import JarvisRuntime

@pytest.mark.asyncio
async def test_random_engineering_task_weather_cli():
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    res = await runtime.process_task("Build a weather CLI application")
    assert res["status"] == "COMPLETED"

    result = res["mission_result"]["result"]
    mission_id = result["mission_id"]

    # 1. Verify dynamic plan & requirements
    assert "plan" in result
    assert result["plan"]["user_request"] == "Build a weather CLI application"

    # 2. Verify confidence & risk evaluation
    assert "confidence" in result
    assert "risk" in result
    assert result["risk"]["risk_level"] == "LOW"

    # 3. Verify workspace files & sandbox test
    files = result["files_changed"]
    assert "app.py" in files
    assert "test_app.py" in files

    assert result["test_result"]["exit_code"] == 0
    assert result["git_result"]["status"] == "COMMITTED"

    # 4. Verify isolated workspace MISSION_REPORT.md
    ws_report = Path("workspace") / mission_id / "MISSION_REPORT.md"
    assert ws_report.exists()
    report_text = ws_report.read_text(encoding="utf-8")
    assert "Mission Intelligence Report" in report_text
    assert "Build a weather CLI application" in report_text

    await runtime.stop()
