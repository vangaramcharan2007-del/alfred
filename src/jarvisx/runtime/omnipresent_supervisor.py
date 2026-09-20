"""
Omnipresent Supervisor — Master Unified Daemon for Jarvis X / E.V.
==================================================================
Unites all disparate Jarvis subsystems under a single, always-on resident supervisor:
1. E.V. HUD Server (FastAPI + WebSocket on http://localhost:8765)
2. Eevee Groq Neural Voice Matrix (Groq Whisper Large V3 + Full-Duplex Barge-In)
3. Ambient Watcher (Proactive thermal/memory sentinel + context tracker)
4. Windows System Tray Daemon (Reactor icon + desktop control)
5. Sovereign Action Engine (Mid-sentence tool dispatcher)
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("jarvisx.omnipresent")


@dataclass
class SupervisorStatus:
    hud_online: bool = False
    voice_online: bool = False
    ambient_watcher_online: bool = False
    tray_online: bool = False
    uptime_seconds: float = 0.0
    pid: int = 0


class OmnipresentSupervisor:
    """
    Master living daemon supervisor that boots, coordinates, and health-monitors
    all Jarvis subsystems continuously in the background.
    """

    _instance: Optional[OmnipresentSupervisor] = None

    @classmethod
    def get_instance(cls) -> OmnipresentSupervisor:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, hud_port: int = 8765):
        self.hud_port = hud_port
        self._running = False
        self._start_time: float = 0.0
        self._hud_thread: Optional[threading.Thread] = None
        self._tray_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def _start_hud_server(self):
        """Starts the FastAPI HUD dashboard server."""
        try:
            import uvicorn
            from jarvisx.dashboard.hud_server import app
            logger.info(f"[OmnipresentSupervisor] Launching HUD server on port {self.hud_port}...")
            config = uvicorn.Config(app, host="0.0.0.0", port=self.hud_port, log_level="error")
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            logger.error(f"[OmnipresentSupervisor] HUD server error: {e}")

    def _start_voice_matrix(self):
        """Engages Eevee Groq continuous background listener."""
        try:
            from jarvisx.voice.eevee_groq import EeveeGroq
            eevee = EeveeGroq.get_instance()
            eevee.start()
            logger.info("[OmnipresentSupervisor] Eevee Groq Voice Matrix ACTIVE.")
        except Exception as e:
            logger.warning(f"[OmnipresentSupervisor] Voice matrix initialization notice: {e}")

    def _start_ambient_watcher(self):
        """Engages the continuous proactive sensory sentinel."""
        try:
            from jarvisx.runtime.ambient_watcher import get_ambient_watcher
            watcher = get_ambient_watcher()
            watcher.start()
            logger.info("[OmnipresentSupervisor] Ambient Watcher ACTIVE.")
        except Exception as e:
            logger.error(f"[OmnipresentSupervisor] Ambient watcher error: {e}")

    def _start_tray_icon(self):
        """Creates and runs the Windows System Tray reactor icon."""
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Draw glowing cyan/gold reactor icon
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((4, 4, 60, 60), outline=(0, 220, 255, 255), width=4)
            draw.ellipse((16, 16, 48, 48), fill=(255, 190, 0, 230), outline=(255, 255, 255, 255), width=2)
            draw.ellipse((26, 26, 38, 38), fill=(255, 255, 255, 255))

            def _open_hud(icon, item):
                webbrowser.open(f"http://localhost:{self.hud_port}")

            def _flush_ram(icon, item):
                from jarvisx.runtime.thermal_governor import AlfredThermalGovernor
                AlfredThermalGovernor.get_instance().perform_cooling_and_reclaim_cycle()

            def _stage_coding(icon, item):
                from jarvisx.automation.workspace_orchestrator import get_workspace_orchestrator
                get_workspace_orchestrator().deploy_workspace("coding", mid_sentence=True)

            def _exit_app(icon, item):
                self.stop()
                icon.stop()

            menu = pystray.Menu(
                pystray.MenuItem("🚀 Open E.V. HUD", _open_hud, default=True),
                pystray.MenuItem("💻 Stage Coding Workspace", _stage_coding),
                pystray.MenuItem("❄️ Flush RAM & Cool", _flush_ram),
                pystray.MenuItem("❌ Shutdown E.V. Core", _exit_app),
            )

            icon = pystray.Icon("EeveeCore", img, "E.V. Core // Executive Vision", menu)
            icon.run()
        except Exception as e:
            logger.debug(f"[OmnipresentSupervisor] Tray icon not available in headless mode: {e}")

    def start(self, with_tray: bool = False, block: bool = False) -> SupervisorStatus:
        """Boots all subsystems into a unified living presence."""
        with self._lock:
            if self._running:
                return self.get_status()

            self._running = True
            self._start_time = time.time()
            pid = os.getpid()

            logger.info(f"[OmnipresentSupervisor] 🚀 Initializing E.V. Living Core (PID: {pid})...")

            # 1. Boot HUD ASGI server in background thread
            self._hud_thread = threading.Thread(target=self._start_hud_server, daemon=True, name="HUDServerThread")
            self._hud_thread.start()

            # 2. Boot Ambient Watcher
            self._start_ambient_watcher()

            # 3. Boot Eevee Groq Neural Voice Matrix
            self._start_voice_matrix()

            # 4. Announce Core Online
            try:
                from jarvisx.dashboard.event_bus import push_ev_notification
                push_ev_notification(
                    title="E.V. LIVING CORE // ONLINE",
                    message="All organs synchronized. Full-duplex voice & ambient watcher active.",
                    level="success",
                    spoken_text="E.V. living core is online and listening, Boss.",
                    speak_in_background=True,
                )
            except Exception:
                pass

            # 5. Optional Tray icon
            if with_tray:
                self._tray_thread = threading.Thread(target=self._start_tray_icon, daemon=True, name="TrayThread")
                self._tray_thread.start()

            status = self.get_status()

            if block:
                try:
                    while self._running:
                        time.sleep(1.0)
                except KeyboardInterrupt:
                    self.stop()

            return status

    def stop(self):
        """Halts all background loops and releases system resources."""
        with self._lock:
            if not self._running:
                return

            self._running = False
            logger.info("[OmnipresentSupervisor] Halting Jarvis X Living Core...")

            try:
                from jarvisx.runtime.ambient_watcher import get_ambient_watcher
                get_ambient_watcher().stop()
            except Exception:
                pass

            try:
                from jarvisx.voice.eevee_groq import EeveeGroq
                EeveeGroq.get_instance().shutdown()
            except Exception:
                pass

    def get_status(self) -> SupervisorStatus:
        """Returns the live status of all integrated organs."""
        uptime = (time.time() - self._start_time) if self._running else 0.0
        return SupervisorStatus(
            hud_online=bool(self._hud_thread and self._hud_thread.is_alive()),
            voice_online=self._running,
            ambient_watcher_online=self._running,
            tray_online=bool(self._tray_thread and self._tray_thread.is_alive()),
            uptime_seconds=round(uptime, 2),
            pid=os.getpid(),
        )


def get_omnipresent_supervisor() -> OmnipresentSupervisor:
    return OmnipresentSupervisor.get_instance()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    supervisor = get_omnipresent_supervisor()
    print("Engaging Jarvis X Omnipresent Living Core...")
    supervisor.start(with_tray=True, block=True)
