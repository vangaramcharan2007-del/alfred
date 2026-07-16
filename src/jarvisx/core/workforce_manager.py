import logging
import asyncio
from typing import Dict, Any

from .workforce_registry import WorkforceRegistry
from .git_worktree_manager import GitWorktreeManager

logger = logging.getLogger("WorkforceManager")

class WorkforceManager:
    """
    Interface between Hermes and Agent Orchestrator.
    Spawns specialist agents, tracks execution status, monitors subprocesses.
    """
    def __init__(self, registry: WorkforceRegistry, worktree_manager: GitWorktreeManager):
        self.registry = registry
        self.worktree_manager = worktree_manager
        self.active_tasks: Dict[str, Dict[str, Any]] = {}

    async def dispatch_task(self, task_id: str, objective: str, required_capability: str) -> bool:
        """
        Dispatches a subtask to the appropriate specialist agent using Agent Orchestrator.
        """
        agent_name = self.registry.find_agent_for_capability(required_capability)
        
        if not agent_name:
            logger.error(f"No agent found with capability: {required_capability}")
            return False

        logger.info(f"Dispatching task {task_id} to {agent_name}...")
        
        # Provision an isolated workspace
        feature_branch = f"feature/{task_id}"
        worktree_path = self.worktree_manager.create_worktree("main", feature_branch)
        
        self.active_tasks[task_id] = {
            "agent": agent_name,
            "status": "RUNNING",
            "worktree": worktree_path,
            "branch": feature_branch
        }

        # Spawn Agent Orchestrator process
        # We simulate this via asyncio subprocess
        cmd = f"python -m agent_orchestrator run --task \"{objective}\" --agent \"{agent_name}\" --workdir \"{worktree_path}\""
        
        logger.debug(f"Executing: {cmd}")
        
        # In a real environment, this is where we actually call the Agent Orchestrator binary/script
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # We don't await the result immediately, Hermes allows this to run async
        asyncio.create_task(self._monitor_subprocess(task_id, process))
        return True

    async def _monitor_subprocess(self, task_id: str, process: asyncio.subprocess.Process):
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            logger.info(f"Task {task_id} completed successfully.")
            self.active_tasks[task_id]["status"] = "COMPLETED"
            # We leave worktree destruction to the aggregator/Hermes after merging
        else:
            logger.error(f"Task {task_id} failed with exit code {process.returncode}.")
            logger.debug(f"Stderr: {stderr.decode()}")
            self.active_tasks[task_id]["status"] = "FAILED"

    def get_task_status(self, task_id: str) -> str:
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]["status"]
        return "UNKNOWN"
