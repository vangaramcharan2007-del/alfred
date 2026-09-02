"""
Context Mode Switcher — Auto-detects user activity and adapts Jarvis behavior.
Modes: CODING, STUDYING, GAMING, BROWSING, IDLE
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

logger = logging.getLogger(__name__)


class ContextMode(Enum):
    IDLE = "idle"
    CODING = "coding"
    STUDYING = "studying"
    GAMING = "gaming"
    BROWSING = "browsing"
    COMMUNICATION = "communication"


# Window title keywords that map to modes
MODE_SIGNATURES: Dict[ContextMode, List[str]] = {
    ContextMode.CODING: [
        "visual studio", "vscode", "pycharm", "intellij", "sublime", "atom",
        "vim", "neovim", "terminal", "powershell", "cmd.exe", "git",
        "jupyter", "notebook", ".py", ".js", ".ts", ".java", ".cpp",
    ],
    ContextMode.STUDYING: [
        "pdf", "lecture", "slides", "powerpoint", "docs.google", "notion",
        "anki", "quizlet", "khan academy", "coursera", "udemy", "textbook",
        "exam", "assignment", "homework", ".pdf", "word",
    ],
    ContextMode.GAMING: [
        "valorant", "minecraft", "fortnite", "steam", "epic games",
        "discord", "obs", "game", "roblox", "gta", "apex",
    ],
    ContextMode.BROWSING: [
        "chrome", "firefox", "edge", "safari", "browser", "youtube",
        "twitter", "reddit", "instagram", "facebook",
    ],
    ContextMode.COMMUNICATION: [
        "whatsapp", "telegram", "slack", "teams", "zoom", "meet",
        "outlook", "gmail", "mail",
    ],
}

# Mode-specific behaviors
MODE_CONFIGS: Dict[ContextMode, Dict[str, Any]] = {
    ContextMode.CODING: {
        "proactive_interval": 60,
        "voice_volume": 0.3,
        "notification_priority": "low",
        "hint_style": "technical",
    },
    ContextMode.STUDYING: {
        "proactive_interval": 30,
        "voice_volume": 0.5,
        "notification_priority": "medium",
        "hint_style": "educational",
    },
    ContextMode.GAMING: {
        "proactive_interval": 0,  # no interruptions
        "voice_volume": 0.0,
        "notification_priority": "critical_only",
        "hint_style": "none",
    },
    ContextMode.BROWSING: {
        "proactive_interval": 45,
        "voice_volume": 0.5,
        "notification_priority": "medium",
        "hint_style": "general",
    },
    ContextMode.COMMUNICATION: {
        "proactive_interval": 120,
        "voice_volume": 0.4,
        "notification_priority": "low",
        "hint_style": "social",
    },
    ContextMode.IDLE: {
        "proactive_interval": 30,
        "voice_volume": 0.6,
        "notification_priority": "all",
        "hint_style": "motivational",
    },
}


class ContextModeSwitcher:
    """Auto-detects user activity from window titles and switches Jarvis behavior."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "ContextModeSwitcher":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.current_mode = ContextMode.IDLE
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        self._check_interval = 10

    def on_mode_change(self, callback: Callable):
        """Register callback(old_mode, new_mode) for mode changes."""
        self._callbacks.append(callback)

    def _get_active_window_title(self) -> str:
        try:
            import pygetwindow as gw
            win = gw.getActiveWindow()
            return win.title.lower() if win and win.title else ""
        except Exception:
            return ""

    def _detect_mode(self, title: str) -> ContextMode:
        if not title:
            return ContextMode.IDLE

        scores: Dict[ContextMode, int] = {}
        for mode, keywords in MODE_SIGNATURES.items():
            score = sum(1 for kw in keywords if kw in title)
            if score > 0:
                scores[mode] = score

        if scores:
            return max(scores, key=scores.get)
        return ContextMode.IDLE

    def get_config(self) -> Dict[str, Any]:
        return MODE_CONFIGS.get(self.current_mode, MODE_CONFIGS[ContextMode.IDLE])

    def _loop(self):
        while self._running:
            title = self._get_active_window_title()
            new_mode = self._detect_mode(title)

            if new_mode != self.current_mode:
                old = self.current_mode
                self.current_mode = new_mode
                logger.info(f"[ContextMode] {old.value} -> {new_mode.value} (window: '{title[:40]}')")

                try:
                    from jarvisx.dashboard.hud_server import push_event_sync
                    push_event_sync("mode_change", {
                        "from": old.value, "to": new_mode.value, "window": title[:60]
                    })
                except Exception:
                    pass

                for cb in self._callbacks:
                    try:
                        cb(old, new_mode)
                    except Exception:
                        pass

            time.sleep(self._check_interval)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="ContextMode")
        self._thread.start()
        logger.info("[ContextMode] Switcher started")

    def stop(self):
        self._running = False
