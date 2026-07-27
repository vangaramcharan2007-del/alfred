from typing import Any
import os
import time
import pyautogui
import webbrowser
import win32clipboard
import win32con
import struct
from jarvisx.tools.base import BaseTool, ToolResult
from jarvisx.core.health import HealthStatus

class WhatsAppTool(BaseTool):
    name = "whatsapp"
    
    def send_files_ui(self, contact_name: str, file_paths: list[str], message: str) -> ToolResult:
        """Automates WhatsApp Desktop app to send files and a message."""
        try:
            import os
            # Launch WhatsApp Desktop App
            os.system("start whatsapp:")
            
            # Wait for WhatsApp to open and load
            time.sleep(5)
            
            # Search for contact (Ctrl + F is standard for search in the Desktop app)
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            pyautogui.write(contact_name)
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1.5)
            
            # Type message
            pyautogui.write(message)
            time.sleep(0.5)
            
            # Send the files by pasting them
            if file_paths:
                # Prepare DROPFILES structure
                stg = struct.pack('iiiii', 20, 0, 0, 0, 1)
                paths = '\0'.join(os.path.abspath(p) for p in file_paths) + '\0\0'
                stg += paths.encode('utf-16le')
                
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_HDROP, stg)
                win32clipboard.CloseClipboard()
                
                # Paste in WhatsApp
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(2)
                
            # Press enter to send
            pyautogui.press('enter')
            
            return ToolResult(success=True, message=f"WhatsApp automation completed for {contact_name}.")
        except Exception as e:
            return ToolResult(success=False, message=f"WhatsApp automation failed: {str(e)}")
