"""
AOV DAG Planner & Orchestrator for Jarvis X.
Decouples high-level reasoning from deterministic execution.
Builds executable action DAGs and provides closed-loop replanning on failure.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from jarvisx.harness.aov_engine import (
    AOVResult,
    ClosedLoopHarness,
    StateDiff,
    StateObserver,
    VerificationRule,
    rule_any_state_delta,
)

logger = logging.getLogger("jarvisx.aov_planner")


@dataclass
class AOVStep:
    step_id: str
    driver: str  # "desktop", "browser", "kernel"
    action: str
    params: Dict[str, Any]
    rules: List[VerificationRule] = field(default_factory=list)
    recovery_action: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)


@dataclass
class PlanExecutionResult:
    plan_id: str
    goal: str
    success: bool
    total_steps: int
    executed_steps: int
    step_results: List[AOVResult]
    elapsed_ms: float
    failure_step_id: Optional[str] = None
    replan_diagnostics: Optional[str] = None


class AOVPlanDAG:
    """Directed Acyclic Graph of verified automation steps."""

    def __init__(self, plan_id: str, goal: str):
        self.plan_id = plan_id
        self.goal = goal
        self.steps: Dict[str, AOVStep] = {}
        self.execution_order: List[str] = []

    def add_step(self, step: AOVStep) -> AOVPlanDAG:
        self.steps[step.step_id] = step
        self.execution_order.append(step.step_id)
        return self


class AOVPlanExecutor:
    """Executes an AOVPlanDAG deterministically with closed-loop verification."""

    def __init__(self):
        from jarvisx.automation.deterministic_desktop_driver import DeterministicDesktopDriver
        self.desktop_driver = DeterministicDesktopDriver.get_instance()
        self.harness = ClosedLoopHarness(max_retries=2, retry_delay_sec=0.2)

    def execute_plan(self, dag: AOVPlanDAG) -> PlanExecutionResult:
        t0 = time.perf_counter()
        results: List[AOVResult] = []

        logger.info(f"[AOVPlanExecutor] Starting execution for plan '{dag.plan_id}': {dag.goal}")

        for step_id in dag.execution_order:
            step = dag.steps[step_id]
            logger.info(f"[AOVPlanExecutor] Running Step {step_id}: {step.action} via {step.driver}...")

            step_res = self._dispatch_step(step)
            results.append(step_res)

            if not step_res.success:
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                diag = (
                    f"Step '{step_id}' ({step.action}) failed verification: {step_res.verification_reason}. "
                    f"Pre-state: {step_res.pre_state.active_window.title if step_res.pre_state.active_window else 'None'} -> "
                    f"Post-state: {step_res.post_state.active_window.title if step_res.post_state.active_window else 'None'}."
                )
                logger.error(f"[AOVPlanExecutor] Execution halted: {diag}")
                return PlanExecutionResult(
                    plan_id=dag.plan_id,
                    goal=dag.goal,
                    success=False,
                    total_steps=len(dag.execution_order),
                    executed_steps=len(results),
                    step_results=results,
                    elapsed_ms=round(elapsed_ms, 2),
                    failure_step_id=step_id,
                    replan_diagnostics=diag,
                )

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        logger.info(f"[AOVPlanExecutor] Plan '{dag.plan_id}' completed successfully in {elapsed_ms:.1f}ms!")

        return PlanExecutionResult(
            plan_id=dag.plan_id,
            goal=dag.goal,
            success=True,
            total_steps=len(dag.execution_order),
            executed_steps=len(results),
            step_results=results,
            elapsed_ms=round(elapsed_ms, 2),
        )

    def _dispatch_step(self, step: AOVStep) -> AOVResult:
        """Dispatches step to appropriate deterministic driver."""
        if step.driver == "desktop":
            if step.action == "focus_window":
                title = step.params.get("title", "")
                return self.desktop_driver.focus_window_verified(title)
            elif step.action == "click":
                x = step.params.get("x", 0)
                y = step.params.get("y", 0)
                return self.desktop_driver.click_element_verified(x, y)
            elif step.action == "type":
                text = step.params.get("text", "")
                return self.desktop_driver.type_text_verified(text)

        # Fallback generic closed-loop execution
        def fallback_act():
            return {"dispatched": step.action, "params": step.params}

        rules = step.rules or [rule_any_state_delta()]
        return self.harness.execute_closed_loop(
            action_name=f"{step.driver}.{step.action}",
            act_fn=fallback_act,
            rules=rules,
        )
