import time
import os
import logging
import pyautogui
import pyperclip

from .ui_controller import WhatsAppUIController

logger = logging.getLogger(__name__)

class WhatsAppUploader:
    """Handles uploading files to WhatsApp."""
    
    def __init__(self, ui_controller: WhatsAppUIController):
        self.ui = ui_controller

    def upload_file(self, filepath: str) -> bool:
        """
        Uploads a file to the active WhatsApp chat.
        Returns True if successful.
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return False

        if not self.ui.window:
            if not self.ui.connect():
                return False

        self.ui.bring_to_foreground()
        time.sleep(0.5)

        try:
            # WhatsApp Desktop file upload via Clipboard
            # 1. Copy file to clipboard (simulated here by opening file dialog or using powershell)
            # Actually, the easiest way to send a file in WhatsApp desktop is:
            # Click Attachment (Ctrl+Alt+Shift+U or tab to it) -> Document -> Enter path
            # But pasting a file directly works too if we copy it to clipboard via powershell.
            
            import subprocess
            # Copy file to clipboard on Windows
            cmd = f'powershell.exe -command "Set-Clipboard -Path \'{filepath}\'"'
            subprocess.run(cmd, shell=True, check=True)
            
            time.sleep(0.5)
            # Paste into WhatsApp
            self.ui.window.type_keys("^v")
            time.sleep(1.0)
            # Press enter to send
            self.ui.window.type_keys("{ENTER}")
            time.sleep(1.0)
            return True
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False
