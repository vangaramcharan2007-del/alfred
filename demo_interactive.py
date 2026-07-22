import os
import sys

def run_interactive():
    sys.path.insert(0, os.path.abspath("src"))
    from jarvisx.core.voice.voice_runtime import VoiceRuntime
    
    print("Initializing Interactive Text Engine (No STT)...")
    print("Type your commands and press Enter. (Type 'exit' to quit)")
    print("\nStarting...\n")
    
    # Initialize with NO microphone. It will use input() for commands.
    runtime = VoiceRuntime(use_microphone=False)
    
    try:
        runtime.run_conversation_loop()
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    run_interactive()
