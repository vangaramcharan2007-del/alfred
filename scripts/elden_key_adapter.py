"""
Alfred Elden Ring Smart Key Adapter (v2.0 - PC Gamer Edition)
Remaps Elden Ring controls to standard PC gaming controls:
- 1 -> HEALING FLASK (Quick Pouch Top: 'e' + 'up')
- 2 -> TORRENT (Quick Pouch Left: 'e' + 'left')
- 3 -> OTHER POTION / PHYSICK (Quick Pouch Right: 'e' + 'right')
- 4 -> SUMMONS / SPIRIT ASHES (Quick Pouch Bottom: 'e' + 'down')
- Spacebar -> JUMP (sends 'f')
- Left Shift -> ROLL / SPRINT (sends 'space')
- Q -> SKILL / ASH OF WAR (sends 'shift + right-click')
- R -> STRONG / HEAVY ATTACK (sends 'shift + left-click')
- Z -> LOCK-ON TARGET (sends middle-click)

Only active when ELDEN RING is the active, focused window!
"""

import time
import sys
import threading
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

def send_pouch_combo(direction_key: str):
    """Executes 'e' + arrow key with precise timing for Elden Ring's engine."""
    try:
        keyboard.press('e')
        time.sleep(0.04)
        keyboard.press(direction_key)
        time.sleep(0.05)
        keyboard.release(direction_key)
        time.sleep(0.02)
        keyboard.release('e')
    except Exception as err:
        print(f"[!] Error sending pouch combo ({direction_key}): {err}")

def trigger_pouch(direction_key: str):
    threading.Thread(target=send_pouch_combo, args=(direction_key,), daemon=True).start()

def main():
    print("=" * 65)
    print("      ALFRED ELDEN RING SMART KEY ADAPTER (v2.0)")
    print("=" * 65)
    print(" [1] -> HEAL (Crimson Flask - Pouch Slot 1: 'e' + 'up')")
    print(" [2] -> TORRENT (Spectral Steed - Pouch Slot 2: 'e' + 'left')")
    print(" [3] -> OTHER POTION (Physick - Pouch Slot 3: 'e' + 'right')")
    print(" [4] -> SUMMONS (Wolves/Spirit - Pouch Slot 4: 'e' + 'down')")
    print(" [Spacebar]   -> JUMP (mapped to 'f')")
    print(" [Left Shift] -> SPRINT / ROLL (mapped to 'space')")
    print(" [Q]          -> ASH OF WAR / SKILL")
    print(" [R]          -> STRONG ATTACK")
    print(" [Z]          -> LOCK-ON TARGET")
    print("=" * 65)
    print("[*] Adapter is ACTIVE and monitors Elden Ring automatically.")
    print("[*] Typing in browser / other windows is 100% normal.")
    print("[*] Press Ctrl+C to stop.")
    print("=" * 65)

    shift_pressed = False

    def on_1(e):
        if is_elden_ring_active() and e.event_type == keyboard.KEY_DOWN:
            trigger_pouch('up')
            return False
        return True

    def on_2(e):
        if is_elden_ring_active() and e.event_type == keyboard.KEY_DOWN:
            trigger_pouch('left')
            return False
        return True

    def on_3(e):
        if is_elden_ring_active() and e.event_type == keyboard.KEY_DOWN:
            trigger_pouch('right')
            return False
        return True

    def on_4(e):
        if is_elden_ring_active() and e.event_type == keyboard.KEY_DOWN:
            trigger_pouch('down')
            return False
        return True

    def on_space(e):
        if is_elden_ring_active():
            if e.event_type == keyboard.KEY_DOWN:
                keyboard.press('f')
            elif e.event_type == keyboard.KEY_UP:
                keyboard.release('f')
            return False
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

    keyboard.hook_key('1', on_1, suppress=True)
    keyboard.hook_key('2', on_2, suppress=True)
    keyboard.hook_key('3', on_3, suppress=True)
    keyboard.hook_key('4', on_4, suppress=True)
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
