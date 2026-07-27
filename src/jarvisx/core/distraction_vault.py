import threading
import time
import logging
import os
import psutil

try:
    import win32gui
    import win32process
except ImportError:
    win32gui = None
    win32process = None

logger = logging.getLogger(__name__)

class GuardianMonitor:
    """
    The Distraction Vault: Forcefully monitors the active window and kills distractions.
    """
    def __init__(self, callback):
        self.running = False
        self.thread = None
        self.callback = callback
        self.distraction_keywords = ["youtube", "netflix", "instagram", "facebook", "game"]
        self.focus_mode = False

    def engage_focus_mode(self):
        self.focus_mode = True
        logger.info("Guardian Monitor: Focus Mode ENGAGED.")

    def disengage_focus_mode(self):
        self.focus_mode = False
        logger.info("Guardian Monitor: Focus Mode DISENGAGED.")

    def start(self):
        if self.running or not win32gui:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True, name="GuardianVault")
        self.thread.start()
        logger.info("Guardian Monitor started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Guardian Monitor stopped.")

    def _monitor_loop(self):
        while self.running:
            time.sleep(1.0)
            if not self.focus_mode:
                continue

            try:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    title = win32gui.GetWindowText(hwnd).lower()
                    
                    for keyword in self.distraction_keywords:
                        if keyword in title:
                            # Kill the process
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            try:
                                proc = psutil.Process(pid)
                                proc.kill()
                                logger.warning(f"Guardian killed distraction: {title}")
                                self.callback(f"distraction_killed:{keyword}")
                            except Exception as e:
                                logger.error(f"Failed to kill {title}: {e}")
            except Exception:
                pass
