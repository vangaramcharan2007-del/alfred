"""
Offline Windows Native Speech Engine for E-V & Alfred.
======================================================
Provides zero-internet local text-to-speech fallback using SAPI5 / PowerShell.
"""

import os
import sys
import tempfile
import subprocess
import logging

logger = logging.getLogger("jarvisx.voice.offline")


def speak_offline(text: str, voice_gender: str = "male") -> bool:
    """Speaks text using local Windows SAPI when internet is disconnected."""
    if not text or not text.strip():
        return False

    clean_text = text.replace('"', '').replace("'", "").replace("\n", " ").strip()
    
    # 1. Method 1: SAPI VBScript dispatch (low latency <0.05s)
    try:
        temp_dir = tempfile.gettempdir()
        vbs_path = os.path.join(temp_dir, f"offline_speak_{os.getpid()}.vbs")
        
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(f'Set voice = CreateObject("SAPI.SpVoice")\n')
            f.write(f'voice.Rate = 0\n')
            f.write(f'voice.Volume = 100\n')
            f.write(f'voice.Speak "{clean_text}"\n')
            f.write(f'Set voice = Nothing\n')

        subprocess.run(["cscript.exe", "//nologo", vbs_path], check=True, timeout=15)
        try:
            os.remove(vbs_path)
        except Exception:
            pass
        return True
    except Exception as e:
        logger.debug(f"[OfflineSpeaker] SAPI VBS failed: {e}")

    # 2. Method 2: PowerShell System.Speech Fallback
    try:
        ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{clean_text}')"
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_cmd], check=True, timeout=15)
        return True
    except Exception as e:
        logger.debug(f"[OfflineSpeaker] PowerShell speech failed: {e}")

    return False


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Offline native speech test successful!"
    speak_offline(msg)
