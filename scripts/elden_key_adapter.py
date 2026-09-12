"""
Alfred Elden Ring Smart Key Adapter:
Remaps awkward Elden Ring controls to standard PC gaming controls:
- Spacebar -> Jump (sends 'f')
- Left Shift -> Roll / Sprint (sends 'space')
- Q -> Skill / Ash of War (sends 'shift+right_click')
- R -> Strong Attack (sends 'shift+left_click')
- Z -> Lock-On (sends middle click)

Only active when ELDEN RING is the active, focused window!
"""

import time
import sys
import ctypes
from ctypes import wintypes
import keyboard
import pyautogui

user32 = ctypes.windll.user32

def get_foreground_window_title() -> str:
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

def is_elden_ring_active() -> bool:
    title = get_foreground_window_title().lower()
    return "elden ring" in title

def main():
    print("=" * 60)
    print("      ALFRED ELDEN RING SMART KEYBOARD ADAPTER")
    print("=" * 60)
    print("[+] Spacebar    -> JUMP (mapped to 'f')")
    print("[+] Left Shift  -> SPRINT / ROLL (mapped to 'space')")
    print("[+] Q           -> ASH OF WAR / SKILL")
    print("[+] R           -> STRONG ATTACK")
    print("[+] Z           -> LOCK-ON TARGET")
    print("[*] Adapter is ACTIVE and monitors Elden Ring automatically.")
    print("[*] Standard typing is preserved when you Alt-Tab out.")
    print("[*] Press Ctrl+C to exit.")
    print("=" * 60)

    # State tracking
    shift_pressed = False

    def on_space(e):
        if is_elden_ring_active():
            if e.event_type == keyboard.KEY_DOWN:
                keyboard.press('f')
            elif e.event_type == keyboard.KEY_UP:
                keyboard.release('f')
            return False  # Suppress original space
        return True

    def on_shift(e):
        nonlocal shift_pressed
        if is_elden_ring_active():
            if e.event_type == keyboard.KEY_DOWN and not shift_pressed:
                shift_pressed = True
                keyboard.press('space')
            elif e.event_type == keyboard.KEY_UP and shift_pressed:
                shift_pressed = False
                keyboard.release('space')
            return False
        return True

    def on_q(e):
        if is_elden_ring_active():
            if e.event_type == keyboard.KEY_DOWN:
                pyautogui.keyDown('shift')
                pyautogui.mouseDown(button='right')
            elif e.event_type == keyboard.KEY_UP:
                pyautogui.mouseUp(button='right')
                pyautogui.keyUp('shift')
            return False
        return True

    def on_r(e):
        if is_elden_ring_active():
            if e.event_type == keyboard.KEY_DOWN:
                pyautogui.keyDown('shift')
                pyautogui.mouseDown(button='left')
            elif e.event_type == keyboard.KEY_UP:
                pyautogui.mouseUp(button='left')
                pyautogui.keyUp('shift')
            return False
        return True

    def on_z(e):
        if is_elden_ring_active():
            if e.event_type == keyboard.KEY_DOWN:
                pyautogui.click(button='middle')
            return False
        return True

    keyboard.hook_key('space', on_space, suppress=True)
    keyboard.hook_key('left shift', on_shift, suppress=True)
    keyboard.hook_key('q', on_q, suppress=True)
    keyboard.hook_key('r', on_r, suppress=True)
    keyboard.hook_key('z', on_z, suppress=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Key Adapter stopped.")

if __name__ == "__main__":
    main()
