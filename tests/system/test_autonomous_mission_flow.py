import pytest
from jarvisx.runtime.runtime import JarvisRuntime

@pytest.mark.asyncio
async def test_system_autonomous_mission_flow():
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    user_prompt = "Create a simple todo application"
    res = await runtime.process_task(user_prompt)

    assert res["status"] == "COMPLETED"
    mission_res = res["mission_result"]
    mission = mission_res["mission"]
    result = mission_res["result"]

    # 1. Understands intent
    assert mission["intent"] == "engineering"

    # 2. Creates mission
    assert mission["mission_id"].startswith("mission_")

    # 3. Generates architecture
    assert "architecture" in result
    assert result["architecture"] != ""

    # 4. Selects LLM & 5. Selects coding agent
    assert mission["capability"] == "coding.agent"
    assert mission["provider"] in ("goose", "openhands")

    # 6. Creates files
    files_created = result["provider_output"]["files_created"]
    assert "app.py" in files_created
    assert "test_app.py" in files_created
    assert "README.md" in files_created

    # 7. Runs tests
    assert result["test_result"]["exit_code"] == 0

    # 8. Generates git changes
    assert result["git_result"]["status"] == "COMMITTED"

    # 9. Stores memory
    assert "evolution_memory" in result
    assert result["evolution_memory"]["success"] is True

    # 10. Reports completion
    assert mission["status"] == "COMPLETED"

    await runtime.stop()
