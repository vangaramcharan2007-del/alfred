"""
Pre-Cog Engine — Zero-Click Automation.
Eliminates the need for user prompts. Monitors real desktop context —
which apps are running, CPU/RAM load, and user idle time —
to autonomously trigger Jarvis modules before the user asks.

Phase 11: REAL CONTEXT — Uses psutil to scan actual running processes.
"""
import logging
import threading
import time
import ctypes
from typing import Optional, Set

import psutil

logger = logging.getLogger(__name__)


class PreCogEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_action: Optional[str] = None
        self._idle_streak = 0  # consecutive idle checks

    def _push_to_ui(self, event_type: str, data: dict):
        """Broadcast events to E.V. UI."""
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def _get_running_process_names(self) -> Set[str]:
        """Get a set of all currently running process names (lowercase)."""
        names = set()
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info.get('name')
                if name:
                    names.add(name.lower())
        except Exception:
            pass
        return names

    def _get_user_idle_seconds(self) -> float:
        """Get seconds since last user input (mouse/keyboard) on Windows."""
        try:
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            return millis / 1000.0
        except Exception:
            return 0.0

    def _analyze_real_context(self):
        """Scan the user's actual running processes and system state."""
        procs = self._get_running_process_names()
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        idle_secs = self._get_user_idle_seconds()

        # ---- CONTEXT 1: VS Code is open → IDE Active ----
        if "code.exe" in procs and self._last_action != "ide_active":
            logger.info("[Pre-Cog] Context Detected: VS Code is actively running.")
            logger.info("[Pre-Cog] Zero-Click Action: Standing by for Coder Swarm dispatch...")
            self._push_to_ui("precog_event", {
                "context": "IDE Active",
                "action": "Coder Swarm on standby"
            })
            self._last_action = "ide_active"

        # ---- CONTEXT 2: Discord/social apps + VS Code = distraction risk ----
        social_apps = {"discord.exe", "telegram.exe", "whatsapp.exe", "slack.exe"}
        active_socials = procs & social_apps
        if active_socials and "code.exe" in procs and self._last_action != "distraction_risk":
            app_names = ", ".join(a.replace(".exe", "").title() for a in active_socials)
            logger.info(f"[Pre-Cog] Context Detected: Distraction risk — {app_names} running alongside VS Code.")
            logger.info("[Pre-Cog] Zero-Click Action: Recommending E.X.E.C. Flow State...")
            self._push_to_ui("precog_event", {
                "context": f"Distraction Risk: {app_names}",
                "action": "Recommending flow state"
            })
            self._last_action = "distraction_risk"

            # Auto-trigger E.X.E.C. flow state
            try:
                from jarvisx.automation.executive_function import ExecutiveFunctionProtocol
                ExecutiveFunctionProtocol.get_instance().initiate_flow_state("Focus Override")
            except Exception:
                pass

        # ---- CONTEXT 3: High system load ----
        if (cpu > 80 or ram > 85) and self._last_action != "high_load":
            logger.info(f"[Pre-Cog] Context Detected: High system load (CPU: {cpu}%, RAM: {ram}%).")
            logger.info("[Pre-Cog] Zero-Click Action: Notifying Hypervisor for load shedding...")
            self._push_to_ui("precog_event", {
                "context": f"High Load: CPU {cpu}% / RAM {ram}%",
                "action": "Hypervisor load shedding"
            })
            self._last_action = "high_load"

        # ---- CONTEXT 4: User idle for 10+ minutes ----
        if idle_secs > 600:
            self._idle_streak += 1
            if self._idle_streak == 1 and self._last_action != "idle_nudge":
                logger.info(f"[Pre-Cog] Context Detected: User idle for {idle_secs:.0f}s.")
                logger.info("[Pre-Cog] Zero-Click Action: Gentle Eevee nudge incoming...")
                self._push_to_ui("precog_event", {
                    "context": f"User idle for {int(idle_secs)}s",
                    "action": "Gentle nudge"
                })
                self._last_action = "idle_nudge"
        else:
            self._idle_streak = 0
            if self._last_action == "idle_nudge":
                self._last_action = None  # Reset so it can trigger again later

        # ---- CONTEXT 5: Chrome eating too much RAM ----
        chrome_count = sum(1 for p in procs if "chrome" in p)
        if chrome_count > 0 and ram > 75 and self._last_action != "chrome_hog":
            logger.info(f"[Pre-Cog] Context Detected: Chrome ({chrome_count} processes) + RAM at {ram}%.")
            logger.info("[Pre-Cog] Zero-Click Action: Suggest closing excess Chrome tabs.")
            self._push_to_ui("precog_event", {
                "context": f"Chrome RAM hog ({chrome_count} procs, {ram}% RAM)",
                "action": "Suggest closing tabs"
            })
            self._last_action = "chrome_hog"

    def _loop(self):
        logger.info("[Pre-Cog] Zero-Click Automation Engine Online. Monitoring real environment.")
        self._push_to_ui("module_boot", {"name": "PreCogEngine", "status": "ONLINE"})

        while self._running:
            try:
                time.sleep(15)  # Check every 15 seconds
                self._analyze_real_context()
            except Exception as e:
                logger.debug(f"[Pre-Cog] Engine error: {e}")

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="PreCog")
        self._thread.start()

    def stop(self):
        self._running = False
