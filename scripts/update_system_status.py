import os
import sys
import json
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scripts.get_battery import get_battery_info
STATUS_FILE = os.path.join(PROJECT_ROOT, "src", "jarvisx", "gui", "system_status.json")

def update_status():
    b = get_battery_info()
    username = os.getenv("USERNAME", "Hokage")
    data = {
        "battery": b["percent"],
        "charging": b["charging"],
        "username": username,
        "timestamp": time.time(),
        "video_path": "file:///E:/naruto-endless-sky.3840x2160.mp4"
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data

if __name__ == "__main__":
    d = update_status()
    print(f"[STATUS UPDATED] Battery: {d['battery']}%, Charging: {d['charging']}, User: {d['username']}")
