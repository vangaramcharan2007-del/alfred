import pytest
from jarvisx.runtime.runtime import JarvisRuntime

@pytest.mark.asyncio
async def test_integration_alfred_startup():
    runtime = JarvisRuntime()
    state = await runtime.start(print_banner=False)
    assert state is not None
    assert runtime.cli is not None
