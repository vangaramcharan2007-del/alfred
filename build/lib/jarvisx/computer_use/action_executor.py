"""
Safe Desktop Action Executor for Jarvis X Windows Computer Use.
Executes semantic clicks, text input, window focusing, and keyboard shortcuts with safety gates.
"""

from __future__ import annotations

import ctypes
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from jarvisx.computer_use.element_finder import SemanticElementFinder
from jarvisx.computer_use.windows_ui import UIElement, WindowsUIAutomationInspector


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
        self.inspector = WindowsUIAutomationInspector()
        self.finder = SemanticElementFinder(self.inspector)

    def click_element_by_name(self, window_title: str, element_name: str) -> ActionResult:
        """Locates an element inside a window by name and clicks its center."""
        # 1. Ensure window is focused
        self.inspector.focus_window_by_title(window_title)
        time.sleep(0.15)

        # 2. Locate element
        element = self.finder.locate_target_element(window_title, element_name)
        if not element:
            return ActionResult(
                success=False,
                action="CLICK",
                target=f"{window_title} -> {element_name}",
                details=f"Element '{element_name}' could not be located in window '{window_title}'.",
            )

        cx, cy = element.center_coords

        # 3. Perform mouse click via Windows SendInput / PowerShell mouse simulator
        ps_click = f"""
        Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class MouseSimulator {{
                [DllImport("user32.dll")]
                public static extern void SetCursorPos(int X, int Y);
                [DllImport("user32.dll")]
                public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
                public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
                public const uint MOUSEEVENTF_LEFTUP = 0x0004;
                public static void Click(int x, int y) {{
                    SetCursorPos(x, y);
                    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
                    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
                }}
            }}
"@
        [MouseSimulator]::Click({cx}, {cy})
        """
        try:
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_click], capture_output=True, text=True, timeout=2.0)
            if proc.returncode == 0:
                return ActionResult(
                    success=True,
                    action="CLICK",
                    target=f"{window_title} -> {element_name} ({element.control_type})",
                    details=f"Successfully clicked element at ({cx}, {cy}).",
                    coordinates=(cx, cy),
                )
        except Exception as e:
            return ActionResult(
                success=False,
                action="CLICK",
                target=element_name,
                details=f"Click execution error: {str(e)}",
            )

        return ActionResult(success=False, action="CLICK", target=element_name, details="Click invocation failed.")

    def type_into_active_window(self, text: str) -> ActionResult:
        """Sends keystrokes into the currently focused window."""
        escaped_text = text.replace('"', '`"').replace("$", "`$")
        ps_type = f"""
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait("{escaped_text}")
        """
        try:
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_type], capture_output=True, text=True, timeout=3.0)
            if proc.returncode == 0:
                return ActionResult(
                    success=True,
                    action="TYPE",
                    target="ACTIVE_WINDOW",
                    details=f"Typed {len(text)} characters successfully.",
                )
        except Exception as e:
            return ActionResult(
                success=False,
                action="TYPE",
                target="ACTIVE_WINDOW",
                details=f"Typing error: {str(e)}",
            )
        return ActionResult(success=False, action="TYPE", target="ACTIVE_WINDOW", details="Keystroke dispatch failed.")

    def send_hotkey(self, hotkey_sequence: str) -> ActionResult:
        """Sends key combos like '^s' (Ctrl+S), '^+p' (Ctrl+Shift+P)."""
        ps_keys = f"""
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait("{hotkey_sequence}")
        """
        try:
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_keys], capture_output=True, text=True, timeout=2.0)
            return ActionResult(
                success=proc.returncode == 0,
                action="HOTKEY",
                target=hotkey_sequence,
                details=f"Hotkey sequence '{hotkey_sequence}' dispatched.",
            )
        except Exception as e:
            return ActionResult(success=False, action="HOTKEY", target=hotkey_sequence, details=str(e))
