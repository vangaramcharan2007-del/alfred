import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, List, Optional

from jarvisx.core.providers.provider_router import ProviderRouter
from .planner import Planner
from .replanner import Replanner
from .execution_monitor import ExecutionMonitor
from .progress_tracker import ProgressTracker
from .dependency_graph import DependencyGraph
from .planning_history import PlanningHistory
from .planning_metrics import PlanningMetrics

logger = logging.getLogger(__name__)

MAX_REPLAN_ATTEMPTS = 3
STATE_DIR = "var/objective_state"


class ObjectiveManager:
    """Entry point for executing a high-level objective with state-preserving replanning."""

    def __init__(self, provider_router: ProviderRouter, registry=None):
        self.router = provider_router
        self._registry = registry
        self.planner = Planner(self.router, registry=registry)
        self.replanner = Replanner(self.router, registry=registry)
        self.monitor = ExecutionMonitor(registry=registry)
        self.history = PlanningHistory()
        self.metrics = PlanningMetrics()
        # Evidence cache: task_id -> evidence dict
        self.evidence_cache: Dict[str, Dict[str, Any]] = {}

    async def execute_objective(self, objective: str, context: str = "") -> Dict[str, Any]:
        """Manages the full lifecycle of an objective."""

        logger.info(f"Starting objective: {objective}")
        tracker = ProgressTracker()
        tracker.start()
        self.evidence_cache.clear()

        # 1. Generate initial plan
        start_plan_t = time.time()
        plan_data = {}
        try:
            plan_data = await self.planner.create_plan(objective, context)
            tasks = plan_data.get("steps", [])
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            tracker.mark_failed("plan_generation")
            self._record(objective, tracker, plan_data, success=False)
            return {"success": False, "error": str(e), "tracker": tracker.get_status(), "evidence": {}}

        self.metrics.add_planning_latency(time.time() - start_plan_t)

        # 2. Execution Loop with state-preserving replanning
        await self._execute_plan_loop(objective, tasks, tracker)

        success = tracker.state == "COMPLETED"
        self._record(objective, tracker, plan_data, success)
        self._persist_state(objective, tracker)

        return {
            "success": success,
            "tracker": tracker.get_status(),
            "evidence": dict(self.evidence_cache)
        }

    async def _execute_plan_loop(self, objective: str, tasks: List[Dict[str, Any]], tracker: ProgressTracker):
        """Runs tasks based on dependency graph. State-preserving replanning on failure."""

        replan_count = 0

        while tracker.state not in ["COMPLETED", "FAILED", "CANCELLED"]:
            graph = DependencyGraph(tasks)

            if graph.detect_cycles():
                logger.error("Cycle detected in plan graph.")
                tracker.mark_failed("cycle_detection")
                break

            executable = graph.get_executable_tasks(tracker.completed_tasks)

            if not executable:
                # Check if all tasks in the current plan are complete
                all_task_ids = {t["id"] for t in tasks}
                if all_task_ids.issubset(tracker.completed_tasks):
                    tracker.complete_objective()
                    break
                else:
                    if tracker.failed_tasks:
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
                    self.evidence_cache[task_id] = res.get("evidence", {})
                    self._persist_state(objective, tracker)
                else:
                    tracker.mark_failed(task_id)
                    self.evidence_cache[task_id] = res.get("evidence", {"error": res.get("error")})
                    failure_occurred = True
                    failed_task_info = task
                    failed_error = res.get("error", "Unknown error")
                    break

            if failure_occurred:
                replan_count += 1
                if replan_count > MAX_REPLAN_ATTEMPTS:
                    logger.error(f"Max replan attempts ({MAX_REPLAN_ATTEMPTS}) exceeded.")
                    tracker.mark_failed("max_replans_exceeded")
                    break

                logger.warning(f"Task failure detected (attempt {replan_count}). Triggering replanner. Error: {failed_error}")
                tracker.increment_retry()
                self.metrics.record_replan()

                # Compute remaining (uncompleted, non-failed) tasks
                remaining_tasks = [
                    t for t in tasks
                    if t["id"] not in tracker.completed_tasks and t["id"] != failed_task_info["id"]
                ]

                try:
                    start_replan_t = time.time()
                    new_tasks = await self.replanner.generate_correction(
                        objective=objective,
                        failed_task=failed_task_info,
                        error_msg=failed_error,
                        completed_task_ids=set(tracker.completed_tasks),
                        remaining_tasks=remaining_tasks,
                        logs=str(results)
                    )
                    self.metrics.add_planning_latency(time.time() - start_replan_t)

                    # STATE-PRESERVING: Replace only the uncompleted portion of the plan.
                    # Completed tasks remain completed. Only new corrective tasks are added.
                    tasks = new_tasks
                    # Remove the failed task from failed_tasks so we can retry
                    tracker.failed_tasks.discard(failed_task_info["id"])
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
            "retries": tracker.retries,
            "evidence_keys": list(self.evidence_cache.keys())
        })

    def _persist_state(self, objective: str, tracker: ProgressTracker):
        """Persist objective state for restart survivability."""
        os.makedirs(STATE_DIR, exist_ok=True)
        state = {
            "objective": objective,
            "tracker": tracker.get_status(),
            "evidence": {k: _safe_serialize(v) for k, v in self.evidence_cache.items()},
            "timestamp": time.time()
        }
        # Use a sanitized filename
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in objective[:60])
        filepath = os.path.join(STATE_DIR, f"{safe_name}.json")
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2, default=str)
        logger.info(f"Persisted objective state to {filepath}")


def _safe_serialize(obj):
    """Make evidence JSON-serializable."""
    if isinstance(obj, dict):
        return {k: _safe_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_safe_serialize(i) for i in obj]
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)
