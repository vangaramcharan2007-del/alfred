import os
import sys
import time

sys.path.insert(0, os.path.abspath("src"))

# Mock STT to inject test text
os.environ["MOCK_STT"] = "1"
os.environ["MOCK_CHROME_FAIL"] = "1" # Force verification failure on Chrome to trigger fallback

import builtins
from jarvisx.core.voice.voice_runtime import VoiceRuntime

# Override the input() built-in temporarily to simulate speech
_original_input = builtins.input

class MockSTT:
    def __init__(self, sequence):
        self.sequence = sequence
        self.idx = 0
        
    def __call__(self, prompt=""):
        if self.idx < len(self.sequence):
            val = self.sequence[self.idx]
            self.idx += 1
            print(f"{prompt}{val}")
            time.sleep(1)
            return val
        time.sleep(1)
        return "exit alfred"

def run_demo():
    print("\n--- JARVIS X PHASE B DEMONSTRATION ---\n")
    
    # We want to test:
    # 1. State machine transitions
    # 2. Permission voice callback
    # 3. Verification failure & fallback
    
    # Mock inputs:
    # 1. Ask to open github
    # 2. Approve permission
    
    test_sequence = [
        "Open Github",
        "yes", # Approve permission
        "exit alfred"
    ]
    
    builtins.input = MockSTT(test_sequence)
    
    runtime = VoiceRuntime(use_microphone=False)
    
    try:
        runtime.run_conversation_loop()
    finally:
        builtins.input = _original_input
        print("\n--- DEMO COMPLETE ---")

if __name__ == "__main__":
    run_demo()
