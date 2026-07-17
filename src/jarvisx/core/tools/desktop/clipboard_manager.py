import pyperclip
from .desktop_permissions import DesktopPermissionManager, DesktopTrustLevel
from .logger import DesktopLogger

class ClipboardManager:
    @staticmethod
    def read() -> str:
        DesktopPermissionManager.require(DesktopTrustLevel.READ_ONLY)
        DesktopLogger.log_action("ClipboardManager", "READ", "Reading clipboard content")
        return pyperclip.paste()

    @staticmethod
    def write(text: str):
        DesktopPermissionManager.require(DesktopTrustLevel.INPUT_CONTROL)
        DesktopLogger.log_action("ClipboardManager", "WRITE", f"Writing to clipboard ({len(text)} chars)")
        pyperclip.copy(text)
        
        # State verification
        if pyperclip.paste() != text:
            DesktopLogger.log_error("ClipboardManager", "WRITE_VERIFY", "Clipboard content mismatch")
            raise RuntimeError("Clipboard write verification failed")
        DesktopLogger.log_action("ClipboardManager", "WRITE_VERIFY", "Clipboard content verified")
