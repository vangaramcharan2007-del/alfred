"""
Ambient Watcher — Proactive Sensory Daemon for Jarvis X / E.V.
==============================================================
Runs continuously in the background to provide real-time autonomous awareness:
1. Memory & Thermal Sentinel: Flushes RAM working sets automatically when bloated (>80%)
2. Active Window & Context Tracker: Observes foreground workflow (VS Code, Chrome, Terminal)
3. Return-to-Desk Detector: Welcomes Charan back after periods of inactivity
4. Live EV HUD Telemetry Dispatch: Streams proactive glass toasts & EV voice notices
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import psutil

logger = logging.getLogger("jarvisx.ambient_watcher")


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.UINT),
        ("dwTime", ctypes.wintypes.DWORD),
    ]


@dataclass
class AmbientTelemetry:
    active_window: str = "Desktop"
    ram_percent: float = 0.0
    cpu_percent: float = 0.0
    idle_seconds: float = 0.0
    proactive_actions_taken: int = 0
    last_action_timestamp: float = 0.0


class AmbientWatcher:
    """
    Continuous sensory sentinel giving Jarvis proactive life and ambient awareness.
    """

    _instance: Optional[AmbientWatcher] = None

    @classmethod
    def get_instance(cls) -> AmbientWatcher:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, check_interval_sec: float = 15.0, ram_threshold_percent: float = 80.0):
        self.check_interval_sec = check_interval_sec
        self.ram_threshold_percent = ram_threshold_percent
        self.telemetry = AmbientTelemetry()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_active_window = ""
        self._was_idle = False
        self._lock = threading.Lock()

    def _push_hud(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.event_bus import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def _speak_notice(self, text: str):
        try:
            from jarvisx.voice.sovereign_neural_tts import get_neural_tts
            tts = get_neural_tts()
            tts.speak(text, voice_key="hyper_realistic_female", blocking=False)
        except Exception as e:
            logger.debug(f"[AmbientWatcher] Voice notice failed: {e}")

    def get_idle_seconds(self) -> float:
        """Returns number of seconds since last user keyboard or mouse activity."""
        try:
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                return max(0.0, millis / 1000.0)
        except Exception:
            pass
        return 0.0

    def get_foreground_window_title(self) -> str:
        """Returns the title of the active foreground window."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            buf = ctypes.create_unicode_buffer(512)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, 512)
            return buf.value.strip() or "Desktop Workspace"
        except Exception:
            return "Desktop Workspace"

    def perform_ambient_check(self) -> Dict[str, Any]:
        """Runs a single pass of proactive system awareness and self-healing."""
        with self._lock:
            # 1. Update live vitals
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            idle_sec = self.get_idle_seconds()
            fg_window = self.get_foreground_window_title()

            self.telemetry.ram_percent = mem.percent
            self.telemetry.cpu_percent = cpu
            self.telemetry.idle_seconds = idle_sec
            self.telemetry.active_window = fg_window

            actions = []

            # 2. Memory & Thermal Sentinel: Auto-flush if RAM bloated
            if mem.percent >= self.ram_threshold_percent:
                try:
                    from jarvisx.runtime.thermal_governor import AlfredThermalGovernor
                    gov = AlfredThermalGovernor.get_instance()
                    rep = gov.perform_cooling_and_reclaim_cycle()
                    reclaimed_mb = round(rep.reclaimed_ram_mb, 1)

                    if reclaimed_mb > 50:
                        self.telemetry.proactive_actions_taken += 1
                        self.telemetry.last_action_timestamp = time.time()
                        actions.append(f"Auto-flushed {reclaimed_mb}MB RAM")

                        # Push HUD glass notification toast
                        self._push_hud("cooling_event", {
                            "reclaimed_ram_mb": reclaimed_mb,
                            "processes_optimized": rep.processes_optimized,
                            "thermal_pressure": "Nominal",
                        })
                        self._push_hud("ev_notification", {
                            "title": "❄️ PROACTIVE SENTINEL",
                            "message": f"Autonomous memory compaction reclaimed +{reclaimed_mb} MB across {rep.processes_optimized} apps.",
                            "level": "success",
                        })
                        self._speak_notice(f"Proactive alert: reclaimed {int(reclaimed_mb)} megabytes of bloated background memory, Boss.")
                except Exception as e:
                    logger.debug(f"[AmbientWatcher] Memory purge error: {e}")

            # 3. Context Transition: User changed primary workspace app
            if fg_window and fg_window != self._last_active_window and len(fg_window) > 2:
                self._last_active_window = fg_window
                self._push_hud("ambient_context_event", {
                    "active_window": fg_window,
                    "timestamp": time.time(),
                })

            # 4. Inactivity & Return Welcomer
            if idle_sec > 600:  # 10 minutes idle
                self._was_idle = True
            elif self._was_idle and idle_sec < 5:
                # User just returned!
                self._was_idle = False
                self._push_hud("ev_notification", {
                    "title": "👋 WELCOME BACK",
                    "message": f"Boss active on desktop. All systems green. Focus: '{fg_window[:30]}'",
                    "level": "cyan",
                })
                self._speak_notice("Welcome back, Boss. Systems ready.")

            return {
                "active_window": fg_window,
                "ram_percent": mem.percent,
                "cpu_percent": cpu,
                "idle_seconds": round(idle_sec, 1),
                "actions": actions,
            }

    def _loop(self):
        logger.info("[AmbientWatcher] Proactive Sensory Loop ONLINE.")
        self._push_hud("module_boot", {"name": "AmbientWatcher", "status": "ONLINE (SENSORY PROACTIVE)"})

        while self._running:
            try:
                self.perform_ambient_check()
            except Exception as e:
                logger.error(f"[AmbientWatcher] Check iteration failed: {e}")
            time.sleep(self.check_interval_sec)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="AmbientWatcherThread")
        self._thread.start()
        logger.info("[AmbientWatcher] Started background monitoring thread.")

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("[AmbientWatcher] Stopped background monitoring thread.")


def get_ambient_watcher() -> AmbientWatcher:
    """Get global AmbientWatcher singleton."""
    return AmbientWatcher.get_instance()
