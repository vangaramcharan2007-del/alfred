import logging
from typing import List, Dict

logger = logging.getLogger("WorkforceAggregator")

class WorkforceAggregator:
    """
    Collects outputs from worker agents, merges results, deduplicates work,
    and summarizes progress for Hermes.
    """
    def __init__(self, worktree_manager):
        self.worktree_manager = worktree_manager

    def merge_completed_task(self, task_id: str, branch: str) -> bool:
        """
        Attempts to merge a completed feature branch back into main.
        """
        logger.info(f"Aggregating results from task {task_id} (branch: {branch})")
        
        try:
            # Rebase feature branch on top of main
            logger.debug(f"Rebasing {branch} onto main...")
            self.worktree_manager._run_git(["checkout", branch])
            self.worktree_manager._run_git(["rebase", "main"])
            
            # Checkout main and merge
            self.worktree_manager._run_git(["checkout", "main"])
            self.worktree_manager._run_git(["merge", "--ff-only", branch])
            
            logger.info(f"Successfully merged {branch} into main.")
            
            # Cleanup worktree
            self.worktree_manager.destroy_worktree(branch)
            self.worktree_manager._run_git(["branch", "-d", branch])
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge {branch}. Conflict detected or rebase failed: {e}")
            # Abort rebase/merge to clean state
            try:
                self.worktree_manager._run_git(["rebase", "--abort"])
            except:
                pass
            try:
                self.worktree_manager._run_git(["merge", "--abort"])
            except:
                pass
            
            return False

    def summarize_progress(self, active_tasks: Dict[str, dict]) -> dict:
        summary = {
            "total": len(active_tasks),
            "completed": 0,
            "failed": 0,
            "running": 0
        }
        for task in active_tasks.values():
            status = task.get("status", "UNKNOWN").lower()
            if status in summary:
                summary[status] += 1
                
        return summary
