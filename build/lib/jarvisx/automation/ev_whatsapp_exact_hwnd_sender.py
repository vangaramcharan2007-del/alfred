"""
Exact HWND-Targeted WhatsApp Message Sender.
============================================
Finds the exact WhatsApp window handle, computes the relative coordinates of the
message input box, clicks it, pastes the 1D Heat Equation derivation, and presses Enter.
"""

import time
import os
import sys
import pyperclip
import pyautogui
import ctypes

pyautogui.FAILSAFE = False

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from jarvisx.automation.ev_neural_voice import speak_ev_neural


def send_exact_hwnd():
    print("=" * 78)
    print(" 🕷️ EXACT HWND WHATSAPP SENDER")
    print("=" * 78)

    whatsapp_msg = (
        "🕷️ *E-V MAX // Dr. E. Suresh 1D Heat Equation Derivation*\n\n"
        "📌 *Problem Statement*:\n"
        "Solve ∂u/∂t = α² ∂²u/∂x² with u(0,t)=0, u(20,t)=0, and u(x,0)=f(x) for length l=20.\n\n"
        "🔹 *Step 1: Suitable Separation of Variables Solution*:\n"
        "u(x,t) = (C1 cos px + C2 sin px) * exp(-α² p² t)\n\n"
        "🔹 *Step 2: Apply Boundary Conditions*:\n"
        "1. u(0,t) = 0 => C1 = 0\n"
        "2. u(20,t) = 0 => sin(20p) = 0 => 20p = nπ => p = nπ / 20\n\n"
        "🔹 *Step 3: Most General Solution (Principle of Superposition)*:\n"
        "u(x,t) = sum_{n=1}^∞ c_n * sin(nπx / 20) * exp(-n²π²α²t / 400)\n\n"
        "🔹 *Step 4: Fourier Sine Coefficient*:\n"
        "c_n = (2/20) ∫[0 to 20] f(x) sin(nπx / 20) dx = (1/10) ∫[0 to 20] f(x) sin(nπx / 20) dx\n\n"
        "💡 *Exam Tip*: Since boundaries are zero at both ends (u=0), always choose the negative separation constant -p² so the temperature decays exponentially with time t -> ∞!"
    )

    pyperclip.copy(whatsapp_msg)
    print("[*] Copied mathematical derivation to clipboard.")

    user32 = ctypes.windll.user32

    # Find WhatsApp Window
    def enum_windows_proc(hwnd, lParam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            if "WhatsApp" in title and user32.IsWindowVisible(hwnd):
                lParam.append((hwnd, title))
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.py_object))
    windows = []
    user32.EnumWindows(EnumWindowsProc(enum_windows_proc), ctypes.byref(ctypes.py_object(windows)))

    if not windows:
        print("[!] WhatsApp window not found by title.")
        return

    hwnd, title = windows[0]
    print(f"[+] Found WhatsApp HWND: {hwnd} ('{title}')")

    # Restore and bring to foreground
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    # Get window rect
    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long),
                    ('right', ctypes.c_long), ('bottom', ctypes.c_long)]

    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    print(f"[+] Window Rect: left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom} (w={w}, h={h})")

    # Compute target input box location inside the WhatsApp window
    # The input text field is at roughly 65% width and 35px from bottom of the window
    input_x = rect.left + int(0.65 * w)
    input_y = rect.bottom - 40

    print(f"[*] Targeting exact input box at ({input_x}, {input_y})...")
    pyautogui.click(input_x, input_y)
    time.sleep(0.3)

    print("[*] Pasting text (Ctrl+V)...")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)

    print("[*] Sending message (Enter)...")
    pyautogui.press('enter')
    print("[✓] Derivation successfully sent to WhatsApp!")

    speak_ev_neural("Derivation posted directly into your WhatsApp chat, boss!")


if __name__ == "__main__":
    send_exact_hwnd()
