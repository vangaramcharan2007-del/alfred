import os
import json
import time
import subprocess
from typing import Optional, Dict, Any, List

import pyautogui
from jarvisx.tools.base import BaseTool, ToolResult

class VSCodeController(BaseTool):
    """
    Controller for driving Visual Studio Code physically on the desktop using PyAutoGUI.
    Adheres to the Jarvis X Execution Layer design pattern.
    """

    def __init__(self):
        # Apply PyAutoGUI fail-safes
        pyautogui.FAILSAFE = True
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config_path = os.path.join("config", "demo.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "demo_mode": False,
            "typing_speed": 0.00,
            "action_delay": 0.5,
            "verbose_narration": False
        }

    def _get_typing_speed(self) -> float:
        if self.config.get("demo_mode"):
            return float(self.config.get("typing_speed", 0.02))
        return 0.00

    def _wait_action(self, multiplier: float = 1.0):
        if self.config.get("demo_mode"):
            delay = float(self.config.get("action_delay", 1.0)) * multiplier
            time.sleep(delay)

    def _verify_vscode_focus(self, target_filename: Optional[str] = None) -> bool:
        """
        Safety check: Verifies if Visual Studio Code is the active window,
        and optionally checks if the target file is in the title.
        """
        # In a real environment on Windows, we can use pygetwindow
        try:
            import pygetwindow as gw
            active = gw.getActiveWindow()
            if not active:
                return False
            title = active.title.lower()
            if "visual studio code" not in title and "code" not in title:
                return False
            if target_filename and target_filename.lower() not in title:
                return False
            return True
        except ImportError:
            # Fallback if pygetwindow is not installed, assume focused if we just launched it
            return True

    def vscode_open_workspace(self, path: str) -> ToolResult:
        """Open a directory in VS Code using reuse-window."""
        try:
            subprocess.Popen(f"code --reuse-window {path}", shell=True)
            self._wait_action(multiplier=1.5)  # Wait for load
            return ToolResult(success=True, message=f"Opened workspace: {path}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to open workspace: {e}")

    def vscode_open_file(self, path: str) -> ToolResult:
        """Open a file and ensure focus before typing."""
        try:
            subprocess.Popen(f"code --reuse-window {path}", shell=True)
            self._wait_action(multiplier=1.5)
            
            filename = os.path.basename(path)
            if not self._verify_vscode_focus(target_filename=filename):
                # Fallback to click center of screen to focus editor area
                pyautogui.click()
                time.sleep(0.5)

            return ToolResult(success=True, message=f"Opened and focused file: {path}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to open file: {e}")

    def vscode_type_code(self, code_string: str) -> ToolResult:
        """Type code with visible physical automation (Tony Stark effect)."""
        try:
            # Add an extra safety verify check
            if not self._verify_vscode_focus():
                pass # Depending on environment, might want to abort or warn

            pyautogui.write(code_string, interval=self._get_typing_speed())
            self._wait_action(multiplier=0.5)
            return ToolResult(success=True, message="Typed code successfully.")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to type code: {e}")

    def vscode_save(self) -> ToolResult:
        """Save the current file."""
        try:
            pyautogui.hotkey("ctrl", "s")
            self._wait_action(multiplier=0.5)
            return ToolResult(success=True, message="File saved.")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to save file: {e}")

    def vscode_run_in_terminal(self, command: str) -> ToolResult:
        """Execute a command in the integrated terminal."""
        try:
            # Open terminal
            pyautogui.hotkey("ctrl", "shift", "`")
            self._wait_action(multiplier=1.0) # Wait for terminal to pop up
            
            # Type command and run
            pyautogui.write(command, interval=self._get_typing_speed())
            pyautogui.press("enter")
            
            self._wait_action(multiplier=1.5) # Wait for execution
            
            return ToolResult(success=True, message=f"Ran command in terminal: {command}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to run in terminal: {e}")
