import asyncio
import logging
import time
from typing import Dict, Any, List

from jarvisx.core.providers.provider_router import ProviderRouter
from .planner import Planner
from .replanner import Replanner
from .execution_monitor import ExecutionMonitor
from .progress_tracker import ProgressTracker
from .dependency_graph import DependencyGraph
from .planning_history import PlanningHistory
from .planning_metrics import PlanningMetrics

logger = logging.getLogger(__name__)

class ObjectiveManager:
    """Entry point for executing a high-level objective."""
    
    def __init__(self, provider_router: ProviderRouter):
        self.router = provider_router
        self.planner = Planner(self.router)
        self.replanner = Replanner(self.router)
        self.monitor = ExecutionMonitor()
        self.history = PlanningHistory()
        self.metrics = PlanningMetrics()

    async def execute_objective(self, objective: str, context: str = "") -> Dict[str, Any]:
        """Manages the full lifecycle of an objective."""
        
        logger.info(f"Starting objective: {objective}")
        tracker = ProgressTracker()
        tracker.start()
        
        # 1. Generate initial plan
        start_plan_t = time.time()
        try:
            plan_data = await self.planner.create_plan(objective, context)
            tasks = plan_data.get("steps", [])
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            tracker.mark_failed("plan_generation")
            self._record(objective, tracker, plan_data={}, success=False)
            return {"success": False, "error": str(e), "tracker": tracker.get_status()}
            
        self.metrics.add_planning_latency(time.time() - start_plan_t)
        
        # 2. Execution Loop
        await self._execute_plan_loop(objective, tasks, tracker)
        
        success = tracker.state == "COMPLETED"
        self._record(objective, tracker, plan_data, success)
        
        return {
            "success": success,
            "tracker": tracker.get_status()
        }

    async def _execute_plan_loop(self, objective: str, tasks: List[Dict[str, Any]], tracker: ProgressTracker):
        """Runs the tasks based on dependency graph. Replans on failure."""
        
        while tracker.state not in ["COMPLETED", "FAILED", "CANCELLED"]:
            graph = DependencyGraph(tasks)
            
            if graph.detect_cycles():
                logger.error("Cycle detected in plan graph.")
                tracker.mark_failed("cycle_detection")
                break
                
            executable = graph.get_executable_tasks(tracker.completed_tasks)
            
            if not executable:
                if len(tracker.completed_tasks) == len(tasks):
                    # All tasks completed successfully
                    tracker.complete_objective()
                    break
                else:
                    # Deadlock or waiting
                    if tracker.failed_tasks:
                        # Some tasks failed, causing downstream to never become executable
                        logger.warning("Tasks stalled due to upstream failures.")
                        break
                    else:
                        logger.error("Deadlock in task execution.")
                        tracker.mark_failed("deadlock")
                        break
            
            # Execute all ready tasks in parallel
            start_exec_t = time.time()
            results = await asyncio.gather(*(self.monitor.execute_task(t) for t in executable))
            self.metrics.add_execution_latency(time.time() - start_exec_t)
            
            failure_occurred = False
            failed_task_info = None
            failed_error = None
            
            for task, res in zip(executable, results):
                task_id = task["id"]
                if res.get("success"):
                    tracker.mark_completed(task_id)
                else:
                    tracker.mark_failed(task_id)
                    failure_occurred = True
                    failed_task_info = task
                    failed_error = res.get("error", "Unknown error")
                    break # Stop processing results on first failure for replanning
            
            if failure_occurred:
                logger.warning(f"Task failure detected. Triggering replanner. Error: {failed_error}")
                tracker.increment_retry()
                self.metrics.record_replan()
                
                try:
                    start_replan_t = time.time()
                    new_tasks = await self.replanner.generate_correction(
                        objective, failed_task_info, failed_error, str(results)
                    )
                    self.metrics.add_planning_latency(time.time() - start_replan_t)
                    
                    # Update tasks list (simple strategy: overwrite)
                    tasks = new_tasks
                    tracker.completed_tasks.clear()
                    tracker.failed_tasks.clear()
                    tracker.state = "RUNNING"
                except Exception as e:
                    logger.error(f"Replanning failed: {e}")
                    tracker.mark_failed("replanning")
                    break

    def _record(self, objective: str, tracker: ProgressTracker, plan_data: Dict[str, Any], success: bool):
        self.metrics.record_outcome(success)
        self.history.record_session({
            "objective": objective,
            "status": tracker.state,
            "plan": plan_data,
            "elapsed_time": tracker.elapsed_time,
            "retries": tracker.retries
        })
