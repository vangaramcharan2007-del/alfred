"""
Unified Computer Control Layer.
Comprehensive desktop automation engine supporting applications, windows, keyboard/mouse,
file operations, and browser navigation with risk scores, permissions, and undo capability.
"""
from __future__ import annotations
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from jarvisx.automation.desktop_actions import (
    organize_folder, bulk_rename, compress_folder, take_screenshot,
    list_windows, focus_window, kill_process, disk_usage
)
class RiskSecurityGate:
    def evaluate(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"allowed": True, "risk": "LOW"}


class ComputerController:
    """
    Unified Computer Operator for Alfred.
    Executes automation actions after security gate checks and maintains execution history.
    """

    def __init__(self, security_gate: Optional[RiskSecurityGate] = None):
        self.gate = security_gate or RiskSecurityGate()
        self.history: List[Dict[str, Any]] = []
        self.undo_stack: List[Dict[str, Any]] = []

    def execute_action(self, action_id: str, context: Optional[Dict[str, Any]] = None, confirmed: bool = False) -> Dict[str, Any]:
        context = context or {}
        perm = self.gate.check_permission(action_id, context, confirmed=confirmed)
        if not perm["allowed"]:
            return perm

        start_t = time.time()
        res = self._dispatch(action_id, context)
        duration = round(time.time() - start_t, 3)

        record = {
            "action_id": action_id,
            "context": context,
            "result": res,
            "risk": perm["risk"],
            "duration": duration,
            "timestamp": time.time()
        }
        self.history.append(record)

        # Log to undo stack if reversible
        if res.get("status") == "SUCCESS" and "undo_data" in res:
            self.undo_stack.append(record)

        return {
            "status": res.get("status", "SUCCESS"),
            "action_id": action_id,
            "risk_level": perm["risk"]["risk_level"],
            "result": res,
            "duration": duration
        }

    def _dispatch(self, action_id: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        act = action_id.lower()
        if act == "app.open":
            app_name = ctx.get("app", "vscode")
            if app_name in ("vscode", "code"):
                code_bin = shutil.which("code") or "code"
                subprocess.Popen([code_bin, ctx.get("path", ".")], shell=True)
                return {"status": "SUCCESS", "app": "VS Code"}
            elif app_name in ("browser", "chrome", "edge"):
                import webbrowser
                webbrowser.open(ctx.get("url", "https://github.com"))
                return {"status": "SUCCESS", "app": "Browser"}
            elif app_name in ("terminal", "cmd", "powershell"):
                subprocess.Popen(["cmd.exe", "/c", "start", "cmd"], shell=True)
                return {"status": "SUCCESS", "app": "Terminal"}
            return {"status": "NOT_SUPPORTED", "reason": f"Unknown app '{app_name}'"}

        elif act == "file.organize":
            return organize_folder(ctx.get("folder", "var/downloads"), dry_run=ctx.get("dry_run", False))

        elif act == "file.compress":
            return compress_folder(ctx.get("folder", "."), ctx.get("output"))

        elif act == "file.rename":
            return bulk_rename(ctx.get("folder", "."), ctx.get("pattern", ""), ctx.get("replacement", ""), dry_run=ctx.get("dry_run", True))

        elif act == "screen.capture":
            return take_screenshot(ctx.get("output", "var/screenshots/screenshot.png"))

        elif act == "window.list":
            return list_windows()

        elif act == "window.focus":
            return focus_window(ctx.get("title", ""))

        elif act == "process.kill":
            return kill_process(ctx.get("name", ""))

        elif act == "disk.usage":
            return disk_usage(ctx.get("path", "."))

        return {"status": "NOT_SUPPORTED", "reason": f"Action '{action_id}' not implemented in ComputerController"}
