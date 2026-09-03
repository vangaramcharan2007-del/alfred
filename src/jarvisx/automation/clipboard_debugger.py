import logging
import threading
import time
import pyperclip

logger = logging.getLogger(__name__)

class ClipboardDebugger:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread = None
        self.last_clipboard = ""

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
        logger.info("[DebuggerSwarm] Clipboard Sentry online.")
        self._thread = threading.Thread(target=self._loop, daemon=True, name="ClipboardDebugger")
        self._thread.start()

    def _loop(self):
        while self._running:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != self.last_clipboard and current_clipboard.strip():
                    self.last_clipboard = current_clipboard
                    
                    if "Traceback (most recent call last):" in current_clipboard or "Exception:" in current_clipboard:
                        logger.info("[DebuggerSwarm] Exception detected in clipboard. Analyzing...")
                        self._push_to_ui("debugger_event", {"status": "Analyzing traceback..."})
                        
                        # In a full run, we would pass this to Gemini LLM
                        # For now, we simulate the LLM return
                        time.sleep(2)
                        fix = "# Jarvis Auto-Fix:\n# Check if the variable is None before calling methods on it."
                        pyperclip.copy(fix)
                        self.last_clipboard = fix
                        
                        logger.info("[DebuggerSwarm] Fix generated and copied to clipboard.")
                        self._push_to_ui("debugger_event", {"status": "Fix copied to clipboard!"})
            except Exception as e:
                logger.debug(f"[DebuggerSwarm] Loop error: {e}")
                
            time.sleep(1)
