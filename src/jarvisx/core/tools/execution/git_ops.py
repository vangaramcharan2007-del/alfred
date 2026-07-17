import logging
from typing import Dict, Any, Optional
from .command_executor import CommandExecutor
from .permissions import PermissionManager, TrustLevel

logger = logging.getLogger(__name__)

class GitOps:
    @staticmethod
    def _run_git(cmd: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        PermissionManager.check_permission(TrustLevel.LEVEL_3_GIT)
        return CommandExecutor.execute(f"git {cmd}", cwd=cwd)

    @staticmethod
    def status(cwd: Optional[str] = None) -> str:
        res = GitOps._run_git("status", cwd)
        return res["stdout"]

    @staticmethod
    def add(files: str = ".", cwd: Optional[str] = None) -> bool:
        res = GitOps._run_git(f"add {files}", cwd)
        return res["success"]

    @staticmethod
    def commit(message: str, cwd: Optional[str] = None) -> bool:
        res = GitOps._run_git(f'commit -m "{message}"', cwd)
        return res["success"]

    @staticmethod
    def push(remote: str = "origin", branch: str = "main", cwd: Optional[str] = None) -> bool:
        res = GitOps._run_git(f"push {remote} {branch}", cwd)
        return res["success"]

    @staticmethod
    def pull(remote: str = "origin", branch: str = "main", cwd: Optional[str] = None) -> bool:
        res = GitOps._run_git(f"pull {remote} {branch}", cwd)
        return res["success"]

    @staticmethod
    def checkout(branch: str, cwd: Optional[str] = None) -> bool:
        res = GitOps._run_git(f"checkout {branch}", cwd)
        return res["success"]

    @staticmethod
    def branch(branch: str, cwd: Optional[str] = None) -> bool:
        res = GitOps._run_git(f"branch {branch}", cwd)
        return res["success"]

    @staticmethod
    def rollback(cwd: Optional[str] = None) -> bool:
        res = GitOps._run_git("reset --hard HEAD~1", cwd)
        return res["success"]
