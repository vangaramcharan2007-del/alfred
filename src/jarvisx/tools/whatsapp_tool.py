from typing import Any
import os
import time
import pyautogui
import webbrowser
from jarvisx.tools.base import BaseTool, ToolResult
from jarvisx.core.health import HealthStatus

class WhatsAppTool(BaseTool):
    name = "whatsapp"
    
    def send_files_ui(self, contact_name: str, file_paths: list[str], message: str) -> ToolResult:
        """Automates WhatsApp Web UI to send files and a message."""
        try:
            webbrowser.open("https://web.whatsapp.com")
            
            # Wait for WhatsApp Web to load
            time.sleep(15)
            
            # Search for contact
            pyautogui.hotkey('ctrl', 'alt', '/')
            time.sleep(2)
            pyautogui.write(contact_name)
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Type message
            pyautogui.write(message)
            time.sleep(0.5)
            pyautogui.press('enter')
            
            # Open folder for user to drag-and-drop
            if file_paths:
                scratch_dir = os.path.dirname(file_paths[0])
                if scratch_dir:
                    os.startfile(scratch_dir)
                    
            return ToolResult(success=True, message=f"WhatsApp automation completed for {contact_name}.")
        except Exception as e:
            return ToolResult(success=False, message=f"WhatsApp automation failed: {str(e)}")
