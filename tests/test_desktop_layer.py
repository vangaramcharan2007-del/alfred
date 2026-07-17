import pytest
from jarvisx.core.tools.desktop import (
    DesktopPermissionManager, DesktopTrustLevel, ClipboardManager,
    ProcessManager, WindowManager, Failsafe
)

def setup_module():
    DesktopPermissionManager.set_level(DesktopTrustLevel.SYSTEM_CONTROL)

def test_clipboard():
    text = "test_clipboard_content"
    ClipboardManager.write(text)
    assert ClipboardManager.read() == text

def test_process_listing():
    assert ProcessManager.is_running("explorer") == True

def test_window_listing():
    windows = WindowManager.list_windows()
    assert len(windows) > 0

def test_failsafe():
    Failsafe.enable()
    import pyautogui
    assert pyautogui.FAILSAFE == True
