import logging
import asyncio
import subprocess

logger = logging.getLogger("DistributedExecutor")

class DistributedExecutor:
    """
    Physically spawns Python subprocesses or Asyncio tasks to execute serialized code/commands.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.active_tasks = {}

    async def execute_task(self, task_id: str, command: str, is_async=False):
        logger.info(f"Node {self.node_id} received EXECUTE_TASK {task_id}")
        
        if is_async:
            logger.info(f"Executing async task {task_id} in event loop...")
            self.active_tasks[task_id] = "running"
            await asyncio.sleep(0.5) # Simulate workload
            self.active_tasks[task_id] = "completed"
            logger.info(f"Task {task_id} completed successfully.")
            return True
        else:
            logger.info(f"Spawning subprocess for task {task_id}: {command}")
            try:
                # In a real environment, careful sandboxing is required here.
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                logger.info(f"Subprocess finished with code {process.returncode}")
                return process.returncode == 0
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                return False
