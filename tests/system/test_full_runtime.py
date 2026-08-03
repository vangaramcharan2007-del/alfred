import pytest
from jarvisx.runtime.runtime import JarvisRuntime

@pytest.mark.asyncio
async def test_system_full_runtime_lifecycle():
    runtime = JarvisRuntime()
    state = await runtime.start(print_banner=False)

    assert state.state_name == "RUNNING"
    assert runtime.bootstrap.state.services["Memory"].status == "ONLINE"
    assert runtime.bootstrap.state.services["LLM Gateway"].status == "ONLINE"
    assert runtime.bootstrap.state.services["Capabilities"].status == "ONLINE"
    assert runtime.bootstrap.state.services["Agents"].status == "ONLINE"
    assert runtime.bootstrap.state.services["Git"].status == "ONLINE"

    sd = await runtime.stop()
    assert sd["status"] == "STOPPED"
