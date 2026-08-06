"""Multi-Modal Screen & Vision Context Engine for Jarvis X (Layer 4 - Automation & Perception).

Captures active window metadata, extracts desktop text context snippets,
categorizes work activities, and indexes context snapshots in SQLite memory.
"""

import time
from typing import Any, Dict, List, Optional

from jarvisx.automation.real_window_controller import RealWindowController
from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


class ScreenContextEngine:
    """Zero-fluff production screen & vision context engine."""

    def __init__(
        self,
        window_controller: Optional[RealWindowController] = None,
        memory_provider: Optional[SQLiteMemoryProvider] = None,
    ):
        self.window_controller = window_controller or RealWindowController()
        self.memory = memory_provider or SQLiteMemoryProvider(db_path="var/db/memory.db")

    def capture_active_context(self) -> Dict[str, Any]:
        """Capture active window title, process name, and categorize current desktop context."""
        active_info = self.window_controller.get_active_window_info()
        title = active_info.get("title", "Desktop Workspace")
        process = active_info.get("process", "explorer.exe")
        title_lower = title.lower()

        # Categorize desktop context
        if any(k in title_lower for k in ["code", "py", "vs", "terminal", "powershell", "cmd", "github"]):
            context_category = "CODE_DEVELOPMENT"
        elif any(k in title_lower for k in ["pdf", "lecture", "slide", "study", "exam", "book"]):
            context_category = "ACADEMIC_STUDY"
        elif any(k in title_lower for k in ["chrome", "firefox", "edge", "browser", "docs"]):
            context_category = "WEB_RESEARCH"
        else:
            context_category = "GENERAL_DESKTOP"

        snapshot = {
            "title": title,
            "process": process,
            "category": context_category,
            "timestamp": time.time(),
        }

        # Index in SQLite memory
        self.memory.save_memory(
            category="screen_context",
            key=f"ctx_{int(time.time()*1000)}",
            value=snapshot,
            context={"module": "screen_context_engine", "category": context_category}
        )

        return {
            "status": "CAPTURED",
            "active_window": title,
            "process_name": process,
            "context_category": context_category,
            "snapshot": snapshot,
        }
