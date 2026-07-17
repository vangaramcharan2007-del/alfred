import pyautogui
from .logger import DesktopLogger

class Failsafe:
    @staticmethod
    def enable():
        pyautogui.FAILSAFE = True
        DesktopLogger.log_action("Failsafe", "ENABLE", "PyAutoGUI FAILSAFE set to True")
        
    @staticmethod
    def trigger():
        DesktopLogger.log_error("Failsafe", "TRIGGER", "Emergency stop triggered")
        raise RuntimeError("Desktop Automation Failsafe Triggered!")
