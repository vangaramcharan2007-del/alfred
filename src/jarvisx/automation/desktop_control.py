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

    def open_browser(self, url: str = "https://github.com") -> Dict[str, Any]:
        try:
            import webbrowser
            webbrowser.open(url)
            return {"status": "SUCCESS", "action": "open_browser", "url": url}
        except Exception as e:
            return {"status": "FAILED", "action": "open_browser", "error": str(e)}

    def open_explorer(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        target = target_dir or "."
        try:
            subprocess.Popen(["explorer.exe", os.path.abspath(target)])
            return {"status": "SUCCESS", "action": "open_explorer", "path": target}
        except Exception as e:
            return {"status": "FAILED", "action": "open_explorer", "error": str(e)}

    def clipboard_get(self) -> str:
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception:
            return ""

    def clipboard_set(self, text: str) -> bool:
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except Exception:
            return False

    def take_screenshot(self, output_path: str = "var/screenshot.png") -> Dict[str, Any]:
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            screenshot.save(output_path)
            return {"status": "SUCCESS", "action": "take_screenshot", "path": output_path}
        except Exception as e:
            return {"status": "FAILED", "action": "take_screenshot", "error": str(e)}

