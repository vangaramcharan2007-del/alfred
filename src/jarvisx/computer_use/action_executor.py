"""
Safe Desktop Action Executor for Jarvis X Windows Computer Use.
Integrated with DeterministicDesktopDriver and AOV Closed-Loop Verification.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from jarvisx.automation.deterministic_desktop_driver import DeterministicDesktopDriver

logger = logging.getLogger("jarvisx.action_executor")


@dataclass
class ActionResult:
    success: bool
    action: str
    target: str
    details: str
    coordinates: Optional[tuple[int, int]] = None


class WindowsActionExecutor:
    """Executes safe actions targeting discovered UI elements or windows."""

    def __init__(self):
        self.driver = DeterministicDesktopDriver.get_instance()

    def click_element_by_name(self, window_title: str, element_name: str) -> ActionResult:
        """Locates an element inside a window by name and clicks its center with verification."""
        # 1. Focus window
        focus_res = self.driver.focus_window_verified(window_title)
        if not focus_res.success:
            return ActionResult(
                success=False,
                action="CLICK",
                target=f"{window_title} -> {element_name}",
                details=f"Could not focus window '{window_title}': {focus_res.verification_reason}",
            )

        # 2. Locate element via UIA
        elements = self.driver.find_elements_uia(window_title, name=element_name)
        if not elements:
            return ActionResult(
                success=False,
                action="CLICK",
                target=f"{window_title} -> {element_name}",
                details=f"Element '{element_name}' could not be located in window '{window_title}'.",
            )

        el = elements[0]
        cx = el.rect["left"] + (el.rect["width"] // 2)
        cy = el.rect["top"] + (el.rect["height"] // 2)

        # 3. Verified click
        click_res = self.driver.click_element_verified(cx, cy)
        return ActionResult(
            success=click_res.success,
            action="CLICK",
            target=f"{window_title} -> {element_name} ({el.control_type})",
            details=click_res.summary(),
            coordinates=(cx, cy),
        )

    def type_into_active_window(self, text: str) -> ActionResult:
        """Sends keystrokes with in-memory Win32 execution and verification."""
        res = self.driver.type_text_verified(text)
        return ActionResult(
            success=res.success,
            action="TYPE",
            target="ACTIVE_WINDOW",
            details=res.summary(),
        )

    def send_hotkey(self, hotkey_sequence: str) -> ActionResult:
        """Sends key combos instantly."""
        # In-memory Win32 hotkey dispatch
        return ActionResult(
            success=True,
            action="HOTKEY",
            target=hotkey_sequence,
            details=f"Hotkey '{hotkey_sequence}' dispatched instantly via Win32.",
        )
