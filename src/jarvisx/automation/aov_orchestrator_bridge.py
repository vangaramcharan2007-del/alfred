"""
Autonomous Brain-to-AOV Orchestrator Bridge for Jarvis X.
Coordinates high-level task goals with:
  1. Windows Keep-Awake power protection.
  2. In-memory Win32 Desktop and Chrome CDP browser drivers.
  3. Closed-loop Act-Observe-Verify DAG execution.
  4. Async human-in-the-loop pager escalation.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from jarvisx.automation.aov_planner import (
    AOVPlanDAG,
    AOVPlanExecutor,
    AOVStep,
    PlanExecutionResult,
)
from jarvisx.automation.chrome_cdp_bridge import ChromeCDPBridge
from jarvisx.automation.deterministic_browser_driver import DeterministicBrowserDriver
from jarvisx.automation.deterministic_desktop_driver import DeterministicDesktopDriver
from jarvisx.communications.async_pager import AsyncPager
from jarvisx.harness.aov_engine import (
    AOVResult,
    ClosedLoopHarness,
    StateObserver,
    VerificationRule,
    rule_any_state_delta,
)
from jarvisx.runtime.windows_power_guard import KeepAwakeGuard

logger = logging.getLogger("jarvisx.aov_bridge")


class AOVOrchestratorBridge:
    """Master orchestrator executing autonomous plans with full environmental guarantees."""

    def __init__(self):
        self.desktop_driver = DeterministicDesktopDriver.get_instance()
        self.browser_driver = DeterministicBrowserDriver.get_instance()
        self.pager = AsyncPager.get_instance()
        self.executor = AOVPlanExecutor()

    async def execute_autonomous_goal(
        self,
        goal_name: str,
        steps: List[Dict[str, Any]],
        attach_chrome_cdp: bool = False,
    ) -> PlanExecutionResult:
        """
        Executes a multi-step autonomous mission wrapped in:
          - Windows KeepAwakeGuard
          - Deterministic AOVPlanDAG validation
          - Human pager on critical roadblocks
        """
        logger.info(f"[AOVBridge] Initializing autonomous mission '{goal_name}'...")

        # 1. Connect to live Chrome CDP if requested
        if attach_chrome_cdp:
            cdp_info = ChromeCDPBridge.probe_cdp_status()
            if cdp_info["active"]:
                logger.info(f"[AOVBridge] Attaching to active Chrome CDP at {cdp_info['port']}...")
                await self.browser_driver.initialize(cdp_url=ChromeCDPBridge.get_cdp_url())
            else:
                logger.info("[AOVBridge] Chrome CDP not active; launching persistent browser context...")
                await self.browser_driver.initialize(headless=True)

        # 2. Build DAG
        dag = AOVPlanDAG(plan_id=f"plan_{int(time.time())}", goal=goal_name)
        for s in steps:
            step = AOVStep(
                step_id=s["step_id"],
                driver=s.get("driver", "desktop"),
                action=s["action"],
                params=s.get("params", {}),
                depends_on=s.get("depends_on", []),
            )
            dag.add_step(step)

        # 3. Execute with Keep-Awake Guard
        with KeepAwakeGuard(mission_name=goal_name, keep_display_awake=True):
            plan_res = self.executor.execute_plan(dag)

        # 4. If execution failed due to an interactive requirement, page user
        if not plan_res.success and plan_res.failure_step_id:
            failed_step = dag.steps.get(plan_res.failure_step_id)
            action_desc = failed_step.action if failed_step else "unknown"
            self.pager.page_user(
                title=f"Jarvis X Alert: {goal_name}",
                message=f"Autonomous mission paused at step '{plan_res.failure_step_id}' ({action_desc}). {plan_res.replan_diagnostics}",
                urgency="CRITICAL_ACTION_REQUIRED",
                requires_input=True,
            )

        return plan_res
