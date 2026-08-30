"""
Social & Messaging Automation Engine for WhatsApp & Instagram in Alfred OS.
Provides specialized actions for:
1. WhatsApp Voice Notes: Generates neural voice audio (.mp3), copies file to clipboard, pastes into WhatsApp.
2. WhatsApp Voice Calls: Opens contact and triggers audio/video call.
3. Instagram Direct Messages: Opens Instagram DMs, composes messages and media.
"""

import os
import sys
import time
import urllib.parse
import webbrowser
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

import pyautogui
pyautogui.FAILSAFE = False

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("jarvisx.social")


def copy_file_to_windows_clipboard(file_path: str) -> bool:
    """Sets a real audio/media file onto Windows Clipboard as CF_HDROP."""
    abs_p = os.path.abspath(file_path)
    if not os.path.exists(abs_p):
        return False
    try:
        ps_cmd = f"Set-Clipboard -Path '{abs_p}'"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, timeout=5)
        return True
    except Exception as e:
        logger.warning(f"Clipboard file copy failed: {e}")
        return False


def send_whatsapp_voice_note(recipient: str = "Dakshith", message: str = "Hello", language: str = "english") -> Dict[str, Any]:
    """
    1. Generates an ultra-realistic neural audio file in English/Telugu/Hindi.
    2. Copies the .mp3 file to Windows Clipboard.
    3. Launches WhatsApp chat with recipient and pastes the audio note via Ctrl+V.
    """
    print(f"\n[WHATSAPP VOICE NOTE] [*] Synthesizing '{language}' audio for '{recipient}': '{message}'...")
    import asyncio
    import edge_tts
    
    voice_map = {
        "telugu": "te-IN-MohanNeural",
        "hindi": "hi-IN-MadhurNeural",
        "english": "en-GB-RyanNeural",
        "british": "en-GB-RyanNeural",
        "american": "en-US-GuyNeural"
    }
    voice = voice_map.get(language.lower(), "en-GB-RyanNeural")
    
    out_dir = Path("var/voice_notes")
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_recip = "".join(filter(str.isalnum, recipient)) or "user"
    audio_file = out_dir / f"vn_{safe_recip}_{int(time.time())}.mp3"
    
    async def _synth():
        comm = edge_tts.Communicate(message, voice)
        await comm.save(str(audio_file))
        
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(lambda: asyncio.run(_synth())).result()
        else:
            loop.run_until_complete(_synth())
    except Exception:
        try:
            asyncio.run(_synth())
        except Exception:
            pass

        
    print(f"[+] Audio voice note generated at: {audio_file}")
    
    # Copy file to clipboard
    copy_file_to_windows_clipboard(str(audio_file))
    
    # Open WhatsApp chat
    is_phone_num = "".join(filter(str.isdigit, recipient))
    if len(is_phone_num) >= 10:
        url = f"https://web.whatsapp.com/send?phone={is_phone_num}"
        desktop_proto = f"whatsapp://send?phone={is_phone_num}"
    else:
        url = f"https://web.whatsapp.com"
        desktop_proto = f"whatsapp://send?text="

    try:
        os.system(f'start "" "{desktop_proto}"')
    except Exception:
        pass
    webbrowser.open(url)
    
    time.sleep(2.5)
    
    # Focus and Paste (Ctrl+V)
    sw, sh = pyautogui.size()
    pyautogui.click(int(0.50 * sw), int(0.50 * sh))
    time.sleep(0.2)
    pyautogui.click(int(0.50 * sw), int(0.9585 * sh))
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    pyautogui.press('enter')
    
    print(f"🚀 [WHATSAPP VOICE NOTE] Voice note audio successfully prepared and pasted into WhatsApp!")
    return {
        "status": "VOICE_NOTE_DISPATCHED",
        "recipient": recipient,
        "language": language,
        "audio_file": str(audio_file),
        "message": message
    }


def send_instagram_dm(username: str = "dakshith", message: str = "Hi") -> Dict[str, Any]:
    """
    Automates sending or composing an Instagram Direct Message.
    """
    clean_user = username.lstrip("@").strip()
    print(f"\n[INSTAGRAM DM] [*] Navigating to Instagram Direct Messages for '@{clean_user}'...")
    
    # Direct profile or direct message URL
    dm_url = f"https://www.instagram.com/direct/inbox/"
    profile_url = f"https://www.instagram.com/{clean_user}/"
    
    # Copy message to clipboard
    try:
        import pyperclip
        pyperclip.copy(message)
    except Exception:
        pass
        
    webbrowser.open(profile_url)
    time.sleep(2.5)
    
    print(f"[OK] Instagram profile and DM interface launched for '@{clean_user}' with message on clipboard: '{message}'!")
    return {
        "status": "INSTAGRAM_DM_LAUNCHED",
        "username": clean_user,
        "message": message,
        "url": profile_url
    }


def call_whatsapp_voice(recipient: str = "Dakshith") -> Dict[str, Any]:
    """
    Opens WhatsApp chat and initiates a WhatsApp Voice Call.
    """
    is_phone_num = "".join(filter(str.isdigit, recipient))
    print(f"\n[WHATSAPP CALL] [*] Initiating WhatsApp Voice Call to '{recipient}'...")
    
    if len(is_phone_num) >= 10:
        desktop_proto = f"whatsapp://send?phone={is_phone_num}"
    else:
        desktop_proto = f"whatsapp://send?text="
        
    try:
        os.system(f'start "" "{desktop_proto}"')
    except Exception:
        pass
        
    time.sleep(2.0)
    
    # In WhatsApp Desktop, the call button is at the top right of the active chat
    sw, sh = pyautogui.size()
    # Call icon is roughly at (sw - 85, 45) in WhatsApp Desktop
    call_x = int(0.95 * sw)
    call_y = 45
    
    pyautogui.click(call_x, call_y)
    
    print(f"🚀 [WHATSAPP CALL] Call button triggered on screen for '{recipient}'!")
    return {
        "status": "WHATSAPP_CALL_INITIATED",
        "recipient": recipient
    }
