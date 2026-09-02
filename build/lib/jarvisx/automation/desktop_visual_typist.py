"""Desktop Visual Typist Utility for Jarvis X (Layer 7 - Interface & Automation).

Simulates visual character-by-character typing directly into an active desktop application window.
"""

import time
import sys
import os

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def type_into_active_window(text: str, delay_between_chars: float = 0.03) -> bool:
    """Type given text character-by-character into whatever window is currently focused on your desktop."""
    if not PYAUTOGUI_AVAILABLE:
        print("[VisualTypist] pyautogui library not installed. Installing or falling back to standard print...")
        return False

    print(f"[VisualTypist] Starting visual typing in 3 seconds... Please click your target window now!")
    for i in range(3, 0, -1):
        print(f"  Counting down: {i}...")
        time.sleep(1)

    pyautogui.typewrite(text, interval=delay_between_chars)
    print("[VisualTypist] Visual typing completed successfully!")
    return True


if __name__ == "__main__":
    sample_code = """import numpy as np

B = np.array([3, 5, 7])
print("Array B =", B)
"""
    type_into_active_window(sample_code)
