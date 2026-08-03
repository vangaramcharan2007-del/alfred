from __future__ import annotations
import os
import shutil
import subprocess
from typing import Dict, Any, List, Optional

class DesktopController:
    """
    Desktop automation engine for opening applications (VS Code, browser, terminal), launching PowerShell/CMD, and managing local processes.
    """
    def open_vscode(self, workspace_path: Optional[str] = None) -> Dict[str, Any]:
        target = workspace_path or "."
        code_bin = shutil.which("code") or "code"
        try:
            subprocess.Popen([code_bin, target], shell=True)
            return {"status": "SUCCESS", "action": "open_vscode", "path": target}
        except Exception as e:
            return {"status": "FAILED", "action": "open_vscode", "error": str(e)}

    def open_terminal(self, cwd: Optional[str] = None) -> Dict[str, Any]:
        try:
            subprocess.Popen(["wt.exe"], shell=True)
            return {"status": "SUCCESS", "action": "open_terminal"}
        except Exception:
            try:
                subprocess.Popen(["cmd.exe", "/c", "start", "cmd"], shell=True)
                return {"status": "SUCCESS", "action": "open_cmd"}
            except Exception as e:
                return {"status": "FAILED", "action": "open_terminal", "error": str(e)}

    def execute_powershell(self, command_line: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        try:
            res = subprocess.run(
                ["powershell.exe", "-Command", command_line],
                cwd=cwd or ".",
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "status": "SUCCESS" if res.returncode == 0 else "FAILED",
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip()
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
