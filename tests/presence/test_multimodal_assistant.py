import pytest
from jarvisx.runtime.runtime import JarvisRuntime
from jarvisx.presence.presence_manager import PresenceManager
from jarvisx.personality.persona import AlfredPersona

@pytest.mark.asyncio
async def test_multimodal_assistant_flow():
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    presence_mgr = PresenceManager()
    persona = AlfredPersona()

    user_utterance = "Alfred, create a Python API from this design document"

    # 1. Process Multimodal Voice + Screen Input
    presence_res = await presence_mgr.process_multimodal_input(user_utterance)
    assert presence_res["wake_detected"] is True
    assert "create a Python API" in presence_res["command"]
    assert presence_res["screen_context"]["status"] == "ANALYZED"

    # 2. Execute Mission from Transcribed Command
    mission_res = await runtime.process_task(presence_res["command"])
    assert mission_res["status"] == "COMPLETED"

    result = mission_res["mission_result"]["result"]
    assert "app.py" in result["files_changed"]
    assert result["test_result"]["exit_code"] == 0

    # 3. Format Alfred Personality Speech Output
    speech_output = persona.format_mission_completion(
        mission_title="Create a Python API",
        test_status=result["test_result"]["status"]
    )

    assert "Sir, the implementation for 'Create a Python API' has been completed." in speech_output
    assert "test suite status is PASS" in speech_output

    await runtime.stop()
