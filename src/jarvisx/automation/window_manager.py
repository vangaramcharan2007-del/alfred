import logging
import threading
import time
import pygetwindow as gw

logger = logging.getLogger(__name__)

class WindowManagerAgent:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread = None
        self.enforce_flow_state = False

    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
        self._running = True
        logger.info("[WindowManager] Flow State Enforcer online.")
        self._thread = threading.Thread(target=self._loop, daemon=True, name="WindowManager")
        self._thread.start()

    def enable_flow_state(self):
        self.enforce_flow_state = True
        logger.info("[WindowManager] Flow State ENFORCED. Rearranging windows...")
        self._arrange_windows()

    def disable_flow_state(self):
        self.enforce_flow_state = False
        logger.info("[WindowManager] Flow State RELAXED.")

    def _arrange_windows(self):
        try:
            # Get screen size roughly from the first window
            windows = gw.getAllWindows()
            for win in windows:
                if "Visual Studio Code" in win.title or "Cursor" in win.title:
                    win.maximize()
                elif "Discord" in win.title or "Slack" in win.title:
                    win.minimize()
            self._push_to_ui("window_event", {"status": "Windows Optimized for Coding."})
        except Exception as e:
            logger.debug(f"[WindowManager] Arrange error: {e}")

    def _loop(self):
        while self._running:
            try:
                if self.enforce_flow_state:
                    # Continually minimize distractions if they pop up
                    windows = gw.getAllWindows()
                    for win in windows:
                        if "Discord" in win.title and not win.isMinimized:
                            win.minimize()
                            logger.info("[WindowManager] Minimized Discord to protect flow state.")
            except Exception as e:
                pass
            time.sleep(5)
