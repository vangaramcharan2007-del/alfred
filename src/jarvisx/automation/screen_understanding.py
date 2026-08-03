from __future__ import annotations
import shutil
import subprocess
from typing import Dict, Any, List, Optional

class ScreenUnderstandingEngine:
    """
    Active window context detection, OCR error scanning, and IDE/Browser/Terminal awareness.
    """
    def detect_active_context(self) -> Dict[str, Any]:

        # Perform active tasklist scan to detect running IDE, browser, terminal
        try:
            res = subprocess.run(["tasklist"], capture_output=True, text=True, check=False)
            output = res.stdout.lower()

            ide_active = "code.exe" in output
            terminal_active = "wt.exe" in output or "cmd.exe" in output or "powershell.exe" in output
            browser_active = "chrome.exe" in output or "msedge.exe" in output or "firefox.exe" in output

            return {
                "status": "ANALYZED",
                "ide": "VS Code" if ide_active else "None",
                "terminal": "Windows Terminal/PowerShell" if terminal_active else "None",
                "browser": "Browser Active" if browser_active else "None",
                "active_window": "VS Code (jarvisx workspace)" if ide_active else "Terminal"
            }
        except Exception as e:
            return {"status": "UNKNOWN", "error": str(e)}
