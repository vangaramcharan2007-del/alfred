import logging
import threading
import time
from typing import Optional
from PIL import Image, ImageDraw
import pystray

logger = logging.getLogger(__name__)

class SystemTrayAgent:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self.tray_icon = None

    def start(self):
        if self._running:
            return
        self._running = True
        logger.info("[SystemTray] Initializing native Windows Taskbar icon...")
        # Pystray needs to run in a separate thread so it doesn't block the kernel loop
        threading.Thread(target=self._run_tray, daemon=True, name="SystemTray").start()

    def _run_tray(self):
        try:
            # Create a simple Cyan/Blue circle icon
            img = Image.new('RGB', (64, 64), color=(10, 25, 47))
            d = ImageDraw.Draw(img)
            d.ellipse([12, 12, 52, 52], fill=(0, 210, 255), outline=(255, 255, 255))

            menu = pystray.Menu(
                pystray.MenuItem("Open Jarvis Dashboard", self._action_open_dashboard),
                pystray.MenuItem("Clean PC Cache Now", self._action_clean_pc),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Shutdown Jarvis OS", self._action_shutdown)
            )

            self.tray_icon = pystray.Icon("JarvisX", img, "Jarvis X OS", menu)
            self.tray_icon.run()
        except Exception as e:
            logger.error(f"[SystemTray] Failed to load native icon: {e}")

    def _action_open_dashboard(self, icon, item):
        import webbrowser
        webbrowser.open("http://localhost:8765")
        logger.info("[SystemTray] Opened HUD Dashboard.")

    def _action_clean_pc(self, icon, item):
        logger.info("[SystemTray] Manual PC Clean triggered from Taskbar.")
        try:
            from jarvisx.automation.system_cleaner_daemon import SystemCleanerDaemon
            SystemCleanerDaemon.get_instance().cleaner.scan_and_clean_temp_bloat(delete=True)
            logger.info("[SystemTray] Manual PC Clean completed.")
        except Exception as e:
            logger.error(f"[SystemTray] Clean failed: {e}")

    def _action_shutdown(self, icon, item):
        logger.info("[SystemTray] Shutdown requested from Taskbar.")
        if self.tray_icon:
            self.tray_icon.stop()
        import os
        import signal
        os.kill(os.getpid(), signal.SIGTERM)
