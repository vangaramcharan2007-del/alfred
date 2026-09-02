"""Jarvis X: Windows Background System Tray Daemon & Always-Listening Core.

Runs silently 24/7 in the Windows system tray.
Provides full duplex background voice listening, mesh health status, and quick access.
"""

from __future__ import annotations
import os
import sys
import time
import threading
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw
import pystray

from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
from jarvisx.mesh.mesh_router import get_mesh_router
from jarvisx.interface.voice_duplex_engine import get_voice_duplex_engine


def create_tray_icon_image() -> Image.Image:
    """Generates a sleek glowing Jarvis cyan/gold reactor icon for the system tray."""
    width = 64
    height = 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Outer glowing circle (Cyan/Teal)
    draw.ellipse((4, 4, 60, 60), outline=(0, 220, 255, 255), width=4)
    # Inner energy core (Gold/Amber)
    draw.ellipse((16, 16, 48, 48), fill=(255, 190, 0, 230), outline=(255, 255, 255, 255), width=2)
    # Center focus point
    draw.ellipse((26, 26, 38, 38), fill=(255, 255, 255, 255))
    return image


class JarvisTrayDaemon:
    """Windows System Tray Daemon keeping Jarvis X alive and listening 24/7 in the background."""

    def __init__(self):
        self.orchestrator = DynamicOrchestrator()
        self.voice_engine = get_voice_duplex_engine()
        self.mesh_router = get_mesh_router()
        self.is_running = True
        self.voice_active = True
        self.tray_icon: Optional[pystray.Icon] = None
        self._voice_thread: Optional[threading.Thread] = None

    def start_background_voice_loop(self):
        """Runs the continuous voice listening loop in a background daemon thread."""
        def _loop():
            self.voice_engine.speak("Jarvis X background core online and listening.")
            while self.is_running:
                if not self.voice_active:
                    time.sleep(1)
                    continue
                try:
                    # Listen for voice speech
                    user_input = self.voice_engine.listen_and_transcribe()
                    if not user_input or user_input.lower() in ["exit", "stop", "quit"]:
                        continue

                    category = self.orchestrator._classify_intent(user_input)
                    import asyncio
                    # Run async execution cleanly
                    asyncio.run(self.orchestrator._execute_subsystem(category, user_input))
                except Exception as e:
                    time.sleep(1)

        self._voice_thread = threading.Thread(target=_loop, daemon=True)
        self._voice_thread.start()

    def show_mesh_status(self, icon=None, item=None):
        """Displays current status of all distributed GPU worker nodes."""
        active = self.mesh_router.get_active_worker()
        worker_3 = self.mesh_router.workers.get("worker_3_rtx5050", {})
        worker_1 = self.mesh_router.workers.get("worker_1_tuf", {})
        
        msg = (
            f"👑 Master (NANI): ONLINE\n"
            f"🧠 Worker 3 (RTX 5050): {'ONLINE' if active and active.get('name') == worker_3.get('name') else 'READY'}\n"
            f"⚡ Worker 1 (RTX 3050): {'ONLINE' if active and active.get('name') == worker_1.get('name') else 'STANDBY'}"
        )
        self.voice_engine.speak("Reporting mesh cluster status. Worker node 3 with RTX 5050 is connected.")
        if self.tray_icon:
            self.tray_icon.notify(title="Jarvis X Cluster Status", message=msg)

    def toggle_voice(self, icon=None, item=None):
        """Toggles active microphone voice listening on/off."""
        self.voice_active = not self.voice_active
        status_text = "Microphone listening resumed." if self.voice_active else "Microphone muted."
        self.voice_engine.speak(status_text)
        if self.tray_icon:
            self.tray_icon.notify(title="Jarvis X Voice", message=status_text)

    def open_terminal(self, icon=None, item=None):
        """Opens the interactive Jarvis X terminal window."""
        project_dir = Path(__file__).resolve().parents[3]
        bat_file = project_dir / "jarvis.bat"
        subprocess.Popen(["cmd.exe", "/c", "start", str(bat_file)], shell=True)

    def stop_daemon(self, icon=None, item=None):
        """Stops the daemon and cleans up tray icon."""
        self.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
        sys.exit(0)

    def run(self):
        """Initializes system tray icon and launches background services."""
        icon_image = create_tray_icon_image()
        
        menu = pystray.Menu(
            pystray.MenuItem("👑 Jarvis X: Sovereign Core (Online)", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🌐 Check Mesh Cluster Status", self.show_mesh_status),
            pystray.MenuItem("🎙️ Toggle Microphone (Mute / Listen)", self.toggle_voice),
            pystray.MenuItem("💻 Open Interactive Terminal", self.open_terminal),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚪 Exit Jarvis X", self.stop_daemon),
        )

        self.tray_icon = pystray.Icon(
            name="JarvisX",
            icon=icon_image,
            title="Jarvis X: Sovereign AI Core",
            menu=menu
        )

        # Start background voice loop
        self.start_background_voice_loop()

        # Run system tray (blocking main thread)
        self.tray_icon.run()


def main():
    daemon = JarvisTrayDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
