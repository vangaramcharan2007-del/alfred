import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.github.github_capability import GitHubCapability

@pytest.mark.asyncio
async def test_github_capability_registration_and_execution():
    registry = CapabilityRegistry()
    github_cap = GitHubCapability()

    await github_cap.register_capability(registry)

    descriptor = registry.get("github.engineering")
    assert descriptor is not None
    assert "create_issue" in descriptor.supported_actions

    # Test issue creation via registry execute
    issue_dict = await registry.execute(
        "github.engineering",
        "create_issue",
        title="Refactor task planner",
        body="Optimize step ordering"
    )
    assert issue_dict["number"] == 1
    assert issue_dict["title"] == "Refactor task planner"

    # Test PR creation via registry execute
    pr_dict = await registry.execute(
        "github.engineering",
        "create_pr",
        title="feat: refactor task planner",
        body="PR implementation",
        head_branch="refactor/task-planner"
    )
    assert pr_dict["number"] == 101
    assert pr_dict["head_branch"] == "refactor/task-planner"
