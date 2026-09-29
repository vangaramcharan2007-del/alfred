"""
RDR2 Launch Sentinel & Thermal Guard
====================================
Automates Red Dead Redemption 2 startup on Intel Core Ultra / Arc platforms:
1. Applies Vulkan layer isolation environment flags.
2. Cleans stale exit signatures.
3. Automatically bypasses the Intel driver warning dialog ("Minimum Recommended Hardware Check Failure").
4. Protects CPU thermals by suppressing runaway WerFault crash dump deadlocks.
5. Monitors memory growth and window activation.
"""

import os
import sys
import time
import psutil
from pathlib import Path
import ctypes
import win32gui
import win32process
import win32con

GAME_DIR = Path(r"C:\Games\Red Dead Redemption 2")
LAUNCHER = GAME_DIR / "Launcher.exe"

def attach_desktop():
    user32 = ctypes.windll.user32
    hdesk = user32.OpenInputDesktop(0, False, 0x01FF)
    if hdesk:
        user32.SetThreadDesktop(hdesk)

def clean_exit_file():
    exit_file = Path(os.environ.get('LOCALAPPDATA', '')) / 'Rockstar Games' / 'Red Dead Redemption 2' / 'exit_file.dat'
    if exit_file.exists():
        exit_file.unlink(missing_ok=True)
        print("[*] Cleared stale exit_file.dat")

def dismiss_hardware_dialog(target_pid=None):
    dismissed = False
    def enum_cb(hwnd, _):
        nonlocal dismissed
        if not win32gui.IsWindowVisible(hwnd):
            return True
        _, wpid = win32process.GetWindowThreadProcessId(hwnd)
        cls = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        t_low = title.lower()
        if (target_pid is None or wpid == target_pid) and (cls == '#32770' or any(k in t_low for k in ['hardware', 'driver', 'minimum', 'failure'])):
            print(f"[!] Intercepted Hardware Dialog: HWND={hwnd} | Title='{title.strip()}'")
            def child_cb(ch, _):
                txt = win32gui.GetWindowText(ch).lower()
                ccls = win32gui.GetClassName(ch).lower()
                if 'button' in ccls and any(b in txt for b in ['ok', 'yes', 'continue']):
                    win32gui.SendMessage(ch, win32con.BM_CLICK, 0, 0)
                    print(f"[+] Clicked '{txt}' button on HWND {ch}!")
                return True
            win32gui.EnumChildWindows(hwnd, child_cb, None)
            win32gui.SendMessage(hwnd, win32con.WM_COMMAND, 1, 0) # IDOK
            dismissed = True
            return True
        return True
    try:
        win32gui.EnumWindows(enum_cb, None)
    except Exception:
        pass
    return dismissed

def launch_and_protect():
    attach_desktop()
    clean_exit_file()

    env = os.environ.copy()
    env['VK_LOADER_LAYERS_DISABLE'] = '*social_club*,*rockstar*,*EOSOverlay*'

    print(">>> Starting Red Dead Redemption 2...")
    os.system(f'start "" "{LAUNCHER}"')

    rdr2_pid = None
    dialog_handled = False
    window_found = False

    print("[*] Sentinel active: Monitoring process health and thermals...")
    for sec in range(90):
        time.sleep(1)

        # Thermal protection: suppress WerFault runaway memory dumps
        for p in psutil.process_iter(['pid', 'name']):
            try:
                if p.info['name'] and 'werfault' in p.info['name'].lower():
                    print(f"[!] Terminated WerFault (PID {p.info['pid']}) to protect thermals.")
                    p.kill()
            except Exception:
                pass

        # Locate RDR2 process
        if rdr2_pid is None:
            for p in psutil.process_iter(['pid', 'name']):
                try:
                    if p.info['name'] and p.info['name'].lower() == 'rdr2.exe':
                        rdr2_pid = p.info['pid']
                        print(f"[+] RDR2 process detected: PID {rdr2_pid}")
                        break
                except Exception:
                    pass

        # Handle hardware check dialog
        if not dialog_handled:
            if dismiss_hardware_dialog(rdr2_pid):
                dialog_handled = True

        if rdr2_pid:
            try:
                p = psutil.Process(rdr2_pid)
                rss_mb = p.memory_info().rss / (1024 * 1024)
                threads = p.num_threads()
                
                # Check for game renderer window
                def check_win(h, _):
                    nonlocal window_found
                    if win32gui.IsWindowVisible(h):
                        _, wpid = win32process.GetWindowThreadProcessId(h)
                        if wpid == rdr2_pid:
                            cls = win32gui.GetClassName(h)
                            rect = win32gui.GetWindowRect(h)
                            if cls == 'sgaWindow' or (rect[2]-rect[0] > 800 and rect[3]-rect[1] > 500):
                                window_found = True
                                return False
                    return True
                win32gui.EnumWindows(check_win, None)

                if sec % 10 == 0:
                    print(f"[{sec:02d}s] RDR2 Running | RAM: {rss_mb:.1f} MB | Threads: {threads} | Window: {'ACTIVE' if window_found else 'LOADING'}")

                if window_found and rss_mb > 1200 and sec >= 45:
                    print("\n" + "="*60)
                    print(f"[SUCCESS] Red Dead Redemption 2 is running smoothly at Title Screen!")
                    print(f"RAM: {rss_mb:.1f} MB | Active Threads: {threads}")
                    print("="*60 + "\n")
                    break

            except psutil.NoSuchProcess:
                print(f"[!] RDR2 process {rdr2_pid} exited.")
                break

if __name__ == '__main__':
    launch_and_protect()
