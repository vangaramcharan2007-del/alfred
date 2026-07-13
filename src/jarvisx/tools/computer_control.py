import time
import subprocess
import webbrowser
import platform
from typing import Optional, Dict, Any, List

import pyautogui

from jarvisx.tools.base import BaseTool, ToolResult
from jarvisx.tools.personalization import PersonalizationTool


class ComputerControlTool(BaseTool):
    """
    Tool for orchestrating desktop automation, browser control, and application execution.
    Adheres strictly to the Computer Control Safety Model based on autonomy levels.
    """

    def __init__(self, personalization: PersonalizationTool):
        self.personalization = personalization
        
        # Failsafe configuration for PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

    def _get_autonomy_level(self) -> int:
        """Helper to get current autonomy level."""
        # Check if personalization has get_autonomy_level, else default to 1
        if hasattr(self.personalization, "get_autonomy_level"):
            res = self.personalization.get_autonomy_level()
            if res.success and "autonomy_level" in res.data:
                return res.data["autonomy_level"]
        return 1

    def _is_action_allowed(self, action_type: str, params: Dict[str, Any]) -> bool:
        """
        Evaluate if an action is permitted under the current autonomy level.
        Levels:
        0 - Observe Only (No Actions)
        1 - Assisted Mode (Require approval, but we simulate that by rejecting direct execution if not flagged as approved)
        2 - Trusted Automation (Browser, files, typing permitted. Restrictions on sensitive actions)
        3 - Autonomous Mode (Full automation)
        """
        level = self._get_autonomy_level()
        
        if level == 0:
            return False
            
        # Hardcoded restrictions that always require confirmation (or Level 3 if we allow it, 
        # but prompt says "Always require confirmation for...")
        sensitive_actions = ["delete", "buy", "purchase", "pay", "send_message", "email", "auth", "sudo"]
        
        # Check for sensitive keywords in text typing or commands
        text_to_type = params.get("text", "").lower()
        cmd_to_run = params.get("command", "").lower()
        
        for sensitive in sensitive_actions:
            if sensitive in text_to_type or sensitive in cmd_to_run:
                # If it's sensitive, maybe we block it unless explicitly approved.
                # For now, block it outright if level < 3. 
                if not params.get("_user_approved", False):
                    return False
                    
        if level == 1 and not params.get("_user_approved", False):
            # Level 1 requires explicit user approval flag.
            return False
            
        return True

    def open_url(self, url: str, _user_approved: bool = False) -> ToolResult:
        """Open a URL in the default web browser."""
        if not self._is_action_allowed("open_url", {"url": url, "_user_approved": _user_approved}):
            level = self._get_autonomy_level()
            return ToolResult(success=False, message=f"Action blocked by safety policy (Autonomy Level {level}).")
            
        try:
            webbrowser.open(url)
            return ToolResult(success=True, message=f"Opened URL: {url}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to open URL: {str(e)}")

    def type_text(self, text: str, _user_approved: bool = False) -> ToolResult:
        """Type text using the keyboard."""
        if not self._is_action_allowed("type_text", {"text": text, "_user_approved": _user_approved}):
            level = self._get_autonomy_level()
            return ToolResult(success=False, message=f"Action blocked by safety policy (Autonomy Level {level}).")
            
        try:
            pyautogui.write(text, interval=0.05)
            return ToolResult(success=True, message="Text typed successfully.")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to type text: {str(e)}")

    def press_key(self, keys: List[str], _user_approved: bool = False) -> ToolResult:
        """Press a key or combination of keys (e.g. ['ctrl', 'c'])."""
        if not self._is_action_allowed("press_key", {"keys": keys, "_user_approved": _user_approved}):
            level = self._get_autonomy_level()
            return ToolResult(success=False, message=f"Action blocked by safety policy (Autonomy Level {level}).")
            
        try:
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            return ToolResult(success=True, message=f"Pressed keys: {keys}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to press keys: {str(e)}")

    def click(self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1, button: str = 'left', _user_approved: bool = False) -> ToolResult:
        """Click the mouse at specific coordinates or current position."""
        if not self._is_action_allowed("click", {"_user_approved": _user_approved}):
            level = self._get_autonomy_level()
            return ToolResult(success=False, message=f"Action blocked by safety policy (Autonomy Level {level}).")
            
        try:
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            else:
                pyautogui.click(clicks=clicks, button=button)
            return ToolResult(success=True, message=f"Clicked at ({x}, {y})")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to click: {str(e)}")

    def run_command(self, command: str, _user_approved: bool = False) -> ToolResult:
        """Launch an application or run a system command."""
        if not self._is_action_allowed("run_command", {"command": command, "_user_approved": _user_approved}):
            level = self._get_autonomy_level()
            return ToolResult(success=False, message=f"Action blocked by safety policy (Autonomy Level {level}).")
            
        try:
            # We use subprocess.Popen to launch it and detach
            subprocess.Popen(command, shell=True)
            return ToolResult(success=True, message=f"Launched command: {command}")
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to run command: {str(e)}")
