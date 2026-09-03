"""
Pre-Cog Engine — Zero-Click Automation.
Eliminates the need for user prompts. Monitors real desktop context —
which apps are running, CPU/RAM load, and user idle time —
to autonomously trigger Jarvis modules before the user asks.

Phase 12: EDITH VISION INTEGRATION — Now takes screenshots if the user is 
stuck or distracted, and triggers Eevee to intervene visually.
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

    def _trigger_vision_nudge(self, context_prompt: str):
        """Asks Edith to look at the screen and Eevee to respond based on what she sees."""
        try:
            from jarvisx.vision.edith_ar import EdithAREngine
            from jarvisx.voice.eevee_companion import EeveeCompanion
            
            edith = EdithAREngine.get_instance()
            eevee = EeveeCompanion.get_instance()
            
            # 1. Ask Edith to read the screen
            analysis = edith.analyze_screen(prompt=context_prompt)
            
            # 2. Tell Eevee what Edith saw, and ask her to gently nudge the user
            eevee_prompt = (
                f"You are Eevee. I just looked at the user's screen. Here is what I saw: '{analysis}'. "
                f"Please provide a very short, cute, gentle spoken nudge (1-2 sentences) to help them based on this."
            )
            
            self._push_to_ui("ev_status", {"text": "Analyzing visual context..."})
            response = eevee._generate_response(eevee_prompt)
            
            self._push_to_ui("tts_response", {"text": response})
            eevee._real_tts_speak(response)
            self._push_to_ui("ev_status", {"text": "Standby."})
            
        except Exception as e:
            logger.error(f"[Pre-Cog] Vision nudge failed: {e}")

    def _analyze_real_context(self):
        """Scan the user's actual running processes and system state."""
        procs = self._get_running_process_names()
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        idle_secs = self._get_user_idle_seconds()

        # ---- CONTEXT 1: User stuck in IDE (Idle + VS Code open) ----
        if "code.exe" in procs and idle_secs > 120 and self._last_action != "stuck_in_code":
            logger.info("[Pre-Cog] Context Detected: User idle in VS Code for 2+ minutes. Might be stuck.")
            logger.info("[Pre-Cog] Zero-Click Action: Triggering Edith Vision Protocol...")
            self._push_to_ui("precog_event", {
                "context": "Stuck in IDE?",
                "action": "Triggering Vision Analysis"
            })
            self._last_action = "stuck_in_code"
            # Offload the vision API call so we don't block the PreCog loop
            threading.Thread(
                target=self._trigger_vision_nudge, 
                args=("The user has been staring at this code for 2 minutes without typing. Are they looking at an error message, a complex function, or a blank file?",),
                daemon=True
            ).start()

        # ---- CONTEXT 2: Distraction Apps Running ----
        social_apps = {"discord.exe", "telegram.exe", "whatsapp.exe", "slack.exe", "chrome.exe"}
        # If they are in a social app, maybe they are distracted.
        # But Chrome could be for work. Let's look at the screen if idle_secs > 60 and Chrome is open.
        if "chrome.exe" in procs and idle_secs > 60 and "code.exe" in procs and self._last_action != "distraction_check":
            logger.info("[Pre-Cog] Context Detected: Chrome and IDE open. Checking for distractions...")
            self._push_to_ui("precog_event", {
                "context": "Possible Distraction",
                "action": "Checking Screen Content"
            })
            self._last_action = "distraction_check"
            threading.Thread(
                target=self._trigger_vision_nudge, 
                args=("The user is supposed to be coding. Look at this screen. Are they on YouTube, Reddit, or a distracting site? Or are they reading documentation?",),
                daemon=True
            ).start()

        # ---- CONTEXT 3: High system load ----
        if (cpu > 80 or ram > 85) and self._last_action != "high_load":
            logger.info(f"[Pre-Cog] Context Detected: High system load (CPU: {cpu}%, RAM: {ram}%).")
            logger.info("[Pre-Cog] Zero-Click Action: Notifying Hypervisor for load shedding...")
            self._push_to_ui("precog_event", {
                "context": f"High Load: CPU {cpu}% / RAM {ram}%",
                "action": "Hypervisor load shedding"
            })
            self._last_action = "high_load"

        # ---- CONTEXT 4: User deeply idle (10+ minutes) ----
        if idle_secs > 600:
            self._idle_streak += 1
            if self._idle_streak == 1 and self._last_action != "idle_nudge":
                logger.info(f"[Pre-Cog] Context Detected: User idle for {idle_secs:.0f}s.")
                self._push_to_ui("precog_event", {
                    "context": f"User idle for {int(idle_secs)}s",
                    "action": "Gentle nudge"
                })
                self._last_action = "idle_nudge"
        else:
            self._idle_streak = 0
            # Reset actions if the user started moving again
            if idle_secs < 5:
                if self._last_action in ("stuck_in_code", "distraction_check", "idle_nudge"):
                    self._last_action = None 

    def _loop(self):
        logger.info("[Pre-Cog] Zero-Click Automation Engine Online. Monitoring real environment.")
        self._push_to_ui("module_boot", {"name": "PreCogEngine", "status": "ONLINE (VISION ACTIVE)"})

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
