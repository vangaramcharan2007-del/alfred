#!/usr/bin/env python3
"""
Jarvis X - Agent Mike Global Hotkey Listener (Option 4)
Registers system-wide hotkey: [Win + Alt + C]
When triggered:
- Forces immediate Chameleon Clock + Visualizer theme re-sync
- Updates Windows 11 Taskbar and DWM accent color
- Plays subtle confirmation chime
"""

import sys
import ctypes
from ctypes import wintypes
import winsound
from pathlib import Path

# Safe streams for headless pythonw.exe execution
if sys.stdout is None:
    class _SafeWriter:
        def write(self, s): pass
        def flush(self): pass
    sys.stdout = _SafeWriter()
if sys.stderr is None:
    class _SafeErrWriter:
        def write(self, s): pass
        def flush(self): pass
    sys.stderr = _SafeErrWriter()

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from jarvisx.agents.customizer_mike import MikeCustomizerAgent

# Win32 Constants
MOD_ALT = 0x0001
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
VK_C = 0x43
WM_HOTKEY = 0x0312
HOTKEY_ID = 101


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]


def listen_for_hotkey(mike: MikeCustomizerAgent = None, run_once: bool = False):
    if mike is None:
        mike = MikeCustomizerAgent()

    user32 = ctypes.windll.user32
    modifiers = MOD_WIN | MOD_ALT | MOD_NOREPEAT

    success = user32.RegisterHotKey(None, HOTKEY_ID, modifiers, VK_C)
    if not success:
        # Fallback without MOD_NOREPEAT if older Windows API
        modifiers = MOD_WIN | MOD_ALT
        success = user32.RegisterHotKey(None, HOTKEY_ID, modifiers, VK_C)

    if not success:
        print("[-] Error: Failed to register global hotkey [Win + Alt + C]. It may be reserved by another app.")
        return False

    print("=" * 65)
    print("  JARVIS X - AGENT MIKE GLOBAL HOTKEY LISTENER")
    print("  Trigger: [Win + Alt + C] -> Instant Aesthetic Harmonization")
    print("=" * 65)
    print("[+] Hotkey [Win + Alt + C] successfully registered in Windows kernel.")
    print("[*] Listening for desktop hotkey events... (Ctrl+C to exit)")

    msg = MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                print("\n[EVENT] >>> [Win + Alt + C] Pressed! Initiating Instant Refresh...")
                res = mike.sync(force=True)
                print(f"[+] Wallpaper       : {res.get('wallpaper_title')}")
                print(f"[+] Theme Matched   : {res.get('theme_name')}")
                print(f"[+] Clock Position  : {res.get('placement')}")
                print(f"[+] Accent Color    : {res.get('accent_color')}")
                print(f"[+] Windows Taskbar : Synced ({res.get('windows_accent_synced')})")
                print(f"[+] Audio Visualizer: Repositioned & Dynamic Palette Applied")
                
                # Feedback chime
                try:
                    winsound.MessageBeep(winsound.MB_OK)
                except Exception:
                    pass

                if run_once:
                    break

            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        print("\n[*] Hotkey listener interrupted by user.")
    finally:
        user32.UnregisterHotKey(None, HOTKEY_ID)
        print("[+] Hotkey [Win + Alt + C] unregistered cleanly.")

    return True


if __name__ == "__main__":
    mike_inst = MikeCustomizerAgent()
    listen_for_hotkey(mike_inst)
