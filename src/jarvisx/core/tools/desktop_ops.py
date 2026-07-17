import time
import psutil
import os
from typing import Dict, Any

from jarvisx.core.tools.desktop.keyboard_controller import KeyboardController
from jarvisx.core.tools.desktop.process_manager import ProcessManager
from jarvisx.core.tools.desktop.window_manager import WindowManager
from jarvisx.core.tools.desktop.mouse_controller import MouseController
from jarvisx.core.tools.desktop.screenshot_manager import ScreenshotManager
from jarvisx.core.tools.desktop.desktop_permissions import DesktopPermissionManager, DesktopTrustLevel
import pygetwindow as gw

class DesktopOps:
    """Desktop automation operations exposed to the ToolRegistry."""
    
    def __init__(self):
        # Escalate permissions to PROCESS_CONTROL so we can actually do desktop automation.
        DesktopPermissionManager.set_level(DesktopTrustLevel.PROCESS_CONTROL)

    def open_application(self, app_name: str) -> Dict[str, Any]:
        ProcessManager.start_process(app_name)
        time.sleep(2)
        
        pid = -1
        executable_path = app_name
        window_title = ""
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if proc.info['name'] and app_name.lower() in proc.info['name'].lower():
                pid = proc.info['pid']
                executable_path = proc.info['exe'] or app_name
                break
                
        active = gw.getActiveWindow()
        if active:
            window_title = active.title

        return {
            "success": True,
            "process_id": pid,
            "executable_path": executable_path,
            "detected_window_title": window_title
        }

    def close_application(self, app_name: str) -> Dict[str, Any]:
        ProcessManager.kill_process(app_name)
        return {"success": True, "closed_app": app_name}

    def type_text(self, text: str) -> Dict[str, Any]:
        KeyboardController.type_text(text)
        active = gw.getActiveWindow()
        title = active.title if active else ""
        return {
            "success": True,
            "character_count": len(text),
            "active_window_title": title
        }

    def press_key(self, key: str) -> Dict[str, Any]:
        if '+' in key:
            keys = key.split('+')
            KeyboardController.hotkey(*keys)
            if 's' in keys and ('ctrl' in keys or 'shift' in keys):
                time.sleep(1.5)
        else:
            KeyboardController.press_key(key)
        return {"success": True, "key_pressed": key}

    def click(self, x: int, y: int) -> Dict[str, Any]:
        MouseController.move(x, y)
        MouseController.click()
        return {"success": True, "x": x, "y": y}

    def move_mouse(self, x: int, y: int) -> Dict[str, Any]:
        MouseController.move(x, y)
        return {"success": True, "x": x, "y": y}

    def list_windows(self) -> Dict[str, Any]:
        windows = WindowManager.list_windows()
        return {"success": True, "windows": windows}

    def capture_screenshot(self) -> Dict[str, Any]:
        path = ScreenshotManager.capture_fullscreen()
        return {"success": True, "saved_image_path": path}
