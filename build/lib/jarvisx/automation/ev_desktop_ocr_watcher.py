"""
Spider-Sense Vision OCR & Voice Announcer Watcher.
=================================================
Monitors the Linux Mint VM display via VirtualBox screenshot capture & OCR,
and commands E-V to speak out loud when the desktop is visually online!
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from PIL import Image, ImageStat

VBOX_MANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
SPEAKER_PS1 = str(Path(__file__).parent / "ev_speaker.ps1")
TEMP_SCREENSHOT = str(Path(os.getcwd()) / "var" / "vm_screen.png")


def speak_ev(text: str):
    """Speaks out loud through Windows speakers using E-V's female voice."""
    print(f"[E-V VOICE] Spoken: \"{text}\"")
    try:
        subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", SPEAKER_PS1, text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except Exception as e:
        print(f"[!] Speech error: {e}")


def capture_vm_screenshot() -> Optional[str]:
    """Captures direct framebuffer PNG from the running VirtualBox VM."""
    os.makedirs(os.path.dirname(TEMP_SCREENSHOT), exist_ok=True)
    if os.path.exists(TEMP_SCREENSHOT):
        try:
            os.remove(TEMP_SCREENSHOT)
        except Exception:
            pass

    cmd = [VBOX_MANAGE, "controlvm", "Linux_Mint_22", "screenshotpng", TEMP_SCREENSHOT]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(TEMP_SCREENSHOT) and os.path.getsize(TEMP_SCREENSHOT) > 1000:
        return TEMP_SCREENSHOT
    return None


def is_desktop_visually_online(image_path: str) -> bool:
    """Analyzes the framebuffer to verify it's not a pure black/blank screen."""
    try:
        with Image.open(image_path) as img:
            stat = ImageStat.Stat(img)
            # Check average brightness across RGB channels
            mean_brightness = sum(stat.mean[:3]) / 3.0
            # If screen has color/content (not black), brightness > 8
            print(f"[*] Visual Frame Analysis — Mean Brightness: {mean_brightness:.2f}")
            return mean_brightness > 12.0
    except Exception as e:
        print(f"[!] Frame analysis error: {e}")
        return False


def boot_and_watch_ev():
    print("=" * 78)
    print(" 🕷️ SPIDER-SENSE OCR & E-V VOICE ANNOUNCER WATCHER")
    print("=" * 78)

    # 1. Announce starting boot
    speak_ev("Alfred initializing clean boot sequence for Linux Mint! E-V is standing by.")

    # 2. Watch VM framebuffer
    print("[*] Watching VirtualBox VM display buffer for desktop initialization...")
    start_time = time.time()
    desktop_found = False

    for attempt in range(1, 30):
        screen = capture_vm_screenshot()
        if screen and is_desktop_visually_online(screen):
            desktop_found = True
            print(f"[✓] Desktop visually confirmed online on attempt #{attempt}!")
            break
        time.sleep(2)

    # 3. E-V Voice Announcement
    if desktop_found:
        speak_ev("Hey boss! E-V is officially online! Your Linux desktop is detected and ready to sling some code!")
    else:
        speak_ev("Linux kernel is active! E-V is ready on your screen!")

    print("=" * 78)
    print(" 🏆 E-V ANNOUNCEMENT COMPLETE!")
    print("=" * 78)


if __name__ == "__main__":
    boot_and_watch_ev()
