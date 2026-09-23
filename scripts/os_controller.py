"""
Jarvis X - OS Puppet Master & App Controller
Provides direct, low-latency control over Windows apps, media playback, system volume, and hardware telemetry.
"""
import os
import sys
import ctypes
import time
import subprocess
import psutil

# Win32 Virtual Key Constants
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

user32 = ctypes.windll.user32

def _send_key(vk_code):
    user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    time.sleep(0.05)
    user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

# 1. Media Playback Controls
def media_play_pause():
    print("[*] Sending Media Play/Pause command...")
    _send_key(VK_MEDIA_PLAY_PAUSE)
    return "Toggled Media Play/Pause"

def media_next():
    print("[*] Sending Media Next Track command...")
    _send_key(VK_MEDIA_NEXT_TRACK)
    return "Skipped to Next Track"

def media_prev():
    print("[*] Sending Media Previous Track command...")
    _send_key(VK_MEDIA_PREV_TRACK)
    return "Returned to Previous Track"

# 2. Volume Controls (via pycaw)
def get_volume():
    try:
        from pycaw.pycaw import AudioUtilities
        device = AudioUtilities.GetSpeakers()
        vol = device.EndpointVolume
        current = round(vol.GetMasterVolumeLevelScalar() * 100)
        is_muted = bool(vol.GetMute())
        return {"volume_percent": current, "is_muted": is_muted}
    except Exception as e:
        return {"error": str(e)}

def set_volume(percent):
    try:
        from pycaw.pycaw import AudioUtilities
        percent = max(0, min(100, int(percent)))
        device = AudioUtilities.GetSpeakers()
        vol = device.EndpointVolume
        vol.SetMasterVolumeLevelScalar(percent / 100.0, None)
        print(f"[+] Master volume set to {percent}%")
        return f"Volume set to {percent}%"
    except Exception as e:
        print("[!] pycaw volume error:", e)
        return str(e)


# 3. System Telemetry & Sentinel
def get_telemetry():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    
    data = {
        "cpu_percent": cpu,
        "ram_percent": mem.percent,
        "ram_used_gb": round(mem.used / (1024**3), 2),
        "ram_total_gb": round(mem.total / (1024**3), 2),
        "battery_percent": battery.percent if battery else None,
        "power_plugged": battery.power_plugged if battery else None
    }
    return data

# 4. App Launcher
APP_MAP = {
    "spotify": r"spotify.exe",
    "terminal": r"wt.exe",
    "notepad": r"notepad.exe",
    "explorer": r"explorer.exe",
    "code": r"code.cmd"
}

def launch_app(app_name):
    target = APP_MAP.get(app_name.lower(), app_name)
    print(f"[*] Launching {app_name} ({target})...")
    subprocess.Popen([r"cmd.exe", "/c", "start", "", target], shell=False)
    return f"Launched {app_name}"

def play_chime(sound_name="success"):
    try:
        import winsound
        sound_file = os.path.join(os.path.dirname(__file__), "..", "var", "sounds", f"jarvis_{sound_name}.wav")
        if os.path.exists(sound_file):
            winsound.PlaySound(os.path.abspath(sound_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "play" or cmd == "pause":
            media_play_pause()
            play_chime("notify")
        elif cmd == "next":
            media_next()
            play_chime("notify")
        elif cmd == "prev":
            media_prev()
            play_chime("notify")
        elif cmd == "volume" and len(sys.argv) > 2:
            set_volume(sys.argv[2])
            play_chime("notify")
        elif cmd == "get-volume":
            print(get_volume())
        elif cmd == "telemetry":
            t = get_telemetry()
            print("=== Jarvis System Telemetry ===")
            print(f"  CPU Load:        {t['cpu_percent']}%")
            print(f"  RAM Usage:       {t['ram_percent']}% ({t['ram_used_gb']} GB / {t['ram_total_gb']} GB)")
            if t['battery_percent'] is not None:
                plug_str = "Plugged in (AC)" if t['power_plugged'] else "On Battery"
                print(f"  Battery:         {t['battery_percent']}% [{plug_str}]")
            play_chime("success")
        elif cmd == "launch" and len(sys.argv) > 2:
            launch_app(sys.argv[2])
            play_chime("success")
        else:
            print("Usage: python os_controller.py [play|next|prev|volume <0-100>|get-volume|telemetry|launch <app>]")
    else:
        print("Usage: python os_controller.py [play|next|prev|volume <0-100>|get-volume|telemetry|launch <app>]")
