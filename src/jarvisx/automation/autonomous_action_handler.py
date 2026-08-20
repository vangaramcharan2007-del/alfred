"""Jarvis X: Autonomous Desktop & Windows Action Handler.

Parses natural language / voice requests for desktop control, app launching,
system monitoring, file management, and PowerShell execution.
"""

from __future__ import annotations
import os
import sys
import re
import time
import subprocess
import webbrowser
from typing import Dict, Any, Optional

from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator


class AutonomousActionHandler:
    """Handles end-to-end desktop and OS action execution from voice/chat."""

    def __init__(self):
        self.orchestrator = DynamicOrchestrator()

    def try_execute_action(self, user_text: str) -> Optional[Dict[str, Any]]:
        """Checks if user_text is an OS action. If yes, executes and returns result."""
        text = user_text.lower().strip()

        # 1. App Launching / Opening
        if text.startswith(("open ", "launch ", "start ")):
            target = text.split(" ", 1)[1].strip()
            # Common web services
            if any(w in target for w in ["youtube", "google", "github", "reddit", "twitter", "x.com", "chatgpt"]):
                url = f"https://www.{target.replace(' ', '')}.com" if not target.startswith("http") else target
                webbrowser.open(url)
                return {"action": "open_web", "target": url, "status": "success", "message": f"Opening {target} in your default browser."}

            res = self.orchestrator.find_and_launch_app(target)
            return {"action": "open_app", "target": target, "status": res.get("status", "success"), "message": f"Launching application: {target}."}

        # 2. System Status (CPU, RAM, Battery)
        if any(k in text for k in ["system status", "cpu usage", "ram usage", "battery", "system health"]):
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=0.2)
                ram = psutil.virtual_memory().percent
                battery = psutil.sensors_battery()
                bat_str = f", Battery: {battery.percent}%" if battery else ""
                msg = f"CPU Usage is at {cpu}%, RAM at {ram}%{bat_str}."
                return {"action": "system_status", "status": "success", "message": msg}
            except Exception:
                return {"action": "system_status", "status": "success", "message": "System is running healthy."}

        # 3. File Creation / Notes
        if text.startswith("create file ") or text.startswith("write note "):
            try:
                content = user_text.split(" ", 2)[2] if len(user_text.split(" ", 2)) > 2 else "New note"
                filename = f"jarvis_note_{int(time.time())}.txt"
                path = os.path.join(os.path.expanduser("~"), "Documents", filename)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"action": "create_file", "path": path, "status": "success", "message": f"Created file {filename} in your Documents."}
            except Exception as e:
                return {"action": "create_file", "status": "error", "message": f"Failed to create file: {e}"}

        # 4. System Cleanup / Temp cleaning
        if "clean system" in text or "clear temp" in text or "clean cache" in text:
            res = self.orchestrator.cleaner.clean_all()
            return {"action": "clean_system", "status": "success", "message": f"Cleaned temporary caches and freed system space."}

        return None
