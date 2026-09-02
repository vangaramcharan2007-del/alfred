"""
Autonomous Computer Use Agent for Jarvis X.
Orchestrates high-level Reason-Act-Observe loops over Windows applications.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from jarvisx.computer_use.action_executor import ActionResult, WindowsActionExecutor
from jarvisx.computer_use.element_finder import SemanticElementFinder
from jarvisx.computer_use.windows_ui import UIElement, WindowInfo, WindowsUIAutomationInspector


@dataclass
class DesktopPlanStep:
    step_num: int
    action_type: str  # FOCUS, CLICK, TYPE, HOTKEY, INSPECT
    target_window: str
    target_element: Optional[str] = None
    input_text: Optional[str] = None
    status: str = "PENDING"


@dataclass
class DesktopMissionResult:
    goal: str
    success: bool
    steps_executed: int
    step_history: List[Dict[str, Any]]
    final_message: str


class AutonomousComputerUseAgent:
    """Agent that drives Windows UI to accomplish high-level desktop missions."""

    def __init__(self):
        self.inspector = WindowsUIAutomationInspector()
        self.finder = SemanticElementFinder(self.inspector)
        self.executor = WindowsActionExecutor()

    def get_desktop_state(self) -> Dict[str, Any]:
        """Captures active windows and top-level interactive layout."""
        windows = self.inspector.list_open_windows()
        return {
            "total_windows": len(windows),
            "windows": [
                {
                    "title": w.title,
                    "process": w.process_name,
                    "is_active": w.is_active,
                    "bounds": f"{w.rect['width']}x{w.rect['height']} at ({w.rect['left']},{w.rect['top']})",
                }
                for w in windows
            ],
        }

    def execute_plan(self, goal: str, steps: List[DesktopPlanStep]) -> DesktopMissionResult:
        """Executes a sequential multi-step desktop automation plan."""
        history = []
        all_success = True

        for step in steps:
            step_record = {"step": step.step_num, "action": step.action_type, "target": step.target_window}
            
            if step.action_type == "FOCUS":
                ok = self.inspector.focus_window_by_title(step.target_window)
                step_record["result"] = "FOCUSED" if ok else "WINDOW_NOT_FOUND"
                if not ok:
                    all_success = False

            elif step.action_type == "CLICK":
                if step.target_element:
                    res: ActionResult = self.executor.click_element_by_name(step.target_window, step.target_element)
                    step_record["result"] = res.details
                    if not res.success:
                        all_success = False

            elif step.action_type == "TYPE":
                if step.input_text:
                    self.inspector.focus_window_by_title(step.target_window)
                    res = self.executor.type_into_active_window(step.input_text)
                    step_record["result"] = res.details
                    if not res.success:
                        all_success = False

            elif step.action_type == "HOTKEY":
                if step.input_text:
                    res = self.executor.send_hotkey(step.input_text)
                    step_record["result"] = res.details

            history.append(step_record)
            time.sleep(0.1)

        return DesktopMissionResult(
            goal=goal,
            success=all_success,
            steps_executed=len(history),
            step_history=history,
            final_message="All steps executed successfully." if all_success else "One or more steps failed.",
        )
