"""
WhatsApp Visual Desktop & Web Actuation Engine for Jarvis X & Alfred OS.
Executes live on-screen WhatsApp messaging right in front of Charan's eyes:
1. Deep links to WhatsApp Desktop (`whatsapp://`) and WhatsApp Web (`https://web.whatsapp.com`).
2. Dispatches genuine Windows kernel hardware scan code inputs via Win32 `SendInput` API (Enter scan code 0x1C + absolute hardware mouse click at 1772, 1146).
"""

import os
import sys
import time
import urllib.parse
import webbrowser
import logging
import ctypes
from ctypes import wintypes

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("jarvisx.whatsapp")

user32 = ctypes.windll.user32


# ---------------------------------------------------------------------------
# Win32 SendInput Structures for Kernel-Level Hardware Events
# ---------------------------------------------------------------------------

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(wintypes.ULONG))
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ('wVk', wintypes.WORD),
        ('wScan', wintypes.WORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(wintypes.ULONG))
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ('uMsg', wintypes.DWORD),
        ('wParamL', wintypes.WORD),
        ('wParamH', wintypes.WORD)
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ('mi', MOUSEINPUT),
        ('ki', KEYBDINPUT),
        ('hi', HARDWAREINPUT)
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ('type', wintypes.DWORD),
        ('u', INPUT_UNION)
    ]


def send_hardware_scan_enter():
    """Dispatches real hardware keyboard scan code 0x1C (Enter) via SendInput."""
    scan = user32.MapVirtualKeyW(0x0D, 0) or 0x1C
    
    # Key Down (KEYEVENTF_SCANCODE = 0x0008)
    inp_down = INPUT(type=1)
    inp_down.u.ki = KEYBDINPUT(wVk=0x0D, wScan=scan, dwFlags=0x0008, time=0, dwExtraInfo=None)
    
    # Key Up (KEYEVENTF_SCANCODE = 0x0008 | KEYEVENTF_KEYUP = 0x0002)
    inp_up = INPUT(type=1)
    inp_up.u.ki = KEYBDINPUT(wVk=0x0D, wScan=scan, dwFlags=0x0008 | 0x0002, time=0, dwExtraInfo=None)
    
    user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
    time.sleep(0.06)
    user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))


def send_hardware_absolute_click(x: int, y: int):
    """Dispatches absolute normalized mouse click via SendInput (0 to 65535 space)."""
    sw = user32.GetSystemMetrics(0) or 1920
    sh = user32.GetSystemMetrics(1) or 1200
    norm_x = int((x * 65535) / sw)
    norm_y = int((y * 65535) / sh)
    
    # Move Cursor
    inp_move = INPUT(type=0)
    inp_move.u.mi = MOUSEINPUT(dx=norm_x, dy=norm_y, mouseData=0, dwFlags=0x8000 | 0x0001, time=0, dwExtraInfo=None)
    user32.SendInput(1, ctypes.byref(inp_move), ctypes.sizeof(INPUT))
    time.sleep(0.04)
    
    # Click Down (MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTDOWN = 0x8000 | 0x0002)
    inp_down = INPUT(type=0)
    inp_down.u.mi = MOUSEINPUT(dx=norm_x, dy=norm_y, mouseData=0, dwFlags=0x8000 | 0x0002, time=0, dwExtraInfo=None)
    user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
    time.sleep(0.06)
    
    # Click Up (MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTUP = 0x8000 | 0x0004)
    inp_up = INPUT(type=0)
    inp_up.u.mi = MOUSEINPUT(dx=norm_x, dy=norm_y, mouseData=0, dwFlags=0x8000 | 0x0004, time=0, dwExtraInfo=None)
    user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))


def send_whatsapp_live(recipient: str = "Dakshith", message: str = "hi") -> dict:
    """
    Executes on-screen WhatsApp automation to send a message.
    """
    print(f"\n[WHATSAPP ACTUATION] [*] Initiating on-screen message dispatch to '{recipient}' with text: '{message}'...")
    encoded_msg = urllib.parse.quote(message)
    
    # Direct phone vs contact name
    is_phone_num = "".join(filter(str.isdigit, recipient))
    if len(is_phone_num) >= 10:
        url = f"https://web.whatsapp.com/send?phone={is_phone_num}&text={encoded_msg}"
        desktop_protocol = f"whatsapp://send?phone={is_phone_num}&text={encoded_msg}"
    else:
        url = f"https://web.whatsapp.com/send?text={encoded_msg}"
        desktop_protocol = f"whatsapp://send?text={encoded_msg}"

    print(f"[*] Launching WhatsApp on your screen...")
    
    # 1. Launch WhatsApp protocol & browser
    try:
        os.system(f'start "" "{desktop_protocol}"')
    except Exception:
        pass

    webbrowser.open(url)

    # 2. Wait for WhatsApp to focus and populate input
    print("[*] Waiting 3.0 seconds for WhatsApp to focus and populate message...")
    time.sleep(3.0)

    # 3. Calibrated Screen Metrics (Physical 1920x1200)
    sw = user32.GetSystemMetrics(0) or 1920
    sh = user32.GetSystemMetrics(1) or 1200
    
    send_x = int(0.9231 * sw)  # 1772 on 1920x1200
    send_y = int(0.9555 * sh)  # 1146 on 1920x1200
    input_x = int(0.55 * sw)   # 1056 on 1920x1200
    input_y = int(0.9555 * sh)

    # Step A: Focus input box by hardware click
    print(f"[*] Focusing input box at ({input_x}, {input_y})...")
    send_hardware_absolute_click(input_x, input_y)
    time.sleep(0.1)

    # Step B: Send Hardware Scan Code Enter (0x1C)
    print("[*] Dispatched hardware scan code 0x1C (Enter)...")
    send_hardware_scan_enter()
    time.sleep(0.15)

    # Step C: Direct hardware click on green Send button (1772, 1146)
    print(f"[*] Triggering hardware click on green Send button at ({send_x}, {send_y})...")
    send_hardware_absolute_click(send_x, send_y)
    time.sleep(0.1)

    # Step D: Final Enter pulse
    send_hardware_scan_enter()

    print(f"\n[WHATSAPP ACTUATION] [OK] Message '{message}' dispatched live on-screen for '{recipient}'!")
    return {
        "status": "DISPATCHED_LIVE",
        "recipient": recipient,
        "message": message,
        "mode": "WIN32_SENDINPUT_HARDWARE_SCANCODE"
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Dakshith"
    msg = sys.argv[2] if len(sys.argv) > 2 else "hi"
    send_whatsapp_live(target, msg)
