from __future__ import annotations
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

class Action:
    """
    Standard Action interface for desktop operator.
    Exposes id, description, can_execute(), execute(), undo(), requires_confirmation, execution_log.
    """
    def __init__(self, action_id: str, description: str, requires_confirmation: bool = False):
        self.id = action_id
        self.description = description
        self.requires_confirmation = requires_confirmation
        self.execution_log: List[Dict[str, Any]] = []

    def can_execute(self) -> bool:
        return True

    def execute(self, context: Optional[Dict[str, Any]] = None, dry_run: bool = False) -> Dict[str, Any]:
        if dry_run:
            res = {"status": "DRY_RUN", "action": self.id, "message": f"[Dry-Run] Would execute {self.description}"}
            self.execution_log.append(res)
            return res
        try:
            res = self._run(context or {})
            self.execution_log.append(res)
            return res
        except Exception as e:
            err_res = {"status": "FAILED", "action": self.id, "error": str(e)}
            self.execution_log.append(err_res)
            return err_res

    def _run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def undo(self) -> Dict[str, Any]:
        return {"status": "NOT_SUPPORTED", "action": self.id, "reason": "Undo operation not implemented for this action."}


class OpenAppAction(Action):
    def __init__(self, app_name: str = "vscode"):
        super().__init__(f"app.open.{app_name}", f"Open application '{app_name}'")
        self.app_name = app_name

    def _run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        target_path = context.get("path", ".")
        if self.app_name in ["vscode", "code"]:
            code_bin = shutil.which("code") or "code"
            subprocess.Popen([code_bin, target_path], shell=True)
            return {"status": "SUCCESS", "app": "VS Code", "path": target_path}
        elif self.app_name in ["browser", "chrome", "edge"]:
            import webbrowser
            webbrowser.open(context.get("url", "https://github.com"))
            return {"status": "SUCCESS", "app": "Browser", "url": context.get("url", "https://github.com")}
        elif self.app_name in ["terminal", "powershell", "cmd"]:
            subprocess.Popen(["cmd.exe", "/c", "start", "cmd"], shell=True)
            return {"status": "SUCCESS", "app": "Terminal"}
        return {"status": "NOT_SUPPORTED", "app": self.app_name, "reason": f"Application '{self.app_name}' launcher not configured"}


class ExecuteTerminalAction(Action):
    def __init__(self):
        super().__init__("terminal.execute", "Execute command in terminal")

    def _run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        command = context.get("command", "dir")
        cwd = context.get("cwd", ".")
        res = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True, timeout=30)
        return {
            "status": "SUCCESS" if res.returncode == 0 else "FAILED",
            "exit_code": res.returncode,
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip()
        }


class ClipboardCopyAction(Action):
    def __init__(self):
        super().__init__("clipboard.copy", "Copy text to clipboard")

    def _run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("text", "")
        try:
            import pyperclip
            pyperclip.copy(text)
            return {"status": "SUCCESS", "text_len": len(text)}
        except Exception:
            return {"status": "NOT_SUPPORTED", "reason": "pyperclip module unavailable"}


class SystemLockAction(Action):
    def __init__(self):
        super().__init__("system.lock", "Lock current workstation", requires_confirmation=True)

    def _run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if sys.platform == "win32":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
            return {"status": "SUCCESS", "action": "system.lock"}
        return {"status": "NOT_SUPPORTED", "reason": f"Lock workstation not implemented for OS '{sys.platform}'"}


class ActionRegistry:
    """
    Registry for production desktop operator actions and multi-step workflows.
    """
    _instance: Optional[ActionRegistry] = None

    def __init__(self):
        self.actions: Dict[str, Action] = {}
        self.workflows: Dict[str, List[str]] = {}
        self._register_default_actions()

    @classmethod
    def get_instance(cls) -> ActionRegistry:
        if cls._instance is None:
            cls._instance = ActionRegistry()
        return cls._instance

    def register_action(self, action: Action):
        self.actions[action.id] = action

    def _register_default_actions(self):
        self.register_action(OpenAppAction("vscode"))
        self.register_action(OpenAppAction("browser"))
        self.register_action(OpenAppAction("terminal"))
        self.register_action(ExecuteTerminalAction())
        self.register_action(ClipboardCopyAction())
        self.register_action(SystemLockAction())

        # Register workflows
        self.workflows["Start Jarvis Development"] = ["app.open.vscode", "app.open.terminal", "app.open.browser"]
        self.workflows["Finish Development"] = ["terminal.execute"]
        self.workflows["Study Mode"] = ["app.open.vscode"]
        self.workflows["Presentation Mode"] = ["app.open.browser"]

    def execute_action(self, action_id: str, context: Optional[Dict[str, Any]] = None, dry_run: bool = False) -> Dict[str, Any]:
        action = self.actions.get(action_id)
        if not action:
            return {"status": "NOT_SUPPORTED", "action_id": action_id, "reason": "Action ID not found in registry"}
        return action.execute(context=context, dry_run=dry_run)

    def execute_workflow(self, workflow_name: str, context: Optional[Dict[str, Any]] = None, dry_run: bool = False) -> Dict[str, Any]:
        steps = self.workflows.get(workflow_name)
        if not steps:
            return {"status": "NOT_SUPPORTED", "workflow": workflow_name, "reason": f"Workflow '{workflow_name}' not registered"}

        results = []
        for action_id in steps:
            res = self.execute_action(action_id, context=context, dry_run=dry_run)
            results.append(res)

        return {
            "status": "SUCCESS",
            "workflow": workflow_name,
            "steps_executed": len(results),
            "results": results
        }
