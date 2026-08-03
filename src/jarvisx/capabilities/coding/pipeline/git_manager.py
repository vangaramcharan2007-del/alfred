from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel

class GitOperationError(RuntimeError):
    pass

class GitPermissionDeniedException(PermissionError):
    pass

class GitManager:
    def __init__(
        self,
        sandbox_manager: Optional[SandboxManager] = None,
        permission_manager: Optional[PermissionManager] = None
    ):
        self.sandbox = sandbox_manager or SandboxManager(allowed_commands=["git"])
        self.permission_manager = permission_manager or PermissionManager()

    async def get_status(self, repo_path: str) -> Dict[str, Any]:
        res = await self.sandbox.execute_command("git status --short", cwd=repo_path)
        return {
            "clean": res.get("stdout", "").strip() == "",
            "output": res.get("stdout", ""),
            "exit_code": res.get("exit_code", 0)
        }

    async def get_diff(self, repo_path: str) -> str:
        res = await self.sandbox.execute_command("git diff", cwd=repo_path)
        return res.get("stdout", "")

    async def create_branch(self, repo_path: str, branch_name: str) -> bool:
        res = await self.sandbox.execute_command(f"git checkout -b {branch_name}", cwd=repo_path)
        return res.get("exit_code") == 0

    async def commit_changes(self, repo_path: str, message: str, capability_name: str = "coding_agent") -> bool:
        # Commit requires WRITE permission
        if not self.permission_manager.check_permission(capability_name, PermissionLevel.WRITE):
            raise GitPermissionDeniedException("Git commit requires WRITE permission.")
        
        await self.sandbox.execute_command("git add .", cwd=repo_path)
        res = await self.sandbox.execute_command(f'git commit -m "{message}"', cwd=repo_path)
        return res.get("exit_code") == 0

    async def push_branch(self, repo_path: str, remote: str = "origin", branch: str = "main", capability_name: str = "coding_agent") -> bool:
        # Push is strictly gated and requires EXECUTE or dangerous actions approval in PermissionManager
        if not self.permission_manager.check_permission(capability_name, PermissionLevel.EXECUTE):
            raise GitPermissionDeniedException("Git push requires explicit EXECUTE approval in PermissionManager.")
        
        res = await self.sandbox.execute_command(f"git push {remote} {branch}", cwd=repo_path)
        return res.get("exit_code") == 0
