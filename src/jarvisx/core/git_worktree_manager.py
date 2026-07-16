import os
import subprocess
import logging
import uuid
from pathlib import Path
from typing import Optional

logger = logging.getLogger("GitWorktreeManager")

class GitWorktreeManager:
    """
    Manages isolated git worktrees for parallel agent execution.
    """
    def __init__(self, repo_path: str, base_worktree_dir: str = "/tmp/jarvisx_worktrees"):
        self.repo_path = Path(repo_path)
        self.base_worktree_dir = Path(base_worktree_dir)
        self.active_worktrees = {}

        if not self.base_worktree_dir.exists():
            self.base_worktree_dir.mkdir(parents=True, exist_ok=True)

    def _run_git(self, args: list, cwd: Optional[Path] = None) -> str:
        cwd = cwd or self.repo_path
        cmd = ["git"] + args
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(cmd)}\nError: {e.stderr}")
            raise

    def create_worktree(self, base_branch: str, feature_branch: str) -> str:
        """
        Creates a new worktree checked out to a new feature branch.
        """
        worktree_id = f"wt-{uuid.uuid4().hex[:8]}"
        worktree_path = self.base_worktree_dir / worktree_id
        
        logger.info(f"Creating git worktree at {worktree_path} on branch {feature_branch}")
        
        # Ensure the feature branch exists or create it from base
        try:
            self._run_git(["rev-parse", "--verify", feature_branch])
            # Branch exists, just add worktree
            self._run_git(["worktree", "add", str(worktree_path), feature_branch])
        except subprocess.CalledProcessError:
            # Branch doesn't exist, create it via worktree add -b
            self._run_git(["worktree", "add", "-b", feature_branch, str(worktree_path), base_branch])

        self.active_worktrees[feature_branch] = str(worktree_path)
        return str(worktree_path)

    def destroy_worktree(self, feature_branch: str) -> bool:
        """
        Removes the worktree associated with the given branch.
        """
        worktree_path = self.active_worktrees.get(feature_branch)
        if not worktree_path:
            logger.warning(f"No active worktree found for branch {feature_branch}")
            return False

        logger.info(f"Destroying git worktree at {worktree_path}")
        try:
            self._run_git(["worktree", "remove", "--force", worktree_path])
            del self.active_worktrees[feature_branch]
            return True
        except subprocess.CalledProcessError:
            logger.error(f"Failed to remove worktree at {worktree_path}")
            return False

    def list_worktrees(self) -> list:
        """
        Lists all active worktrees known to git.
        """
        output = self._run_git(["worktree", "list"])
        return output.splitlines()

    def prevent_conflict(self, branch: str) -> bool:
        """
        Stub to implement sequential rebasing strategy if multiple agents
        are modifying the same paths in the future.
        """
        pass
