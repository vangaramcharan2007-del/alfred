import logging

logger = logging.getLogger("AgentFeedbackLoop")

class AgentFeedbackLoop:
    """
    Detects CI failures, test failures, and merge conflicts.
    Retries fixes automatically up to max_retries before escalating.
    """
    def __init__(self, workforce_manager, max_retries=3):
        self.workforce_manager = workforce_manager
        self.max_retries = max_retries

    async def handle_task_completion(self, task_id: str, context: dict) -> bool:
        """
        Called when a worker agent finishes a task.
        Analyzes output for failures.
        """
        failures = self._analyze_output(context)
        
        if not failures:
            logger.info(f"Task {task_id} completed successfully with no detected failures.")
            return True
            
        logger.warning(f"Failures detected for task {task_id}: {failures}")
        return await self._attempt_retry(task_id, failures)

    def _analyze_output(self, context: dict) -> list:
        failures = []
        logs = context.get("execution_logs", "").lower()
        
        if "test failed" in logs or "assertionerror" in logs:
            failures.append("test_failure")
        if "merge conflict" in logs:
            failures.append("merge_conflict")
        if "build failed" in logs or "error:" in logs:
            failures.append("ci_failure")
            
        return failures

    async def _attempt_retry(self, task_id: str, failures: list) -> bool:
        task_info = self.workforce_manager.active_tasks.get(task_id)
        if not task_info:
            logger.error(f"Cannot retry unknown task {task_id}")
            return False
            
        retries = task_info.get("retries", 0)
        
        if retries >= self.max_retries:
            logger.error(f"Task {task_id} exceeded max retries ({self.max_retries}). Escalating to Alfred.")
            self.workforce_manager.active_tasks[task_id]["status"] = "ESCALATED"
            return False
            
        task_info["retries"] = retries + 1
        logger.info(f"Retrying task {task_id} (Attempt {task_info['retries']}/{self.max_retries}) to fix: {failures}")
        
        # In reality, we would re-dispatch with the specific failure context
        await self.workforce_manager.dispatch_task(
            task_id, 
            f"Fix the following failures: {failures}", 
            task_info["agent"]
        )
        return True
