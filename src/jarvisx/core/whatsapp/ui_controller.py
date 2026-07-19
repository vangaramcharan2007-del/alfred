import time
import logging
from typing import Optional

try:
    from pywinauto import Application, Desktop
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    
from jarvisx.tools.win_control import WinController

logger = logging.getLogger(__name__)

class WhatsAppUIController:
    """Controls the WhatsApp Desktop UI using pywinauto and native APIs."""
    
    def __init__(self):
        self.win_control = WinController()
        self.app = None
        self.window = None

    def is_whatsapp_running(self) -> bool:
        handles = self.win_control.find_window("WhatsApp")
        return len(handles) > 0

    def bring_to_foreground(self) -> bool:
        return self.win_control.safe_bring_to_foreground("WhatsApp")

    def connect(self) -> bool:
        if not PYWINAUTO_AVAILABLE:
            logger.warning("pywinauto not available.")
            return False

        if not self.is_whatsapp_running():
            logger.warning("WhatsApp is not running.")
            return False

        try:
            self.app = Application(backend="uia").connect(title_re=".*WhatsApp.*")
            self.window = self.app.window(title_re=".*WhatsApp.*")
            return True
        except ElementNotFoundError:
            logger.error("Could not connect to WhatsApp window.")
            return False
        except Exception as e:
            logger.error(f"Error connecting to WhatsApp: {e}")
            return False

    def select_chat(self, contact_name: str) -> bool:
        """Selects a chat by typing into the search bar."""
        if not self.window:
            if not self.connect():
                return False

        self.bring_to_foreground()
        time.sleep(0.5)

        try:
            # Type into the search box
            # This relies on keyboard shortcuts since WhatsApp UI tree can be deep
            # Ctrl+F focuses search in WhatsApp Desktop
            self.window.type_keys("^f")
            time.sleep(0.5)
            self.window.type_keys(f"{contact_name}{{ENTER}}", with_spaces=True)
            time.sleep(1.0)
            return True
        except Exception as e:
            logger.error(f"Failed to select chat: {e}")
            return False
