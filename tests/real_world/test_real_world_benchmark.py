import pytest
from jarvisx.runtime.runtime import JarvisRuntime

REAL_USER_SCENARIOS = [
    "Add login to this Flask project",
    "Why does this API return 500?",
    "Optimize this slow script",
    "Explain this repository",
    "Convert this script into a package",
    "Add JWT token validation middleware",
    "Fix database connection leak",
    "Create Dockerfile and docker-compose service",
    "Add OpenAPI endpoint validation tests",
    "Refactor monolithic script into modular components"
]

@pytest.mark.asyncio
@pytest.mark.parametrize("user_request", REAL_USER_SCENARIOS)
async def test_real_world_developer_scenarios(user_request):
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    res = await runtime.process_task(user_request)
    assert res["status"] == "COMPLETED"

    result = res["mission_result"]["result"]
    assert len(result["files_changed"]) > 0
    assert result["test_result"]["exit_code"] == 0
    assert result["git_result"]["status"] == "COMMITTED"

    await runtime.stop()
