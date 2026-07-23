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

async def main():
    print("[Jarvis X] Booting live demonstration...")
    runtime = create_default_runtime()
    voice_manager = runtime.voice_manager
    
    # 1. Orchestrate Request
    user_input = "friday open vscode explaining me array basics in python code"
    print(f"\nUser: {user_input}")
    
    response = await runtime.alfred.process(user_input, trace_id="live-demo")
    
    print(f"\nFriday (Text Output):\n{response.message}\n")
    
    # 2. Open VS Code dynamically using the computer tool/subprocess
    # We know Friday just created array_basics.py in the CWD.
    if os.path.exists("array_basics.py"):
        print("[Jarvis X] Instructing the host machine to open VS Code...")
        try:
            # Open VS Code. If 'code' isn't in path, try falling back to just opening the file directly.
            subprocess.Popen(["code", "array_basics.py"], shell=True)
        except Exception:
            os.startfile("array_basics.py")
            
    # 3. Voice Over
    print("[Jarvis X] Synthesizing Friday's voice narration...")
    start_time = time.time()
    audio_bytes = voice_manager.synthesize_for_agent("Friday", response.message)
    elapsed = time.time() - start_time
    print(f"[Jarvis X] Voice synthesized in {elapsed:.2f} seconds.")
    
    if audio_bytes and len(audio_bytes) > 100:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        print(f"[Jarvis X] Playing audio...")
        if os.name == 'nt':
            os.startfile(tmp_path)
            # Give it time to play the narration
            await asyncio.sleep(15)
        else:
            print("[Jarvis X] Open the file manually to hear the audio.")
    else:
        print("[Jarvis X] Failed to generate valid audio bytes. Voice fallback might have occurred.")

if __name__ == "__main__":
    asyncio.run(main())
