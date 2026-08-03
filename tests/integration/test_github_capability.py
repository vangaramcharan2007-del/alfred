import os
import pytest
from jarvisx.missions.mission_executor import MissionExecutor
from jarvisx.missions.mission import Mission

@pytest.mark.asyncio
async def test_integration_github_capability_explicit_not_available():
    # Ensure token is unset to test explicit NOT_AVAILABLE contract
    old_tok = os.environ.pop("GITHUB_TOKEN", None)
    try:
        executor = MissionExecutor()
        mission = Mission(title="GitHub Integration Test", user_request="Test GitHub PR handling")
        result = await executor.execute(mission)

        assert "github_pr" in result
        assert result["github_pr"]["status"] == "NOT_AVAILABLE"
        assert "GITHUB_TOKEN missing" in result["github_pr"]["reason"]
    finally:
        if old_tok:
            os.environ["GITHUB_TOKEN"] = old_tok
