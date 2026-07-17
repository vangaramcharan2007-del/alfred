import pyautogui
from .desktop_permissions import DesktopPermissionManager, DesktopTrustLevel
from .logger import DesktopLogger
from .failsafe import Failsafe

class MouseController:
    @staticmethod
    def move(x: int, y: int, duration: float = 0.5):
        DesktopPermissionManager.require(DesktopTrustLevel.INPUT_CONTROL)
        Failsafe.enable()
        DesktopLogger.log_action("MouseController", "MOVE", f"Moving cursor to ({x}, {y})")
        pyautogui.moveTo(x, y, duration=duration)
        
        # State verification
        cx, cy = pyautogui.position()
        # allow 1px deviation
        if abs(cx - x) > 1 or abs(cy - y) > 1:
            DesktopLogger.log_error("MouseController", "MOVE_VERIFY", f"Cursor at ({cx}, {cy}) instead of ({x}, {y})")
            raise RuntimeError(f"Mouse move verification failed. Expected ({x}, {y}), got ({cx}, {cy})")

    @staticmethod
    def click(button: str = 'left'):
        DesktopPermissionManager.require(DesktopTrustLevel.INPUT_CONTROL)
        Failsafe.enable()
        DesktopLogger.log_action("MouseController", "CLICK", f"Clicking {button} button")
        pyautogui.click(button=button)

    @staticmethod
    def double_click():
        DesktopPermissionManager.require(DesktopTrustLevel.INPUT_CONTROL)
        Failsafe.enable()
        DesktopLogger.log_action("MouseController", "DOUBLE_CLICK", "Double clicking")
        pyautogui.doubleClick()

    @staticmethod
    def scroll(clicks: int):
        DesktopPermissionManager.require(DesktopTrustLevel.INPUT_CONTROL)
        Failsafe.enable()
        DesktopLogger.log_action("MouseController", "SCROLL", f"Scrolling {clicks} units")
        pyautogui.scroll(clicks)
