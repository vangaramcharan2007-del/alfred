import win32gui
import win32process
import psutil

def enum_windows_callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process_name = psutil.Process(pid).name()
            except:
                process_name = "Unknown"
            windows.append((hwnd, title, process_name))

windows = []
win32gui.EnumWindows(enum_windows_callback, windows)

print("Active Windows:")
for hwnd, title, process_name in windows:
    if 'chrome' in process_name.lower() or 'opera' in process_name.lower() or 'brave' in process_name.lower() or 'edge' in process_name.lower():
        print(f"ID: {hwnd} | Title: {title} | Process: {process_name}")
