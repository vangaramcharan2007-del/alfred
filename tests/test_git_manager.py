import pytest
import tempfile
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel
from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager
from jarvisx.capabilities.coding.pipeline.git_manager import GitManager, GitPermissionDeniedException

@pytest.mark.asyncio
async def test_git_manager_push_gating():
    pm = PermissionManager()
    sandbox = SandboxManager(allowed_commands=["git", "echo", "python"])
    git_mgr = GitManager(sandbox_manager=sandbox, permission_manager=pm)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Push should fail without EXECUTE permission
        with pytest.raises(GitPermissionDeniedException):
            await git_mgr.push_branch(tmpdir, capability_name="coding_agent")

        # Grant dangerous actions / EXECUTE permission
        pm.grant_dangerous_actions()
        pm.request_permission("coding_agent", PermissionLevel.EXECUTE)

        # Now push passes permission check (git push itself might fail on dummy repo, but permission check passes)
        try:
            await git_mgr.push_branch(tmpdir, capability_name="coding_agent")
        except GitPermissionDeniedException:
            pytest.fail("GitPermissionDeniedException raised unexpectedly when EXECUTE permission granted.")
        except Exception:
            pass
