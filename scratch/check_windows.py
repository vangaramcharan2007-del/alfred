import win32gui

def enumHandler(hwnd, lParam):
    title = win32gui.GetWindowText(hwnd)
    if title:
        print(f"[{title}]")

win32gui.EnumWindows(enumHandler, None)
