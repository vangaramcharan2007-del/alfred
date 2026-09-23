import os
import mss
import io
import base64
import json
import urllib.request
from PIL import Image

env_path = r"c:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\.env"
openrouter_key = ""

with open(env_path) as f:
    for line in f:
        if line.startswith("OPENROUTER_API_KEY="):
            openrouter_key = line.split("=", 1)[1].strip().strip('"').strip("'")

def capture_screen_base64():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.thumbnail((1280, 800))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=75)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_screen(prompt="What application or window is on screen right now? Be brief."):
    print("Capturing screen...")
    b64_image = capture_screen_base64()
    print("Screen captured! Sending to Vision AI...")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvisx.local",
        "X-Title": "Jarvis X Perception",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "model": "google/gemma-4-26b-a4b-it:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    }
                ]
            }
        ]
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            reply = data["choices"][0]["message"]["content"]
            print("\n=== Jarvis Screen Perception Result ===")
            print(reply)
            return reply
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code, e.read().decode())
        # Try fallback model
        payload["model"] = "openrouter/free"
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            reply = data["choices"][0]["message"]["content"]
            print("\n=== Jarvis Screen Perception (Fallback) ===")
            print(reply)
            return reply

if __name__ == "__main__":
    analyze_screen()
