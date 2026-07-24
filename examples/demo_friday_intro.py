import os
import sys
import asyncio
import tempfile
import time
import subprocess

# Ensure src is in path for local execution
if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\ffmpeg-shared\ffmpeg-master-latest-win64-gpl-shared\bin")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jarvisx.runtime import create_default_runtime
from jarvisx.core.state import update_agent_state

async def play_tts(voice_manager, text):
    print(f"[Jarvis X] Synthesizing TTS narration...")
    import pyttsx3
    import threading
    
    def speak():
        script = (
            "import sys, pyttsx3\n"
            "engine = pyttsx3.init()\n"
            "voices = engine.getProperty('voices')\n"
            "for v in voices:\n"
            "    if 'Zira' in v.name or 'female' in v.name.lower():\n"
            "        engine.setProperty('voice', v.id)\n"
            "        break\n"
            "engine.setProperty('rate', 170)\n"
            "engine.say(sys.stdin.read())\n"
            "engine.runAndWait()\n"
        )
        import subprocess
        subprocess.run(["python", "-c", script], input=text.encode("utf-8"))
        
    t = threading.Thread(target=speak)
    t.start()
    
    # Optional small delay so voice starts
    await asyncio.sleep(0.5)

async def main():
    print("[Jarvis X] Booting live demonstration...")
    
    # Reset introduction state to ensure cinematic sequence fires
    update_agent_state("friday", "friday_introduced", False)
    update_agent_state("friday", "friday_greeted", False)
    
    runtime = create_default_runtime()
    voice_manager = runtime.voice_manager
    
    # 1. First request triggering Alfred and the cinematic intro
    user_input = "Alfred, create the NumPy tutorial programs."
    print(f"\nUser: {user_input}")
    
    response = await runtime.alfred.process(user_input, trace_id="live-demo-numpy")
    
    # Handle possible audio event returned in response
    if response.data and "events" in response.data:
        for ev in response.data["events"]:
            if ev.get("type") == "audio" and ev.get("action") == "play_once":
                audio_file = ev.get("file")
                audio_path = os.path.abspath(os.path.join("assets", "voices", audio_file))
                print(f"[Jarvis X] TRIGGERING CINEMATIC EVENT: Playing {audio_file} once...")
                if os.path.exists(audio_path) and os.name == 'nt':
                    os.startfile(audio_path)
                    await asyncio.sleep(4) # Let it play for a moment

    print(f"\nResponse (Text Output):\n{response.message}\n")
    
    # Voice Over using TTS for the dynamic text
    await play_tts(voice_manager, response.message)
            
    # Verify files
    print("\n[Jarvis X] Verifying created files...")
    for f in ["numpy_indexing.py", "numpy_basics.py", "numpy_random.py"]:
        path = os.path.join("jarvis_workspace", f)
        print(f"  - {f}: {'Exists' if os.path.exists(path) else 'Missing'}")

    # 2. Trigger explanation mode
    print("\n--------------------------------------------------")
    user_input_2 = "Yes"
    print(f"\nUser: {user_input_2}")
    
    response_2 = await runtime.alfred.process(user_input_2, trace_id="live-demo-explanation")
    print(f"\nFriday (Text Output):\n{response_2.message}\n")
    
    await play_tts(voice_manager, response_2.message)

if __name__ == "__main__":
    asyncio.run(main())
