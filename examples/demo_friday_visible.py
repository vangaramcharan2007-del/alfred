import os
import sys
import asyncio
import tempfile
import time
import subprocess
import json

if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\ffmpeg-shared\ffmpeg-master-latest-win64-gpl-shared\bin")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jarvisx.runtime import create_default_runtime
from jarvisx.core.state import update_agent_state

def ensure_demo_config():
    os.makedirs("config", exist_ok=True)
    with open(os.path.join("config", "demo.json"), "w") as f:
        json.dump({
            "demo_mode": True,
            "typing_speed": 0.02,
            "action_delay": 2,
            "verbose_narration": True
        }, f)

async def play_tts(voice_manager, text):
    print(f"\n[Friday]: {text}")
    print("[Jarvis X] Synthesizing TTS narration...")
    audio_bytes = voice_manager.synthesize_for_agent("Friday", text)
    if audio_bytes and len(audio_bytes) > 50:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        if os.name == 'nt':
            os.startfile(tmp_path)
            # Give it some time to speak before continuing
            await asyncio.sleep(len(text) * 0.06)

async def main():
    print("[Jarvis X] Booting Visible Coding Demonstration...")
    
    ensure_demo_config()
    update_agent_state("friday", "friday_introduced", True) # Skip intro
    update_agent_state("friday", "friday_greeted", False)
    update_agent_state("friday", "mission_stage", "idle")
    
    runtime = create_default_runtime()
    voice_manager = runtime.voice_manager
    
    print("\n--------------------------------------------------")
    user_input = "Friday, create the NumPy tutorial programs."
    print(f"You:\n{user_input}\n")
    
    response = await runtime.alfred.process(user_input, trace_id="live-demo-numpy-visible")
    
    # In Demo Mode, Friday responds with a block of text, but the physical actions 
    # were taken in real time. We will just print her response for now, 
    # or narrate it segment by segment (though the file was already typed during handle())
    # For a true asynchronous narration, we'd use events. We'll just play it out.
    await play_tts(voice_manager, response.message)
    
    print("\n--------------------------------------------------")
    user_input_2 = "yes"
    print(f"You:\n{user_input_2}\n")
    
    response_2 = await runtime.alfred.process(user_input_2, trace_id="live-demo-execute")
    await play_tts(voice_manager, response_2.message)
    
    print("\n--------------------------------------------------")
    user_input_3 = "yes"
    print(f"You:\n{user_input_3}\n")
    
    response_3 = await runtime.alfred.process(user_input_3, trace_id="live-demo-explain")
    await play_tts(voice_manager, response_3.message)
    
    print("\n[Jarvis X] Demonstration Complete.")

if __name__ == "__main__":
    asyncio.run(main())
