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
    print("[Jarvis X] Synthesizing TTS narration...")
    # Because Alfred injected text before Friday's, we can just render the whole response via Friday's voice,
    # or separate them. To match the spec exactly, we render the entire string here via VoiceManager (Zira).
    audio_bytes = voice_manager.synthesize_for_agent("Friday", response.message)
    if audio_bytes and len(audio_bytes) > 100:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        print(f"[Jarvis X] Playing TTS audio...")
        if os.name == 'nt':
            os.startfile(tmp_path)
            await asyncio.sleep(5)
            
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
    
    print("[Jarvis X] Synthesizing explanation TTS narration...")
    audio_bytes_2 = voice_manager.synthesize_for_agent("Friday", response_2.message)
    if audio_bytes_2 and len(audio_bytes_2) > 100:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes_2)
            tmp_path_2 = tmp.name
        
        print(f"[Jarvis X] Playing TTS audio...")
        if os.name == 'nt':
            os.startfile(tmp_path_2)

if __name__ == "__main__":
    asyncio.run(main())
