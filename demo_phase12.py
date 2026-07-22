import os
import sys
import time
from pathlib import Path

def run_demo():
    sys.path.insert(0, os.path.abspath("src"))
    
    # 1. Setup Preferences (Phase 12.3)
    pref_file = Path("var/preferences.json")
    pref_file.parent.mkdir(parents=True, exist_ok=True)
    with open(pref_file, "w") as f:
        f.write('{"references": {"my editor": {"target": "vscode", "confidence": 5}}}')
        
    # Set MOCK_STT=1 to auto-approve permissions initially so it doesn't hang in CI
    # But wait, we want to test Interactive Permission (Phase 12.2).
    # We will simulate input by mocking the input() function or just letting the user see it!
    # Let's mock input just for the script, but print the prompts so the user sees it.
    
    from jarvisx.core.voice.voice_runtime import VoiceRuntime
    
    # Mock TTS and Input
    class MockTTS:
        def speak(self, text):
            print(f"Alfred: \"{text}\"")
        def list_voices(self): return []
        def get_current_voice(self): return "Mock"
        
    runtime = VoiceRuntime(use_microphone=False)
    runtime.tts = MockTTS()
    
    # Mocking input to automatically say "y" when PermissionManager calls it
    original_input = __builtins__.input
    def auto_yes_input(prompt):
        print(f"{prompt}y")
        return "y"
    __builtins__.input = auto_yes_input
    
    print("\n--- PHASE 12.3: ALFRED MEMORY & PHASE 12.2: PERMISSIONS ---")
    print("User: \"Alfred, open my editor\"")
    # This should resolve to "vscode" and ask for permission
    runtime._process_command("open my editor")
    
    print("\n--- PHASE 12.1: RUNTIME RELIABILITY (FALLBACK) ---")
    print("User: \"Open GitHub\" (but Chrome is going to crash)")
    
    # Simulate Chrome crash
    os.environ["MOCK_CHROME_FAIL"] = "1"
    runtime._process_command("open GitHub")
    os.environ["MOCK_CHROME_FAIL"] = "0"
    
    print("\nDemo Complete! Restoring input...")
    __builtins__.input = original_input

if __name__ == "__main__":
    run_demo()
