"""
Active Window & Environmental Context Sensor for Jarvis OS Harness.
Continuously senses user's focused application, active workspace, and context mode
(Coding, Terminal DevOps, Web Research, Gaming, Media) in real time.
"""

from __future__ import annotations

import ctypes
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import psutil

logger = logging.getLogger("jarvisx.harness.context")


@dataclass
class WindowContext:
    """Active window context state."""
    window_title: str
    process_name: str
    pid: int
    context_mode: str  # CODING, TERMINAL_DEVOPS, WEB_RESEARCH, GAMING, PRODUCTIVITY, GENERAL
    active_project_hint: Optional[str] = None
    timestamp: float = 0.0


class ActiveWindowContextSensor:
    """Monitors the active foreground window and determines environmental context."""

    def __init__(self, check_interval_sec: float = 1.0):
        self.check_interval = check_interval_sec
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self.current_context: Optional[WindowContext] = None
        self._callbacks: List[Callable[[WindowContext], None]] = []

    def add_listener(self, callback: Callable[[WindowContext], None]):
        self._callbacks.append(callback)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(
            target=self._watch_loop,
            daemon=True,
            name="ActiveWindowContextWatcherThread"
        )
        self._thread.start()
        logger.info("Active Window Context Sensor started.")

    def stop(self):
        self.is_running = False

    def get_current_context(self) -> WindowContext:
        if self.current_context:
            return self.current_context
        return self._detect_context()

    def _watch_loop(self):
        last_title = ""
        last_pname = ""

        while self.is_running:
            try:
                ctx = self._detect_context()
                if ctx.window_title != last_title or ctx.process_name != last_pname:
                    last_title = ctx.window_title
                    last_pname = ctx.process_name
                    self.current_context = ctx
                    for cb in self._callbacks:
                        try:
                            cb(ctx)
                        except Exception as ex:
                            logger.error(f"Context callback error: {ex}")
            except Exception:
                pass
            time.sleep(self.check_interval)

    def _detect_context(self) -> WindowContext:
        """Detects the foreground window on Windows."""
        title = "Unknown Window"
        pname = "unknown.exe"
        pid = 0

        if sys.platform == "win32":
            try:
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd:
                    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                    buf = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value

                    lpdw_process_id = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_process_id))
                    pid = lpdw_process_id.value
                    if pid:
                        p = psutil.Process(pid)
                        pname = p.name().lower()
            except Exception:
                pass

        # Classify context mode
        mode = "GENERAL"
        project_hint = None

        if "code.exe" in pname or "visual studio" in title.lower() or "pycharm" in pname:
            mode = "CODING"
            if " - " in title:
                parts = title.split(" - ")
                if len(parts) >= 2:
                    project_hint = parts[-2]
        elif any(t in pname for t in ("windowsterminal.exe", "powershell.exe", "cmd.exe", "wt.exe", "bash.exe")):
            mode = "TERMINAL_DEVOPS"
        elif any(b in pname for b in ("chrome.exe", "msedge.exe", "firefox.exe", "brave.exe")):
            mode = "WEB_RESEARCH"
        elif any(g in pname for g in ("rdr2.exe", "tlou-i.exe", "valorant", "cs2.exe", "cyberpunk", "minecraft", "fortnite")):
            mode = "GAMING"
        elif any(p in pname for p in ("word.exe", "excel.exe", "notion.exe", "slack.exe", "teams.exe", "whatsapp")):
            mode = "PRODUCTIVITY"

        return WindowContext(
            window_title=title,
            process_name=pname,
            pid=pid,
            context_mode=mode,
            active_project_hint=project_hint,
            timestamp=time.time()
        )
