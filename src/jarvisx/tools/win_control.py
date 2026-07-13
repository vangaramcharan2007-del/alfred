import win32gui
import win32con
import ctypes

class WinController:
    def __init__(self):
        pass

    def _enum_windows_callback(self, hwnd, extra):
        partial_name, handles = extra
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if partial_name.lower() in title.lower():
                handles.append(hwnd)

    def find_window(self, partial_title: str) -> list:
        handles = []
        win32gui.EnumWindows(self._enum_windows_callback, (partial_title, handles))
        return handles

    def safe_bring_to_foreground(self, partial_title: str) -> bool:
        handles = self.find_window(partial_title)
        if not handles:
            return False
            
        hwnd = handles[0]
        try:
            # Check if valid
            if not win32gui.IsWindow(hwnd):
                return False

            # If minimized, restore it
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            # Bring to foreground safely
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception:
            # Fallback for complex foreground locks
            ctypes.windll.user32.SwitchToThisWindow(hwnd, True)
            return True
