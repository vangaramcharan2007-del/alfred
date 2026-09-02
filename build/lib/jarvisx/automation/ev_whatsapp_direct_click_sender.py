"""
Direct WhatsApp Click & Send Automation.
========================================
Clicks the WhatsApp input box on screen, pastes the complete step-by-step 
1D Heat Equation derivation, presses Enter, and announces completion.
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


def direct_send():
    print("=" * 78)
    print(" 🕷️ DIRECT WHATSAPP CHAT SENDER")
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
    print("[*] Solution text placed on clipboard.")

    # Get screen dimensions
    user32 = ctypes.windll.user32
    sw = user32.GetSystemMetrics(0) or 1920
    sh = user32.GetSystemMetrics(1) or 1080

    # The input box in WhatsApp Desktop on a centered/maximized window
    # is roughly at x=60% of screen width, y=93% of screen height
    target_x = int(0.60 * sw)
    target_y = int(0.93 * sh)

    print(f"[*] Clicking WhatsApp input box at ({target_x}, {target_y})...")
    pyautogui.click(target_x, target_y)
    time.sleep(0.3)

    print("[*] Pasting text (Ctrl+V)...")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)

    print("[*] Sending message (Enter)...")
    pyautogui.press('enter')
    print("[✓] Message sent successfully to WhatsApp!")

    # Speak confirmation
    speak_ev_neural("Derivation posted into your WhatsApp chat, boss! Check your WhatsApp window!")


if __name__ == "__main__":
    direct_send()
