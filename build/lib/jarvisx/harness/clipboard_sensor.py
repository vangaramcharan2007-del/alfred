"""
Ambient Clipboard Sensor & Error Interceptor for Jarvis OS Harness.
Continuously watches the Windows clipboard for copied tracebacks, compiler errors,
code snippets, URLs, and shell commands, and automatically prepares/executes resolutions.
"""

from __future__ import annotations

import logging
import re
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import pyperclip

logger = logging.getLogger("jarvisx.harness.clipboard")


@dataclass
class ClipboardEvent:
    """Classified clipboard event payload."""
    event_type: str  # PYTHON_ERROR, TERMINAL_COMMAND, WEB_URL, CODE_SNIPPET, RAW_TEXT
    content: str
    parsed_metadata: Dict[str, Any]
    timestamp: float = 0.0


class AmbientClipboardSensor:
    """Continuous background sensor that listens for clipboard changes and auto-triages intent."""

    def __init__(self, check_interval_sec: float = 0.8):
        self.check_interval = check_interval_sec
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._last_content = ""
        self._callbacks: List[Callable[[ClipboardEvent], None]] = []

    def add_listener(self, callback: Callable[[ClipboardEvent], None]):
        """Adds a listener callback for clipboard events."""
        self._callbacks.append(callback)

    def start(self):
        """Starts the background clipboard listener."""
        if self.is_running:
            return
        self.is_running = True
        try:
            self._last_content = pyperclip.paste() or ""
        except Exception:
            self._last_content = ""

        self._thread = threading.Thread(
            target=self._watch_loop,
            daemon=True,
            name="AmbientClipboardWatcherThread"
        )
        self._thread.start()
        logger.info("Ambient Clipboard Sensor started.")

    def stop(self):
        """Stops the clipboard listener."""
        self.is_running = False

    def _watch_loop(self):
        while self.is_running:
            try:
                content = pyperclip.paste()
                if content and content != self._last_content:
                    self._last_content = content
                    event = self._analyze_content(content)
                    if event:
                        for cb in self._callbacks:
                            try:
                                cb(event)
                            except Exception as ex:
                                logger.error(f"Callback error on clipboard event: {ex}")
            except Exception:
                pass
            time.sleep(self.check_interval)

    def _analyze_content(self, text: str) -> Optional[ClipboardEvent]:
        """Classifies copied text and extracts actionable parameters."""
        raw = text.strip()
        if not raw or len(raw) < 4:
            return None

        # 1. Python Error / Traceback Detection
        if "Traceback (most recent call last):" in raw or re.search(r'File "([^"]+)", line (\d+)', raw):
            match = re.search(r'File "([^"]+)", line (\d+)(?:, in (\w+))?', raw)
            file_path = match.group(1) if match else "unknown"
            line_num = int(match.group(2)) if match else 0
            err_line = raw.strip().splitlines()[-1] if raw.strip().splitlines() else "Unknown Error"

            return ClipboardEvent(
                event_type="PYTHON_ERROR",
                content=raw,
                parsed_metadata={
                    "file_path": file_path,
                    "line_number": line_num,
                    "error_summary": err_line,
                    "recommended_action": "AUTONOMOUS_CODE_HEAL"
                },
                timestamp=time.time()
            )

        # 2. Web URL
        if raw.startswith("http://") or raw.startswith("https://"):
            return ClipboardEvent(
                event_type="WEB_URL",
                content=raw,
                parsed_metadata={
                    "url": raw,
                    "recommended_action": "RESEARCH_AGGREGATION"
                },
                timestamp=time.time()
            )

        # 3. Shell / Terminal Command (e.g. git, npm, pip, python, docker)
        first_word = raw.split()[0].lower() if raw.split() else ""
        if first_word in ("git", "npm", "pip", "python", "docker", "pytest", "cargo", "curl", "powershell", "kubectl"):
            return ClipboardEvent(
                event_type="TERMINAL_COMMAND",
                content=raw,
                parsed_metadata={
                    "command": raw,
                    "tool": first_word,
                    "recommended_action": "DEVOPS_EXECUTION"
                },
                timestamp=time.time()
            )

        # 4. Code Snippet
        if any(keyword in raw for keyword in ("def ", "class ", "import ", "const ", "function ", "async ", "SELECT ", "public static void")):
            return ClipboardEvent(
                event_type="CODE_SNIPPET",
                content=raw,
                parsed_metadata={
                    "lines": len(raw.splitlines()),
                    "recommended_action": "CODE_ANALYSIS"
                },
                timestamp=time.time()
            )

        return ClipboardEvent(
            event_type="RAW_TEXT",
            content=raw[:200],
            parsed_metadata={"length": len(raw)},
            timestamp=time.time()
        )
