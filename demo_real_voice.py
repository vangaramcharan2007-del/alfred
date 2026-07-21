import os
import sys

def run_real_voice():
    sys.path.insert(0, os.path.abspath("src"))
    from jarvisx.core.voice.voice_runtime import VoiceRuntime
    
    print("Initializing Real Voice Engine...")
    print("Required Commands to Speak:")
    print("1. 'Alfred' (simulated by script waiting for input since we don't have Porcupine)")
    print("2. 'Open GitHub'")
    print("3. 'Create folder Demo'")
    print("4. 'Stop'")
    print("5. 'Exit'")
    print("\nStarting in 3 seconds...")
    import time
    time.sleep(3)
    
    runtime = VoiceRuntime(use_microphone=True)
    runtime.run_conversation_loop()

if __name__ == "__main__":
    run_real_voice()
