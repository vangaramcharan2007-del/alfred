import os
import sys
import asyncio
import tempfile
import time

# Ensure src is in path for local execution
if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\ffmpeg-shared\ffmpeg-master-latest-win64-gpl-shared\bin")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jarvisx.runtime import create_default_runtime

async def main():
    print("[Jarvis X] Initializing runtime...")
    runtime = create_default_runtime()
    voice_manager = runtime.voice_manager
    
    print("\n[Jarvis X] Available Voice Configurations:")
    for agent in ["Alfred", "Friday", "Edith"]:
        config = voice_manager.get_voice_config(agent)
        print(f"  - {agent}: {config}")
        
    print("\n--------------------------------------------------")
    
    # 1. Alfred speaking
    print("[Jarvis X] Testing Alfred's voice (pyttsx3 default fallback)...")
    alfred_text = "Hello, I am Alfred. Let me introduce you to our newest team member."
    print(f"Text: '{alfred_text}'")
    # Actually, pyttsx3 provider just returns a dummy byte string and plays audio natively if we set it up,
    # but in our current pyttsx3 provider we just return b"[pyttsx3 TTS] ..." so we will simulate it with local pyttsx3 here.
    import pyttsx3
    engine = pyttsx3.init()
    engine.say(alfred_text)
    engine.runAndWait()
    
    print("\n--------------------------------------------------")
    
    # 2. Friday speaking (f5_tts)
    print("[Jarvis X] Testing Friday's cloned voice (F5-TTS)...")
    friday_text = "Friday, introduce yourself."
    print(f"User: '{friday_text}'")
    
    response_text = "Hello, I am Friday. My neural pathways are fully integrated, and I am online."
    print(f"Friday: '{response_text}'")
    
    print("\n[Jarvis X] Generating cloned voice audio. This may take a few seconds on CPU...")
    start_time = time.time()
    
    # Use the VoiceManager to synthesize
    audio_bytes = voice_manager.synthesize_for_agent("Friday", response_text)
    
    elapsed = time.time() - start_time
    print(f"[Jarvis X] Audio generated in {elapsed:.2f} seconds.")
    
    if audio_bytes and len(audio_bytes) > 100:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        print(f"[Jarvis X] Playing Friday's voice from {tmp_path}...")
        if os.name == 'nt':
            os.startfile(tmp_path)
            # Give it time to open before the script exits
            await asyncio.sleep(5)
        else:
            print("[Jarvis X] Open the file manually to hear the audio.")
    else:
        print("[Jarvis X] Failed to generate valid audio bytes. Fallback might have occurred.")

if __name__ == "__main__":
    asyncio.run(main())
