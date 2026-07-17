import pyautogui
from .desktop_permissions import DesktopPermissionManager, DesktopTrustLevel
from .logger import DesktopLogger
from .failsafe import Failsafe

class KeyboardController:
    @staticmethod
    def type_text(text: str, interval: float = 0.05):
        DesktopPermissionManager.require(DesktopTrustLevel.INPUT_CONTROL)
        Failsafe.enable()
        DesktopLogger.log_action("KeyboardController", "TYPE", f"Typing {len(text)} characters")
        pyautogui.write(text, interval=interval)
        # State verification: difficult for raw typing, rely on caller to verify results

    @staticmethod
    def press_key(key: str):
        DesktopPermissionManager.require(DesktopTrustLevel.INPUT_CONTROL)
        Failsafe.enable()
        DesktopLogger.log_action("KeyboardController", "PRESS", f"Pressing {key}")
        pyautogui.press(key)

    @staticmethod
    def hotkey(*keys):
        DesktopPermissionManager.require(DesktopTrustLevel.INPUT_CONTROL)
        Failsafe.enable()
        DesktopLogger.log_action("KeyboardController", "HOTKEY", f"Triggering hotkey: {keys}")
        pyautogui.hotkey(*keys)
