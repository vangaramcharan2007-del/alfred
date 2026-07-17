import pygetwindow as gw
from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError
from .desktop_permissions import DesktopPermissionManager, DesktopTrustLevel
from .logger import DesktopLogger
import time

class WindowManager:
    @staticmethod
    def list_windows() -> list[str]:
        DesktopPermissionManager.require(DesktopTrustLevel.READ_ONLY)
        return [win.title for win in gw.getAllWindows() if win.title]

    @staticmethod
    def focus_window(title: str) -> bool:
        DesktopPermissionManager.require(DesktopTrustLevel.PROCESS_CONTROL)
        DesktopLogger.log_action("WindowManager", "FOCUS", f"Focusing window: {title}")
        
        try:
            windows = gw.getWindowsWithTitle(title)
            if not windows:
                DesktopLogger.log_error("WindowManager", "FOCUS", f"Window {title} not found")
                raise RuntimeError(f"Window {title} not found")
                
            windows = [w for w in windows if w.width > 0 and w.height > 0]
            if not windows:
                DesktopLogger.log_error("WindowManager", "FOCUS", f"No visible window {title} found")
                raise RuntimeError(f"No visible window {title} found")
                
            target = windows[0]
            
            try:
                app = Application(backend="win32").connect(handle=target._hWnd, timeout=5)
                dlg = app.window(handle=target._hWnd)
                dlg.set_focus()
            except Exception:
                try:
                    target.activate()
                except Exception:
                    pass
            
            time.sleep(0.5)
            
            if target.isActive:
                DesktopLogger.log_action("WindowManager", "FOCUS_VERIFY", f"Window {title} is active")
                return True
                
            DesktopLogger.log_error("WindowManager", "FOCUS_VERIFY", f"Failed to activate {title}")
            return False
            
        except Exception as e:
            DesktopLogger.log_error("WindowManager", "FOCUS", str(e))
            raise e

    @staticmethod
    def close_window(title: str) -> bool:
        DesktopPermissionManager.require(DesktopTrustLevel.PROCESS_CONTROL)
        DesktopLogger.log_action("WindowManager", "CLOSE", f"Closing window: {title}")
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].close()
            time.sleep(0.5)
            # State verification
            windows_after = gw.getWindowsWithTitle(title)
            if windows_after:
                DesktopLogger.log_error("WindowManager", "CLOSE_VERIFY", f"Failed to close {title}")
                raise RuntimeError(f"Failed to close window {title}")
            DesktopLogger.log_action("WindowManager", "CLOSE_VERIFY", f"Window {title} closed")
            return True
        DesktopLogger.log_error("WindowManager", "CLOSE", f"Window {title} not found")
        return False
