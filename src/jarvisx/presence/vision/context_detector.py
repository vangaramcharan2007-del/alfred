from __future__ import annotations
from typing import Dict, Any, List

class DesktopContextDetector:
    """
    Detects active environment context (IDE, Browser, Terminal) and active errors.
    """
    def detect_context(self, active_window_title: str) -> Dict[str, Any]:
        title_lower = active_window_title.lower()

        app_type = "UNKNOWN"
        if "code" in title_lower or "pycharm" in title_lower or "ide" in title_lower:
            app_type = "IDE"
        elif "chrome" in title_lower or "edge" in title_lower or "firefox" in title_lower:
            app_type = "BROWSER"
        elif "terminal" in title_lower or "powershell" in title_lower or "cmd" in title_lower:
            app_type = "TERMINAL"

        has_traceback = "traceback" in title_lower or "error" in title_lower or "failed" in title_lower or "code" in title_lower

        return {
            "active_window": active_window_title,
            "application_type": app_type,
            "has_error": has_traceback,
            "suggested_action": "investigate_traceback" if has_traceback else "read_design_doc"
        }
